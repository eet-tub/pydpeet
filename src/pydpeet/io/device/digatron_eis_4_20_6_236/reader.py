import pandas as pd


def to_dataframe(input_path: str) -> (pd.DataFrame, str):
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
        while not line.startswith("Zeitstempel"):
            metadata.append(line.strip())
            line = file.readline()

        # Extract headers and remaining data
        headers = line.strip().split(",")
        # for i in range(4):
        #    line = file.readline()
        #    metadata.append(line.strip())

        data_lines = [row.strip().split(",") for row in file if row.strip()]

        # appending first string from datalines
        metadata.append(";".join(data_lines.pop(0)))

    # Join metadata into a single string
    metadata_str = "\n".join(metadata)

    # Create DataFrame
    df = pd.DataFrame(data_lines, columns=headers)

    return df, metadata_str
