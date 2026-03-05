import inspect
import logging

import numpy as np
import pandas as pd

from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.analyze.utils import (
    StepTimer,
    _check_columns,
)


def add_resistance_internal(
    df: pd.DataFrame,
    config: BatteryConfig = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Calculate the internal resistance of a battery from given test data.

    The internal resistance is calculated from the voltage and current differences
    between consecutive points. The calculation is only performed when the following
    conditions are met:

    1. The time difference is positive (i.e. time is increasing)
    2. The absolute time difference is less than or equal to `max_time_diff`
    3. The absolute current difference is greater than or equal to `min_current_diff`
    4. The absolute voltage difference is greater than or equal to `min_voltage_diff`

    If `ignore_negative_resistance_values` is True, any calculated internal resistances
    with a value less than or equal to zero are set to NaN. (mainly for a bug in Neware)

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing battery test data
    config (BatteryConfig): Configuration object containing parameters for internal resistance calculation
    ignore_negative_resistance_values (bool, optional): Whether to set calculated internal resistances with a value less than or equal to zero to NaN (should only appear for Neware cells)

    Returns:
    pandas.DataFrame: DataFrame with added 'internal_resistance[ohm]', 'delta_t', 'delta_current', and 'delta_voltage' columns
    """
    required_cols = ["Test_Time[s]", "Current[A]", "Voltage[V]"]
    _check_columns(df, required_cols)

    if config is None:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}")

    min_current_diff = config.min_current_diff
    max_time_diff = config.max_time_diff
    min_voltage_diff = config.min_voltage_diff
    ignore_negative_resistance_values = config.ignore_negative_resistance_values

    df_mod = df.copy()
    logging.info(f"Starting internal resistance computation on dataframe of size {len(df_mod)}...")

    # Calculate differences
    with StepTimer(verbose) as st:
        delta_t = df_mod["Test_Time[s]"].diff()
        delta_current = df_mod["Current[A]"].diff()
        delta_voltage = df_mod["Voltage[V]"].diff()
        st.log("calculated delta_t, delta_I, delta_V")

    # Only calculate resistance when:
    mask = (
        (delta_t > 0)  # Time is increasing
        & ((delta_t <= max_time_diff) | (delta_t == 0))  # Within max time window
        & (abs(delta_current) >= min_current_diff)  # Significant current change
        & (abs(delta_voltage) >= min_voltage_diff)  # Significant voltage change
    )

    # Calculate resistance only for valid points
    with StepTimer(verbose) as st:
        with np.errstate(divide="ignore", invalid="ignore"):
            resistance = delta_voltage / delta_current
            resistance[~((delta_current != 0) & mask)] = np.nan  # Set invalid calculations to NaN
        st.log("computed internal resistance for valid points")

    # Assign the calculated resistances
    df_mod["InternalResistance[ohm]"] = resistance

    if ignore_negative_resistance_values:
        df_mod["InternalResistance[ohm]"] = df_mod["InternalResistance[ohm]"].mask(
            df_mod["InternalResistance[ohm]"] <= 0
        )

    return df_mod
