import logging

import pandas as pd

from pydpeet.io.configs.config import STANDARD_COLUMNS


def mapping(data_frame: pd.DataFrame, column_map: dict, missing_columns: list) -> pd.DataFrame:
    """
    Renames and maps specific columns in the DataFrame to standardized names.
    If a standardized column doesn't exist in the DataFrame, it is added with default None values.
    Non-mapped columns will remain unchanged in the resulting DataFrame.

    Parameters:
    dataFrame (pandas.DataFrame): The input DataFrame to be processed.
    column_map (dict): A dictionary mapping existing column names to new standardized names.
    missing_columns (list): A list of column names to ensure their existence in the DataFrame.

    Returns:
    pandas.DataFrame: The updated DataFrame with standardized column names.

    Assumptions:
    column_map and missing_columns contain all standard columns
    (If you want to rename more or add more columns do it after the conversion)
    """
    if data_frame is None:
        raise ValueError("dataFrame is None")
    if column_map is None:
        raise ValueError("column_map is None")
    if missing_columns is None:
        raise ValueError("missing_columns is None")
    if type(data_frame) is not pd.DataFrame:
        raise ValueError("dataFrame is not a DataFrame")
    if type(column_map) is not dict:
        raise ValueError("column_map is not a dictionary")
    if type(missing_columns) is not list:
        raise ValueError("missing_columns is not a list")
    standard_columns_excluding_metadata = [col for col in STANDARD_COLUMNS if not col.startswith("Meta_Data")]
    if not all(col in list(column_map.values()) + missing_columns for col in standard_columns_excluding_metadata):
        raise ValueError("column_map and missing_columns do not contain all standard columns")
    if any(col not in STANDARD_COLUMNS for col in list(column_map.values()) + missing_columns):
        raise ValueError("column_map and missing_columns contain columns that are not standard columns")

    # Create a copy of the DataFrame to avoid modifying the original
    df = data_frame.copy()

    # Add missing columns with None values if they do not exist, and issue warnings
    for missing in missing_columns:
        if missing not in df.columns:
            logging.warning(f"Missing column: '{missing}'. Adding Collumn (with None values) named: '{missing}'.")
            df[missing] = None

    # Warn if a column that should be mapped is missing and add it with None values
    for original_col in column_map.keys():
        if original_col not in df.columns:
            logging.warning(f"Column to be mapped '{original_col}' does not exist in DataFrame. Adding it with None values.")
            df[original_col] = None

    # Rename the existing columns as per the column_map
    # Columns not in the column_map will remain unchanged
    df.rename(columns=column_map, inplace=True)

    return df
