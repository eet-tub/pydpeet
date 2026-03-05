import pandas as pd
from pydpeet.io.utils.formatter_utils import (
    absolute_time_timedate_typecast,
    apply_convert_to_float_if_possible,
    move_strings_from_column_to_metadata,
    nan_to_none_in_column,
    replace_empty_with_none_in_standard_columns,
    round_testtime,
    typecast
)


def get_data_into_format(data_frame: pd.DataFrame):
    data_frame = replace_empty_with_none_in_standard_columns(data_frame)
    typecast(data_frame, "Step_Count", int)
    data_frame = apply_convert_to_float_if_possible(data_frame, "Voltage[V]")
    data_frame = apply_convert_to_float_if_possible(data_frame, "Current[A]")
    data_frame = round_testtime(data_frame)
    data_frame = absolute_time_timedate_typecast(data_frame)
    typecast(data_frame, "EIS_Z_Real[Ohm]", float)
    typecast(data_frame, "EIS_Z_Imag[Ohm]", float)
    data_frame = nan_to_none_in_column(data_frame, "Current[A]")
    data_frame = move_strings_from_column_to_metadata(data_frame, "Voltage[V]")
    return data_frame
