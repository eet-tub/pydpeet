import numpy as np
import pandas


def typecast(data_frame: pandas.DataFrame, column_name: str, datatype) -> pandas.DataFrame:
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
        if data_frame is None:
            raise ValueError(f"{data_frame} is None")
        if column_name is None:
            raise ValueError(f"{column_name} is None")
        if datatype is None:
            raise ValueError(f"{datatype} is None")
        if type(column_name) is not str:
            raise ValueError(f"{column_name} is not a string")
        if column_name not in data_frame.columns:
            raise ValueError(f"{column_name} is not in {data_frame.columns}")
        data_frame[column_name] = data_frame[column_name].astype(datatype)
    except Exception:
        print(f"\033[31mWARNING: Error converting column:{column_name} to {datatype.__name__}\033[0m")
    return data_frame


def testtime_hours_to_seconds_with_string_interpretation(data_frame: pandas.DataFrame, astype_string: bool) -> pandas.DataFrame | None:
    """
    Convert "Testtime[s]" column from hours to seconds with string interpretation. (assumes hours are in "HH:MM:SS.MS" format)

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
        if data_frame is None:
            raise ValueError(f"{data_frame} is None")
        if not isinstance(astype_string, bool):
            raise ValueError(f"{astype_string} is not a boolean")
        if "Testtime[s]" not in data_frame.columns:
            raise ValueError(f"Testtime[s] is not in {data_frame.columns}")
        if astype_string:
            data_frame["Testtime[s]"] = data_frame["Testtime[s]"].astype(str).apply(_time_to_seconds)
        else:
            data_frame["Testtime[s]"] = data_frame["Testtime[s]"].apply(_time_to_seconds)
    except Exception:
        print("\033[31mWARNING: Error fixing Testtime[s] \033[0m")
    return data_frame


def _time_to_seconds(time):
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


def apply_convert_to_float_if_possible(data_frame: pandas.DataFrame, column_name: str) -> pandas.DataFrame:
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
        if data_frame is None:
            raise ValueError("dataFrame is None")
        if column_name is None:
            raise ValueError("column_name is None")
        if column_name not in data_frame.columns:
            raise ValueError(f"{column_name} is not in {data_frame.columns}")
        data_frame[column_name] = data_frame[column_name].apply(_convert_to_float_if_possible)
    except Exception:
        print(f"\033[31mWARNING: Error applying convert_to_float_if_possible for {column_name}\033[0m")
    return data_frame


def _convert_to_float_if_possible(x):
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


def replace_empty_with_none_in_standard_columns(data_frame: pandas.DataFrame):
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
    from ppb.convert import STANDARD_COLUMNS
    try:
        if data_frame is None:
            raise ValueError("dataFrame is None")
        if data_frame.empty:
            raise ValueError("dataframe is empty")
        data_frame[STANDARD_COLUMNS] = data_frame[STANDARD_COLUMNS].replace("", None)
    except Exception as e:
        print(f"\033[31mWARNING: Error replacing empty with None. Reason: {e} \033[0m")
    return data_frame


def testtime_hours_to_seconds_direct(data_frame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Convert "Testtime[s]" column from hours to seconds.

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
        if data_frame is None:
            raise ValueError("dataFrame is None")
        if "Testtime[s]" not in data_frame.columns:
            raise ValueError("Testtime[s] is not in dataFrame.columns")
        data_frame["Testtime[s]"] = data_frame["Testtime[s]"].apply(_convert_to_hours_to_seconds_direct_if_possible)
    except Exception as e:
        print(f"\033[31mWARNING: Error fixing Testtime[s] (converting hours to seconds). Reason: {e} \033[0m")
    return data_frame


def _convert_to_hours_to_seconds_direct_if_possible(x):
    try:
        return np.float64(x) * 3600
    except (ValueError, TypeError):
        return x



def round_testtime(data_frame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Round the values in the "Testtime[s]" column of the DataFrame to 5 decimal places.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame containing the "Testtime[s]" column to be rounded.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with rounded "Testtime[s]" values.
    """

    try:
        if data_frame is None:
            raise ValueError("dataFrame is None")
        if data_frame.empty:
            raise ValueError("dataframe is empty")
        if "Testtime[s]" not in data_frame.columns:
            raise ValueError("Testtime[s] is not in dataFrame.columns")

        data_frame["Testtime[s]"] = round(data_frame["Testtime[s]"].astype(float), 5)
    except Exception as e:
        print(f"\033[31mWARNING: Error fixing Testtime[s] (rounding). Reason: {e} \033[0m")
    return data_frame

