import logging
import os
from datetime import datetime

from pydpeet.citations import citeme
from pydpeet.convert.configs.config import Config, DataOutputFiletype
from pydpeet.convert.convert import convert_file
from pydpeet.convert.export import export
from pydpeet.convert.utils.timing import measure_time
from pydpeet.convert.zyklisierer.neware.reader import find_main_files
import pandas as pd


@measure_time
@citeme.internship('PPB25', {
    'author': 'Daniel Schröder, Alexander Hinrichsen, Jan Kalisch, Cataldo De Simone',
    'title': 'Python Package zur Batteriemessdatenverarbeitung',
    'school': 'Technische Universität Berlin',
    'year': '2025'
})
def convert_files_in_directory(
        config: Config,
        input_path: str,
        output_path: str = None,
        keep_all_additional_data: bool = False,
        custom_folder_path: str = None,
        data_output_filetype: DataOutputFiletype = DataOutputFiletype.parquet
) -> None:
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
    data_output_filetype : DataOutputFiletype, optional
        The file type to use when exporting the data. Defaults to
        DataOutputFiletype.parquet.
    """
    if config is None:
        raise ValueError("config must be provided")
    if input_path is None:
        raise ValueError("input_path must be provided")
    # if output_path is None:
    #     raise ValueError("output_path must be provided")
    if not isinstance(keep_all_additional_data, bool):
        raise ValueError("keep_all_additional_data must be a boolean if provided")
    if custom_folder_path is not None and custom_folder_path is not str:
        raise ValueError("custom_folder_path must be a string if provided")

    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if type(config) is str:
        config_name = config
    else:
        config_name = config.name

    if config == Config.Neware:
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
                data_output_filetype,
                os.path.join(input_path, filename),
                filename,
                keep_all_additional_data,
                output_path
            )
            
            

def _process_file(
        config: Config,
        config_name: str,
        current_date: str,
        custom_folder_path: str,
        file_path: str,
        filename: str,
        keep_all_additional_data: bool
) -> pd.DataFrame:
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

    


def _process_file_and_export(
        config: Config,
        config_name: str,
        current_date: str,
        custom_folder_path: str,
        data_output_filetype: DataOutputFiletype,
        file_path: str,
        filename: str,
        keep_all_additional_data: bool,
        output_path: str
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
        export(df, output_path, output_filename, data_output_filetype)
        logging.info(f"Successfully processed and exported: {output_filename}")
    except Exception as e:
        logging.warning(f"Issue processing file {filename}: {e}")
