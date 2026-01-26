import pandas as pd


def to_DataFrame(input_path: str) -> (pd.DataFrame, str):
    """
    Parses the input file from the Safion Cycler into a pandas DataFrame.

    Parameters:
    input_path (str): Path to the input file.

    Returns:
    (pandas.DataFrame, str): A tuple containing the DataFrame with data and metadata as a string.
    """

    # Initialize variables
    meta_data_string = ""
    excitation_data = []
    impedance_spectrum_data = []

    # Read the input file
    with open(input_path, 'r', encoding='us-ascii') as f:
        lines = f.readlines()

    # Temporary variables to store data for each segment
    current_segment = None
    current_data = []

    for line in lines:
        line = line.strip()  # Remove any leading/trailing whitespace

        if not line:  # Empty line indicates a segment boundary
            if current_segment == "excitation_data":
                # Store the excitation data in a list for conversion to DataFrame later
                excitation_data.append(current_data)
            elif current_segment == "impedance_spectrum_data":
                # Store impedance spectrum data in a list for conversion to DataFrame later
                impedance_spectrum_data.append(current_data)
            else:
                # Add the meta data to the string
                meta_data_string += '\n'.join(current_data) + '\n'

            # Reset for the next segment
            current_segment = None
            current_data = []

        elif line.lower() == "excitation signal" or line.lower() == "excitation signal (sweep)":
            # This segment starts excitation_data
            if current_segment == "excitation_data":
                excitation_data.append(current_data)
            current_segment = "excitation_data"
            current_data = []

        elif line.lower() == "impedance spectrum":
            # This segment starts impedance_spectrum_data
            if current_segment == "impedance_spectrum_data":
                impedance_spectrum_data.append(current_data)
            current_segment = "impedance_spectrum_data"
            current_data = []

        else:
            # If it's not an empty line and not one of the special segments,
            # it belongs to either meta_data or the current segment.
            current_data.append(line)

    # Handle the last segment after the loop ends
    if current_segment == "excitation_data":
        excitation_data.append(current_data)
    elif current_segment == "impedance_spectrum_data":
        impedance_spectrum_data.append(current_data)
    elif current_segment == "meta_data":
        meta_data_string += '\n'.join(current_data) + '\n'

    # Split the first string into columns to get the headers
    headers_ex = excitation_data[0][0].strip().split(',')
    headers_ex = [item for item in headers_ex if item != '']
    headers_im = impedance_spectrum_data[0][0].strip().split(',')
    headers_im = ['impedance_frequency' if header == 'frequency' else header for header in headers_im]

    # Split strings by ',' and create DataFrame for excitation data
    excitation_data_split = [row.split(',') for row in excitation_data[0][1:]]
    excitation_df = pd.DataFrame(excitation_data_split, columns=headers_ex)

    # Split strings by ',' and create DataFrame for impedance spectrum data
    impedance_spectrum_data_split = [row.split(',') for row in impedance_spectrum_data[0][1:]]
    impedance_spectrum_df = pd.DataFrame(impedance_spectrum_data_split, columns=headers_im)

    # Combine DataFrames (meta_data_string does not need to be converted to a DataFrame)
    df_merged = pd.concat([excitation_df, impedance_spectrum_df], axis=1, ignore_index=False, sort=False)

    return df_merged, meta_data_string
