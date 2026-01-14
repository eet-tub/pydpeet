import gc
import os
import re

import pandas as pd

import logging

import pyarrow

from pydpeet.process.analyze.calculations.efficiency import add_internal_resistance, add_coulomb_efficiency
from pydpeet.process.analyze.calculations.throughput import calculate_average_positive_chargeThroughput, calculate_average_negative_charge_throughput
from pydpeet.process.analyze.calculations.utils import plot_columns, ColumnName, plot_single_column_all_files
from pydpeet.process.analyze.configs.step_analyzer_config import STEP_ANALYZER_PRIMITIVES_CONFIG, SEGMENT_SEQUENCE_CONFIG, \
    THRESHOLD_DICT
from pydpeet.process.analyze.calculations.campaign import CampaignBuilder
from pydpeet.process.merge.series import run_series, _sort_dfs
from pydpeet.process.analyze.calculations.soc_methods import SocMethod
from pydpeet.process.analyze.configs.battery_config import am23nmc


from pydpeet.convert.configs.config import Config
from pydpeet.convert.convert import convert
from pydpeet.convert.directory_standardization import directory_standardization
from pydpeet.convert.export import export
# from pydpeet.process.sequence.old_utils.CONFIG_function_calls import THRESHOLD_DICT_NEWARE
from pydpeet.process.sequence.step_analyzer import step_analyzer_primitives, step_analyzer_seqments_and_sequences
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
from collections import defaultdict

from pydpeet.process.sequence.utils.preprocessing.calculate_thresholds import calculate_minimum_definitive_differences

# for logging texts
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)





