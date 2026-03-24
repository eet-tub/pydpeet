from pathlib import Path

import pandas as pd

from pydpeet import BatteryConfig
from pydpeet.process.sequence.utils.configs.CONFIG_Fallback import FALLBACK_CONFIG

# Get the directory where the current script is located
BASE_DIR = Path(__file__).resolve().parent

# Build correct file paths
df_path = BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted.parquet"
df_primitives_path = BASE_DIR / "basytec_6_3_1_0-TC23LFP09_CU_25deg-converted-primitives.parquet"
# df_segments_and_sequences_path = BASE_DIR / "PLACEHOLDER.parquet"
# Read parquet files
DF = pd.read_parquet(df_path)  # TODO updaten zu neuem bennenungs standard
DF_PRIMITIVES = pd.read_parquet(df_primitives_path)  # TODO updaten zu neuem bennenungs standard
# DF_SEGMENTS_AND_SEQUENCES = pd.read_parquet(df_segments_and_sequences_path)


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

    class Mock_add_resistance_internal:
        df = DF
        config = BatteryConfig()
        verbose = True
        required_columns = ["Voltage[V]", "Current[A]", "Test_Time[s]"]
        required_columns_dtypes = [("Voltage[V]", float), ("Current[A]", float), ("Test_Time[s]", float)]
        add_columns = ["InternalResistance[ohm]"]

    class Mock_add_soc:
        df = DF.copy()
        df_primitives = DF_PRIMITIVES.copy()
        neware_bool = True
        standard_method = "PLACEHOLDER"
        methods = "PLACEHOLDER"
        config = BatteryConfig()
        lower_soc_for_voltage = 0.0
        upper_soc_for_voltage = 1.0
        lower_voltage_for_soc = 0.0
        upper_voltage_for_soc = 0.0
        verbose = True
        restart_for_testindex = True
        required_columns = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        required_columns_dtypes = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        add_columns = ["PLACEHOLDER"]

    class Mock_convert:
        config = "neware_8_0_0_516"
        input_path = "PLACEHOLDER"
        output_path = "PLACEHOLDER"
        keep_all_additional_data = False
        custom_folder_path = "PLACEHOLDER"

    class Mock_df_primitives_correction:
        df_primitives = DF.copy()
        correction_config = "PLACEHOLDER"
        data_columns = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        thresholds = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        reindex = True
        reannotate = True
        required_columns = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        required_columns_dtypes = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        add_columns = ["PLACEHOLDER"]

    class Mock_extract_ocv_iocv:
        min_pause_lenght = "PLACEHOLDER"
        min_loops = "PLACEHOLDER"
        visualize = "PLACEHOLDER"
        df_primitives = DF_PRIMITIVES.copy()
        df = DF.copy()
        config = "PLACEHOLDER"
        required_columns = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        required_columns_dtypes = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        result_columns = ["PLACEHOLDER"]

    class Mock_extract_sequence_overview:
        df_primitives = DF_PRIMITIVES.copy()
        SEGMENT_SEQUENCE_CONFIG = "PLACEHOLDER"
        SHOW_RUNTIME = True
        required_columns = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        required_columns_dtypes = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        result_columns = ["PLACEHOLDER"]

    class Mock_filter_and_split_df_by_blocks:
        df_segments_and_sequences = "PLACEHOLDER"  # DF_SEGMENTS_AND_SEQUENCES
        df_primitives = DF_PRIMITIVES.copy()
        rules = ["PLACEHOLDER"]
        combine_op = "or"
        print_blocks = False
        also_return_filtered_df = True
        required_columns = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        required_columns_dtypes = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        result_columns = ["PLACEHOLDER"]

    class Mock_generate_instructions:
        df_primitives = DF_PRIMITIVES.copy()
        end_condition_map = "PLACEHOLDER"
        threshold_warnings = "PLACEHOLDER"

    class Mock_mapping:
        df = DF.copy()
        column_map = "PLACEHOLDER"
        missing_columns = "PLACEHOLDER"
        required_columns = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        required_columns_dtypes = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
        add_columns = ["PLACEHOLDER"]

    class Mock_merge_into_series:
        df_list = ([DF.copy(), DF.copy()],)
        time_between_tests_seconds = 60.0
        verbose = True
        sort_dfs = True
        add_columns = []

    class Mock_read:
        config = "PLACEHOLDER"
        input_path = "PLACEHOLDER"
        keep_all_additional_data = False
        custom_folder_path = None

    class Mock_set_logging_style:
        level = "PLACEHOLDER"
        formatting_string = "PLACEHOLDER"

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

    class Mock_write:
        data_input = "PLACEHOLDER"
        output_path = "PLACEHOLDER"
        output_file_name = "PLACEHOLDER"
        data_output_filetype = "PLACEHOLDER"

    class Mock_write_to_bibtex:
        filename = "PLACEHOLDER"
