import os
import pandas as pd
from pathlib import Path


def remove_duplicate_values(df: pd.DataFrame, column_name: str = "Absolute Time[yyyy-mm-dd hh:mm:ss]", keep: str = "first") -> pd.DataFrame:
    return df.drop_duplicates(subset=[column_name], keep=keep)


def read_to_dataframe(file_path: str) -> pd.DataFrame:
    """
    Reads a parquet file into a pandas DataFrame.

    Parameters:
    file_path (str): The path to the parquet file.

    Returns:
    pandas.DataFrame: The DataFrame containing the data from the parquet file.
    """
    return pd.read_parquet(file_path)


# def load_file(file_name: str) -> pd.DataFrame:

#     project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     res_dir = os.path.join(project_dir, 'res')
#     input_path = os.path.join(res_dir, file_name)

#     df = pd.read_parquet(input_path)

#     return df


def load_file(file_name: str, base_path: str | Path) -> pd.DataFrame:
    base_path = Path(base_path).parent
    print(f"Base path for loading file: {base_path}")
    input_path = base_path / "res" / file_name
    return pd.read_parquet(input_path)
