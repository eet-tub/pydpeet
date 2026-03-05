import logging

import numpy as np
import pandas as pd


def typecast(
        df: pd.DataFrame,
        column_name: str,
        datatype
) -> pd.DataFrame | None:
    """
    Try to typecast a column in a DataFrame to a given type.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame to be modified
    column_name : str
        Name of the column to be typecast
    datatype : type
        datatype to which the column should be typecast

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    try:
        if df is None:
            raise ValueError(f"{df} is None")
        if column_name is None:
            raise ValueError(f"{column_name} is None")
        if datatype is None:
            raise ValueError(f"{datatype} is None")
        if type(column_name) is not str:
            raise ValueError(f"{column_name} is not a string")
        if column_name not in df.columns:
            raise ValueError(f"{column_name} is not in {df.columns}")
        df[column_name] = df[column_name].astype(datatype)
    except Exception:
        logging.warning(f"Error converting column:{column_name} to {datatype.__name__}")
    return df


def testtime_hours_to_seconds_with_string_interpretation(
        df: pd.DataFrame,
        astype_string: bool
) -> pd.DataFrame | None:
    """
    Convert "Test_Time[s]" column from hours to seconds with string interpretation. (assumes hours are in "HH:MM:SS.MS" format)

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame to be modified
    astype_string : bool, optional
        Whether to convert the column to string type before applying the
        conversion function. This is useful if the column contains both numeric
        and string values.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    try:
        if df is None:
            raise ValueError(f"{df} is None")
        if not isinstance(astype_string, bool):
            raise ValueError(f"{astype_string} is not a boolean")
        if "Test_Time[s]" not in df.columns:
            raise ValueError(f"Test_Time[s] is not in {df.columns}")
        if astype_string:
            df["Test_Time[s]"] = df["Test_Time[s]"].astype(str).apply(_time_to_seconds)
        else:
            df["Test_Time[s]"] = df["Test_Time[s]"].apply(_time_to_seconds)
    except Exception:
        logging.warning("Error fixing Test_Time[s]")
    return df


def _time_to_seconds(time: str) -> float | None:
    """
    Convert a time string from the format "HH:MM:SS" to a total number of seconds.

    Parameters
    ----------
    time : str
        Time string to be converted, expected in the format "HH:MM:SS".
        If the input is not in this format, attempts to convert it to a float.

    Returns
    -------
    float
        Total time in seconds. If the input is None or cannot be split into
        hours, minutes, and seconds, returns the input as a float.

    Raises
    ------
    ValueError
        If the input time is None.
    """
    try:
        if time is None:
            raise ValueError(f"{time} is None")
        h, m, s = time.split(":")
        return float(s) + int(m) * 60 + int(h) * 3600
    except Exception:
        if time is None:
            return time
        return float(time)


def apply_convert_to_float_if_possible(
        df: pd.DataFrame,
        column_name: str
) -> pd.DataFrame | None:
    """
    Apply a function to a DataFrame column that tries to convert its values to float if possible.

    This function tries to convert the values to a float, and returns the value as a
    float if successful. If not successful, the value is returned as is.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame containing the column to be modified.
    column_name : str
        Name of the column in the DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with the column converted to float if possible.
    """
    try:
        if df is None:
            raise ValueError("dataFrame is None")
        if column_name is None:
            raise ValueError("column_name is None")
        if column_name not in df.columns:
            raise ValueError(f"{column_name} is not in {df.columns}")
        df[column_name] = df[column_name].apply(_convert_to_float_if_possible)
    except Exception:
        logging.warning(f"Error applying convert_to_float_if_possible for {column_name}")
    return df


def _convert_to_float_if_possible(x) -> float:
    """
    Try to convert a value to a float if possible.

    This function takes a value, and tries to convert it to a float. If the
    conversion is successful, the function returns the value as a float. If
    not successful, the value is returned as is.

    Parameters
    ----------
    x : any
        Value to be converted to a float if possible.

    Returns
    -------
    any
        Value converted to a float if possible, otherwise the original value.

    """
    try:
        return np.float64(x)
    except (ValueError, TypeError):
        return x


