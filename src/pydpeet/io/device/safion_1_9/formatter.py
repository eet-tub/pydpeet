import pandas as pd

from pydpeet.io.utils.formatter_utils import typecast


def get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
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
    typecast(df, "Step_Count", int)
    typecast(df, "EIS_f[Hz]", float)
    typecast(df, "EIS_Z_Real[Ohm]", float)
    typecast(df, "EIS_Z_Imag[Ohm]", float)

    return df
