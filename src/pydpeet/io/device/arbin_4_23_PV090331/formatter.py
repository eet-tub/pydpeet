import pandas as pd

from pydpeet.io.utils.formatter_utils import round_testtime


def get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
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
    df = round_testtime(df)

    return df
