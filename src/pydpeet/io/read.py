from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, TypeAlias  # Add this import

import pandas as pd

from pydpeet.io.configs.config import Config
from pydpeet.io.convert import (
    convert_file,
    convert_files_in_directory,
)
from pydpeet.utils.guardrails import _guardrail_boolean

ConfigLike: TypeAlias = Config | str
PathLike: TypeAlias = str | Path


def read(
    config: ConfigLike,
    input_path: object,
    keep_all_additional_data: bool = False,
    custom_folder_path: Optional[str] = None,
) -> pd.DataFrame | list[pd.DataFrame]:
    """
    Read and convert battery test data into the unified PyDPEET format.

    This is the main high-level import function of PyDPEET. The function
    automatically detects whether the provided input path points to a file,
    a directory, or a list of files/directories and converts the contained
    battery test data into the unified PyDPEET dataframe format.

    Depending on the provided input, the function either returns a single
    dataframe or a list of dataframes.

    The conversion itself is performed using the selected device configuration.

    Parameters
    ----------
    config : ConfigLike
        Device configuration used for parsing and mapping the raw battery
        test data into the unified PyDPEET format.

        This can either be:

        - a predefined PyDPEET configuration
        - a custom configuration object
        - a configuration dictionary

    input_path : str | list[str]
        Path to the input data.

        Supported inputs are:

        - path to a single raw data file
        - path to a directory containing raw data files
        - list of file and/or directory paths

    keep_all_additional_data : bool, default=False
        If ``True``, all additional columns that are not part of the unified
        PyDPEET format are preserved in the returned dataframe.

        If ``False``, only standardized PyDPEET columns are kept.

    custom_folder_path : str | None, default=None
        Optional custom folder path used by specific device configurations
        that require additional external metadata or lookup files.

    Returns
    -------
    pandas.DataFrame | list[pandas.DataFrame]
        Converted dataframe(s) in the unified PyDPEET format.

        - If a single file or directory is provided, a single dataframe is returned.
        - If a list of paths is provided, a list of dataframes is returned.

    Raises
    ------
    ValueError
        Raised if:

        - the provided input path does not exist
        - an input path has an invalid type
        - a list contains unsupported entries

    Notes
    -----
    The returned dataframe follows the standardized PyDPEET format
    contains following columns, when available in the raw data and depending on the selected device configuration:

    - ``Date_Time``
    - ``Test_Time[s]``
    - ``Voltage[V]``
    - ``Current[A]``
    - ``Step_Count``
    - ``Temperature[°C]``
    - ``EIS_f[Hz]``
    - ``EIS_Z_Real[Ohm]``
    - ``EIS_Z_Imag[Ohm]``

    depending on the available raw data and the selected device configuration.

    Examples
    --------
    More Usage Examples can be found in following tutorial notebooks:
        :doc:`Tutorial 01: Convert and Import <../../examples/notebooks/Tutorial_01_Convert_Import>`

    Read a single file:

    >>> import pydpeet as eet
    >>> df = eet.read(
    ...     config="neware_8_0_0_516",
    ...     input_path="measurement.csv",
    ... )

    Read all files in a directory:

    >>> df = eet.read(
    ...     config="neware_8_0_0_516",
    ...     input_path="data/",
    ... )

    Read multiple files and directories:

    >>> dfs = eet.read(
    ...     config="neware_8_0_0_516",
    ...     input_path=[
    ...         "measurement_01.csv",
    ...         "measurement_02.csv",
    ...         "folder_with_measurements/",
    ...     ],
    ... )

    Keep additional raw columns:

    >>> df = eet.read(
    ...     config="neware_8_0_0_516",
    ...     input_path="measurement.csv",
    ...     keep_all_additional_data=True,
    ... )



    See Also
    --------
    convert : Lower-level conversion interface.
    write : Export unified PyDPEET dataframes.
    merge_into_series : Merge multiple datasets into a continuous series.
    """
    # References
    # ----------
    # """

    # Validate boolean parameter using guardrail
    _guardrail_boolean(keep_all_additional_data, hard_fail_none=True, hard_fail_wrong_type=True)

    if isinstance(input_path, str):
        if os.path.isfile(input_path):
            return convert_file(config, input_path, None, keep_all_additional_data, custom_folder_path)
        elif os.path.isdir(input_path):
            return convert_files_in_directory(config, input_path, None, keep_all_additional_data, custom_folder_path)
        else:
            raise ValueError("Input path is invalid!")
    elif isinstance(input_path, list):
        dfs = []
        for input_item in input_path:
            if isinstance(input_item, str):
                if os.path.isfile(input_item):
                    dfs.append(convert_file(config, input_item, None, keep_all_additional_data, custom_folder_path))
                elif os.path.isdir(input_item):
                    dfs.append(
                        convert_files_in_directory(
                            config, input_item, None, keep_all_additional_data, custom_folder_path
                        )
                    )
                else:
                    raise ValueError("Input path item is invalid!")
            else:
                raise ValueError("Input path item is of invalid type!")
        return dfs
    else:
        raise ValueError("Input path is of invalid type!")