def replace_empty_with_none_in_standard_columns(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Replace empty strings with None in the columns specified in src.convert.STANDARD_COLUMNS.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    from pydpeet.io.convert import STANDARD_COLUMNS

    try:
        if df is None:
            raise ValueError("dataFrame is None")
        if df.empty:
            raise ValueError("dataframe is empty")
        df[STANDARD_COLUMNS] = df[STANDARD_COLUMNS].replace("", None)
    except Exception as e:
        logging.warning(f"Error replacing empty with None. Reason: {e}")
    return df


def testtime_hours_to_seconds_direct(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Convert "Test_Time[s]" column from hours to seconds.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame to be modified

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame
    """
    try:
        if df is None:
            raise ValueError("dataFrame is None")
        if "Test_Time[s]" not in df.columns:
            raise ValueError("Test_Time[s] is not in dataFrame.columns")
        df["Test_Time[s]"] = df["Test_Time[s]"].apply(_convert_to_hours_to_seconds_direct_if_possible)
    except Exception as e:
        logging.warning(f"Error fixing Test_Time[s] (converting hours to seconds). Reason: {e}")
    return df


def _convert_to_hours_to_seconds_direct_if_possible(x) -> float:
    # TODO: Docstring
    try:
        return np.float64(x) * 3600
    except (ValueError, TypeError):
        return x


def round_testtime(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Round the values in the "Test_Time[s]" column of the DataFrame to 5 decimal places.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame containing the "Test_Time[s]" column to be rounded.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with rounded "Test_Time[s]" values.
    """
    try:
        if df is None:
            raise ValueError("dataFrame is None")
        if df.empty:
            raise ValueError("dataframe is empty")
        if "Test_Time[s]" not in df.columns:
            raise ValueError("Test_Time[s] is not in dataFrame.columns")

        df["Test_Time[s]"] = round(df["Test_Time[s]"].astype(float), 5)
    except Exception as e:
        logging.warning(f"Error fixing Test_Time[s] (rounding). Reason: {e}")
    return df


def nan_to_none_in_column(
        df: pd.DataFrame,
        column_name: str
) -> pd.DataFrame | None:
    """
    Replace NaN values in a DataFrame column (column_name) with None.

    Parameters
    ----------
    dataFrame : pandas.DataFrame
        DataFrame containing the column to be modified.
    column_name : str
        Name of the column in the DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with NaN values replaced with None.
    """
    try:
        if df is None:
            raise ValueError("dataFrame is None")
        if column_name is None:
            raise ValueError("column_name is None")
        if type(column_name) is not str:
            raise ValueError("column_name is not a string")
        if column_name not in df.columns:
            raise ValueError(f"{column_name} is not in {df.columns}")
        df[column_name] = df[column_name].replace({np.nan: None})
    except Exception:
        logging.warning(f"Error fixing {column_name} (replacing NaN with None)")
    return df


def move_strings_from_column_to_metadata(
        df: pd.DataFrame,
        column_name: str
) -> pd.DataFrame | None:
    """
    Move strings from a column into the "Meta_Data" column and replace them with None.

    This function takes a DataFrame and a column name as input, and moves all strings in that column to the
    "Meta_Data" column. The strings are joined together with a newline character and added to the existing
    "Meta_Data" content. The original column is then replaced with None values.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame containing the column to be modified.
    column_name : str
        Name of the column in the DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with strings moved to "Meta_Data" and replaced with None in the original column.
    """
    concatenated_string = "\n"
    try:
        if df is None:
            raise ValueError("dataFrame is None")
        if not isinstance(column_name, str):
            raise ValueError(f"column_name is not a string. Type is {type(column_name)}")
        if column_name not in df.columns:
            raise ValueError(f"{column_name} is not in {df.columns}")
        if "Meta_Data" not in df.columns:
            raise ValueError("Meta_Data Column doesn't exsist")

        strings = df[column_name].apply(lambda x: x if isinstance(x, str) else None)
        concatenated_string = concatenated_string.join(filter(None, strings))

        df.loc[0, "Meta_Data"] = str(df.loc[0, "Meta_Data"]) + "\n\n" + concatenated_string
        df[column_name] = df[column_name].apply(lambda x: None if isinstance(x, str) else x).astype(object)
        df[column_name] = df[column_name].replace({np.nan: None})
    except Exception:
        logging.warning("Error adding Messages to Meta_Data")
    return df


def fix_time_format(
        df: pd.DataFrame,
        input_format: str = None
) -> pd.DataFrame | None:
    """
    Fix the format of the "Date_Time" column.

    This function takes a DataFrame and an optional input format as input, and
    attempts to convert the "Date_Time" column to a
    datetime object using the given input format. If the input format is not
    given, the function will try to infer the format from the data. The
    resulting datetime object is then formatted as a string in the format
    '%Y-%m-%d %H:%M:%S' and replaces the original column.
    Fills empty parts with pandas.NaT.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame containing the column to be modified.
    input_format : str, optional
        Format string to use when converting the column to a datetime object.
        If not given, the function will try to infer the format from the data.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with the "Date_Time" column
        converted to the correct format.
    """
    column_name = "Date_Time"

    try:
        if df is None:
            raise ValueError("data_frame is None")
        if not isinstance(input_format, str):
            raise ValueError(f"input_format is not a string. Type is {type(column_name)}")
        if column_name not in df.columns:
            raise ValueError(f"{column_name} is not in {df.columns}")
        if "Date_Time" not in df.columns:
            raise ValueError("Date_Time Column doesn't exsist")
        try:
            df[column_name] = pd.to_datetime(df[column_name], format=input_format, errors="coerce")
        except Exception:
            raise ValueError("Error changing to datetime")
        try:
            df[column_name] = df[column_name].dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            raise ValueError("Error changing to correct order in Timeformat")
    except Exception:
        logging.warning("Error fixing timeformat Date_Time")
    return df


def absolute_time_timedate_typecast(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Convert the "Date_Time" column in the DataFrame to a datetime object.

    This function attempts to typecast the specified column in the DataFrame to a pandas datetime object.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame containing the column to be converted.

    Returns
    -------
    pandas.DataFrame
        The DataFrame with the "Date_Time" column converted to datetime objects.
    """
    try:
        if df is None:
            raise ValueError("data_frame is None")
        if "Date_Time" not in df.columns:
            raise ValueError("Date_Time Column doesn't exsist")
        df["Date_Time"] = pd.to_datetime(df["Date_Time"], errors="coerce")
    except Exception:
        logging.warning("Error typecasting Date_Time")
    return df
