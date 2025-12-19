import pandas as pd

from pydpeet.convert.configs.const import PANDAS_EXCEL_ENGINE


def to_DataFrame(input_path: str) -> (pd.DataFrame, str):
    """
    Parses the input file from the Arbin Cycler into a pandas DataFrame.

    Parameters:
    input_path (str): Path to the input file.

    Returns:
    (pandas.DataFrame, str): A tuple containing the DataFrame with data and metadata as a string.
    """

    # load Excel data
    excel_data = pd.ExcelFile(input_path, engine = PANDAS_EXCEL_ENGINE)

    return read_sheets(excel_data)

def read_sheets (excel_file : pd.ExcelFile) -> (pd.DataFrame, str):

    """
    Reads data from all sheets in an Excel file and returns them as a tuple of a DataFrame and a string.

    The first sheet that starts with "Detail" is used as the main data sheet. If there are more sheets with this name,
    they are appended to the first sheet.

    All other sheets are concatenated into a single string as metadata.

    Parameters:
    excel_file (pd.ExcelFile): The Excel file to read from.

    Returns:
    (pd.DataFrame, str): A tuple containing the DataFrame with data and metadata as a string.
    """

    # variables for the dataframe and String
    arbin_df = None
    metadata_str = []
    iterator = 0

    # iterate all sheets
    for sheet_name in excel_file.sheet_names:
        # find sheet that starts with "Detail"
        if sheet_name.startswith("Detail"):
            # if it´s the first sheet, that starts with the channel, it gets added to df
            if iterator == 0:
                arbin_df = excel_file.parse(sheet_name, header=0)
            # if it´s the second or higher Sheet, it will be appended without the header and the first row,
            # because first row of 2nd sheet and last row of first sheet are the same
            else:
                # get Data from further Sheet(s)
                # remove the first two rows (header and multiple row)
                further_sheet_data = excel_file.parse(sheet_name, header=0).iloc[1:]
                # concat bot sheets into one
                arbin_df = pd.concat([arbin_df, further_sheet_data])
            iterator += 1
        else:  # combine all other sheets into a string as metadata
            sheet_data = excel_file.parse(sheet_name, header=None)  # no header
            sheet_str = f"Sheet: {sheet_name}\n{sheet_data.to_string(index=False, header=False)}"
            metadata_str.append(sheet_str)

    # combine all metadata sheets into one string
    metadata_str_combined = "\n\n".join(metadata_str)

    return arbin_df, metadata_str_combined
