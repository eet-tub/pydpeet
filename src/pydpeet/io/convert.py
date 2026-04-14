from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from pandas import Index

from pydpeet.io.configs.config import (
    FORMATTER_CONFIGS,
    MAPPER_CONFIGS,
    READER_CONFIGS,
    STANDARD_COLUMNS,
    Config,
    DataOutputFiletype,
)
from pydpeet.io.device.neware_8_0_0_516.reader import find_main_files
from pydpeet.io.map import mapping
from pydpeet.io.utils.ext_path import ExtPath
from pydpeet.io.utils.load_custom_module import load_custom_module
from pydpeet.io.utils.timing import measure_time
from pydpeet.io.write import write
from pydpeet.utils.guardrails import _guardrail_boolean

ConfigLike = Config | str
PathLike = str | Path


def convert(
    config: ConfigLike,
    input_path: object,
    output_path: str = None,
    keep_all_additional_data: bool = False,
    custom_folder_path: str = None,
) -> pd.DataFrame | list[pd.DataFrame] | None:
    # Boolean guardrails
    _guardrail_boolean(keep_all_additional_data, hard_fail_none=True, hard_fail_wrong_type=True)

    if isinstance(input_path, str):
        if os.path.isfile(input_path):
            return convert_file(config, input_path, output_path, keep_all_additional_data, custom_folder_path)
        elif os.path.isdir(input_path):
            return convert_files_in_directory(
                config, input_path, output_path, keep_all_additional_data, custom_folder_path
            )
        else:
            raise ValueError("Input path is invalid!")
    elif isinstance(input_path, list):
        dfs = []
        for input_item in input_path:
            if isinstance(input_item, str):
                if os.path.isfile(input_item):
                    dfs.append(
                        convert_file(config, input_item, output_path, keep_all_additional_data, custom_folder_path)
                    )
                elif os.path.isdir(input_item):
                    dfs.append(
                        convert_files_in_directory(
                            config, input_item, output_path, keep_all_additional_data, custom_folder_path
                        )
                    )
                else:
                    raise ValueError("Input path item is invalid!")
            else:
                raise ValueError("Input path item is of invalid type!")
        return dfs
    else:
        raise ValueError("Input path is of invalid type!")


# TODO: Add output path functionality
@measure_time
def convert_file(
    config: ConfigLike,
    input_path: str,
    output_path: str = None,
    keep_all_additional_data: bool = False,
    custom_folder_path: str = None,
) -> pd.DataFrame:
    """
    Standardize a measurement file according to the given configuration and returns the standardized DataFrame.

    Parameters
    ----------
    config : Config
        The configuration to use for standardizing the file.
    input_path : str
        The path to the file to standardize.
    keep_all_additional_data : bool, optional
        Whether to keep all additional data in the output DataFrame. If False, any
        columns not specified in the configuration will be dropped. Defaults to
        False.
    custom_folder_path : str, optional
        The path to the directory containing the custom reader, mapper, and
        formatter reference for the given configuration.

    Returns
    -------
    DataFrame
        The standardized DataFrame.
    """
    if isinstance(config, str):
        config = Config.from_string(config)
    if Config.not_exists(config):
        raise ValueError("Config must be provided!")
    if ExtPath.is_not_valid(input_path):
        raise ValueError("Input_path must be provided!")
    if custom_folder_path is not None and ExtPath.is_not_valid(custom_folder_path):
        raise ValueError("Custom_folder_path must be valid if provided!")

    df, meta_data = _convert_file_to_pandas_data_frame(config, input_path, custom_folder_path)
    df = _column_mapping(df, config, custom_folder_path)
    if not keep_all_additional_data:
        df = _drop_additional_data(df)
    df = _add_metadata_to_dataframe(df, meta_data)
    df = _reorder_columns(df)
    df = _get_data_into_format(df, config, custom_folder_path)

    return df


