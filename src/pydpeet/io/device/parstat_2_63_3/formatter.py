import pandas as pd

from pydpeet.io.utils.formatter_utils import round_testtime, typecast


def get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format the given DataFrame into a standard format.

    This function takes a DataFrame and applies some formatting to it. It rounds the
    "Testtime[s]" column to 5 decimal places, and typecasts the "StepID", "Voltage[V]",
    "Current[A]", "Testtime[s]", "EISFreq[Hz]", "Zre[Ohm]" and "Zim[Ohm]" columns to
    int, float, float, float, float, float and float respectively.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame to be formatted

    Returns
    -------
    pandas.DataFrame
        Formatted DataFrame
    """
    df = round_testtime(df)
    typecast(df, "StepID", int)
    typecast(df, "Voltage[V]", float)
    typecast(df, "Current[A]", float)
    typecast(df, "Testtime[s]", float)
    typecast(df, "EISFreq[Hz]", float)
    typecast(df, "Zre[Ohm]", float)
    typecast(df, "Zim[Ohm]", float)

    return df
