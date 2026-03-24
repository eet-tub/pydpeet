import logging
from typing import Any

import numpy as np
import pandas as pd


def _handle_failure(message: str, hard_fail: bool) -> None:
    """
    Handles failure behavior based on hard_fail flag.
    """
    if hard_fail:
        logging.error(message)
        raise ValueError(message)
    else:
        logging.warning(message)
    return


def _guardrail_dataframe(
    data_frame: Any,
    hard_fail_none: bool = True,
    hard_fail_wrong_type: bool = True,
    hard_fail_empty: bool = True,
    hard_fail_missing_required_columns: tuple[bool, list[str]] = (True, []),
    hard_fail_wrong_column_dtypes: tuple[bool, list[tuple[str, type]]] = (True, []),
    hard_fail_inf_values: tuple[bool, list[str]] = (True, []),
    hard_fail_nan_values: tuple[bool, list[str]] = (True, []),
    hard_fail_none_values: tuple[bool, list[str]] = (True, []),
) -> None:
    if data_frame is None:
        message = "Input Data_Frame is None"
        _handle_failure(message, hard_fail_none)

    if not isinstance(data_frame, pd.DataFrame):
        message = "Input Data_Frame is not a pandas DataFrame"
        _handle_failure(message, hard_fail_wrong_type)

    if data_frame.empty:
        message = "Input Data_Frame is empty"
        _handle_failure(message, hard_fail_empty)

    if len(hard_fail_missing_required_columns[1]) > 0:
        missing_columns = [col for col in hard_fail_missing_required_columns[1] if col not in data_frame.columns]
        if len(missing_columns) > 0:
            message = f"The following required columns are missing in the DataFrame: {missing_columns}"
            _handle_failure(message, hard_fail_missing_required_columns[0])

    if len(hard_fail_wrong_column_dtypes[1]) > 0:
        for col, expected_dtype in hard_fail_wrong_column_dtypes[1]:
            if col in data_frame.columns:
                actual_dtype = data_frame[col].dtype
                if expected_dtype == str and actual_dtype == object:  # noqa: E721
                    if all(isinstance(x, str) for x in data_frame[col].dropna()):
                        message = (
                            f"Column '{col}' has wrong data type."
                            f"Expected: {expected_dtype} but got {actual_dtype}."
                            f"Column '{col}' has rows that are None and is therefore treated as a object."
                        )
                        _handle_failure(message, False)
                        continue  # This is actually correct - strings stored as object when there are None rows; jump into next loop

                if expected_dtype == float and actual_dtype in (int, np.int64, np.int32, np.int16, np.int8):  # noqa: E721
                    message = (
                        f"Column '{col}' expected: {expected_dtype} but got {actual_dtype}."
                        f"Auto-converting column '{col}' from {actual_dtype} to {expected_dtype}"
                    )
                    data_frame[col] = data_frame[col].astype(expected_dtype)
                    _handle_failure(message, False)
                    continue  # Skip the final check since we already converted to the expected_dtype

                if actual_dtype != expected_dtype:
                    message = f"Column '{col}' has wrong data type. Expected: {expected_dtype} but got {actual_dtype}."
                    _handle_failure(message, hard_fail_wrong_column_dtypes[0])

    if len(hard_fail_inf_values[1]) > 0:
        for col in hard_fail_inf_values[1]:
            if (
                col in data_frame.columns
                and pd.api.types.is_numeric_dtype(data_frame[col])
                and np.isinf(data_frame[col]).any()
            ):
                message = f"Column '{col}' contains infinite values."
                _handle_failure(message, hard_fail_inf_values[0])

    if len(hard_fail_nan_values[1]) > 0:
        for col in hard_fail_nan_values[1]:
            if col in data_frame.columns and data_frame[col].isna().any():
                message = f"Column '{col}' contains NaN values."
                _handle_failure(message, hard_fail_nan_values[0])

    if len(hard_fail_none_values[1]) > 0:
        for col in hard_fail_none_values[1]:
            if col in data_frame.columns and data_frame[col].apply(lambda x: x is None).any():
                message = f"Column '{col}' contains None values."
                _handle_failure(message, hard_fail_none_values[0])

    return


def _guardrail_boolean(
    boolean: Any,
    hard_fail_none: bool = True,
    hard_fail_wrong_type: bool = True,
) -> None:
    if boolean is None:
        _handle_failure("Input boolean is None", hard_fail_none)

    if not isinstance(boolean, bool):
        _handle_failure("Input boolean is not a bool", hard_fail_wrong_type)

    return


def _guardrail_int(
    integer: Any,
    hard_fail_none: bool = True,
    hard_fail_wrong_type: bool = True,
    hard_fail_negative: bool = True,
    hard_fail_zero: bool = True,
) -> None:
    if integer is None:
        _handle_failure("Input integer is None", hard_fail_none)

    if not isinstance(integer, int):
        _handle_failure("Input integer is not a int", hard_fail_wrong_type)

    if integer < 0:
        _handle_failure(f"Input integer {integer} is negative", hard_fail_negative)

    if integer == 0:
        _handle_failure(f"Input integer {integer} is zero", hard_fail_zero)


def _guardrail_float(
    float_: Any,
    hard_fail_none: bool = True,
    hard_fail_wrong_type: bool = True,
    hard_fail_negative: bool = True,
    hard_fail_zero: bool = True,
) -> None:
    if float_ is None:
        _handle_failure("Input float_ is None", hard_fail_none)

    if not isinstance(float_, float):
        _handle_failure("Input float_ is not a float", hard_fail_wrong_type)

    if float_ < 0.0:
        _handle_failure(f"Input float_ {float_} is negative", hard_fail_negative)

    if float_ == 0.0:
        _handle_failure(f"Input float_ {float_} is zero", hard_fail_zero)
