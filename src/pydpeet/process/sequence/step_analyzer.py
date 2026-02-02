import os
from typing import List, Tuple, Dict
import pandas as pd

from pydpeet.citations import citeme
# "_" used to differentiate between functions that a user should access from outside
# and functions that aren't expected to be called directly

# LOG_TIME
from pydpeet.process.sequence.utils.console_prints.log_time import log_time
# ANNOTATION
from pydpeet.process.sequence.utils.annotate.annotate_primitives import _annotate_primitives, _merged_annotations
# PROCESSING
from pydpeet.process.sequence.utils.processing.split_in_segments import _split_in_segments_using_incremental_linear_fit
from pydpeet.process.sequence.utils.processing.attempt_to_merge_neighboring_segments import \
    _attempt_to_merge_neighboring_segments
from pydpeet.process.sequence.utils.processing.widen_constant_segments import _widen_constant_segments
from pydpeet.process.sequence.utils.processing.supress_smaller_segments import _add_segment_lengths, \
    _keep_max_segment_id
from pydpeet.process.sequence.utils.processing.analyze_segments import _analyze_segments
from pydpeet.process.sequence.utils.processing.check_CV_results import _check_CV_0Aend_segments
from pydpeet.process.sequence.utils.processing.check_zero_length import _check_zero_length_segments
from pydpeet.process.sequence.utils.processing.check_power_zero_watt_segments import _check_power_zero_watt_segments
# POSTPROCESSING
from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction
# CONFIG Fallback
from pydpeet.process.sequence.utils.configs.CONFIG_Fallback import FALLBACK_CONFIG


