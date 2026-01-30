import logging
from time import perf_counter
import pandas
import numpy as np
from pathlib import Path

# import Daniel's & Jan's work
from pydpeet.process.sequence.step_analyzer import step_analyzer_seqments_and_sequences, step_analyzer_primitives
from pydpeet.process.analyze.extract.OCV.res.CONFIG_Standard_DVA_ICA import *
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
from pydpeet.process.analyze.calculations.soc_methods import add_soc
from pydpeet.process.analyze.calculations.soc_methods import SocMethod

# plot import
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def iocv_detection(min_pause_lenght: float = 120,
                   min_loops: float = 70,
                   visualize: bool = True,
                   df_primitives: pandas.DataFrame = None,
                   df: pandas.DataFrame = None,
                   config = None
                   )-> pandas.DataFrame:
    """
    Compute iOCV blocks from given DataFrames.

    Parameters
    ----------
    min_pause_lenght : float
        The minimum length of a pause in seconds.
    min_loops : float
        The minimum number of unique IDs.
    visualize : bool
        Whether to visualize the iOCV curves.
    df_primitives : pandas.DataFrame
        The DataFrame containing the primitives.
    df : pandas.DataFrame
        The original DataFrame.
    soc_max_voltage : float
        The maximum voltage of the battery.
    soc_min_voltage : float
        The minimum voltage of the battery.
    soc_c_ref : float
        The reference capacity of the battery.
    Returns
    -------
    pd.DataFrame
        A DataFrame containing all iOCV blocks.

    """

    # Sanity Checks for Input
    if df is not None and df_primitives is not None:
        raise ValueError("Please provide either df or df_primitives, not both!")


    if df is not None:
        df.drop_duplicates(subset=['Testtime[s]'], inplace=True)
        df.dropna(subset=['Testtime[s]'], inplace=True)
        df = df.sort_values('Testtime[s]')

        df_primitives = step_analyzer_primitives(df=df,
                                                 STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
                                                 #SHOW_RUNTIME=False,
                                                 #check_CV_0Aend_segments_bool=False,
                                                 #check_zero_length_segments_bool=False,
                                                 #supress_IO_warnings=True
                                                 )


    if df_primitives is not None:
        if df_primitives['Testtime[s]'].duplicated().any():
            raise ValueError("Duplicated 'Testtime[s]' values found!")

        if df_primitives['Testtime[s]'].isna().any():
            raise ValueError("NaN values found in 'Testtime[s]'")

        if not np.all(np.diff(df_primitives['Testtime[s]']) > 0):
            raise ValueError("'Testtime[s]' is not monotonically increasing!")

        logging.info("Checking if SOC exists in dataframe...")
        
        if 'SOC' in df_primitives.columns:
            logging.info("SOC already exists in df_primitives, skipping SOC calculation...")
        else:
            logging.info("SOC column does not exist in df_primitives, adding it...")
            df_primitives = add_soc(df=df_primitives,
                                    df_primitives=df_primitives,
                                    standard_method = SocMethod.WITH_RESET_WHEN_FULL, 
                                    config=config)

        df_segments_and_sequences = step_analyzer_seqments_and_sequences(df_primitives, SEGMENT_SEQUENCE_CONFIG)

    else:
        raise ValueError("No df_primitives found!")

# Applying Rules for iOCV Sequences
    _rules = [
        "Discharge_iOCV",
        "Charge_iOCV"
    ]
    _STANDARD_COLUMNS = [
        "Testtime[s]",
        "Voltage[V]",
        "Current[A]",
        "Power[W]",
    ]
    logging.info("Applying rules and standard columns to compute iOCV blocks...")
    dfs_per_block = filter_and_split_df_by_blocks(
        df_segments_and_sequences=df_segments_and_sequences,
        df_primitives=df_primitives,
        rules=_rules,
        # standard_columns=_STANDARD_COLUMNS,
        combine_op='or',
        print_blocks=True,
    )

    logging.info("Filtering iOCV Points...")

    #Filtering iOCV Points
    dfs_per_block = [df[df["Type"] == "Rest"] for df in dfs_per_block[0]]
    dfs_per_block = [df.loc[df.groupby("ID")["Testtime[s]"].idxmax()] for df in dfs_per_block]
    dfs_per_block = [df for df in dfs_per_block if df["ID"].nunique() >= min_loops]
    dfs_per_block = [df for df in dfs_per_block if df["Duration"].min() >= min_pause_lenght]

    logging.info("Filtering iOCV Charge and Discharge blocks...")

    dfs_with_type = []
    for df_block in dfs_per_block:
        if df_block.empty:
            continue

        first_id = df_block["ID"].iloc[0]
        matching_row = df_segments_and_sequences[df_segments_and_sequences["ID"] == first_id]

        if matching_row.empty:
            iocv_type = "Unknown"
        elif matching_row["Charge_iOCV"].iloc[0] != 0:
            iocv_type = "Charge"
        elif matching_row["Discharge_iOCV"].iloc[0] != 0:
            iocv_type = "Discharge"
        else:
            iocv_type = "Unknown"

        df_block["iOCV_type"] = iocv_type
        dfs_with_type.append(df_block)

    dfs_per_block = dfs_with_type

    if visualize:
        logging.info("Plotting iOCV curves...")

        fig, ax1 = plt.subplots(figsize=(12,8))
        ax1.set_xlabel('SOC', fontsize=15)
        ax1.set_ylabel('Voltage[V]', fontsize=15, color='blue')
        ax1.tick_params(axis='y', labelcolor='b', labelsize=15)
        ax1.tick_params(axis='x', labelsize=15)

        # Separate Charge and Discharge blocks
        charge_blocks = [df for df in dfs_per_block if df['iOCV_type'].iloc[0] == "Charge"]
        discharge_blocks = [df for df in dfs_per_block if df['iOCV_type'].iloc[0] == "Discharge"]

        # Custom colormaps
        charge_cmap = LinearSegmentedColormap.from_list("charge_cmap", ["green", "blue"])
        discharge_cmap = LinearSegmentedColormap.from_list("discharge_cmap", ["red", "yellow"])

        for i, df in enumerate(charge_blocks):
            color = charge_cmap(i / max(len(charge_blocks) - 1, 1))
            label = f"Charge iOCV {i + 1}"
            ax1.plot(df['SOC'], df['Voltage[V]'], color=color, label=label, linewidth=2, linestyle='-', markersize=1)

        for i, df in enumerate(discharge_blocks):
            color = discharge_cmap(i / max(len(discharge_blocks) - 1, 1))
            label = f"Discharge iOCV {i + 1}"
            ax1.plot(df['SOC'], df['Voltage[V]'], color=color, label=label, linewidth=2, linestyle='-', markersize=1)

        # Combine legends
        handles1, labels1 = ax1.get_legend_handles_labels()
        ax1.legend(handles1, labels1, loc='lower right', fontsize=15)
        ax1.set_title('iOCV over SOC', fontsize=15)
        ax1.grid(True, linestyle='--', alpha=0.7)

        plt.tight_layout()
        plt.show()

    logging.info("Returning Dataframe with iOCV blocks...")
    return dfs_per_block