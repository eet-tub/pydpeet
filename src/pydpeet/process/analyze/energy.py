import inspect
import logging

import pandas as pd
from scipy import integrate

from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.analyze.power import add_power
from pydpeet.process.analyze.utils import (
    StepTimer,
    _check_columns,
)


def add_cumulative_energy(
    df: pd.DataFrame,
    config: BatteryConfig = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Calculates cumulative energy [Wh] from 'Test_Time[s]' and 'Power[W]' columns and adds it as a new column.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing 'Test_Time[s]' and 'Power[W]' columns
    - cumu_energy_method (CumulativeEnergyMethod): Method to use for cumulative energy calculation
    - config (BatteryConfig): Config object containing max and min voltage values

    Returns:
    - pandas.DataFrame: DataFrame with added 'CumulativeEnergy[Wh]' column
    """
    logging.info("Calculating CumulativeEnergy[Wh]...")

    if config is None:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}")

    df_mod = df.copy()
    if "Power[W]" not in df_mod.columns:
        logging.info("Power[W] column missing → adding via add_power.")
        with StepTimer(verbose) as st:
            df_mod = add_power(df_mod)
            st.log("added Power[W] column")

    with StepTimer(verbose) as st:
        _check_columns(df_mod, ["Test_Time[s]", "Power[W]"])
        df_mod["CumulativeEnergy[Wh]"] = (
            integrate.cumulative_trapezoid(df_mod["Power[W]"], x=df_mod["Test_Time[s]"], initial=0) / 3600
        )
        st.log("calculated CumulativeEnergy[Wh]")

    return df_mod
