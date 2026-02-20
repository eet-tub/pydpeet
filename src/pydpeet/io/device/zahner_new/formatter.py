import pandas

from pydpeet.io.utils.formatter_utils import nan_to_none_in_column, round_testtime, typecast


def get_data_into_format_zahner_1(dataFrame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Rounds the values in the "Testtime[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "StepID" and "EISFreq[Hz]" columns to int and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    round_testtime(dataFrame)
    nan_to_none_in_column(dataFrame, "Testtime[s]")
    typecast(dataFrame, "StepID", int)
    typecast(dataFrame, "EISFreq[Hz]", float)

    return dataFrame


def get_data_into_format_zahner_2(dataFrame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Rounds the values in the "Testtime[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "StepID", "Voltage[V]", and "Current[A]" columns to int, float, and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    dataFrame = round_testtime(dataFrame)
    dataFrame = nan_to_none_in_column(dataFrame, "Testtime[s]")
    typecast(dataFrame, "StepID", int)
    typecast(dataFrame, "Voltage[V]", float)
    typecast(dataFrame, "Current[A]", float)

    return dataFrame


def get_data_into_format_zahner_3(dataFrame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Rounds the values in the "Testtime[s]" column of the DataFrame to 5 decimal places, replaces NaN values with None, and typecasts the "StepID", "Voltage[V]", "Current[A]", and "EISFreq[Hz]" columns to int, float, float, and float, respectively.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    dataFrame = round_testtime(dataFrame)
    dataFrame = nan_to_none_in_column(dataFrame, "Testtime[s]")
    typecast(dataFrame, "StepID", int)
    typecast(dataFrame, "Voltage[V]", float)
    typecast(dataFrame, "Current[A]", float)
    typecast(dataFrame, "EISFreq[Hz]", float)

    return dataFrame
