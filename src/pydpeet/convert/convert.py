from pathlib import Path

from pandas import DataFrame, Index

from pydpeet.citations import citeme
from pydpeet.convert.configs.config import Config, READER_CONFIGS, MAPPER_CONFIGS, STANDARD_COLUMNS, FORMATTER_CONFIGS
from pydpeet.convert.map import mapping
from pydpeet.convert.utils.ext_path import ExtPath
from pydpeet.convert.utils.load_custom_module import load_custom_module
from pydpeet.convert.utils.timing import measure_time

from typing import Union

ConfigLike = Union[Config, str]


@measure_time
def convert_file(config: ConfigLike, input_path: str, keep_all_additional_data: bool = False,
            custom_folder_path: str = None) -> DataFrame:
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
        raise ValueError("config must be provided")
    if ExtPath.is_not_valid(input_path):
        raise ValueError("input_path must be provided")
    if custom_folder_path is not None and ExtPath.is_not_valid(custom_folder_path):
        raise ValueError("custom_folder_path must be valid if provided")

    data_frame, meta_data = _convert_file_to_pandas_data_frame(config, input_path, custom_folder_path)
    data_frame = _column_mapping(data_frame, config, custom_folder_path)
    if not keep_all_additional_data:
        data_frame = _drop_additional_data(data_frame)
    data_frame = _add_metadata_to_dataframe(data_frame, meta_data)
    data_frame = _reorder_columns(data_frame)
    data_frame = _get_data_into_format(data_frame, config, custom_folder_path)

    return data_frame


def _convert_file_to_pandas_data_frame(config: Config, input_path: str, custom_folder: str = None
                                       ) -> tuple[DataFrame, str]:
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
    print("converting file to pandas DataFrame...")

    if Config.not_exists(config):
        raise ValueError(f"Unknown config: {config}")

    data_frame = None
    meta_data = ""
    if config == Config.Custom:
        if ExtPath.is_not_valid(custom_folder):
            raise ValueError(f"Custom folder path must be provided for {Config.Custom}!")

        custom_reader = load_custom_module(custom_folder, "Reader")
        if custom_reader.to_data_frame is None:
            raise ValueError("to_data_frame in custom reader is None.")

        data_frame, meta_data = custom_reader.to_data_frame(input_path)
    elif config in READER_CONFIGS:
        data_frame, meta_data = READER_CONFIGS[config](input_path)

    return data_frame, meta_data


def _column_mapping(data_frame: DataFrame, config: Config, custom_folder: str = None) -> DataFrame:
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
    print("mapping columns...")

    if data_frame is None:
        raise ValueError("Data frame is None.")
    if Config.not_exists(config):
        raise ValueError(f"Unknown config: {config}")

    if config in MAPPER_CONFIGS:
        column_map, missing_required_columns = MAPPER_CONFIGS[config]
        return mapping(data_frame, column_map, missing_required_columns)
    elif config == Config.Custom:
        if ExtPath.is_not_valid(custom_folder):
            raise ValueError(f"Custom folder path must be provided for {Config.Custom}!")

        custom_mapper = load_custom_module(custom_folder, "Mapper")

        if custom_mapper.COLUMN_MAP is None:
            raise ValueError("COLUMN_MAP in custom mapper is None.")
        if custom_mapper.MISSING_REQUIRED_COLUMNS is None:
            raise ValueError("MISSING_REQUIRED_COLUMNS in custom mapper is None.")

        return mapping(data_frame, custom_mapper.COLUMN_MAP, custom_mapper.MISSING_REQUIRED_COLUMNS)


def _drop_additional_data(data_frame: DataFrame) -> DataFrame:
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
    print("dropping additional data...")

    if data_frame is None:
        raise ValueError("Data frame is None.")

    return data_frame[[col for col in data_frame.columns if col in STANDARD_COLUMNS]]


def _add_metadata_to_dataframe(data_frame: DataFrame, meta_data: str) -> DataFrame:
    """
    Add the given meta data as a column in the DataFrame.

    The first row of the "Metadata" column is set to the given meta data. All
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
        The modified DataFrame with the added "Metadata" column.
    """
    print("adding metadata to Dataframe...")

    if data_frame is None:
        raise ValueError("Data frame is None.")

    data_frame["Metadata"] = None  # NO, this is faster then .loc
    data_frame.loc[0, "Metadata"] = str(meta_data)
    return data_frame


def _reorder_columns(data_frame: DataFrame) -> DataFrame:
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
    print("Getting columns in correct order...")

    if data_frame is None:
        raise ValueError("Data frame is None.")

    if data_frame.columns.size == 0:
        raise ValueError("Data frame is empty or has no columns.")

    print("Checking for duplicate extra columns...")
    duplicates_fixed = _rename_duplicate_extra_columns(data_frame.columns)
    if not data_frame.columns.equals(duplicates_fixed):
        data_frame.columns = duplicates_fixed

    print("Selecting and ordering standard columns...")
    ordered_standard_columns = [col for col in STANDARD_COLUMNS if col in data_frame.columns]

    print("Selecting extra columns...")
    extra_columns = [col for col in data_frame.columns if col not in STANDARD_COLUMNS]

    print("Combining standard and extra columns...")
    ordered_columns = ordered_standard_columns + extra_columns

    reordered = data_frame[ordered_columns]
    print("Reordered DataFrame columns!")

    return reordered


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
        print(
            "\033[31mWARNING: Duplicate non-standard-columns were detected and renamed (by appending numbers) to ensure unique column names.\033[0m"
        )
    return Index(result)


def _get_data_into_format(data_frame: DataFrame, config: Config, custom_folder: str = None) -> DataFrame:
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
    print("Starting to fix data format...")

    if data_frame is None:
        raise ValueError("Data frame is None.")
    if config is None:
        raise ValueError("Config is None.")
    if config not in FORMATTER_CONFIGS and config != Config.Custom:
        raise ValueError(f"Unknown config: {config}")
    if ExtPath.is_not_valid(custom_folder) and config == Config.Custom:
        raise ValueError(f"Valid custom folder path must be provided for {Config.Custom}")

    if config == Config.Custom:
        print("Loading custom formatter module...")
        try:
            custom_formatter = load_custom_module(custom_folder, "Formatter")
        except Exception as e:
            raise ValueError(f"Error loading custom formatter module: {e}")
        try:
            data_frame = custom_formatter.get_data_into_format(data_frame)
        except Exception as e:
            raise ValueError(f"Error applying custom formatter: {e}")
    else:
        print(f"Using formatter for config: {config}")
        try:
            FORMATTER_CONFIGS[config](data_frame)
        except Exception as e:
            raise ValueError(f"Error applying formatter: {e}")

    print("Data format fixed.")
    return data_frame
