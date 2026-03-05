import logging

import pandas as pd

from pydpeet.process.analyze.utils import (
    StepTimer,
    _check_columns,
)


def add_power(
    df: pd.DataFrame,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Calculates power [W] from 'Current[A]' and 'Voltage[V]' columns and adds it as a new column.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing 'Current[A]' and 'Voltage[V]' columns

    Returns:
    - pandas.DataFrame: DataFrame with added 'Power[W]' column
    """
    logging.info("Calculating Power[W]...")

    df_mod = df.copy()
    with StepTimer(verbose) as st:
        _check_columns(df_mod, ["Current[A]", "Voltage[V]"])
        df_mod["Power[W]"] = df_mod["Current[A]"] * df_mod["Voltage[V]"]
        st.log("calculated Power[W]")

    return df_mod