# TODO: Implement better way of handling case where output_path is None?
@measure_time
def convert_files_in_directory(
    config: Config,
    input_path: str,
    output_path: str = None,
    keep_all_additional_data: bool = False,
    custom_folder_path: str = None,
) -> list[pd.DataFrame] | None:
    """
    Standardize a directory of files according to the given configuration and outputs them to an output_path.

    Parameters
    ----------
    config : Config
        The configuration to use for standardizing the directory.
    input_path : str
        The path to the directory to standardize.
    output_path : str
        The path to the directory where the standardized files will be written.
    keep_all_additional_data : bool, optional
        Whether to keep all additional data in the output files. If False, any
        columns not specified in the configuration will be dropped. Defaults to
        False.
    custom_folder_path : str, optional
        The path to the directory containing the custom reader, mapper, and
        formatter reference for the given configuration.
    """
    if config is None:
        raise ValueError("Config must be provided!")
    if input_path is None:
        raise ValueError("Input_path must be provided!")
    # if output_path is None:
    #     raise ValueError("output_path must be provided")
    if not isinstance(keep_all_additional_data, bool):
        raise ValueError("Keep_all_additional_data must be a boolean if provided!")
    if custom_folder_path is not None and custom_folder_path is not str:
        raise ValueError("Custom_folder_path must be a string if provided!")

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if type(config) is str:
        config_name = config
    else:
        config_name = config.name

    if config == Config.Neware_8_0_0_516:
        files = find_main_files(input_path)
    else:
        files = os.listdir(input_path)

    if output_path is None:
        dfs = []
        for filename in files:
            df = _process_file(
                config,
                config_name,
                current_date,
                custom_folder_path,
                os.path.join(input_path, filename),
                filename,
                keep_all_additional_data,
            )
            dfs.append(df)
        return dfs
    else:
        os.makedirs(output_path, exist_ok=True)
        for filename in files:
            _process_file_and_export(
                config,
                config_name,
                current_date,
                custom_folder_path,
                DataOutputFiletype.parquet,
                os.path.join(input_path, filename),
                filename,
                keep_all_additional_data,
                output_path,
            )
        return None


def _process_file(
    config: Config,
    config_name: str,
    current_date: str,
    custom_folder_path: str,
    file_path: str,
    filename: str,
    keep_all_additional_data: bool,
) -> pd.DataFrame | None:
    """
    Process a single file and save the standardized DataFrame to the given output_path.

    Parameters
    ----------
    config : Config
        The configuration to use for standardizing the file.
    config_name : str
        The name of the configuration.
    current_date : str
        The current date in the format %Y-%m-%d_%H-%M-%S.
    custom_folder_path : str
        The path to the directory containing the custom reader, mapper, and
        formatter reference for the given configuration.
    data_output_filetype : DataOutputFiletype
        The file type to use when exporting the data.
    file_path : str
        The path to the file to standardize.
    filename : str
        The name of the file to standardize.
    keep_all_additional_data : bool
        Whether to keep all additional data in the output DataFrame.
    output_path : str
        The path to the directory where the standardized file will be written.
    """
    logging.info(f"Processing file: {filename}")
    try:
        df = convert_file(config, file_path, keep_all_additional_data, custom_folder_path)
        output_filename = f"{os.path.splitext(filename)[0]}_{config_name}_{current_date}"
        logging.info(f"Successfully processed: {output_filename}")
        return df
    except Exception as e:
        logging.warning(f"Issue processing file {filename}: {e}")
        return None


def _process_file_and_export(
    config: Config,
    config_name: str,
    current_date: str,
    custom_folder_path: str,
    data_output_filetype: DataOutputFiletype,
    file_path: str,
    filename: str,
    keep_all_additional_data: bool,
    output_path: str,
) -> None:
    """
    Process a single file and save the standardized DataFrame to the given output_path.

    Parameters
    ----------
    config : Config
        The configuration to use for standardizing the file.
    config_name : str
        The name of the configuration.
    current_date : str
        The current date in the format %Y-%m-%d_%H-%M-%S.
    custom_folder_path : str
        The path to the directory containing the custom reader, mapper, and
        formatter reference for the given configuration.
    data_output_filetype : DataOutputFiletype
        The file type to use when exporting the data.
    file_path : str
        The path to the file to standardize.
    filename : str
        The name of the file to standardize.
    keep_all_additional_data : bool
        Whether to keep all additional data in the output DataFrame.
    output_path : str
        The path to the directory where the standardized file will be written.
    """
    logging.info(f"Processing file: {filename}")
    try:
        df = convert_file(config, file_path, keep_all_additional_data, custom_folder_path)
        output_filename = f"{os.path.splitext(filename)[0]}_{config_name}_{current_date}"
        write(df, output_path, output_filename, data_output_filetype)
        logging.info(f"Successfully processed and exported: {output_filename}")
    except Exception as e:
        logging.warning(f"Issue processing file {filename}: {e}")


