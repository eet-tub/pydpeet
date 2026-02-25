import pandas

from pydpeet.io.utils.formatter_utils import round_testtime


def get_data_into_format(dataFrame: pandas.DataFrame):
    """
    Rounds the values in the "Testtime[s]" column of the DataFrame to 5 decimal places.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame containing the "Testtime[s]" column to be rounded.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with rounded "Testtime[s]" values.
    """
    dataFrame = round_testtime(dataFrame)
    return dataFrame