@citeme.bachelorthesis('Daniel_BA', {
    'author': 'Daniel Schröder',
    'title': 'Automatisierte Erkennung charakteristischer Abschnitte in Batteriemessdaten auf Basis von Strom, Spannung und Zeit',
    'school': 'Technische Universität Berlin',
    'year': '2026'
})
def step_analyzer_primitives(
        df: pd.DataFrame,
        STEP_ANALYZER_PRIMITIVES_CONFIG: Dict = None,
        SEGMENTS_TO_DETECT_CONFIG: List[Tuple[str, float]] = None,
        ADJUST_SEGMENTS_CONFIG: List[Tuple[str, float]] = None,
        THRESHOLDS_PRIMITIVE_ANNOTATION: Dict[str, float] = None,
        THRESHOLD_CV_SEGMENTS_0A_END: float = None,
        THRESHOLD_CONSOLE_PRINTS_CV_CHECK: int = None,
        THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK: int = None,
        THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH: int = None,
        THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK: int = None,
        SHOW_RUNTIME: bool = True,
        check_CV_0Aend_segments_bool: bool = True,
        check_zero_length_segments_bool: bool = True,
        check_Power_zero_W_segments_bool: bool = True,
        supress_IO_warnings: bool = False,
        PRECOMPILE: bool = True,  # When debugging use PRECOMPILE=False, else you'll see the dummy data!
        FORCE_PRECOMPILATION: bool = False,

) -> pd.DataFrame:
    """
    Function to perform step analysis to create a segmentation of a dataframe into primitive Segments.

    Parameters:
    df (pd.DataFrame): Input dataframe to perform primitive step analysis on.
    STEP_ANALYZER_PRIMITIVES_CONFIG (Dict): Configuration for step analysis (combined Dict of following parameters)
    SEGMENTS_TO_DETECT_CONFIG (List[Tuple[str, float]]): Threshold values for each column to detect segments
        Example: [("Voltage[V]", 0.1), ("Current[A]", 0.1), ("Power[W]", 0.1)]
    ADJUST_SEGMENTS_CONFIG (List[Tuple[str, float]]): Threshold values for each column to adjust the segments
        Example: [("Voltage[V]", 0.1), ("Current[A]", 0.1), ("Power[W]", 0.1)]
    THRESHOLDS_PRIMITIVE_ANNOTATION (Dict[str, float]): Threshold values for each column to annotate primitives
        Example: {"V": 0.1, "I": 0.1, "P": 0.1} #Same key as DATA_COLUMNS
    THRESHOLD_CV_SEGMENTS_0A_END (float): Threshold value for CV 0A end segments
    THRESHOLD_CONSOLE_PRINTS_CV_CHECK (int): Threshold value for CV check console prints
    THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK (int): Threshold value for zero length check console prints
    THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH (int): Threshold value for finetuning width check console prints
    THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK (int): Threshold value for power zero watt check console prints
    SHOW_RUNTIME (bool): Whether to show the runtime of this function, by default True
    check_CV_0Aend_segments_bool (bool): Whether to check CV 0A end segments, by default True
    check_zero_length_segments_bool (bool): Whether to check zero length segments, by default True
    check_Power_zero_W_segments_bool (bool): Whether to check power zero watt segments, by default True
    supress_IO_warnings (bool): Whether to supress IO warnings, by default False
    PRECOMPILE (bool): Whether to allow to precompile the functions, by default True
    FORCE_PRECOMPILATION (bool): Whether to force precompilation, by default False

    Returns:
    df_primitives (pd.DataFrame): The final annotated dataframe
    """
    # --- Merge Configuration Priority ---
    fallback = FALLBACK_CONFIG.copy()
    config_dict = STEP_ANALYZER_PRIMITIVES_CONFIG or {}
    merged_config = {**fallback, **config_dict}

    explicit_overrides = {
        "SEGMENTS_TO_DETECT_CONFIG": SEGMENTS_TO_DETECT_CONFIG,
        "ADJUST_SEGMENTS_CONFIG": ADJUST_SEGMENTS_CONFIG,
        "THRESHOLDS_PRIMITIVE_ANNOTATION": THRESHOLDS_PRIMITIVE_ANNOTATION,
        "THRESHOLD_CV_SEGMENTS_0A_END": THRESHOLD_CV_SEGMENTS_0A_END,
        "THRESHOLD_CONSOLE_PRINTS_CV_CHECK": THRESHOLD_CONSOLE_PRINTS_CV_CHECK,
        "THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK": THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK,
        "THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH": THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH,
        "THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK": THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK,
        "SHOW_RUNTIME": SHOW_RUNTIME,
        "check_CV_0Aend_segments_bool": check_CV_0Aend_segments_bool,
        "check_zero_length_segments_bool": check_zero_length_segments_bool,
        "check_Power_zero_W_segments_bool": check_Power_zero_W_segments_bool,
        "supress_IO_warnings": supress_IO_warnings,
        "PRECOMPILE": PRECOMPILE,
        "FORCE_PRECOMPILATION": FORCE_PRECOMPILATION
    }

    # prefer manual variables over the fallback
    for key, val in explicit_overrides.items():
        if val is not None:
            merged_config[key] = val

    SEGMENTS_TO_DETECT_CONFIG = merged_config["SEGMENTS_TO_DETECT_CONFIG"]
    ADJUST_SEGMENTS_CONFIG = merged_config["ADJUST_SEGMENTS_CONFIG"]
    THRESHOLDS_PRIMITIVE_ANNOTATION = merged_config["THRESHOLDS_PRIMITIVE_ANNOTATION"]
    THRESHOLD_CV_SEGMENTS_0A_END = merged_config["THRESHOLD_CV_SEGMENTS_0A_END"]
    SHOW_RUNTIME = merged_config["SHOW_RUNTIME"]
    THRESHOLD_CONSOLE_PRINTS_CV_CHECK = merged_config["THRESHOLD_CONSOLE_PRINTS_CV_CHECK"]
    THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK = merged_config["THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK"]
    THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH = merged_config["THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH"]
    THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK = merged_config["THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK"]
    check_CV_0Aend_segments_bool = merged_config["check_CV_0Aend_segments_bool"]
    check_zero_length_segments_bool = merged_config["check_zero_length_segments_bool"]
    check_Power_zero_W_segments_bool = merged_config["check_Power_zero_W_segments_bool"]
    supress_IO_warnings = merged_config["supress_IO_warnings"]
    PRECOMPILE = merged_config["PRECOMPILE"]
    FORCE_PRECOMPILATION = merged_config["FORCE_PRECOMPILATION"]

    DATA_COLUMNS = { #standard values
        "V": "Voltage[V]",
        "I": "Current[A]",
        "P": "Power[W]",
    }

    # --- Warn if using fallback ---
    if STEP_ANALYZER_PRIMITIVES_CONFIG is None and not supress_IO_warnings:
        print(
            "\033[94mInput Warning: Using EXAMPLE_STEP_ANALYZER_PRIMITIVES_CONFIG as fallback configuration. Manual Parameters will be kept.\033[0m"
        )

    #TODO variable to choose if copy should be used?
    df_step = df.copy()

    # --- Guardrails ---
    if df is None or df.empty or not isinstance(df, pd.DataFrame):
        raise ValueError("Input dataframe is None or empty")
    if "Voltage[V]" not in df_step.columns:
        print("\033[94mInput Error: 'Voltage[V]' column not found in input dataframe.\033[0m")
        raise ValueError("Input Error: 'Voltage[V]' column not found in input dataframe.")
    if "Current[A]" not in df_step.columns:
        print("\033[94mInput Error: 'Current[A]' column not found in input dataframe.\033[0m")
        raise ValueError("Input Error: 'Current[A]' column not found in input dataframe.")
    if "Testtime[s]" not in df_step.columns:
        print("\033[94mInput Error: 'Testtime[s]' column not found in input dataframe.\033[0m")
        raise ValueError("Input Error: 'Testtime[s]' column not found in input dataframe.")
    if SEGMENTS_TO_DETECT_CONFIG is None or len(SEGMENTS_TO_DETECT_CONFIG) == 0:
        raise ValueError("SEGMENTS_TO_DETECT_CONFIG is None or empty")
    if ADJUST_SEGMENTS_CONFIG is None or len(ADJUST_SEGMENTS_CONFIG) == 0:
        raise ValueError("ADJUST_SEGMENTS_CONFIG is None or empty")
    if THRESHOLDS_PRIMITIVE_ANNOTATION is None or len(THRESHOLDS_PRIMITIVE_ANNOTATION) == 0:
        raise ValueError("THRESHOLDS_PRIMITIVE_ANNOTATION is None or empty")
    if THRESHOLD_CV_SEGMENTS_0A_END is None or not isinstance(THRESHOLD_CV_SEGMENTS_0A_END, float):
        raise ValueError("THRESHOLD_CV_SEGMENTS_OA_END is None or not a float")
    if THRESHOLD_CONSOLE_PRINTS_CV_CHECK is None or not isinstance(THRESHOLD_CONSOLE_PRINTS_CV_CHECK, int):
        raise ValueError("THRESHOLD_CONSOLE_PRINTS_CV_CHECK is None or not a int")
    if THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK is None or not isinstance(THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK, int):
        raise ValueError("THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK is None or not a int")
    if THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH is None or not isinstance(THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH, int):
        raise ValueError("THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH is None or not a int")
    if THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK is None or not isinstance(THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK, int):
        raise ValueError("THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK is None or not a int")

    # --- Data cleanup ---
    if not supress_IO_warnings:
        print("\033[94mInput Warning: Dropping NaN values in 'Testtime[s]', dropping duplicates and sorting 'Testtime[s]' column.\033[0m")
    df_step.dropna(subset=['Testtime[s]'], inplace=True)
    df_step.drop_duplicates(subset=['Testtime[s]'], inplace=True)
    df_step.sort_values(by=['Testtime[s]'], inplace=True)

    # --- Guardrails & IO Warnings ---
    if not supress_IO_warnings:
        for column_name, threshold in SEGMENTS_TO_DETECT_CONFIG:
            if threshold < 0:
                print(f"\033[94mInput Warning: Threshold for {column_name} is negative, using abs({threshold}) instead.\033[0m")
                SEGMENTS_TO_DETECT_CONFIG = [(column_name, abs(threshold)) for column_name, threshold in SEGMENTS_TO_DETECT_CONFIG]
        if THRESHOLD_CV_SEGMENTS_0A_END < 0.0:
            print(f"\033[94mInput Warning: THRESHOLD_CV_SEGMENTS_0A_END is negative, using abs({THRESHOLD_CV_SEGMENTS_0A_END}) instead.\033[0m")
            THRESHOLD_CV_SEGMENTS_0A_END = abs(THRESHOLD_CV_SEGMENTS_0A_END)
        if THRESHOLD_CONSOLE_PRINTS_CV_CHECK < 0:
            print(f"\033[94mInput Warning: THRESHOLD_CONSOLE_PRINTS_CV_CHECK is negative, using abs({THRESHOLD_CONSOLE_PRINTS_CV_CHECK}) instead.\033[0m")
            THRESHOLD_CONSOLE_PRINTS_CV_CHECK = abs(THRESHOLD_CONSOLE_PRINTS_CV_CHECK)
        if THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK < 0:
            print(f"\033[94mInput Warning: THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK is negative, using abs({THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK}) instead.\033[0m")
            THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK = abs(THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK)
        if THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH < 0:
            print(f"\033[94mInput Warning: THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH is negative, using abs({THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH}) instead.\033[0m")
            THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH = abs(THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH)
        if THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK < 0:
            print(f"\033[94mInput Warning: THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK is negative, using abs({THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK}) instead.\033[0m")
            THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK = abs(THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK)

    if PRECOMPILE:
        if len(df_step) > 100_000 or FORCE_PRECOMPILATION:
            with log_time("precompiling step_analyzer_primitives and df_primitives_correction",
                          SHOW_RUNTIME=SHOW_RUNTIME):
                precompilation_step_analyzer()

        else:
            print(
                f"\033[91mInput Warning: Input dataframe is small ({len(df_step)} < 100_000 rows. Skipping precompilation unless you set FORCE_PRECOMPILATION = True.\033[0m")

    if SHOW_RUNTIME: print(f"detecting segments in dataframe of size {len(df_step)}...")

    with log_time("calculating Power[W]", SHOW_RUNTIME=SHOW_RUNTIME):
        df_step["Power[W]"] = df_step["Voltage[V]"] * df_step["Current[A]"]

    for column_name, threshold in SEGMENTS_TO_DETECT_CONFIG:
        with log_time(f"separating {column_name} into segments using incremental linear fit",
                      SHOW_RUNTIME=SHOW_RUNTIME):
            df_step = _split_in_segments_using_incremental_linear_fit(df=df_step,
                                                                      column_name=column_name,
                                                                      threshold=threshold)

    keep_max_segment_id_config = []
    for key, col_name in DATA_COLUMNS.items():
        segment_col = f"Segment_{col_name}"
        with log_time(f"adding Length_{segment_col} to calculate the dominating segments", SHOW_RUNTIME=SHOW_RUNTIME):
            df_step = _add_segment_lengths(df=df_step, column_name=col_name)
        keep_max_segment_id_config.append((f"Length_{segment_col}", segment_col))

    with log_time("suppressing smaller segments", SHOW_RUNTIME=SHOW_RUNTIME):
        df_step = _keep_max_segment_id(df=df_step,
                                       keep_max_segment_id_config=keep_max_segment_id_config)

    with log_time("attempting to merge neighboring segments", SHOW_RUNTIME=SHOW_RUNTIME):
        df_step = _attempt_to_merge_neighboring_segments(df=df_step,
                                                         adjust_segments_config=ADJUST_SEGMENTS_CONFIG)

    with log_time("fine tuning width of constant segments to better fit the data", SHOW_RUNTIME=SHOW_RUNTIME):
        df_step = _widen_constant_segments(df=df_step,
                                           adjust_segments_config=ADJUST_SEGMENTS_CONFIG,
                                           Threshold_segments_to_print=THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH,
                                           supress_IO_warnings=supress_IO_warnings)

    if SHOW_RUNTIME:
        print("starting annotation...")

    df_primitives = _annotate_primitives(
        df_step,
        data_columns=DATA_COLUMNS,
        thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION,
        show_runtime=SHOW_RUNTIME
    )

    with log_time("dropping temporary length and segment columns", SHOW_RUNTIME=SHOW_RUNTIME):
        columns_to_drop = [f"Length_Segment_{v}" for v in DATA_COLUMNS.values()] + \
                          [f"Segment_{v}" for v in DATA_COLUMNS.values()]
        df_primitives = df_primitives.drop(columns=columns_to_drop)


    # Can be removed if we choose to always apply these additional corrections
    if check_CV_0Aend_segments_bool or check_Power_zero_W_segments_bool or check_zero_length_segments_bool:
        if SHOW_RUNTIME:
            print("starting additional data checks and corrections...")
    else:
        if not supress_IO_warnings:
            print("\033[94mInput Warning:  Skipping additional data checks and corrections...\033[0m")

    if check_CV_0Aend_segments_bool:
        df_primitives = _check_CV_0Aend_segments(df_primitives=df_primitives,
                                                 tolerance=THRESHOLD_CV_SEGMENTS_0A_END,
                                                 SHOW_RUNTIME=SHOW_RUNTIME,
                                                 DATA_COLUMNS=DATA_COLUMNS,
                                                 THRESHOLDS_PRIMITIVE_ANNOTATION=THRESHOLDS_PRIMITIVE_ANNOTATION,
                                                 supress_IO_warnings=supress_IO_warnings,
                                                 THRESHOLD_CONSOLE_PRINTS_CV_CHECK=THRESHOLD_CONSOLE_PRINTS_CV_CHECK,
                                                 THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK=THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK)

    if check_zero_length_segments_bool:
        df_primitives = _check_zero_length_segments(df_primitives,
                                                    SHOW_RUNTIME=SHOW_RUNTIME,
                                                    DATA_COLUMNS=DATA_COLUMNS,
                                                    THRESHOLDS_PRIMITIVE_ANNOTATION=THRESHOLDS_PRIMITIVE_ANNOTATION,
                                                    supress_IO_warnings=supress_IO_warnings,
                                                    THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK=THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK)

    if check_Power_zero_W_segments_bool:
        df_primitives = _check_power_zero_watt_segments(df_primitives=df_primitives,
                                                        SHOW_RUNTIME=SHOW_RUNTIME,
                                                        THRESHOLDS_PRIMITIVE_ANNOTATION=THRESHOLDS_PRIMITIVE_ANNOTATION,
                                                        supress_IO_warnings=supress_IO_warnings,
                                                        THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK=THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK,
                                                        DATA_COLUMNS=DATA_COLUMNS)

    if check_CV_0Aend_segments_bool or check_zero_length_segments_bool or check_Power_zero_W_segments_bool:
        with log_time("updating annotations", SHOW_RUNTIME=SHOW_RUNTIME):
            df_primitives = _merged_annotations(df=df_primitives,
                                                data_columns=DATA_COLUMNS,
                                                thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION)

    return df_primitives


