import pandas
from pydpeet.convert.utils.formatter_utils import typecast


def get_data_into_format(dataFrame: pandas.DataFrame):
    """
    Format a DataFrame into standard format required by the database.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be formatted.

    Returns
    -------
    pandas.DataFrame
        Formatted DataFrame.
    """
    typecast(dataFrame, "StepID", int)
    typecast(dataFrame, "EISFreq[Hz]", float)
    typecast(dataFrame, "Zre[Ohm]", float)
    typecast(dataFrame, "Zim[Ohm]", float)

    return dataFrame
