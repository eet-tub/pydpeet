import pandas as pd

from pydpeet.io.utils.formatter_utils import nan_to_none_in_column, round_testtime, typecast


def get_data_into_format_zahner_1(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds the values in the "Testtime[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "StepID" and "EISFreq[Hz]" columns to int and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    round_testtime(df)
    nan_to_none_in_column(df, "Testtime[s]")
    typecast(df, "StepID", int)
    typecast(df, "EISFreq[Hz]", float)

    return df


def get_data_into_format_zahner_2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds the values in the "Testtime[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "StepID", "Voltage[V]", and "Current[A]" columns to int, float, and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    df = round_testtime(df)
    df = nan_to_none_in_column(df, "Testtime[s]")
    typecast(df, "StepID", int)
    typecast(df, "Voltage[V]", float)
    typecast(df, "Current[A]", float)

    return df


def get_data_into_format_zahner_3(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds the values in the "Testtime[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "StepID", "Voltage[V]", "Current[A]", and "EISFreq[Hz]" columns to int, float, float, and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    df = round_testtime(df)
    df = nan_to_none_in_column(df, "Testtime[s]")
    typecast(df, "StepID", int)
    typecast(df, "Voltage[V]", float)
    typecast(df, "Current[A]", float)
    typecast(df, "EISFreq[Hz]", float)

    return df
