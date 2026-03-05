import logging
import os.path
import re
import warnings
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from plistlib import InvalidFileException

import pandas as pd

from pydpeet.io.configs.const import PANDAS_EXCEL_ENGINE

_BASE_CHILD_FILE_PATTERN = r"_(\d+).(xlsx|xls)"


def to_dataframe(input_path: str) -> tuple[pd.DataFrame, str]:
    """
    Parses the input file from the Neware Cycler into a pandas DataFrame.

    This function reads various sheets from the input Excel file in parallel using a thread pool.
    It processes the data by handling different types of sheets and extracts metadata information.

    Parameters:
    input_path (str): Path to the input file.

    Returns:
    (DataFrame, str): A tuple containing the merged DataFrame with processed data and metadata as a string.
    """

    sheets = _read_sheets(input_path)
    with ThreadPoolExecutor() as executor:
        record_auxvol_auxtemp_future = executor.submit(_handle_record_auxvol_auxtemp, sheets["record"], sheets.get("auxVol"), sheets.get("auxTemp"))

        test_sheet = sheets["test"]
        future_meta_data = executor.submit(_extract_meta_data, sheets["unit"], test_sheet, sheets["log"])

        cycle_step_test_future = executor.submit(_handle_cycle_step_test, sheets["cycle"], sheets["step"], test_sheet)

        merged = _handle_final(cycle_step_test_future.result(), record_auxvol_auxtemp_future.result())

        return merged, future_meta_data.result()


def _read_sheets(main_file_path: str) -> dict[str, pd.DataFrame] | None:
    """
    Reads the main Excel file and its children into a dictionary of DataFrames.

    It checks if the main file exists and is a .xlsx or .xls file.
    If the file is valid, it calls `_read_sheets_from` to read the main file and its children.

    Parameters:
    main_file_path (str): Path to the main Excel file.

    Returns:
    Dict[str, DataFrame] | None: A dictionary containing DataFrames for each sheet.
    """
    logging.info(f"Reading sheets from {main_file_path}...")
    if not os.path.exists(main_file_path):
        raise FileNotFoundError(f"Not found: {main_file_path}")
    if not os.path.isfile(main_file_path) or not main_file_path.endswith(".xlsx") or main_file_path.endswith(".xls"):
        raise InvalidFileException("Input file is not a .xlsx or .xls file")

    return _read_sheets_from(main_file_path, _find_children(main_file_path))


def _find_children(main_file_path) -> list[str]:
    """
    Finds all child Excel files associated with the given main file.

    The files are identified by their name pattern, which is the same as the main file name,
    followed by "_<number>.xlsx" or "_<number>.xls".

    The found files are then sorted by the number in the file name.

    Parameters:
    main_file_path (str): Path to the main Excel file.

    Returns:
    list[str]: A list of paths to the child Excel files.
    """
    main_file_name, _ = os.path.splitext(os.path.basename(main_file_path))
    child_file_pattern = rf"{main_file_name}{_BASE_CHILD_FILE_PATTERN}"
    main_file_dir = os.path.dirname(main_file_path)
    child_file_paths = [child_file_path for file_name in os.listdir(main_file_dir) if ((child_file_path := os.path.join(main_file_dir, file_name)).endswith(".xlsx") or child_file_path.endswith(".xls")) and re.fullmatch(child_file_pattern, file_name) and child_file_path != main_file_path]
    child_file_paths.sort(key=lambda file: int(match.group(1)) if (match := re.search(_BASE_CHILD_FILE_PATTERN, file)) is not None else 0)

    return child_file_paths


def find_main_files(input_path: str) -> list[str]:
    """
    Finds all main Excel files in the specified directory.

    This function scans the given directory and returns a list of Excel files
    that are not identified as child files. Main files are those with extensions
    '.xlsx' or '.xls' and do not match the child file naming pattern defined by
    `_BASE_CHILD_FILE_PATTERN`.

    Parameters:
    input_path (str): The path to the directory to search for main Excel files.

    Returns:
    list[str]: A list of main Excel file names found in the directory.
    """
    return [file for file in os.listdir(input_path) if (file.endswith(".xlsx") or file.endswith(".xls")) and not re.search(_BASE_CHILD_FILE_PATTERN, file)]


def _read_sheets_from(
        main_file: str,
        children: list[str]
) -> dict[str, pd.DataFrame] | None:
    """
    Reads sheets from the main Excel file and its children into a dictionary of DataFrames.

    If there are no children, it reads the main file directly.
    If there are children, it reads the main file and its children in parallel using a thread pool.
    Each child sheet is concatenated to the main sheet with the same name.

    Parameters:
    main_file (str): Path to the main Excel file.
    children (list[str]): List of paths to the child Excel files.

    Returns:
    Dict[str, DataFrame] | None: A dictionary containing DataFrames for each sheet.
    """
    if len(children) == 0:
        excel = pd.ExcelFile(main_file, engine=PANDAS_EXCEL_ENGINE)
        return {sheet_name: excel.parse(sheet_name) for sheet_name in excel.sheet_names}

    with ThreadPoolExecutor() as executor:
        main_file_future = executor.submit(pd.ExcelFile, main_file, engine=PANDAS_EXCEL_ENGINE)
        children_excels = list(executor.map(lambda child: pd.ExcelFile(child, engine=PANDAS_EXCEL_ENGINE), children))
        main_file = main_file_future.result()
        main_sheets_future = executor.submit(main_file.parse, main_file.sheet_names)
        children_sheets = list(executor.map(lambda child: child.parse(child.sheet_names), children_excels))
        main_sheets = main_sheets_future.result()
        for child_sheets in children_sheets:
            for child_sheet_name, child_sheet in child_sheets.items():
                for main_sheet_name, main_sheet in main_sheets.items():
                    if child_sheet_name == main_sheet_name:
                        main_sheets[main_sheet_name] = pd.concat([main_sheet, child_sheet], ignore_index=True)

        return main_sheets


