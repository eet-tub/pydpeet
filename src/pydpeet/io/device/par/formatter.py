import pandas as pd

from pydpeet.io.utils.formatter_utils import _round_testtime


def _get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds the "Test_Time[s]" column to five decimal places.

    The numeric data types are already inferred by pandas when the reader
    parses the .par file into a DataFrame.

    Parameters:
    df (pandas.DataFrame): DataFrame in the standardized PyDPEET format.

    Returns:
    pandas.DataFrame: The formatted DataFrame.
    """
    return _round_testtime(df)
