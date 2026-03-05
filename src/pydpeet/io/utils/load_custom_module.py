import os
from importlib.util import (
    module_from_spec,
    spec_from_file_location
)
from types import ModuleType


def load_custom_module(
        folder_path: str,
        module_name: str
) -> ModuleType:
    """
    Loads a custom Python module from a specified folder.

    Parameters:
    folder_path (str): The path to the folder containing the module file.
    module_name (str): The name of the module to load (without the .py extension).

    Returns:
    module: The loaded Python module object.

    Raises:
    FileNotFoundError: If the module file does not exist in the specified folder.
    """
    module_path = os.path.join(folder_path, f"{module_name}.py")
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Module {module_name}.py not found in the specified folder: {folder_path}")
    spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module
