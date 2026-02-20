import pandas

from pydpeet.io.utils.formatter_utils import round_testtime, testtime_hours_to_seconds_direct


def get_data_into_format(dataFrame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Takes a pandas DataFrame and applies two functions to it:

    1. `testtime_hours_to_seconds_direct`: converts the "Testtime[s]" column from hours to seconds with string interpretation.
    2. `round_testtime`: rounds the "Testtime[s]" column down to the nearest second.

    Returns the modified DataFrame.
    """
    dataFrame = testtime_hours_to_seconds_direct(dataFrame)
    dataFrame = round_testtime(dataFrame)
    return dataFrame
