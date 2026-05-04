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
        raise ValueError("needs to be a .txt or .csv")

    metadata = []

    # Open the file and process lines
    with open(input_path, encoding="us-ascii") as file:
        # Read metadata until the header line is found
        line = file.readline()
        while line and "Segment" not in line:
            metadata.append(line.strip())
            line = file.readline()

        if not line:
            raise ValueError("Header 'Segment' not found in file.")

        # Extract headers and remaining data
        headers = [h.strip() for h in line.strip().split(separator)]
        data_lines = [row.strip().split(separator) for row in file if row.strip()]

    # Join metadata into a single string
    metadata_str = "\n".join(metadata)

    # Create DataFrame
    df = pd.DataFrame(data_lines, columns=headers)

    if "Point" not in df.columns:
        df.insert(0, "Point", range(1, len(df) + 1))

    return df, metadata_str