def _convert_file_to_pandas_data_frame(
    config: Config,
    input_path: str,
    custom_folder: str = None,
) -> tuple[pd.DataFrame, str]:
    """
    Convert a file to a pandas DataFrame using the given configuration.

    Parameters
    ----------
    config : Config
        The configuration to use for converting the file.
    input_path : str
        The path to the file to convert.
    custom_folder : str, optional
        The path to the directory containing the custom reader, mapper, and
        formatter reference for the given configuration.

    Returns
    -------
    tuple[DataFrame, str]
        A tuple containing the converted DataFrame and the meta data.
    """
    logging.info("converting file to pandas DataFrame...")

    if Config.not_exists(config):
        raise ValueError(f"Unknown config: {config}")

    df = None
    meta_data = ""
    if config == Config.Custom:
        if ExtPath.is_not_valid(custom_folder):
            raise ValueError(f"Custom folder path must be provided for {Config.Custom}!")

        custom_reader = load_custom_module(custom_folder, "Reader")
        if custom_reader.to_data_frame is None:
            raise ValueError("to_data_frame in custom reader is None.")

        df, meta_data = custom_reader.to_data_frame(input_path)
    elif config in READER_CONFIGS:
        df, meta_data = READER_CONFIGS[config](input_path)

    return df, meta_data


def _column_mapping(
    df: pd.DataFrame,
    config: Config,
    custom_folder: str = None,
) -> pd.DataFrame:
    """
    Map the columns of a pandas DataFrame according to the given configuration.

    Parameters
    ----------
    data_frame : DataFrame
        The DataFrame to map the columns of.
    config : Config
        The configuration to use for mapping the columns.
    custom_folder : str, optional
        The path to the directory containing the custom mapper module for the given configuration.

    Returns
    -------
    DataFrame
        The DataFrame with the mapped columns.
    """
    logging.info("mapping columns...")

    if df is None:
        raise ValueError("Data frame is None.")
    if Config.not_exists(config):
        raise ValueError(f"Unknown config: {config}")

    if config in MAPPER_CONFIGS:
        column_map, missing_required_columns = MAPPER_CONFIGS[config]
        return mapping(df, column_map, missing_required_columns)
    elif config == Config.Custom:
        if ExtPath.is_not_valid(custom_folder):
            raise ValueError(f"Custom folder path must be provided for {Config.Custom}!")

        custom_mapper = load_custom_module(custom_folder, "Mapper")

        if custom_mapper.COLUMN_MAP is None:
            raise ValueError("COLUMN_MAP in custom mapper is None.")
        if custom_mapper.MISSING_REQUIRED_COLUMNS is None:
            raise ValueError("MISSING_REQUIRED_COLUMNS in custom mapper is None.")

        return mapping(df, custom_mapper.COLUMN_MAP, custom_mapper.MISSING_REQUIRED_COLUMNS)


def _drop_additional_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop columns that are not in STANDARD_COLUMNS from a DataFrame.

    Parameters
    ----------
    data_frame : DataFrame
        The DataFrame to drop columns from.

    Returns
    -------
    DataFrame
        The DataFrame with columns dropped.
    """
    logging.info("dropping additional data...")

    if df is None:
        raise ValueError("Data frame is None.")

    return df[[col for col in df.columns if col in STANDARD_COLUMNS]]


def _add_metadata_to_dataframe(
    df: pd.DataFrame,
    meta_data: str,
) -> pd.DataFrame:
    """
    Add the given meta data as a column in the DataFrame.

    The first row of the "Meta_Data" column is set to the given meta data. All
    other rows are set to None.

    Parameters
    ----------
    data_frame : DataFrame
        The DataFrame to add the meta data to.
    meta_data : str
        The meta data to add as a column.

    Returns
    -------
    DataFrame
        The modified DataFrame with the added "Meta_Data" column.
    """
    logging.info("adding metadata to Dataframe...")

    if df is None:
        raise ValueError("Data frame is None.")

    df["Meta_Data"] = None  # NO, this is faster then .loc
    df.loc[0, "Meta_Data"] = str(meta_data)
    return df


def _reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder the columns of a DataFrame to ensure standard columns are prioritized.

    This function reorders the columns of the given DataFrame by first checking
    and renaming any duplicate extra columns. It then selects the standard columns
    in their defined order, followed by any extra columns in their original order.
    The reordered DataFrame is then returned.

    Parameters
    ----------
    data_frame : DataFrame
        The DataFrame whose columns need to be reordered.

    Returns
    -------
    DataFrame
        The DataFrame with columns reordered to have standard columns first, followed
        by extra columns.

    Raises
    ------
    ValueError
        If the data_frame is None or empty.
    """
    logging.info("Getting columns in correct order...")

    if df is None:
        raise ValueError("Data frame is None.")

    if df.columns.size == 0:
        raise ValueError("Data frame is empty or has no columns.")

    logging.info("Checking for duplicate extra columns...")
    duplicates_fixed = _rename_duplicate_extra_columns(df.columns)
    if not df.columns.equals(duplicates_fixed):
        df.columns = duplicates_fixed

    logging.info("Selecting and ordering standard columns...")
    ordered_standard_columns = [col for col in STANDARD_COLUMNS if col in df.columns]

    logging.info("Selecting extra columns...")
    extra_columns = [col for col in df.columns if col not in STANDARD_COLUMNS]

    logging.info("Combining standard and extra columns...")
    ordered_columns = ordered_standard_columns + extra_columns

    df_reordered = df[ordered_columns]
    logging.info("Reordered DataFrame columns!")

    return df_reordered


