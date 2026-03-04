import pandas as pd

from pydpeet.io.utils.formatter_utils import absolute_time_timedate_typecast, fix_time_format


def get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies a series of transformations to the input DataFrame to
    ensure that the "Absolute Time[yyyy-mm-dd hh:mm:ss]" column is in the correct
    datetime format. The time format is initially fixed using the specified
    input format, and then typecast to pandas datetime objects.

    Parameters
    ----------
    data_frame : pd.DataFrame
        The DataFrame to be formatted.

    Returns
    -------
    pd.DataFrame
        The formatted DataFrame with the "Absolute Time[yyyy-mm-dd hh:mm:ss]"
        column converted to datetime objects.
    """
    fix_time_format(df, input_format="%d.%m.%Y %H:%M:%S")
    absolute_time_timedate_typecast(df)

    return df
