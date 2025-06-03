import pandas
from ppb.utils.formatter_utils import round_testtime
from ppb.utils.formatter_utils import typecast

def get_data_into_format(data_frame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Format the given DataFrame into a standard format.

    This function takes a DataFrame and applies some formatting to it. It rounds the
    "Testtime[s]" column to 5 decimal places, and typecasts the "StepID", "Voltage[V]",
    "Current[A]", "Testtime[s]", "EISFreq[Hz]", "Zre[Ohm]" and "Zim[Ohm]" columns to
    int, float, float, float, float, float and float respectively.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame to be formatted

    Returns
    -------
    pandas.DataFrame
        Formatted DataFrame
    """
    data_frame = round_testtime(data_frame)
    typecast(data_frame, "StepID", int)
    typecast(data_frame, "Voltage[V]", float)
    typecast(data_frame, "Current[A]", float)
    typecast(data_frame, "Testtime[s]", float)
    typecast(data_frame, "EISFreq[Hz]", float)
    typecast(data_frame, "Zre[Ohm]", float)
    typecast(data_frame, "Zim[Ohm]", float)
    return data_frame