def _rename_duplicate_extra_columns(columns: Index) -> Index:
    """
    Rename columns that are not in STANDARD_COLUMNS to ensure all columns have unique names.

    Parameters
    ----------
    columns : Index
        The Index of column names to modify.

    Returns
    -------
    Index
        The modified Index with any duplicate non-standard columns renamed.

    Notes
    -----
    Duplicates are renamed by appending "_<count>" where <count> is the number of
    times that column name has appeared before.
    """
    result = columns.to_list()
    duplicate_counts = {}

    for idx, col_name in enumerate(result):
        if col_name not in STANDARD_COLUMNS:
            count = duplicate_counts.setdefault(col_name, 0)
            if count > 0:
                result[idx] = f"{col_name}_{count}"
            duplicate_counts[col_name] += 1

    if any(count > 0 for count in duplicate_counts.values()):
        logging.warning(
            "Duplicate non-standard-columns were detected and renamed (by appending numbers) to ensure unique column names."
        )

    return Index(result)


def _get_data_into_format(
    df: pd.DataFrame,
    config: Config,
    custom_folder: str = None,
) -> pd.DataFrame:
    """
    Apply the appropriate data formatting function to a DataFrame based on the given configuration.

    This function modifies the format of the data in the DataFrame according to the
    specified configuration. If the configuration is set to custom, it loads a custom
    formatter module from the provided directory and applies it. Otherwise, it uses
    a predefined formatter function based on the configuration.

    Parameters
    ----------
    data_frame : DataFrame
        The DataFrame whose data needs to be formatted.
    config : Config
        The configuration determining which formatter to use.
    custom_folder : str, optional
        The path to the directory containing the custom formatter module if the
        configuration is set to custom.

    Returns
    -------
    DataFrame
        The DataFrame with its data formatted according to the specified configuration.

    Raises
    ------
    ValueError
        If the data_frame is None, config is None, or if the config is unknown.
        If the custom_folder path is invalid for a custom config.
        If there is an error loading or applying the custom formatter module.
        If there is an error applying the predefined formatter.
    """
    logging.info("Starting to fix data format...")

    if df is None:
        raise ValueError("Data frame is None.")
    if config is None:
        raise ValueError("Config is None.")
    if config not in FORMATTER_CONFIGS and config != Config.Custom:
        raise ValueError(f"Unknown config: {config}")
    if ExtPath.is_not_valid(custom_folder) and config == Config.Custom:
        raise ValueError(f"Valid custom folder path must be provided for {Config.Custom}")

    if config == Config.Custom:
        logging.info("Loading custom formatter module...")
        try:
            custom_formatter = load_custom_module(custom_folder, "Formatter")
        except Exception as e:
            raise ValueError(f"Error loading custom formatter module: {e}") from e
        try:
            df = custom_formatter.get_data_into_format(df)
        except Exception as e:
            raise ValueError(f"Error applying custom formatter: {e}") from e
    else:
        logging.info(f"Using formatter for config: {config}")
        try:
            FORMATTER_CONFIGS[config](df)
        except Exception as e:
            raise ValueError(f"Error applying formatter: {e}") from e

    logging.info("Data format fixed.")

    return df
