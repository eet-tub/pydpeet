import pandas as pd

from pydpeet.io.utils.formatter_utils import absolute_time_timedate_typecast, apply_convert_to_float_if_possible, move_strings_from_column_to_metadata, nan_to_none_in_column, replace_empty_with_none_in_standard_columns, round_testtime, typecast


def get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format the given DataFrame into a standard format.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame to be formatted

    Returns
    -------
    pandas.DataFrame
        The formatted DataFrame
    """
    df = replace_empty_with_none_in_standard_columns(df)
    typecast(df, "Step_Count", int)
    df = apply_convert_to_float_if_possible(df, "Voltage[V]")
    df = apply_convert_to_float_if_possible(df, "Current[A]")
    df = round_testtime(df)
    df = absolute_time_timedate_typecast(df)
    typecast(df, "EIS_Z_Real[Ohm]", float)
    typecast(df, "EIS_Z_Imag[Ohm]", float)
    df = nan_to_none_in_column(df, "Current[A]")
    df = move_strings_from_column_to_metadata(df, "Voltage[V]")

    return df
