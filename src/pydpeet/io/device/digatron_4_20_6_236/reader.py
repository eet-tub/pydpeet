import logging

import pandas as pd


def _to_dataframe(input_path: str) -> tuple[pd.DataFrame, str]:
    """
    Parses the input file from the Digatron Cycler into a pandas DataFrame.

    Parameters:
    input_path (str): Path to the input file.

    Returns:
    (pandas.DataFrame, str): A tuple containing the DataFrame with data and metadata as a string.
    """
    metadata = []

    # Open the file and process lines
    with open(input_path, encoding="iso-8859-1") as file:
        # Read metadata until the header line is found
        line = file.readline()
        while line and not line.startswith("Zeitstempel"):
            metadata.append(line.strip())
            line = file.readline()

        if not line:
            raise ValueError(f"Header line starting with 'Zeitstempel' not found in {input_path}")

        # Extract headers and remaining data
        headers = line.strip().split(",")
        data_lines = [row.strip().split(",") for row in file if row.strip()]

        # Strip trailing empty fields (e.g. caused by trailing commas) to fix:
        # Error: 98 columns passed, passed data had 99 columns
        def _strip_trailing_empty_fields(fields: list[str]) -> list[str]:
            fields = list(fields)
            while fields and fields[-1] == "":
                fields.pop()
            return fields

        headers = _strip_trailing_empty_fields(headers)
        data_lines = [_strip_trailing_empty_fields(row) for row in data_lines]

        # appending first string from datalines
        metadata.append(",".join(data_lines.pop(0)))

    # Join metadata into a single string
    metadata_str = "\n".join(metadata)

    # Create DataFrame
    df = pd.DataFrame(data_lines, columns=headers)

    # Convert numeric columns to appropriate types
    for col in headers:
        try:
            # Handle duplicate column names by appending an index to duplicates
            cols = pd.Series(df.columns)
            for dup in df.columns[df.columns.duplicated(keep=False)]:
                cols[df.columns.get_loc(dup)] = [
                    f"{dup}_{d_idx}" if d_idx != 0 else dup for d_idx in range(df.columns.get_loc(dup).sum())
                ]
            df.columns = cols

            df[col] = pd.to_numeric(df[col])
        except ValueError:
            # Leave non-numeric columns as is
            pass

    if "T_Batt" not in df.columns:
        df["T_Batt"] = None
        logging.warning("Column 'T_Batt' not found in the data. Filling with None values.")

    return df, metadata_str