def _extract_meta_data(
        unit_sheet: pd.DataFrame,
        test_sheet: pd.DataFrame,
        log_sheet: pd.DataFrame
) -> str:
    """
    Extracts and concatenates metadata from the provided DataFrames.

    This function takes three DataFrames as input, representing unit, test, and log sheets.
    It converts the unit sheet and log sheet to strings without the index and appends them
    to the metadata list. From the test sheet, it searches for the first occurrence of a row
    containing "Step Plan" and appends a string representation of the test sheet with this row
    concatenated to the result.

    Parameters:
    unit_sheet (DataFrame): The DataFrame representing the unit sheet.
    test_sheet (DataFrame): The DataFrame representing the test sheet.
    log_sheet (DataFrame): The DataFrame representing the log sheet.

    Returns:
    str: A single string containing the concatenated metadata from the input DataFrames.
    """
    meta_data = [unit_sheet.to_string(index=False)]
    for _, row in test_sheet.iterrows():
        if "Step Plan" in row.values:
            meta_data.append(pd.concat([test_sheet, pd.DataFrame([row])], ignore_index=True).to_string(index=False))
            break
    meta_data.append(log_sheet.to_string(index=False))

    return "\n".join(meta_data)


def _handle_cycle_step_test(
        cycle_sheet: pd.DataFrame,
        step_sheet: pd.DataFrame,
        test_sheet: pd.DataFrame
) -> pd.DataFrame:
    """
    Handles the cycle, step, and test sheets by merging them together.

    This function takes DataFrames for the cycle, step, and test sheets as input.
    It first merges the cycle and step sheets on the 'Cycle Index' column.
    Then it calls the _handle_test function to handle the test sheet.
    Finally, it merges the cycle_step_test sheet with the test sheet on the 'Step Index' column.

    Parameters:
    cycle_sheet (DataFrame): The DataFrame representing the cycle sheet.
    step_sheet (DataFrame): The DataFrame representing the step sheet.
    test_sheet (DataFrame): The DataFrame representing the test sheet.

    Returns:
    DataFrame: A DataFrame containing the merged data from the cycle, step, and test sheets.
    """
    logging.info("Handling sheets cycle, step and test...")
    logging.info("merging cycle and step...")

    cycle_step_test = pd.merge(cycle_sheet, step_sheet, left_on="Cycle Index", right_on="Cycle Index", how="left")
    test = _handle_test(test_sheet)

    logging.info("merging cycle_step_test and test...")

    return pd.merge(cycle_step_test, test, left_on="Step Index", right_on="Step Index", how="left")


def _handle_test(test: pd.DataFrame) -> pd.DataFrame:
    """
    Handles the test sheet by selecting the relevant columns and renaming them to fit the standard.

    This function takes a DataFrame representing the test sheet as input.
    It first identifies the index of the row containing the headers.
    Then it creates a new DataFrame from the data below the headers and assigns it the correct column names.
    Finally, it renames the columns to fit the standard and returns the DataFrame.

    Parameters:
    test (DataFrame): The DataFrame representing the test sheet.

    Returns:
    DataFrame: A DataFrame containing the handled test sheet data.
    """
    logging.info("handling test sheet...")

    headers_idx = test[test.apply(lambda row: row.astype(str).str.contains("Step Index").any(), axis=1)].index[0]
    data = pd.DataFrame(test.iloc[headers_idx + 1 :].values, columns=test.iloc[headers_idx])
    data["Step Index"] = pd.to_numeric(data["Step Index"], errors="coerce")
    data.rename(
        columns={
            "Energy(Wh)": "Energy(Wh) - Test",
            "Capacity(Ah)": "Capacity(Ah) - Test",
            "Power(W)": "Power(W) - Test",
            "Voltage(V)": "Voltage[V] - Test",
            "Current(A)": "Current[A] - Test",
        },
        inplace=True,
    )

    return data


@contextmanager
def _capture_settingwithcopy_debug():
    original = warnings.showwarning

    def _handler(message, category, filename, lineno, file=None, line=None):
        if category is pd.errors.SettingWithCopyWarning:
            logging.debug("%s:%d: %s", filename, lineno, message)
        else:
            original(message, category, filename, lineno, file, line)

    warnings.showwarning = _handler
    try:
        yield
    finally:
        warnings.showwarning = original


