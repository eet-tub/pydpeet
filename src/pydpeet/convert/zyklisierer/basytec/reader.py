import logging

import pandas as pd
from io import StringIO


def to_DataFrame(input_path: str) -> (pd.DataFrame, str):
    """
    Parses the input file from the basytec cycler into a pandas DataFrame.
    It first converts the data portion to CSV format in memory.

    Parameters:
        input_path (str): Path to the input file.

    Returns:
        (pd.DataFrame, str): A tuple containing the DataFrame with the data and metadata as a string.
    """
    with open(input_path, 'r', encoding='iso-8859-1') as file:
        lines = file.readlines()

    # Collect all metadata lines (those starting with '~')
    metadata_lines = []
    data_start_idx = 0
    for idx, line in enumerate(lines):
        if line.startswith('~'):
            metadata_lines.append(line.strip())
        else:
            data_start_idx = idx
            break

    if not metadata_lines:
        logging.warning("The file does not contain expected metadata lines starting with '~'.")

    # The last metadata line is used as the header; remove it from metadata_lines.
    header_line = metadata_lines.pop().lstrip('~').strip()
    headers = header_line.split()

    # Join the remaining metadata lines into a single string.
    metadata_str = "\n".join(metadata_lines)

    # Convert the remaining data lines into CSV format.
    csv_lines = [",".join(headers)]  # CSV header
    for line in lines[data_start_idx:]:
        line = line.strip()
        if line:  # Skip empty lines.
            # Split on whitespace then join with commas.
            csv_lines.append(",".join(line.split()))

    csv_content = "\n".join(csv_lines)

    # Use StringIO to read the CSV content into a DataFrame.
    df = pd.read_csv(StringIO(csv_content))

    return df, metadata_str
