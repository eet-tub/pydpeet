import pandas as pd

from pydpeet.io.utils.formatter_utils import (
    absolute_time_timedate_typecast,
    testtime_hours_to_seconds_with_string_interpretation,
    typecast,
)


def get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format a DataFrame from a Neware cycler into a standard format.

    The DataFrame is modified in-place.

    Parameters
    ----------
    data_frame : pd.DataFrame
        DataFrame to be formatted

    Returns
    -------
    pd.DataFrame
        Formatted DataFrame
    """
    testtime_hours_to_seconds_with_string_interpretation(df, True)
    df = absolute_time_timedate_typecast(df)
    typecast(df, "Step_Count", int)
    typecast(df, "Temperature[°C]", float)

    return df
