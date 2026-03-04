import pandas as pd

from pydpeet.io.utils.formatter_utils import round_testtime, testtime_hours_to_seconds_direct


def get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a pandas DataFrame and applies two functions to it:

    1. `testtime_hours_to_seconds_direct`: converts the "Test_Time[s]" column from hours to seconds with string interpretation.
    2. `round_testtime`: rounds the "Test_Time[s]" column down to the nearest second.

    Returns the modified DataFrame.
    """
    df = testtime_hours_to_seconds_direct(df)
    df = round_testtime(df)

    return df
