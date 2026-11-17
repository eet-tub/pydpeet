import logging
from io import StringIO

import pandas as pd


def _to_dataframe(input_path: str) -> tuple[pd.DataFrame, str]:
    """
    Parses the input file from the basytec cycler into a pandas DataFrame.
    It first converts the data portion to CSV format in memory.

    BaSyTec exports normally start with a block of metadata lines prefixed with
    '~', the last of which holds the column header. Some exports omit that block
    entirely and put the column header on the first line; those files are
    supported too, in which case the returned metadata string is empty.

    Parameters:
        input_path (str): Path to the input file.

    Returns:
        (pd.DataFrame, str): A tuple containing the DataFrame with the data and metadata as a string.
    """
    with open(input_path, encoding="iso-8859-1") as file:
        lines = file.readlines()

    # Collect all metadata lines (those starting with '~')
    metadata_lines = []
    data_start_idx = len(lines)
    for idx, line in enumerate(lines):
        if line.startswith("~"):
            metadata_lines.append(line.strip())
        else:
            data_start_idx = idx
            break

    if metadata_lines:
        # The last metadata line is used as the header; remove it from metadata_lines.
        header_line = metadata_lines.pop().lstrip("~").strip()
        # Join the remaining metadata lines into a single string.
        metadata_str = "\n".join(metadata_lines)
    else:
        # No '~' metadata block: some BaSyTec exports write the column header
        # directly as the first line. Use it as the header and start the data
        # on the following line.
        if not lines:
            raise ValueError("The file is empty. Cannot determine column headers.")
        header_line = lines[data_start_idx].lstrip("~").strip()
        data_start_idx += 1
        metadata_str = ""
        logging.info("No '~' metadata lines found. Using the first line as the column header.")

    headers = header_line.split()

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

    if "T1[°C]" not in df.columns:
        df["T1[°C]"] = None
        logging.warning("Column 'T1[°C]' not found in the data. Filling with None values.")

    return df, metadata_str
