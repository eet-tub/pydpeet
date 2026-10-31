from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional, TypeAlias

import pandas as pd

from pydpeet.io.configs.config import _EXTENSION_GROUPS, ReadConfig
from pydpeet.io.convert import (
    _convert_file,
    _convert_files_in_directory,
)
from pydpeet.utils.guardrails import (
    _FILETYPE_BLACKLIST,
    _guardrail_blacklisted_filetype,
    _guardrail_boolean,
)

ConfigLike: TypeAlias = ReadConfig | str
PathLike: TypeAlias = str | Path


def convert(
    config: Optional[ConfigLike] = None,
    input_path: object = None,
    output_path: Optional[str] = None,
    keep_all_additional_data: bool = False,
    custom_folder_path: Optional[str] = None,
) -> pd.DataFrame | list[pd.DataFrame] | None:
    """
    Convert battery test data into the unified PyDPEET format.

    This is the main high-level import function of PyDPEET. The function
    automatically detects whether the provided input path points to a file,
    a directory, or a list of files/directories and converts the contained
    battery test data into the unified PyDPEET dataframe format.

    Depending on the provided input, the function either returns a single
    dataframe or a list of dataframes.

    The conversion itself is performed using the selected device configuration.

    Parameters
    ----------
    config : ConfigLike, optional
        Device configuration used for parsing and mapping the raw battery
        test data into the unified PyDPEET format.

        This can either be:

        - a predefined PyDPEET configuration
        - a custom configuration object
        - a configuration dictionary

        If ``None`` (default), the filetype is auto-detected from the file
        extension and each matching configuration is tried until one succeeds.
    input_path : str | list[str]
        Path to the input data.

        Supported inputs are:

        - path to a single raw data file
        - path to a directory containing raw data files
        - list of file and/or directory paths

    output_path : str, optional
        If provided, the converted data is written to this directory.
        When ``None`` (default), the converted DataFrames are returned.

    keep_all_additional_data : bool, default=False
        If ``True``, all additional columns that are not part of the unified
        PyDPEET format are preserved in the returned dataframe.

        If ``False``, only standardized PyDPEET columns are kept.

    custom_folder_path : str | None, default=None
        Optional custom folder path used by specific device configurations
        that require additional external metadata or lookup files.

    Returns
    -------
    pandas.DataFrame | list[pandas.DataFrame] | None
        Converted dataframe(s) in the unified PyDPEET format.

        - If a single file is provided, a single dataframe is returned.
        - If a directory or list of paths is provided, a list of dataframes is returned.
        - If ``output_path`` is provided, ``None`` is returned after writing.

    Raises
    ------
    ValueError
        Raised if:

        - the provided input path does not exist
        - an input path has an invalid type
        - a list contains unsupported entries
        - an explicitly provided file has a blacklisted filetype

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

    # Reject blacklisted filetypes for explicitly provided files.
    # Directories are handled later so only the blacklisted files inside them get skipped.
    if isinstance(input_path, str):
        if os.path.isfile(input_path):
            _guardrail_blacklisted_filetype(input_path)
    elif isinstance(input_path, list):
        for item in input_path:
            if isinstance(item, str) and os.path.isfile(item):
                _guardrail_blacklisted_filetype(item)

    _guardrail_boolean(keep_all_additional_data, hard_fail_none=True, hard_fail_wrong_type=True)

    if isinstance(config, str):
        config = ReadConfig._from_string(config)

    # ---- explicit config: use existing helpers (preserves per-config logic like _find_main_files) ----
    if config is not None:
        if isinstance(input_path, str):
            if os.path.isfile(input_path):
                return _convert_file(config, input_path, output_path, keep_all_additional_data, custom_folder_path)
            if os.path.isdir(input_path):
                return _convert_files_in_directory(
                    config, input_path, output_path, keep_all_additional_data, custom_folder_path
                )
            raise ValueError("Input path is invalid!")
        if isinstance(input_path, list):
            results: list[pd.DataFrame | list[pd.DataFrame] | None] = []
            for item in input_path:
                if not isinstance(item, str):
                    raise ValueError("Input path item is of invalid type!")
                if os.path.isfile(item):
                    results.append(
                        _convert_file(config, item, output_path, keep_all_additional_data, custom_folder_path)
                    )
                elif os.path.isdir(item):
                    results.append(
                        _convert_files_in_directory(
                            config, item, output_path, keep_all_additional_data, custom_folder_path
                        )
                    )
                else:
                    raise ValueError("Input path item is invalid!")
            return results
        raise ValueError("Input path is of invalid type!")

    # ---- auto-detection: flatten everything to files, try configs per file ----
    logging.warning("No config specified — using automatic config detection")
    if not isinstance(input_path, str | list):
        raise ValueError("Input path is of invalid type!")

    all_files: list[str] = []
    input_was_str = isinstance(input_path, str)

    for raw in [input_path] if input_was_str else input_path:
        if not isinstance(raw, str):
            raise ValueError("Input path item is of invalid type!")
        if os.path.isfile(raw):
            all_files.append(raw)
        elif os.path.isdir(raw):
            dir_files = [os.path.join(raw, f) for f in os.listdir(raw) if os.path.isfile(os.path.join(raw, f))]
            if not dir_files:
                raise ValueError(f"Directory '{raw}' is empty or contains no files")
            all_files.extend(dir_files)
        else:
            raise ValueError("Input path is invalid!")

    results = []
    for fp in all_files:
        suffix = Path(fp).suffix.lower()
        if suffix in _FILETYPE_BLACKLIST:
            _guardrail_blacklisted_filetype(fp, hard_fail=False)
            continue
        group = _EXTENSION_GROUPS.get(suffix)
        if group is None:
            logging.warning("Could not detect filetype for '%s', skipping", fp)
            continue
        for cfg in group:
            try:
                logging.info("trying config %s for file %s", cfg, fp)
                result = _convert_file(cfg, fp, output_path, keep_all_additional_data, custom_folder_path)
                logging.info("config %s succeeded for file %s", cfg, fp)
                results.append(result)
                break
            except Exception as e:
                logging.warning("config %s failed for %s: %s", cfg, fp, e)

    if not results:
        logging.error("No config could successfully process any file")
        raise ValueError("No files could be processed!")

    return results[0] if isinstance(input_path, str) and os.path.isfile(input_path) else results


def read(
    config: Optional[ConfigLike] = None,
    input_path: object = None,
    keep_all_additional_data: bool = False,
    custom_folder_path: Optional[str] = None,
) -> pd.DataFrame | list[pd.DataFrame]:
    """
    Read and convert battery test data into the unified PyDPEET format.

    Convenience wrapper around :func:`convert` that always returns DataFrames
    (no ``output_path`` for saving files).

    See :func:`convert` for full documentation.
    """
    return convert(config, input_path, None, keep_all_additional_data, custom_folder_path)  # type: ignore[return-value]
