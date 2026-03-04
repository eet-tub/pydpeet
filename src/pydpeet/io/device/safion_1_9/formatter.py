import pandas as pd

from pydpeet.io.utils.formatter_utils import typecast


def get_data_into_format(df: pd.DataFrame) -> pd.DateFrame:
    """
    Format a DataFrame into standard format required by the database.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be formatted.

    Returns
    -------
    pandas.DataFrame
        Formatted DataFrame.
    """
    typecast(df, "StepID", int)
    typecast(df, "EISFreq[Hz]", float)
    typecast(df, "Zre[Ohm]", float)
    typecast(df, "Zim[Ohm]", float)

    return df
