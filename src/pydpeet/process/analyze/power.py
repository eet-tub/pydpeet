import inspect
import logging

from scipy import integrate

from pydpeet.process.analyze.utils import _check_columns, StepTimer
from pydpeet.process.analyze.configs.battery_config import BatteryConfig

# ** Functions that add new columns to the DataFrame and are not complex enough be in a separate file **


def add_power(df, verbose=True):
    """
    Calculates power [W] from 'Current[A]' and 'Voltage[V]' columns and adds it as a new column.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing 'Current[A]' and 'Voltage[V]' columns

    Returns:
    - pandas.DataFrame: DataFrame with added 'Power[W]' column
    """
    logging.info("Calculating Power[W]...")
    with StepTimer(verbose) as st:
        _check_columns(df, ['Current[A]', 'Voltage[V]'])
        df['Power[W]'] = df['Current[A]'] * df['Voltage[V]']
        st.log("calculated Power[W]")
    return df