import logging
import os

import pandas as pd

from pydpeet.io.configs.config import DataOutputFiletype


# TODO:
# Adjust to accept dataframes or lists of dataframes
# or write dedicated wrapper for list inputs
def write(
    data_input: pd.DataFrame,
    output_path: str,
    output_file_name: str,
    data_output_filetype: DataOutputFiletype = DataOutputFiletype.parquet,
) -> None:
    """
    Export the given DataFrame to the given output path.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        DataFrame to be exported.
    output_path : str
        Path to the directory where the file will be saved. Must exist.
    output_file_name : str
        Name of the file to be saved.
    data_output_filetype : DataOutputFiletype, optional
        The file type to use when exporting the DataFrame. Defaults to
        DataOutputFiletype.parquet.

    Raises
    ------
    ValueError
        If data_frame is None, or if output_path or output_file_name are None.
    TypeError
        If data_frame is not a pandas.DataFrame, or if data_output_filetype is not
        a DataOutputFiletype.
    """
    if data_input is None:
        raise ValueError("data_frame is None")
    if not isinstance(data_input, pd.DataFrame):
        raise TypeError(f"data_frame is not a pandas.DataFrame, but {type(data_input)}")
    if output_path is None:
        raise ValueError("output_path is None")
    if not isinstance(output_path, str):
        raise ValueError(f"output_path is not a string, but {type(output_path)}")
    if output_file_name is None:
        raise ValueError("output_file_name is None")
    if not isinstance(output_file_name, str):
        raise ValueError(f"output_file_name is not a string, but {type(output_file_name)}")
    if data_output_filetype is None:
        raise ValueError("data_output_filetype is None")
    if not isinstance(data_output_filetype, DataOutputFiletype):
        raise ValueError(f"data_output_filetype is not a DataOutputFiletype, but {type(data_output_filetype)}")

    abs_path = os.path.abspath(output_path)

    if not os.path.exists(abs_path):
        os.makedirs(abs_path)

    _do_export(data_input, os.path.join(abs_path, output_file_name), data_output_filetype)


def _do_export(
    df: pd.DataFrame,
    output_path: str,
    data_output_filetype: DataOutputFiletype,
) -> None:
    """
    Export a DataFrame to a file in the specified format.

    This function exports the given DataFrame to a file at the specified output
    path in the format specified by data_output_filetype. The function supports
    exporting to Parquet, CSV, and XLSX file formats.

    Parameters
    ----------
    data_frame : pandas.DataFrame
        The DataFrame to be exported.
    output_path : str
        The path (excluding file extension) where the file will be saved.
    data_output_filetype : DataOutputFiletype
        The format in which to export the DataFrame. Can be one of
        DataOutputFiletype.parquet, DataOutputFiletype.csv, or
        DataOutputFiletype.xlsx.
    """
    logging.info(f"exporting to {output_path}")
    match data_output_filetype:
        case DataOutputFiletype.parquet:
            full_output_path = f"{output_path}_Data.parquet"
            df.to_parquet(full_output_path, index=False, engine="pyarrow")
        case DataOutputFiletype.csv:
            full_output_path = f"{output_path}_Data.csv"
            df.to_csv(full_output_path, index=False)
        case DataOutputFiletype.xlsx:
            full_output_path = f"{output_path}_Data.xlsx"
            df.to_excel(full_output_path, index=False)
