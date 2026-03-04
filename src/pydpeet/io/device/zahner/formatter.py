import pandas as pd

from pydpeet.io.utils.formatter_utils import nan_to_none_in_column, round_testtime, typecast


def get_data_into_format_zahner_1(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format a DataFrame in the format of a Zahner EIS file, type 1.

    The DataFrame is modified in-place.

    The modifications are as follows:

    - The "Testtime[s]" column is rounded to 5 decimal places.
    - NaN values in the "Testtime[s]" column are replaced with None.
    - The "StepID" column is typecast to int.
    - The "EISFreq[Hz]" column is typecast to float.
    - The "Zre[Ohm]" column is typecast to float.
    - The "Zim[Ohm]" column is typecast to float.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame.
    """
    df = round_testtime(df)
    df = nan_to_none_in_column(df, "Testtime[s]")
    typecast(df, "StepID", int)
    typecast(df, "EISFreq[Hz]", float)
    typecast(df, "Zre[Ohm]", float)
    typecast(df, "Zim[Ohm]", float)

    return df


def get_data_into_format_zahner_2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format a DataFrame in the format of a Zahner EIS file, type 2.

    The DataFrame is modified in-place.

    The modifications are as follows:

    - The "Testtime[s]" column is rounded to 5 decimal places.
    - NaN values in the "Testtime[s]" column are replaced with None.
    - The "StepID" column is typecast to int.
    - The "Voltage[V]" column is typecast to float.
    - The "Current[A]" column is typecast to float.
    - The "Testtime[s]" column is typecast to float.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame.
    """
    df = round_testtime(df)
    df = nan_to_none_in_column(df, "Testtime[s]")
    typecast(df, "StepID", int)
    typecast(df, "Voltage[V]", float)
    typecast(df, "Current[A]", float)
    typecast(df, "Testtime[s]", float)

    return df
