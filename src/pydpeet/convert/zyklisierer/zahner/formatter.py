import pandas
from pydpeet.convert.utils.formatter_utils import round_testtime
from pydpeet.convert.utils.formatter_utils import nan_to_none_in_column
from pydpeet.convert.utils.formatter_utils import typecast


def get_data_into_format_zahner_1(dataFrame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Format a DataFrame in the format of a Zahner EIS file, type 1.

    The DataFrame is modified in-place.

    The modifications are as follows:

    - The "Testtime[s]" column is rounded to 5 decimal places.
    - NaN values in the "Testtime[s]" column are replaced with None.
    - The "StepID" column is typecast to int.
    - The "EISFreq[Hz]" column is typecast to float.
    - The "Zre[Ohm]" column is typecast to float.
    - The "Zim[Ohm]" column is typecast to float.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame.
    """
    dataFrame = round_testtime(dataFrame)
    dataFrame = nan_to_none_in_column(dataFrame, "Testtime[s]")
    typecast(dataFrame, "StepID", int)
    typecast(dataFrame, "EISFreq[Hz]", float)
    typecast(dataFrame, "Zre[Ohm]", float)
    typecast(dataFrame, "Zim[Ohm]", float)

    return dataFrame


def get_data_into_format_zahner_2(dataFrame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Format a DataFrame in the format of a Zahner EIS file, type 2.

    The DataFrame is modified in-place.

    The modifications are as follows:

    - The "Testtime[s]" column is rounded to 5 decimal places.
    - NaN values in the "Testtime[s]" column are replaced with None.
    - The "StepID" column is typecast to int.
    - The "Voltage[V]" column is typecast to float.
    - The "Current[A]" column is typecast to float.
    - The "Testtime[s]" column is typecast to float.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame.
    """
    dataFrame = round_testtime(dataFrame)
    dataFrame = nan_to_none_in_column(dataFrame, "Testtime[s]")
    typecast(dataFrame, "StepID", int)
    typecast(dataFrame, "Voltage[V]", float)
    typecast(dataFrame, "Current[A]", float)
    typecast(dataFrame, "Testtime[s]", float)

    return dataFrame