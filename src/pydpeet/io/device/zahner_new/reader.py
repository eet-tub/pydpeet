import pandas as pd


def _to_dataframe(input_path: str) -> tuple[pd.DataFrame, str]:
    """
    Parses the input file from the Zahner Cycler into a pandas DataFrame.

    Parameters:
    input_path (str): Path to the input file.

    Returns:
    (pd.DataFrame, str): A tuple containing the DataFrame with data and metadata as a string.
    """
    metadata = []

    # Open the file and process lines
    try:
        with open(input_path, encoding="us-ascii") as file:
            # Read metadata until a data header line is detected
            line = file.readline()
            while line and not (line.strip().startswith("time") or line.strip().startswith("Number")):
                metadata.append(line.strip())
                line = file.readline()

            if not line:
                raise ValueError("Header line starting with 'time' or 'Number' not found")

            # Detect delimiter and process the header
            if ";" in line:
                delimiter = ";"
            elif "," in line:
                delimiter = ","
            else:
                delimiter = None  # Whitespace-delimited

            # Read and parse data lines
            if delimiter:
                headers = line.strip().split(delimiter)
                data_lines = [row.strip().split(delimiter) for row in file if row.strip()]
            else:
                headers = line.strip().split()
                data_lines = [row.strip().split() for row in file if row.strip()]
    except UnicodeDecodeError as e:
        raise ValueError("File could not be decoded") from e

    # Join metadata into a single string
    metadata_str = "\n".join(metadata)

    # Create DataFrame
    df = pd.DataFrame(data_lines, columns=headers)

    return df, metadata_str
