import logging

import numpy as np
import pandas as pd

from pydpeet.io.utils.formatter_utils import (
    _round_testtime,
    _to_numeric_if_possible,
    _typecast,
    _unix_time_to_datetime,
)

# Columns of the standardized format which must contain numeric data.
_NUMERIC_COLUMNS = [
    "Test_Time[s]",
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Step_Count",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
]


def _get_data_into_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a pandas DataFrame and applies three functions to it:

    1. `_unix_time_to_datetime`: converts the "Date_Time" column from Unix time
       (seconds since 1970-01-01T00:00:00 UTC) to pandas datetime objects.
    2. `round_testtime`: rounds the "Test_Time[s]" column to five decimal places.
    3. `_to_numeric_if_possible` / `_typecast`: casts the numeric columns to their
       correct datatypes. Columns without missing values are cast to more
       specific datatypes where applicable ("Step_Count" is cast to int).

    Returns the modified DataFrame.
    """
    df = _unix_time_to_datetime(df)
    df = _round_testtime(df)

    for col in _NUMERIC_COLUMNS:
        df = _to_numeric_if_possible(df, col)
    try:
        if df["Step_Count"].notna().all():
            df = _typecast(df, "Step_Count", np.dtype("int64"))
    except Exception:
        logging.warning("Error fixing Step_Count (casting to int)")

    return df
