import logging
from pathlib import Path

import pandas as pd


def to_dataframe(input_path: str) -> tuple[pd.DataFrame, str]:
    """
    Parses the input file from the Parstat Cycler into a pandas DataFrame.

    Parameters:
    input_path (str): Path to the input file.

    Returns:
    (pandas.DataFrame, str): A tuple containing the DataFrame with data and metadata as a string.
    """

    suffix = Path(input_path).suffix.lower()

    if suffix == ".txt":
        separator = "\t"
    elif suffix == ".csv":
        separator = ","
    else:
        raise ValueError("File type must be TXT or CSV.")

    metadata = []

    # Open the file and process lines
    with open(input_path, encoding="us-ascii") as file:
        # Read metadata until the header line is found
        line = file.readline()
        while line and (("Potential" not in line) or ("Zre" not in line) or ("|Z|" not in line)):
            metadata.append(line.strip())
            line = file.readline()

        if not line:
            raise ValueError("Header was not found or is not valid.")

        # Extract headers and remaining data
        headers = [h.strip() for h in line.split(separator)]
        data_lines = [[v.strip() for v in row.split(separator)] for row in file if row.strip()]

    # Join metadata into a single string
    metadata_str = "\n".join(metadata)

    # Create DataFrame
    df = pd.DataFrame(data_lines, columns=headers)

    if "Point" not in df.columns:
        df.insert(0, "Point", 1)
        logging.warning("Column 'Point' (maps to 'Step_Count') was missing. Set all values to 1.")

    return df, metadata_str
