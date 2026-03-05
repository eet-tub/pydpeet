import pandas as pd

from pydpeet.io.utils.formatter_utils import absolute_time_timedate_typecast, testtime_hours_to_seconds_with_string_interpretation


def get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format the given DataFrame into a standard format.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame to be formatted

    Returns
    -------
    pandas.DataFrame
        The formatted DataFrame
    """
    df = testtime_hours_to_seconds_with_string_interpretation(df, True)
    df = absolute_time_timedate_typecast(df)

    return df
