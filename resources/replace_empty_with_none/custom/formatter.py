import pandas as pd
from ppb.utils.formatter_utils import apply_convert_to_float_if_possible
from ppb.utils.formatter_utils import nan_to_none_in_column
from ppb.utils.formatter_utils import replace_empty_with_none_in_standard_columns
from ppb.utils.formatter_utils import move_strings_from_column_to_metadata
from ppb.utils.formatter_utils import typecast
from ppb.utils.formatter_utils import round_testtime
from ppb.utils.formatter_utils import absolute_time_timedate_typecast


def get_data_into_format(data_frame: pd.DataFrame):
    data_frame = replace_empty_with_none_in_standard_columns(data_frame)
    typecast(data_frame, "StepID", int)
    data_frame = apply_convert_to_float_if_possible(data_frame, "Voltage[V]")
    data_frame = apply_convert_to_float_if_possible(data_frame, "Current[A]")
    data_frame = round_testtime(data_frame)
    data_frame = absolute_time_timedate_typecast(data_frame)
    typecast(data_frame, "Zre[Ohm]", float)
    typecast(data_frame, "Zim[Ohm]", float)
    data_frame = nan_to_none_in_column(data_frame, "Current[A]")
    data_frame = move_strings_from_column_to_metadata(data_frame, "Voltage[V]")
    return data_frame








