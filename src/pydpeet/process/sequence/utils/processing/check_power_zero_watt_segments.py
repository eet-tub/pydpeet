import logging

import numpy as np
import pandas as pd

from pydpeet.process.sequence.utils.console_prints.log_time import log_time
from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction


def _check_power_zero_watt_segments(
    df_primitives: pd.DataFrame,
    SHOW_RUNTIME: bool,
    THRESHOLDS_PRIMITIVE_ANNOTATION: dict[str, float],
    supress_IO_warnings: bool,
    THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK: int,
    DATA_COLUMNS: dict[str, str],
) -> pd.DataFrame:
    """
    Check all segments in the dataframe for power segments with 0W and correct them by replacing them with a current or voltage segment.

    Parameters:
    df_primitives (pd.DataFrame): DataFrame containing the primitives
    SHOW_RUNTIME (bool): whether to print runtime information
    THRESHOLDS_PRIMITIVE_ANNOTATION (dict): dictionary of threshold values for primitive annotation
        Example: {"I": 0.1, "P": 0.1, "V": 0.1}
    supress_IO_warnings (bool): whether to suppress runtime warnings
    THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK (int): threshold for the number of corrected segments to print
    DATA_COLUMNS (dict): dictionary of column names to be kept in the DataFrame
        Example: {"I": "Current[A]", "P": "Power[W]", "V": "Voltage[V]"}

    Returns:
    pd.DataFrame: Dataframe with added columns for annotated primitives
    """
    with log_time("checking Power segments with 0W", SHOW_RUNTIME=SHOW_RUNTIME):
        tol_current = THRESHOLDS_PRIMITIVE_ANNOTATION["I"]
        tol_voltage = THRESHOLDS_PRIMITIVE_ANNOTATION["V"]

        mask_P_current_zero = (df_primitives["Variable"] == "P") & (np.abs(df_primitives["Current[A]"]) < tol_current)
        mask_P_current_nonzero = (df_primitives["Variable"] == "P") & (
            np.abs(df_primitives["Voltage[V]"]) < tol_voltage
        )

        zero_Watt_ids_current = df_primitives.loc[mask_P_current_zero, "ID"].unique().tolist()
        zero_Watt_ids_voltage = df_primitives.loc[mask_P_current_nonzero, "ID"].unique().tolist()

        if not supress_IO_warnings:
            if zero_Watt_ids_current or zero_Watt_ids_voltage:
                logging.warning("Power Segments with 0W found.")
            if THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK:
                if zero_Watt_ids_current:
                    if len(zero_Watt_ids_current) > THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK:
                        logging.warning(
                            f"Replaced with current segment: {zero_Watt_ids_current[:THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK]}, ..."
                        )
                    else:
                        logging.warning(
                            f"Replaced with current segment: {zero_Watt_ids_current[:THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK]}"
                        )
                if zero_Watt_ids_voltage:
                    if len(zero_Watt_ids_voltage) > THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK:
                        logging.warning(
                            f"Replaced with voltage segment: {zero_Watt_ids_voltage[:THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK]}, ..."
                        )
                    else:
                        logging.warning(
                            f"Replaced with voltage segment: {zero_Watt_ids_voltage[:THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK]}"
                        )

    with log_time("correcting Power segments with 0W", SHOW_RUNTIME=SHOW_RUNTIME):
        correction_config = {
            "replace_ID": {
                **{id: "I" for id in zero_Watt_ids_current},
                **{id: "V" for id in zero_Watt_ids_voltage},
            }
        }
        df_primitives = df_primitives_correction(
            df_primitives=df_primitives,
            correction_config=correction_config,
            data_columns=DATA_COLUMNS,
            thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION,
            reindex=False,
            reannotate=False,
        )

    return df_primitives
