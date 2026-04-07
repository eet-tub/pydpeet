from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

from pydpeet.io.configs.config import Config
from pydpeet.io.convert import (
    convert_file,
    convert_files_in_directory,
)
from pydpeet.utils.guardrails import _guardrail_boolean

ConfigLike = Config | str
PathLike = str | Path


def read(
    config: ConfigLike,
    input_path: object,
    keep_all_additional_data: bool = False,
    custom_folder_path: str = None,
) -> pd.DataFrame | list[pd.DataFrame]:
    # Validate boolean parameter using guardrail
    _guardrail_boolean(keep_all_additional_data, hard_fail_none=True, hard_fail_wrong_type=True)

    # TODO: Docstring
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
            if isinstance(input_path, str):
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
