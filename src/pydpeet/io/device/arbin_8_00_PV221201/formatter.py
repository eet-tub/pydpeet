import pandas
from pydpeet.io.utils.formatter_utils import absolute_time_timedate_typecast
from pydpeet.io.utils.formatter_utils import testtime_hours_to_seconds_with_string_interpretation


def get_data_into_format(data_frame: pandas.DataFrame) -> pandas.DataFrame:
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
    data_frame = testtime_hours_to_seconds_with_string_interpretation(data_frame, True)
    data_frame = absolute_time_timedate_typecast(data_frame)
    return data_frame








