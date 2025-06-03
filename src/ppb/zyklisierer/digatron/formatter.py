import pandas as pd
from ppb.utils.formatter_utils import fix_time_format
from ppb.utils.formatter_utils import absolute_time_timedate_typecast


def get_data_into_format(data_frame: pd.DataFrame):
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
    fix_time_format(data_frame, input_format='%d.%m.%Y %H:%M:%S')
    absolute_time_timedate_typecast(data_frame)
    return data_frame