def _handle_record_auxvol_auxtemp(
        df_record: pd.DataFrame,
        df_auxvol: pd.DataFrame | None,
        df_auxtemp: pd.DataFrame | None
) -> pd.DataFrame:
    """
    Processes and merges the record, auxiliary voltage, and auxiliary temperature sheets.

    This function takes DataFrames for the record, auxiliary voltage, and auxiliary temperature
    sheets. It renames columns in the record DataFrame to fit the standardized naming convention.
    If auxiliary voltage and temperature DataFrames are provided, it re-indexes their headers
    and merges them with the record DataFrame on the 'DataPoint' column.

    Parameters:
    df_record (DataFrame): The DataFrame representing the record sheet.
    df_auxvol (DataFrame | None): The DataFrame representing the auxiliary voltage sheet, or None if not available.
    df_auxtemp (DataFrame | None): The DataFrame representing the auxiliary temperature sheet, or None if not available.

    Returns:
    DataFrame: A DataFrame containing the merged data from the record, auxiliary voltage, and
    auxiliary temperature sheets.
    """
    logging.info("hadling record auxvol auxtemp sheets...")

    df_record.rename(columns={"Current(A)": "Current[A] - record", "Step Type": "Step Type - record"}, inplace=True)

    result = df_record
    if df_auxvol is not None:
        df_auxvol = _re_index_headers(df_auxvol, ["DataPoint", "Date", "V1", "Aux. ΔV"], "Single cell voltage(V)")
        with _capture_settingwithcopy_debug():
            df_auxvol.rename(columns={"Date": "Date - auxVol", "DataPoint": "DataPoint - auxVol"}, inplace=True)
        logging.info("merging record and auxvol...")
        result = pd.merge(df_record, df_auxvol, left_on="DataPoint", right_on="DataPoint - auxVol", how="left")

    if df_auxtemp is not None:
        df_auxtemp = _re_index_headers(df_auxtemp, ["DataPoint", "Date", "T1", "Aux. ΔT"], "Single cell temperature(℃)")
        with _capture_settingwithcopy_debug():
            df_auxtemp.rename(columns={"Date": "Date - auxTemp", "DataPoint": "DataPoint - auxTemp"}, inplace=True)
        logging.info("merging record_auxvol and auxtemp...")
        result = pd.merge(result, df_auxtemp, left_on="DataPoint", right_on="DataPoint - auxTemp", how="left")

    return result


def _re_index_headers(
        df: pd.DataFrame,
        expected_headers: list[str],
        keyword: str
) -> pd.DataFrame:
    """
    Checks if the headers of a DataFrame need to be reindexed and reindexes them if necessary.

    This function takes a DataFrame and a list of expected headers as input.
    It then checks if the headers of the DataFrame need to be reindexed by comparing them with the expected headers.
    If the headers need to be reindexed, it does so by taking the first row of the DataFrame as the new headers and then dropping the first row.
    Finally, it returns the DataFrame with the reindexed headers.

    Parameters:
    df (DataFrame): The DataFrame to be processed.
    expected_headers (list[str]): The list of expected headers.
    keyword (str): A keyword to check if the headers need to be reindexed.

    Returns:
    DataFrame: The DataFrame with the reindexed headers.
    """
    logging.info("checking if headers need to be reindexed...")
    if not all(header in df.columns for header in expected_headers) and keyword in df.columns:
        logging.info("reindexing headers...")
        df.columns = df.iloc[0].values
        df = df.iloc[1:]
    else:
        logging.info("no need to reindex headers...")

    return df


def _handle_final(
        step: pd.DataFrame,
        record: pd.DataFrame
) -> pd.DataFrame:
    """
    Merges the step and record DataFrames based on the 'step_id' column.

    This function takes two DataFrames as input: 'step' and 'record'. It merges the two DataFrames
    based on the 'step_id' column, which is obtained by identifying the index of rows in the 'record'
    DataFrame where the 'Time' column (or a similar column) is 0 or a timedelta of 0. The 'step' DataFrame
    is merged with the 'record' DataFrame using the 'step_id' column as the merge key. The resulting
    DataFrame is returned.

    Parameters:
    step (DataFrame): The DataFrame representing the step sheet.
    record (DataFrame): The DataFrame representing the record sheet.

    Returns:
    DataFrame: A DataFrame containing the merged data from the step and record sheets.
    """
    logging.info("handling final merge...")

    step = step.reset_index(drop=True)

    # Build reset mask from Time column
    time_series = record["Time"]
    time_td = pd.to_timedelta(time_series, errors="coerce")
    time_num = pd.to_numeric(time_series, errors="coerce")

    reset_mask = (time_td.eq(pd.Timedelta(0)) | time_num.eq(0)).fillna(False)

    # Keep only rising edges (first True in each block)
    reset_mask &= ~reset_mask.shift(1, fill_value=False)

    # Prevent first row from triggering a reset
    reset_mask.iloc[0] = False

    record["step_id"] = reset_mask.cumsum()

    record.drop(columns=["Step Type - record"], inplace=True)

    merged = step.merge(record, left_index=True, right_on="step_id", how="left")

    return merged
