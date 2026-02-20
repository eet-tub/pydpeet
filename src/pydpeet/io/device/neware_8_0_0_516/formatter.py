import pandas as pd
from pydpeet.io.utils.formatter_utils import testtime_hours_to_seconds_with_string_interpretation
from pydpeet.io.utils.formatter_utils import absolute_time_timedate_typecast
from pydpeet.io.utils.formatter_utils import typecast

def get_data_into_format(data_frame: pd.DataFrame) -> pd.DataFrame:
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
    testtime_hours_to_seconds_with_string_interpretation(data_frame, True)
    data_frame = absolute_time_timedate_typecast(data_frame)
    typecast(data_frame, "StepID", int)
    typecast(data_frame, "Temperature[°C]", float)
    return data_frame