@citeme.bachelorthesis('Daniel_BA', {
    'author': 'Daniel Schröder',
    'title': 'Automatisierte Erkennung charakteristischer Abschnitte in Batteriemessdaten auf Basis von Strom, Spannung und Zeit',
    'school': 'Technische Universität Berlin',
    'year': '2026'
})
def step_analyzer_seqments_and_sequences(df_primitives: pd.DataFrame,
                                         SEGMENT_SEQUENCE_CONFIG: dict = None,
                                         SHOW_RUNTIME: bool = True
                                         ) -> pd.DataFrame:
    """

    Create a DataFrame of segments and sequences from a DataFrame of primitives. (ID, longest sequence, segments/sequence)
    Each Segment/Sequence is listed per ID with an incrementally increasing value per match.

    The rules dictionary can contain the following keys:
        - "min_length_sec": minimum length of the segment in seconds
        - "min_avg_abs": minimum average absolute value of the segment
        - "max_slope": maximum slope of the segment
        - "min_abs_slope": minimum absolute slope of the segment
        - "direction": direction of the segment
        - "variable": variable name of the segment
        - "type": type of the segment

    "loop": True can be used to support looping sequences
    "merge": True can be used to support merging multiple subsequences and segments


    Parameters:
        df_primitives (pd.DataFrame): A DataFrame of primitives created using step_analyzer_primitives(). With the following columns:
            standard_columns = ['Testtime[s]', 'Voltage[V]', 'Current[A]', 'Power[W]', "ID", "Variable", "Duration", "Length", "Min", "Max", "Avg", "Type", "Direction", "Slope"]
        SEGMENT_SEQUENCE_CONFIG (dict): A dictionary containing the configuration for the analysis.
            Example:{{"Current": {"rules": {"variable": "I", ...}}}, {"Discharge_iOCV": {"loop": True, "minimum_IDs": 4, "sequence": ["CC_Discharge","Pause"]}}, ...}
        SHOW_RUNTIME (bool): If True, the function logs the time taken to perform each step.

    Returns:
        df_segments_and_sequences (pd.DataFrame): A DataFrame containing the columns 'ID', 'Sequence', and all columns
                                                  specified in SEGMENT_SEQUENCE_CONFIG.

    """


    if SEGMENT_SEQUENCE_CONFIG is None or not isinstance(SEGMENT_SEQUENCE_CONFIG, dict):
        raise ValueError("SEGMENT_SEQUENCE_CONFIG is None or not a dict")

    if df_primitives is None or not isinstance(df_primitives, pd.DataFrame):
        raise ValueError("df_primitives is None or not a DataFrame")

    standard_columns = ['Testtime[s]', 'Voltage[V]', 'Current[A]', 'Power[W]', "ID", "Variable", "Duration", "Length", "Min", "Max", "Avg", "Type", "Direction", "Slope"]
    if not set(standard_columns).issubset(set(df_primitives.columns)):
        print("\033[94mInput Warning: df_primitives doesn't have the standard columns.\033[0m")

    if SHOW_RUNTIME: print("analyzing segments...")
    with log_time("filtering by ID", SHOW_RUNTIME=SHOW_RUNTIME):
        df_ID_filtered = df_primitives.loc[df_primitives.groupby('ID')['ID'].idxmin()]
    # Not with log_time() since it's handled internally
    df_segments_and_sequences = _analyze_segments(df=df_ID_filtered,
                                                  SHOW_RUNTIME=SHOW_RUNTIME,
                                                  SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG)

    return df_segments_and_sequences