if __name__ == '__main__':

    # value for step_analyzer, for use with Basytec set on False, for Neware on True
    neware_bool = False

    convert_directory_with_ppb = True
    merge_parquet_files = True             # creates testseries from parquet files
    skip_already_merged_files = False
    add_new_columns = True
    skip_already_added_columns = False
    plot_new_Columns = True

    # paths to RAW Data and output for converted Data (.parquet files)
    input_dir_converting = r"D:\Daten_BA\RAW_new\Basytec_test"
    output_dir_converting = r"D:\Daten_BA\parquet_neu\Example_Usage\Basytec_test_parquet"

    # paths to Dat (.parquet files) and output for merged files (testseries)
    input_dir_merging = output_dir_converting
    output_dir_merging = r"D:\Daten_BA\parquet_neu\Example_Usage\Basytec_test_merged"

    # paths to Data with testseries and output for Data with added columns
    input_dir_adding_columns = output_dir_merging
    output_dir_adding_columns = r"D:\Daten_BA\parquet_neu\Example_Usage\Basytec_test_with_added_Columns"

    # path to Data with added columns for plotting
    input_dir_plotting = r"D:\Daten_BA\parquet_neu\Example_Usage\Basytec_test_with_added_Columns"

    # Regex to extract cells
    cell_pattern = re.compile(r"(AM\d+NMC\d+)")

    # --------------- Example for converting directory with ppb -------------------
    if convert_directory_with_ppb:
        if neware_bool:
            directory_standardization(config = Config.Neware, input_path = input_dir_converting, output_path = output_dir_converting)
        else:
            directory_standardization(config = Config.BaSyTec, input_path = input_dir_converting, output_path = output_dir_converting)

        print("\nProcessing complete.")

    # --------------- Example for converting directory with ppb -------------------

    # --------------- Example for merging parquet files with run_series -------------------

    if merge_parquet_files:
        os.makedirs(output_dir_merging, exist_ok=True)
        # Step 1: Find all parquet files and group by cell ID
        cell_files = defaultdict(list)

        for filename in os.listdir(input_dir_merging):
            if filename.endswith(".parquet"):
                match = cell_pattern.search(filename)
                if match:
                    cell_id = match.group(1)
                    filepath = os.path.join(input_dir_merging, filename)
                    cell_files[cell_id].append(filepath)

        # Step 2: Process each group of cell files
        for cell_id, file_list in cell_files.items():
            print(f"\nProcessing cell {cell_id} with {len(file_list)} files...")

            output_path_merged = os.path.join(output_dir_merging, f"{cell_id}_series.parquet")

            # Skip already processed files
            if skip_already_merged_files and os.path.exists(output_path_merged):
                print(f"Skipping {cell_id}, merged file already exists.")
                continue

            try:
                # Step 4: Read all parquet files into a list of DataFrames
                dfs = [pd.read_parquet(f) for f in file_list]

                # Step 5: Sort DataFrames and process them
                dfs_sorted = _sort_dfs(dfs)

                del dfs
                gc.collect()

                merged_df = run_series(dfs_sorted)

                del dfs_sorted
                gc.collect()

                # Step 6: Save merged DataFrame
                merged_df.to_parquet(output_path_merged, index=False)
                print(f"Saved merged series for {cell_id} -> {output_path_merged}")

                del merged_df
                gc.collect()

            except Exception as e:
                print(f"Error processing {cell_id}: {e}")

    # --------------- Example for merging parquet files with run_series -------------------

    # --------------- Example for using calculations funcions to add new columns (for whole directory) -------------------

    if add_new_columns:

        os.makedirs(output_dir_adding_columns, exist_ok=True)

        for filename in os.listdir(input_dir_adding_columns):
            if not filename.endswith(".parquet"):
                continue

            match = cell_pattern.search(filename)
            if not match:
                print(f"Skipping {filename}, no valid cell ID found.")
                continue

            cell_id = match.group(1)
            input_path = os.path.join(input_dir_adding_columns, filename)
            output_path = os.path.join(output_dir_adding_columns, f"{cell_id}_with_extra_columns.parquet")

            if skip_already_added_columns:
                # Skip already processed files
                if os.path.exists(output_path):
                    print(f"Skipping {filename}, output already exists.")
                    continue

            print(f"\nProcessing {filename} -> Cell {cell_id}")

            try:
                if neware_bool:
                    # Neware
                    MIN_DEFINITIVE_VOLTAGE_DIFFERENCE, MIN_DEFINITIVE_CURRENT_DIFFERENCE = calculate_minimum_definitive_differences(
                        *THRESHOLD_DICT)
                else:
                    # Basytec
                    MIN_DEFINITIVE_VOLTAGE_DIFFERENCE = 0.001
                    MIN_DEFINITIVE_CURRENT_DIFFERENCE = 0.001

                ####### depending on the Noise needs to be adjusted even for measurements of the same device #######
                SEGMENTS_TO_DETECT_CONFIG = [
                    # devide threshold by 2 because it's looking above and below the target line
                    ("Voltage[V]", MIN_DEFINITIVE_VOLTAGE_DIFFERENCE / 2),
                    ("Current[A]", MIN_DEFINITIVE_CURRENT_DIFFERENCE / 2),
                    ("Power[W]", (MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE) / 2),
                ]
                ####### depending on the Noise needs to be adjusted even for measurements of the same device #######
                # ORDER IS IMPORTANT!
                ADJUST_SEGMENTS_CONFIG = [
                    ("Voltage[V]", MIN_DEFINITIVE_VOLTAGE_DIFFERENCE),
                    ("Current[A]", MIN_DEFINITIVE_CURRENT_DIFFERENCE),
                    ("Power[W]", (MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE)),
                ]

                THRESHOLD_CV_SEGMENTS_0A_END = MIN_DEFINITIVE_CURRENT_DIFFERENCE

                # Load merged parquet
                df_merged = pd.read_parquet(input_path, engine="pyarrow")

                # Initialize campaign builder with config and cell name only
                builder = (
                    CampaignBuilder(df_merged, verbose=False)
                    .set_config(config=am23nmc)
                    .set_cell_name(name=cell_id)
                )

                # Build base campaign to hold the DataFrame
                campaign = builder.build()

                # Free up df_merged memory
                del df_merged
                gc.collect()

                # run step analyzer to get charge and discharge segments
                df_primitives = step_analyzer_primitives(
                    campaign,
                    STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
                    SEGMENTS_TO_DETECT_CONFIG=SEGMENTS_TO_DETECT_CONFIG,
                    ADJUST_SEGMENTS_CONFIG=ADJUST_SEGMENTS_CONFIG,
                    check_CV_0Aend_segments_bool=neware_bool,
                    WIDEN_CONSTANT_SEGMENTS_BOOL=neware_bool,
                    check_zero_length_segments_bool=neware_bool
                )

                df_segments_and_sequences = step_analyzer_seqments_and_sequences(
                    df_primitives,
                    SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG
                )

                rules = [
                    'CCCV_Charge',
                ]
                dfs_per_block_charge, _ = filter_and_split_df_by_blocks(
                    df_segments_and_sequences=df_segments_and_sequences,
                    df_primitives=df_primitives,
                    rules=rules,
                    combine_op='or',
                    also_return_filtered_df=True
                )

                rules = [
                    'CCCV_Discharge',
                ]
                dfs_per_block_Discharge, _ = filter_and_split_df_by_blocks(
                    df_segments_and_sequences=df_segments_and_sequences,
                    df_primitives=df_primitives,
                    rules=rules,
                    combine_op='or',
                    also_return_filtered_df=True
                )

                dfs_per_block_charge = _sort_dfs(dfs_per_block_charge)
                dfs_per_block_Discharge = _sort_dfs(dfs_per_block_Discharge)

                # run actual functions to add new columns (for new cells just adjust the config and the cell name)
                # if logging is not wanted, set verbose = False
                builder.set_df(campaign)

                # Add columns requiring df_primitives
                builder.add_capacity(df_primitives, neware_bool)
                builder.add_soh(df_primitives,neware_bool)
                builder.add_soc(
                    df_primitives,neware_bool,
                    standard_method=SocMethod.WITH_RESET_WHEN_FULL_AND_EMPTY,
                    methods=[SocMethod.WITH_RESET_WHEN_FULL_AND_EMPTY, SocMethod.WITHOUT_RESET],
                    restart_for_testindex=True
                )

                # Free primitives and segment DataFrames
                del df_primitives, df_segments_and_sequences
                gc.collect()

                # Add columns using charge/discharge splits
                builder.add_charge_throughput()
                builder.add_coulomb_efficiency(dfs_per_block_charge, dfs_per_block_Discharge)
                builder.add_power()
                builder.add_cumulative_energy()
                builder.add_equivalent_full_cycles()
                builder.add_internal_resistance(ignore_negative_resistance_values=False)

                # Free charge/discharge DataFrames
                del dfs_per_block_charge, dfs_per_block_Discharge
                gc.collect()

                # Save processed DataFrame
                final_df = builder.build()
                final_df.to_parquet(output_path, index=False)
                del final_df
                gc.collect()

                print(f"Saved {output_path}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue

        # finally:
        #     # Free memory safely
        #     for var in ["df_merged", "df_primitives", "df_segments_and_sequences",
        #
        #                 "dfs_per_block_charge", "dfs_per_block_Discharge", "campaign"]:
        #
        #         if var in locals():
        #             del locals()[var]
        #
        #     gc.collect()

    # --------------- Example for using analysis tools to add new columns (for whole directory) -------------------

    # --------------- Example for plotting columns (for whole directory) -------------------

    if plot_new_Columns:

        for filename in os.listdir(input_dir_plotting):
            if not filename.endswith(".parquet"):
                continue

            match = cell_pattern.search(filename)
            if not match:
                print(f"Skipping {filename}, no valid cell ID found.")
                continue

            cell_id = match.group(1)
            input_path = os.path.join(input_dir_plotting, filename)

            df_merged = pd.read_parquet(input_path, engine = "pyarrow")
            print(f"Plotting Cell_ {filename}")
            plot_columns(df_merged, columns = [ColumnName.COULOMB_EFFICIENCY])
            # plot_columns(df_merged, columns=[ColumnName.CURRENT, ColumnName.VOLTAGE
            #     , ColumnName.SOC, ColumnName.CAPACITY, ColumnName.SOH
            #     , ColumnName.INTERNAL_RESISTANCE, ColumnName.COULOMB_EFFICIENCY
            #                                  ])
            del df_merged
            gc.collect()

    # --------------- Example for converting single files with ppb -------------------

    # input_file = "D:/Daten_BA/RAW_new/Tests/20250224132359-CheckUp-1-4-AM23NMC00002.xlsx"
    # output_file_name = "20250224132359-CheckUp-1-4-AM23NMC00002"
    #
    # data_frame = convert(config=Config.Neware, input_path=input_file, keep_all_additional_data=False)
    #
    # output_path = '../analysis/res/AM23NMC00002'
    # export(data_frame=data_frame, output_path=output_path, output_file_name=output_file_name)

    # --------------- Example for converting single files with ppb -------------------


    # --------------- Example for using analysis tools to add new columns (for single file) -------------------

    # # read DataFrame
    # df_merged = pd.read_parquet('D:/Programs/JetBrains/PyCharm Professional/pydpeet_neu/src/analysis/res/AM23NMC00002_with_extra_columns.parquet')
    #
    # # run step analyzer to get charge and discharge segments
    # df_primitives = step_analyzer_primitives(df_merged,STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG)
    #
    # df_segments_and_sequences = step_analyzer_seqments_and_sequences(df_primitives,
    #                                                                  SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG)
    #
    # rules = [
    #     'CCCV_Charge',
    # ]
    # dfs_per_block_charge, df_filtered = filter_and_split_df_by_blocks(
    #     df_segments_and_sequences=df_segments_and_sequences,
    #     df_primitives=df_primitives,
    #     rules=rules,
    #     combine_op='or',
    #     also_return_filtered_df=True
    # )
    #
    # rules = [
    #     'CCCV_Discharge',
    # ]
    # dfs_per_block_Discharge, _ = filter_and_split_df_by_blocks(
    #     df_segments_and_sequences=df_segments_and_sequences,
    #     df_primitives=df_primitives,
    #     rules=rules,
    #     combine_op='or',
    #     also_return_filtered_df=True
    # )
    #
    # dfs_per_block_charge = _sort_dfs(dfs_per_block_charge)
    # dfs_per_block_Discharge = _sort_dfs(dfs_per_block_Discharge)

    #
    # # run actual functions to add new columns (for new cells just adjust the config and the cell name)
    # # if logging is not wanted, set verbose = False
    # campaign = (
    #     CampaignBuilder(df_merged, verbose = True)
    #     .set_config(config = am23nmc)
    #     .set_cell_name(name = "Test1")
    #     .add_coulomb_efficiency(dfs_per_block_charge, dfs_per_block_Discharge)
    #     .add_power()
    #     .add_resistance()
    #     .add_cumulative_capacity()
    #     .add_cumulative_energy()
    #     .add_capacity_throughput()
    #     .add_capacity(df_primitives)
    #     .add_soh()
    #     .add_equivalent_full_cycles()
    #     .add_charge_throughput()
    #     .add_soc(standard_method=SocMethod.WITH_RESET_WHEN_FULL_AND_EMPTY, restart_for_testindex=True,
    #              THRESHOLD_DICT=THRESHOLD_DICT_NEWARE)
    #     .add_internal_resistance(ignore_negative_resistance_values=False)
    #     .build()
    # )
    #
    # # save DataFrame with new columns
    # output_path_DataFrame = 'D:/Programs/JetBrains/PyCharm Professional/pydpeet_neu/src/analysis/res/AM23NMC00002_with_extra_columns.parquet'
    # campaign.to_parquet(output_path_DataFrame)
    #
    #
    # plotting functions

    # df = pd.read_parquet(r'D:\Programs\JetBrains\PyCharm Professional\pydpeet_neu\src\analysis\res\AM23NMC00002.parquet')
    # # run step analyzer to get charge and discharge segments
    # df_primitives = step_analyzer_primitives(df,
    #                                          STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG)
    #
    # df_segments_and_sequences = step_analyzer_seqments_and_sequences(df_primitives,
    #                                                                  SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG)
    #
    # rules = [
    #     'CCCV_Charge',
    # ]
    # dfs_per_block_charge, df_filtered = filter_and_split_df_by_blocks(
    #     df_segments_and_sequences=df_segments_and_sequences,
    #     df_primitives=df_primitives,
    #     rules=rules,
    #     combine_op='or',
    #     also_return_filtered_df=True
    # )
    #
    # rules = [
    #     'CCCV_Discharge',
    # ]
    # dfs_per_block_Discharge, _ = filter_and_split_df_by_blocks(
    #     df_segments_and_sequences=df_segments_and_sequences,
    #     df_primitives=df_primitives,
    #     rules=rules,
    #     combine_op='or',
    #     also_return_filtered_df=True
    # )
    #
    # dfs_per_block_charge = _sort_dfs(dfs_per_block_charge)
    # dfs_per_block_Discharge = _sort_dfs(dfs_per_block_Discharge)
    # df = add_internal_resistance(df, config = am23nmc)
    # df = add_coulomb_efficiency(df, dfs_per_block_charge, dfs_per_block_Discharge, config = am23nmc)
    #
    # plot_columns(df, columns = [ColumnName.INTERNAL_RESISTANCE, ColumnName.COULOMB_EFFICIENCY])
    #
    # plot_columns(df, columns = [ColumnName.CURRENT, ColumnName.VOLTAGE
    #                                   ,ColumnName.SOC, ColumnName.CAPACITY
    #                                   ,ColumnName.INTERNAL_RESISTANCE, ColumnName.COULOMB_EFFICIENCY
    #                                   ])
    # plot_columns(df, columns = [ColumnName.SOH, ColumnName.EQUIVALENT_FULL_CYCLES,
    #                                    ColumnName.CAPACITY_THROUGHPUT, ColumnName.POWER,
    #                                    ColumnName.CHARGE_THROUGHPUT, ColumnName.ABSOLUTE_CHARGE_THROUGHPUT,
    #                                    ColumnName.TEMPERATURE])

    # --------------- Example for using analysis tools to add new columns (for single file) -------------------




