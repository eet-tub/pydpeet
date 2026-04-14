from pathlib import Path

import pandas as pd

from pydpeet import BatteryConfig, SocMethod
from pydpeet.process.sequence.utils.configs.CONFIG_Fallback import FALLBACK_CONFIG, SEGMENT_SEQUENCE_CONFIG

# Get the directory where the current script is located
BASE_DIR = Path(__file__).resolve().parent

# Build correct file paths
df_path = BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted.parquet"
df_with_additional_path = BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-with-additional.parquet"
df_primitives_path = BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-primitives.parquet"
df_primitives_correction_expected_path = (
    BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-primitives-corrected.parquet"
)

df_segments_and_sequences_path = (
    BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-segments-and-sequences.parquet"
)
df_neware_path = BASE_DIR / "neware_8_0_0_516-Cal_Ageing_Checkup3.parquet"
df_neware_expected_ocv_iocv_block_0_path = (
    BASE_DIR / "neware_8_0_0_516-Cal_Ageing_Checkup3_extract_ocv_iocv_block_0.parquet"
)
df_neware_expected_ocv_iocv_block_1_path = (
    BASE_DIR / "neware_8_0_0_516-Cal_Ageing_Checkup3_extract_ocv_iocv_block_1.parquet"
)
df_neware_primitives_path = BASE_DIR / "neware_8_0_0_516-Cal_Ageing_Checkup3_primitives.parquet"
# Expected result for add_capacity
df_add_capacity_expected_path = BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-add_capacity.parquet"
# Expected result for add_primitive_segments
df_add_primitive_segments_expected_path = (
    BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-add_primitive_segments.parquet"
)
# Expected result for add_resistance_internal
df_add_resistance_internal_expected_path = (
    BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-add_resistance_internal.parquet"
)
# Expected result for add_soc
df_add_soc_expected_path = BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-add_soc.parquet"
# Expected result for extract_sequence_overview
df_extract_sequence_overview_expected_path = (
    BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-extract_sequence_overview.parquet"
)
# Expected result for generate_instructions
df_generate_instructions_expected_path = (
    BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-generate_instructions.txt"
)
# Expected result for merge_into_series
df_merge_into_series_expected_path = BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-merge_into_series.parquet"
# Read parquet files
DF = pd.read_parquet(df_path)
DF_WITH_ADDITIONAL = pd.read_parquet(df_with_additional_path)
DF_PRIMITIVES = pd.read_parquet(df_primitives_path)
DF_PRIMITIVES_CORRECTION_EXPECTED = pd.read_parquet(df_primitives_correction_expected_path)

# Read neware data files
DF_NEWARE = pd.read_parquet(df_neware_path)
DF_NEWARE_EXPECTED_OCV_IOCV_BLOCK_0 = pd.read_parquet(df_neware_expected_ocv_iocv_block_0_path)
DF_NEWARE_EXPECTED_OCV_IOCV_BLOCK_1 = pd.read_parquet(df_neware_expected_ocv_iocv_block_1_path)
DF_NEWARE_PRIMITIVES = pd.read_parquet(df_neware_primitives_path)
DF_SEGMENTS_AND_SEQUENCES = pd.read_parquet(df_segments_and_sequences_path)
DF_ADD_CAPACITY_EXPECTED = pd.read_parquet(df_add_capacity_expected_path)
DF_ADD_PRIMITIVE_SEGMENTS_EXPECTED = pd.read_parquet(df_add_primitive_segments_expected_path)
DF_ADD_RESISTANCE_INTERNAL_EXPECTED = pd.read_parquet(df_add_resistance_internal_expected_path)
DF_ADD_SOC_EXPECTED = pd.read_parquet(df_add_soc_expected_path)
DF_EXTRACT_SEQUENCE_OVERVIEW_EXPECTED = pd.read_parquet(df_extract_sequence_overview_expected_path)
DF_MERGE_INTO_SERIES_EXPECTED = pd.read_parquet(df_merge_into_series_expected_path)
# Load generate_instructions expected result from text file
with open(df_generate_instructions_expected_path, encoding="utf-8") as f:
    GENERATE_INSTRUCTIONS_EXPECTED = [line.strip() for line in f if line.strip()]