def nan_to_none_in_column(dataFrame: pandas.DataFrame, column_name: str) -> pandas.DataFrame | None:
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
        if dataFrame is None:
            raise ValueError(f"dataFrame is None")
        if column_name is None:
            raise ValueError(f"column_name is None")
        if type(column_name) is not str:
            raise ValueError(f"column_name is not a string")
        if column_name not in dataFrame.columns:
            raise ValueError(f"{column_name} is not in {dataFrame.columns}")
        dataFrame[column_name] = dataFrame[column_name].replace({np.nan: None})
    except Exception:
        print(f"\033[31mWARNING: Error fixing {column_name} (replacing NaN with None) \033[0m")
    return dataFrame


def move_strings_from_column_to_metadata(data_frame: pandas.DataFrame, column_name: str) -> pandas.DataFrame | None:
    """
    Move strings from a column into the "Metadata" column and replace them with None.

    This function takes a DataFrame and a column name as input, and moves all strings in that column to the
    "Metadata" column. The strings are joined together with a newline character and added to the existing
    "Metadata" content. The original column is then replaced with None values.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame containing the column to be modified.
    column_name : str
        Name of the column in the DataFrame to be modified.

    Returns
    -------
    pandas.DataFrame
        Modified DataFrame with strings moved to "Metadata" and replaced with None in the original column.
    """
    concatenated_string = '\n'
    try:
        if data_frame is None:
            raise ValueError(f"dataFrame is None")
        if not isinstance(column_name, str):
            raise ValueError(f"column_name is not a string. Type is {type(column_name)}")
        if column_name not in data_frame.columns:
            raise ValueError(f"{column_name} is not in {data_frame.columns}")
        if "Metadata" not in data_frame.columns:
            raise ValueError(f"Metadata Column doesn't exsist")

        strings = data_frame[column_name].apply(lambda x: x if isinstance(x, str) else None)
        concatenated_string = concatenated_string.join(filter(None, strings))

        data_frame.loc[0, "Metadata"] = str(data_frame.loc[0, "Metadata"]) + '\n\n' + concatenated_string
        data_frame[column_name] = (data_frame[column_name].apply(lambda x: None if isinstance(x, str) else x).astype
                                   (object))
        data_frame[column_name] = data_frame[column_name].replace({np.nan: None})
    except Exception:
        print("\033[31mWARNING: Error adding Messages to Metadata \033[0m")
    return data_frame


def fix_time_format(data_frame: pandas.DataFrame, input_format: str = None) -> pandas.DataFrame | None:
    """
    Fix the format of the "Absolute Time[yyyy-mm-dd hh:mm:ss]" column.

    This function takes a DataFrame and an optional input format as input, and
    attempts to convert the "Absolute Time[yyyy-mm-dd hh:mm:ss]" column to a
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
        Modified DataFrame with the "Absolute Time[yyyy-mm-dd hh:mm:ss]" column
        converted to the correct format.
    """
    column_name = "Absolute Time[yyyy-mm-dd hh:mm:ss]"

    try:
        if data_frame is None:
            raise ValueError("data_frame is None")
        if not isinstance(input_format, str):
            raise ValueError(f"input_format is not a string. Type is {type(column_name)}")
        if column_name not in data_frame.columns:
            raise ValueError(f"{column_name} is not in {data_frame.columns}")
        if "Absolute Time[yyyy-mm-dd hh:mm:ss]" not in data_frame.columns:
            raise ValueError(f"Absolute Time[yyyy-mm-dd hh:mm:ss] Column doesn't exsist")
        try:
            data_frame[column_name] = pandas.to_datetime(data_frame[column_name], format=input_format, errors='coerce')
        except Exception:
            raise ValueError("Error changing to datetime")
        try:
            data_frame[column_name] = data_frame[column_name].dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            raise ValueError("Error changing to correct order in Timeformat")
    except Exception:
        print("\033[31mWARNING: Error fixing timeformat Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m")
    return data_frame


def absolute_time_timedate_typecast(data_frame: pandas.DataFrame) -> pandas.DataFrame:
    """
    Convert the "Absolute Time[yyyy-mm-dd hh:mm:ss]" column in the DataFrame to a datetime object.

    This function attempts to typecast the specified column in the DataFrame to a pandas datetime object.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame containing the column to be converted.

    Returns
    -------
    pandas.DataFrame
        The DataFrame with the "Absolute Time[yyyy-mm-dd hh:mm:ss]" column converted to datetime objects.
    """
    try:
        if data_frame is None:
            raise ValueError("data_frame is None")
        if "Absolute Time[yyyy-mm-dd hh:mm:ss]" not in data_frame.columns:
            raise ValueError(f"Absolute Time[yyyy-mm-dd hh:mm:ss] Column doesn't exsist")
        data_frame["Absolute Time[yyyy-mm-dd hh:mm:ss]"] = pandas.to_datetime(data_frame["Absolute Time[yyyy-mm-dd hh:mm:ss]"], errors='coerce')
    except Exception:
        print("\033[31mWARNING: Error typecasting Absolute Time[yyyy-mm-dd hh:mm:ss] \033[0m")
    return data_frame