@citeme.bachelorthesis('Daniel_BA', {
    'author': 'Daniel Schröder',
    'title': 'Automatisierte Erkennung charakteristischer Abschnitte in Batteriemessdaten auf Basis von Strom, Spannung und Zeit',
    'school': 'Technische Universität Berlin',
    'year': '2026'
})
def precompilation_step_analyzer():
    """
    Precompilation of the step analyzer function using dummy data.

    This function precompiles the numba.njit subfunctions of the step analyzer using dummy data.
    This is useful for having *consistent* runtimes when these subfunctions are called to run multiple times.

    Parameters:
        None

    Returns:
        None
    """
    from pydpeet.process.sequence.utils.configs.CONFIG_preprocessing import STEP_ANALYZER_PRIMITIVES_CONFIG_PRECOMPILE, \
         THRESHOLDS_PRIMITIVE_ANNOTATION, DATA_COLUMNS,  SEGMENT_SEQUENCE_CONFIG
    # precompile using dummy data
    _project_dir = os.path.dirname(os.path.abspath(__file__))
    _res_dir = os.path.join(_project_dir, 'res')
    _input_path = os.path.join(_res_dir, "TEST_INPUT_Daniel_sampled_every_60s_with_first_last.parquet")
    _df_file = pd.read_parquet(_input_path)
    _df_primitives = step_analyzer_primitives(df=_df_file,
                                              STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG_PRECOMPILE,
                                              SHOW_RUNTIME=False,
                                              check_CV_0Aend_segments_bool=True,
                                              check_zero_length_segments_bool=True,
                                              supress_IO_warnings=True,
                                              PRECOMPILE=False)

    correction_config = {
        "replace_ID": {
            1: "V",
        }
    }
    _df_primitives = df_primitives_correction(df_primitives=_df_primitives,
                                              correction_config=correction_config,
                                              data_columns=DATA_COLUMNS,
                                              thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION)

    _ = step_analyzer_seqments_and_sequences(df_primitives=_df_primitives,
                                             SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG,
                                             SHOW_RUNTIME=False)
