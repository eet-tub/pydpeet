import shutil
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from pydpeet.io.configs.config import Config

_TEST_ROOT = Path(__file__).parent
RES_PATH = _TEST_ROOT / "res"
TEMP_PATH = _TEST_ROOT / "tmp"


def with_zip_file_for_path(zip_file: Path, test_func_for_path: Callable[[Path], Any]) -> list[Any]:
    extract_dir = zip_file.parent / "unzipped"
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        return test_func_for_path(extract_dir)
    finally:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)  # Clean up extracted files


def with_zip_files(zip_files_path: Path, test_func_for_each_file: Callable) -> None:
    for zip_file in zip_files_path.iterdir():
        if zip_file.suffix == ".zip":
            with_zip_file(zip_file, test_func_for_each_file)
        else:
            print(f"{zip_file.name} is not a zip file! Skipping.")


def with_zip_file(zip_file: Path, test_func_for_each_file: Callable[[str], Any]) -> list[Any]:
    extract_dir = zip_file.parent / "unzipped"
    try:
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        return [test_func_for_each_file(str(file)) for file in extract_dir.iterdir()]
    finally:
        if extract_dir.exists():
            shutil.rmtree(extract_dir)  # Clean up extracted files


def mock_config() -> Config:
    return MagicMock(spec=Config, return_value="Unknown config")
