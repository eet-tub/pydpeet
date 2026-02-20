import inspect
import logging

from scipy import integrate

from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.analyze.power import add_power
from pydpeet.process.analyze.utils import StepTimer, _check_columns

# ** Functions that add new columns to the DataFrame and are not complex enough be in a separate file **


def add_cumulative_energy(df, config: BatteryConfig = None, verbose=True):
    """
    Calculates cumulative energy [Wh] from 'Testtime[s]' and 'Power[W]' columns and adds it as a new column.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing 'Testtime[s]' and 'Power[W]' columns
    - cumu_energy_method (CumulativeEnergyMethod): Method to use for cumulative energy calculation
    - config (BatteryConfig): Config object containing max and min voltage values

    Returns:
    - pandas.DataFrame: DataFrame with added 'CumulativeEnergy[Wh]' column
    """
    logging.info("Calculating CumulativeEnergy[Wh]...")

    if config is None:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}")

    if "Power[W]" not in df.columns:
        logging.info("Power[W] column missing → adding via add_power.")
        with StepTimer(verbose) as st:
            df = add_power(df)
            st.log("added Power[W] column")

    with StepTimer(verbose) as st:
        _check_columns(df, ["Testtime[s]", "Power[W]"])
        df["CumulativeEnergy[Wh]"] = integrate.cumulative_trapezoid(df["Power[W]"], x=df["Testtime[s]"], initial=0) / 3600
        st.log("calculated CumulativeEnergy[Wh]")

    return df