# Load expected results for filter_and_split_df_by_blocks from subfolder
EXPECTED_RESULTS_DIR = BASE_DIR / "filter_and_split_df_by_blocks_expected"
DF_FILTERED = pd.read_parquet(EXPECTED_RESULTS_DIR / "df_filtered.parquet")

# Load expected blocks for filter_and_split_df_by_blocks
EXPECTED_BLOCKS = []
if EXPECTED_RESULTS_DIR.exists():
    # Sort numerically by extracting number from filename (block_0, block_1, block_2... not block_0, block_1, block_10)
    block_files = sorted(EXPECTED_RESULTS_DIR.glob("block_*.parquet"), key=lambda f: int(f.stem.split("_")[1]))
    for block_file in block_files:
        EXPECTED_BLOCKS.append(pd.read_parquet(block_file))


class Mocks:
    class Mock_add_capacity:
        df = DF
        df_primitives = DF_PRIMITIVES
        neware_bool = True
        config = BatteryConfig()
        verbose = True
        required_columns_df = ["Voltage[V]", "Current[A]", "Test_Time[s]"]
        required_column_dtypes_df = [("Voltage[V]", float), ("Current[A]", float), ("Test_Time[s]", float)]
        required_columns_df_primitives = [
            "Test_Time[s]",
            "Voltage[V]",
            "Current[A]",
            "Power[W]",
            "ID",
            "Variable",
            "Duration",
            "Length",
            "Min",
            "Max",
            "Avg",
            "Type",
            "Direction",
            "Slope",
        ]
        required_column_dtypes_df_primitives = [
            ("Test_Time[s]", float),
            ("Voltage[V]", float),
            ("Current[A]", float),
            ("Power[W]", float),
            ("ID", int),
            ("Variable", str),
            ("Duration", float),
            ("Length", float),
            ("Min", float),
            ("Max", float),
            ("Avg", float),
            ("Type", str),
            ("Direction", str),
            ("Slope", float),
        ]

        add_columns = ["Capacity[Ah]"]
        df_expected = DF_ADD_CAPACITY_EXPECTED.copy()

    class Mock_add_primitive_segments:
        df = DF
        STEP_ANALYZER_PRIMITIVES_CONFIG = FALLBACK_CONFIG
        SEGMENTS_TO_DETECT_CONFIG = FALLBACK_CONFIG["SEGMENTS_TO_DETECT_CONFIG"]
        ADJUST_SEGMENTS_CONFIG = FALLBACK_CONFIG["ADJUST_SEGMENTS_CONFIG"]
        THRESHOLDS_PRIMITIVE_ANNOTATION = FALLBACK_CONFIG["THRESHOLDS_PRIMITIVE_ANNOTATION"]
        THRESHOLD_CV_SEGMENTS_0A_END = FALLBACK_CONFIG["THRESHOLD_CV_SEGMENTS_0A_END"]
        THRESHOLD_CONSOLE_PRINTS_CV_CHECK = FALLBACK_CONFIG["THRESHOLD_CONSOLE_PRINTS_CV_CHECK"]
        THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK = FALLBACK_CONFIG["THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK"]
        THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH = FALLBACK_CONFIG["THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH"]
        THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK = FALLBACK_CONFIG[
            "THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK"
        ]
        SHOW_RUNTIME = True
        check_CV_0Aend_segments_bool = True
        check_zero_length_segments_bool = True
        check_Power_zero_W_segments_bool = True
        supress_IO_warnings = True
        PRECOMPILE = True
        FORCE_PRECOMPILATION = True
        required_columns = ["Voltage[V]", "Current[A]", "Test_Time[s]"]
        required_columns_dtypes = [("Voltage[V]", float), ("Current[A]", float), ("Test_Time[s]", float)]
        add_columns = [
            "Power[W]",
            "ID",
            "Variable",
            "Duration",
            "Length",
            "Min",
            "Max",
            "Avg",
            "Type",
            "Direction",
            "Slope",
        ]
        df_expected = DF_ADD_PRIMITIVE_SEGMENTS_EXPECTED.copy()

    class Mock_add_resistance_internal:
        df = DF
        config = BatteryConfig()
        verbose = True
        required_columns = ["Voltage[V]", "Current[A]", "Test_Time[s]"]
        required_columns_dtypes = [("Voltage[V]", float), ("Current[A]", float), ("Test_Time[s]", float)]
        add_columns = ["InternalResistance[ohm]"]
        df_expected = DF_ADD_RESISTANCE_INTERNAL_EXPECTED.copy()

    class Mock_add_soc:
        df = DF.copy()
        df_primitives = DF_PRIMITIVES.copy()
        neware_bool = True
        standard_method = SocMethod.WITHOUT_RESET
        methods = [SocMethod.WITHOUT_RESET, SocMethod.WITH_RESET_WHEN_FULL]
        config = BatteryConfig()
        lower_soc_for_voltage = 0.0
        upper_soc_for_voltage = 1.0
        lower_voltage_for_soc = 0.0
        upper_voltage_for_soc = 0.0
        verbose = True
        restart_for_testindex = True
        required_columns = ["Test_Time[s]", "Current[A]", "Voltage[V]"]
        required_columns_dtypes = [("Test_Time[s]", float), ("Current[A]", float), ("Voltage[V]", float)]
        add_columns = ["Capacity[Ah]", "SOC", "SOC_WITH_RESET_WHEN_FULL"]
        df_expected = DF_ADD_SOC_EXPECTED.copy()

    class Mock_convert:
        config = "basytec_6_3_1_0"
        input_path = str(BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg.txt")
        output_path = None
        keep_all_additional_data = False
        custom_folder_path = None
        required_columns = [
            "Meta_Data",
            "Step_Count",
            "Voltage[V]",
            "Voltage[V]",
            "Current[A]",
            "Temperature[°C]",
            "Test_Time[s]",
            "Date_Time",
            "EIS_f[Hz]",
            "EIS_Z_Real[Ohm]",
            "EIS_Z_Imag[Ohm]",
            "EIS_DC[A]",
        ]
        df_expected_without_additional_data = DF.copy()
        df_expected_with_additional_data = DF_WITH_ADDITIONAL.copy()

    class Mock_df_primitives_correction:
        df_primitives = DF_PRIMITIVES.copy()
        correction_config = {
            "replace_ID": {5: "V"},
            "replace_time": {(100.0, 200.0): "I"},
            "replace_time_and_merge": {(500.0, 600.0): "P"},
            "merge_left": [10],
            "merge_right": [15],
            "merge_range": [(20, 25)],
        }
        data_columns = {"I": "Current[A]", "P": "Power[W]", "V": "Voltage[V]"}
        thresholds = {"V": 0.1, "I": 0.1, "P": 0.1}
        reindex = True
        reannotate = True
        required_columns = [
            "Voltage[V]",
            "Current[A]",
            "Test_Time[s]",
            "Power[W]",
            "ID",
            "Variable",
            # "Duration", #TODO look if they all are needed or not
            # "Length",
            # "Min",
            # "Max",
            # "Avg",
            # "Type",
            # "Direction",
            # "Slope",
        ]
        required_columns_dtypes = [
            ("Voltage[V]", float),
            ("Current[A]", float),
            ("Test_Time[s]", float),
            ("Power[W]", float),
            ("ID", int),
            ("Variable", str),
            # ("Duration", float),
            # ("Length", float),
            # ("Min", float),
            # ("Max", float),
            # ("Avg", float),
            # ("Type", str),
            # ("Direction", str),
            # ("Slope", float),
        ]
        add_columns = []
        df_primitives_expected = DF_PRIMITIVES_CORRECTION_EXPECTED.copy()

    class Mock_extract_ocv_iocv:
        min_pause_lenght = 120.0
        min_loops = 70.0
        visualize = False
        df = DF_NEWARE.copy()
        df_primitives = DF_NEWARE_PRIMITIVES.copy()
        config = BatteryConfig(c_ref=4.75, max_voltage=4.2, min_voltage=2.5, voltage_intervall=0.01)
        required_columns_df = ["Voltage[V]", "Current[A]", "Test_Time[s]"]
        required_columns_dtypes_df = [("Voltage[V]", float), ("Current[A]", float), ("Test_Time[s]", float)]
        required_columns_df_primitives = ["Test_Time[s]", "Type", "Duration", "ID", "Voltage[V]"]
        required_columns_dtypes_df_primitives = [
            ("Test_Time[s]", float),
            ("Type", str),
            ("Duration", float),
            ("ID", int),
            ("Voltage[V]", float),
        ]
        result_columns = ["iOCV_type", "SOC"]
        expected_ocv_iocv = [
            DF_NEWARE_EXPECTED_OCV_IOCV_BLOCK_0.copy(),
            DF_NEWARE_EXPECTED_OCV_IOCV_BLOCK_1.copy(),
        ]

    class Mock_extract_sequence_overview:
        df_primitives = DF_PRIMITIVES.copy()
        SEGMENT_SEQUENCE_CONFIG = SEGMENT_SEQUENCE_CONFIG.copy()
        SHOW_RUNTIME = True
        required_columns = [
            "Test_Time[s]",
            "Voltage[V]",
            "Current[A]",
            "Power[W]",
            "ID",
            "Variable",
            "Duration",
            "Length",
            "Min",
            "Max",
            "Avg",
            "Type",
            "Direction",
            "Slope",
        ]
        required_columns_dtypes = [
            ("Test_Time[s]", float),
            ("Voltage[V]", float),
            ("Current[A]", float),
            ("Power[W]", float),
            ("ID", int),
            ("Variable", str),
            ("Duration", float),
            ("Length", float),
            ("Min", float),
            ("Max", float),
            ("Avg", float),
            ("Type", str),
            ("Direction", str),
            ("Slope", float),
        ]
        add_columns = ["Sequence"]
        df_expected = DF_EXTRACT_SEQUENCE_OVERVIEW_EXPECTED.copy()

    class Mock_filter_and_split_df_by_blocks:
        df_segments_and_sequences = DF_SEGMENTS_AND_SEQUENCES.copy()
        df_primitives = DF_PRIMITIVES.copy()
        rules = ["CC_Discharge", "Pause"]
        combine_op = "or"
        print_blocks = False
        also_return_filtered_df = True
        # Required columns for df_segments_and_sequences: ID + rule columns
        required_columns_df_segments = ["ID", "CC_Discharge", "Pause"]
        required_columns_dtypes_df_segments = [("ID", int), ("CC_Discharge", int), ("Pause", int)]
        # Required columns for df_primitives: ID, Test_Time[s], Voltage[V], Current[A], Power[W], Variable
        required_columns_df_primitives = ["ID", "Test_Time[s]", "Voltage[V]", "Current[A]", "Power[W]", "Variable"]
        required_columns_dtypes_df_primitives = [
            ("ID", int),
            ("Test_Time[s]", float),
            ("Voltage[V]", float),
            ("Current[A]", float),
            ("Power[W]", float),
            ("Variable", str),
        ]
        # Columns to use for NaN/inf testing (must be float columns)
        nan_inf_test_column_df_segments = "Test_Time[s]"  # Use from df_primitives since df_segments has no float cols
        nan_inf_test_column_df_primitives = "Test_Time[s]"
        # Expected results
        expected_dfs_per_block = EXPECTED_BLOCKS
        expected_df_filtered = DF_FILTERED.copy()

    class Mock_generate_instructions:
        df_primitives = DF_PRIMITIVES.copy()
        end_condition_map = {"CC": "voltage", "CV": "current", "CP": "voltage", "Pause": "time"}
        threshold_warnings = 5
        required_columns = [
            "Test_Time[s]",
            "Voltage[V]",
            "Current[A]",
            "Power[W]",
            "ID",
            "Variable",
            "Duration",
            "Length",
            "Min",
            "Max",
            "Avg",
            "Type",
            "Direction",
            "Slope",
        ]
        required_columns_dtypes = [
            ("Test_Time[s]", float),
            ("Voltage[V]", float),
            ("Current[A]", float),
            ("Power[W]", float),
            ("ID", int),
            ("Variable", str),
            ("Duration", float),
            ("Length", float),
            ("Min", float),
            ("Max", float),
            ("Avg", float),
            ("Type", str),
            ("Direction", str),
            ("Slope", float),
        ]
        expected = GENERATE_INSTRUCTIONS_EXPECTED.copy()

    class Mock_mapping:
        # Create raw DataFrame by reversing column_map on converted DF
        _column_map = {
            "Time[h]": "Test_Time[s]",
            "U[V]": "Voltage[V]",
            "I[A]": "Current[A]",
            "T1[°C]": "Temperature[°C]",
            "Line": "Step_Count",
        }
        _inverse_map = {v: k for k, v in _column_map.items()}
        df = DF.copy().rename(columns=_inverse_map)
        column_map = _column_map.copy()
        missing_columns = ["Date_Time", "EIS_f[Hz]", "EIS_Z_Real[Ohm]", "EIS_Z_Imag[Ohm]", "EIS_DC[A]"]
        required_columns = list(_column_map.keys())
        required_columns_dtypes = [
            ("Time[h]", float),
            ("U[V]", float),
            ("I[A]", float),
            ("T1[°C]", float),
            ("Line", int),
        ]
        add_columns = ["Meta_Data", "Date_Time", "EIS_f[Hz]", "EIS_Z_Real[Ohm]", "EIS_Z_Imag[Ohm]", "EIS_DC[A]"]

    class Mock_merge_into_series:
        # Create a list of DataFrames to merge (use smaller slices for testing)
        _df1 = DF.copy().iloc[:1000].reset_index(drop=True)
        _df2 = DF.copy().iloc[1000:2000].reset_index(drop=True)
        df_list = [_df1, _df2]
        time_between_tests_seconds = 60.0
        verbose = True
        sort_dfs = True
        required_columns = ["Test_Time[s]"]  # Required in each DataFrame
        add_columns = ["TestIndex"]  # Column added by the function
        df_expected = DF_MERGE_INTO_SERIES_EXPECTED.copy()

    class Mock_read:
        config = "basytec_6_3_1_0"
        input_path = str(BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg.txt")
        keep_all_additional_data = False
        custom_folder_path = None
        df_expected_without_additional_data = DF.copy()
        df_expected_with_additional_data = DF_WITH_ADDITIONAL.copy()

    class Mock_set_logging_style:
        level = "WARNING"
        formatting_string = "%(levelname)s | %(pathname)s:%(lineno)d | %(message)s"

    class Mock_visualize_phases:
        dataframe = DF_PRIMITIVES.copy()
        start_time = None
        end_time = None
        visualize_phases_config = [
            ("V", "blue"),
            ("I", "red"),
            ("P", "green"),
        ]
        segment_alpha = 0.3
        line_visualization_config = [
            ("Voltage[V]", "blue", (2.3, 4.3)),
            ("Current[A]", "red", (-10, 10)),
            ("Power[W]", "green", (-40, 40)),
        ]
        use_lines_for_segments = True
        show_column_names = True
        show_time = True
        show_id = True
        width_height_ratio = [1.0, 0.3]
        show_runtime = True
        add_columns = []
        required_columns = ["Test_Time[s]", "ID", "Variable", "Voltage[V]", "Current[A]", "Power[W]"]
        required_columns_dtypes = [
            ("Test_Time[s]", float),
            ("ID", int),
            ("Variable", str),
            ("Voltage[V]", float),
            ("Current[A]", float),
            ("Power[W]", float),
        ]

    class Mock_write:
        data_input = "PLACEHOLDER"
        output_path = "PLACEHOLDER"
        output_file_name = "PLACEHOLDER"
        data_output_filetype = "PLACEHOLDER"

    class Mock_write_to_bibtex:
        filename = "PLACEHOLDER"
