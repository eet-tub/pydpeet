import logging
from typing import List

import numpy as np
import pandas as pd

from pydpeet.process.analyze.calculations.utils import StepTimer, drop_duplicate_testtime


# ** series and campaign utilities **

def run_series(df_list, time_between_tests_seconds: float = 60.0, verbose=True, sort_dfs=True):
    """
    Run a list of DataFrames as a single aging test series.

    Each DataFrame is treated as a single test in the series. The 'Testtime[s]' column of each DataFrame is adjusted to create a continuous time axis. A pause row is added after each DataFrame (except the last one) to indicate a pause in the test series.

    The function returns a single DataFrame with the merged test series.

    Parameters:
    df_list (List[List[pandas.DataFrame]]): List of DataFrames (or list of (df, filename) pairs).
    time_between_tests_seconds (float, optional): Time between tests in seconds. Defaults to 60.0.
    verbose (bool, optional): If True, log debug messages. Defaults to True.
    sort_dfs (bool, optional): If True, sort the DataFrames by their 'Absolute Time[yyyy-mm-dd hh:mm:ss]' column. Defaults to True.

    Returns:
    pandas.DataFrame: Merged DataFrame with a single test series.
    """
    if not df_list:
        logging.info("No DataFrames provided.")
        return pd.DataFrame()

    if time_between_tests_seconds <= 0:
        raise ValueError("time_between_tests_seconds must be > 0")

    first_item = df_list[0]
    if isinstance(first_item, (tuple, list)) and len(first_item) == 2:
        # Already (df, filename) pairs
        input_pairs = df_list
    else:
        # Wrap plain DataFrames with None as filename
        input_pairs = [(df, None) for df in df_list]

    if verbose:
        logging.info("Sorting DataFrames...")

    if sort_dfs:
        sorted_dfs = _sort_dfs(input_pairs, verbose=verbose)
    else:
        # Keep only the DataFrame from the pairs (df, filename)
        sorted_dfs = [df for df, _ in input_pairs]

    time_offset = 0.0
    numeric_cols, datetime_cols, object_cols = [], [], []
    col_order = []
    numeric_storage = []
    other_storage = {}
    valid_index = 0  # counts only valid DataFrames

    if verbose:
        logging.info(f"Adjusting Testtime and adding {time_between_tests_seconds}s pauses...")

    with StepTimer(verbose) as st:
        for i, raw_df in enumerate(sorted_dfs):
            if raw_df is None or raw_df.empty or 'Testtime[s]' not in raw_df.columns:
                continue

            df = raw_df.copy()

            # Skip battery description files (existing behavior)
            if 'StepID' in df.columns:
                first_val = df['StepID'].iloc[0]
                if isinstance(first_val, str) and first_val.lower() == "test":
                    logging.warning(f"Skipping DataFrame {i} because StepID starts with 'Test'")
                    continue

            last_valid_idx = df['Testtime[s]'].last_valid_index()
            if last_valid_idx is None:
                logging.info(f"DataFrame {i} skipped: 'Testtime[s]' is all NaN")
                continue

            # Initialize column types only once
            if not numeric_cols:
                col_order = df.columns.tolist()
                for column in df.columns:
                    dt = df[column].dtype
                    if pd.api.types.is_numeric_dtype(dt):
                        numeric_cols.append(column)
                    elif pd.api.types.is_datetime64_any_dtype(dt):
                        datetime_cols.append(column)
                    else:
                        object_cols.append(column)
                other_storage = {c: [] for c in datetime_cols + object_cols}

            # Convert StepID to int64
            if 'StepID' in df.columns:
                df['StepID'] = pd.to_numeric(df['StepID'], errors='coerce').fillna(0).astype(np.int64)

            # Ensure Testtime[s] is numeric and safe for addition
            df['Testtime[s]'] = pd.to_numeric(df['Testtime[s]'], errors='coerce').fillna(0.0)

            # --- Apply the current cumulative offset to this DataFrame ---
            df['Testtime[s]'] = df['Testtime[s]'] + time_offset

            # Assign sequential TestIndex
            df['TestIndex'] = valid_index
            valid_index += 1

            # Ensure TestIndex is tracked in numeric columns / col_order
            if 'TestIndex' not in numeric_cols:
                numeric_cols.append('TestIndex')
            if 'TestIndex' not in col_order:
                col_order.append('TestIndex')

            # Store numeric and other columns
            numeric_storage.append(df[numeric_cols].to_numpy())
            for column in datetime_cols + object_cols:
                other_storage[column].extend(df[column].tolist())

            # Compute the maximum Testtime after offset (this is the basis for next offset)
            df_max = df['Testtime[s]'].dropna().max()

            # If not the last DataFrame, add a pause row placed at df_max + time_between_tests_seconds
            if i < len(sorted_dfs) - 1:
                pause_value = float(df_max + time_between_tests_seconds)
                pause_numeric = []
                for column in numeric_cols:
                    if column == 'Testtime[s]':
                        pause_numeric.append(pause_value)
                    elif column == 'TestIndex':
                        pause_numeric.append(-1)
                    else:
                        pause_numeric.append(np.nan)
                # ensure shape matches (1, n_numeric_cols)
                numeric_storage.append(np.array([pause_numeric]))

                for column in datetime_cols:
                    other_storage[column].append(pd.NaT)
                for column in object_cols:
                    other_storage[column].append(pd.NA)

                if verbose:
                    st.log(f"Added pause row after DataFrame {i} at {pause_value}s")

                # --- Set time_offset for the next DataFrame to df_max + pause ---
                time_offset = df_max + time_between_tests_seconds
            else:
                # Last DataFrame: update time_offset to the end of this df (no extra pause needed)
                time_offset = df_max

    # If no valid numeric data, return empty DataFrame
    if not numeric_storage:
        return pd.DataFrame()

    with StepTimer(verbose) as st:
        logging.info("Merging DataFrames...")
        numeric_array = np.vstack(numeric_storage)

        data_dict = {}
        for idx, column in enumerate(numeric_cols):
            data_dict[column] = numeric_array[:, idx]
            logging.info(f"Merged numeric column: {column}")
        for column in datetime_cols + object_cols:
            data_dict[column] = other_storage[column]
            logging.info(f"Merged non-numeric column: {column}")

        dfs_merged = pd.DataFrame(data_dict, columns=col_order)
        dfs_merged['Testtime[s]'] = dfs_merged['Testtime[s]'].astype(float)
        st.log(f"Final merged DataFrame shape: {dfs_merged.shape}")

    dfs_merged = drop_duplicate_testtime(dfs_merged)
    return dfs_merged



# def run_series(df_list, time_between_tests_seconds: float = 60.0, verbose=True, sort_dfs=True):
#     if not df_list:
#         logging.info("No DataFrames provided.")
#         return pd.DataFrame()
#
#     if time_between_tests_seconds <= 0:
#         raise ValueError("time_between_tests_seconds must be > 0")
#
#     first_item = df_list[0]
#     input_pairs = df_list if isinstance(first_item, (tuple, list)) and len(first_item) == 2 else [(df, None) for df in df_list]
#
#     if sort_dfs:
#         sorted_dfs = _sort_dfs(input_pairs, verbose=verbose)
#     else:
#         sorted_dfs = [df for df, _ in input_pairs]
#
#     # --- Initialize column order from first valid DataFrame ---
#     col_order, numeric_cols, datetime_cols, object_cols = [], [], [], []
#     for raw_df in sorted_dfs:
#         if raw_df is None or raw_df.empty or 'Testtime[s]' not in raw_df.columns:
#             continue
#         df = raw_df.copy()
#         if 'StepID' in df.columns:
#             first_val = df['StepID'].iloc[0]
#             if isinstance(first_val, str) and first_val.lower() == "test":
#                 continue
#         # Found first valid DataFrame
#         col_order = df.columns.tolist()
#         for column in df.columns:
#             dt = df[column].dtype
#             if pd.api.types.is_numeric_dtype(dt):
#                 numeric_cols.append(column)
#             elif pd.api.types.is_datetime64_any_dtype(dt):
#                 datetime_cols.append(column)
#             else:
#                 object_cols.append(column)
#         break
#
#     if not col_order:
#         logging.info("No valid DataFrames to merge.")
#         return pd.DataFrame()
#
#     time_offset = 0.0
#     valid_index = 0
#
#     if verbose:
#         logging.info(f"Adjusting Testtime and adding {time_between_tests_seconds}s pauses...")
#
#     def row_generator():
#         nonlocal time_offset, valid_index
#         with StepTimer(verbose) as st:
#             for i, raw_df in enumerate(sorted_dfs):
#                 if raw_df is None or raw_df.empty or 'Testtime[s]' not in raw_df.columns:
#                     continue
#
#                 df = raw_df.copy()
#
#                 # Skip battery description files
#                 if 'StepID' in df.columns:
#                     first_val = df['StepID'].iloc[0]
#                     if isinstance(first_val, str) and first_val.lower() == "test":
#                         if verbose:
#                             print(f"Skipping DataFrame {i} because StepID starts with 'Test'")
#                         continue
#
#                 last_valid_idx = df['Testtime[s]'].last_valid_index()
#                 if last_valid_idx is None:
#                     logging.info(f"DataFrame {i} skipped: 'Testtime[s]' is all NaN")
#                     continue
#
#                 if 'StepID' in df.columns:
#                     df['StepID'] = pd.to_numeric(df['StepID'], errors='coerce').fillna(0).astype(np.int64)
#
#                 df['Testtime[s]'] = pd.to_numeric(df['Testtime[s]'], errors='coerce').fillna(0.0)
#                 df['Testtime[s]'] += time_offset
#                 df['TestIndex'] = valid_index
#                 valid_index += 1
#
#                 for row in df.itertuples(index=False, name=None):
#                     yield row
#
#                 last_time = df['Testtime[s]'].iloc[last_valid_idx]
#
#                 # Pause row
#                 if i < len(sorted_dfs) - 1:
#                     pause_row = []
#                     for col in col_order:
#                         if col == 'Testtime[s]':
#                             pause_row.append(last_time + time_between_tests_seconds)
#                         elif col == 'TestIndex':
#                             pause_row.append(-1)
#                         elif col in numeric_cols:
#                             pause_row.append(np.nan)
#                         elif col in datetime_cols:
#                             pause_row.append(pd.NaT)
#                         else:
#                             pause_row.append(pd.NA)
#                     yield tuple(pause_row)
#                     if verbose:
#                         st.log(f"Added pause row after DataFrame {i} at {last_time + time_between_tests_seconds}s")
#                     time_offset = last_time + time_between_tests_seconds
#
#     with StepTimer(verbose) as st:
#         logging.info("Merging DataFrames...")
#         merged_df = pd.DataFrame.from_records(row_generator(), columns=col_order)
#         merged_df['Testtime[s]'] = merged_df['Testtime[s]'].astype(float)
#         st.log(f"Final merged DataFrame shape: {merged_df.shape}")
#
#     return merged_df


# def run_series(df_list, time_between_tests_seconds: float = 60.0, verbose=True, sort_dfs=True):
#     """
#     Run a list of DataFrames as a single aging test series.
#
#     Each DataFrame is treated as a single test in the series. The 'Testtime[s]' column of each DataFrame is adjusted to create a continuous time axis. A pause row is added after each DataFrame (except the last one) to indicate a pause in the test series.
#
#     Returns a single DataFrame with the merged test series.
#     """
#     if not df_list:
#         logging.info("No DataFrames provided.")
#         return pd.DataFrame()
#
#     if time_between_tests_seconds <= 0:
#         raise ValueError("time_between_tests_seconds must be > 0")
#
#     # Wrap plain DataFrames with filename if needed
#     first_item = df_list[0]
#     if isinstance(first_item, (tuple, list)) and len(first_item) == 2:
#         input_pairs = df_list
#     else:
#         input_pairs = [(df, None) for df in df_list]
#
#     # Sort if needed
#     if sort_dfs:
#         sorted_dfs = _sort_dfs(input_pairs, verbose=verbose)
#     else:
#         sorted_dfs = [df for df, _ in input_pairs]
#
#     all_dfs = []
#     time_offset = 0.0
#     valid_index = 0  # counts only valid DataFrames
#
#     if verbose:
#         logging.info(f"Adjusting Testtime and adding {time_between_tests_seconds}s pauses...")
#
#     with StepTimer(verbose) as st:
#         for i, raw_df in enumerate(sorted_dfs):
#             if raw_df is None or raw_df.empty or 'Testtime[s]' not in raw_df.columns:
#                 continue
#
#             df = raw_df.copy()
#             last_valid_idx = df['Testtime[s]'].last_valid_index()
#             if last_valid_idx is None:
#                 logging.info(f"DataFrame {i} skipped: 'Testtime[s]' is all NaN")
#                 continue
#
#             # Ensure Testtime[s] is numeric
#             df['Testtime[s]'] = pd.to_numeric(df['Testtime[s]'], errors='coerce').fillna(0.0)
#             df['Testtime[s]'] += time_offset
#
#             # Assign sequential TestIndex
#             df['TestIndex'] = valid_index
#             valid_index += 1
#
#             all_dfs.append(df)
#
#             last_time = df['Testtime[s]'].iloc[last_valid_idx]
#
#             # Add pause row if not last DataFrame
#             if i < len(sorted_dfs) - 1:
#                 pause_row = pd.DataFrame({col: [pd.NA] for col in df.columns})
#                 pause_row['Testtime[s]'] = last_time + time_between_tests_seconds
#                 pause_row['TestIndex'] = -1
#                 all_dfs.append(pause_row)
#
#                 if verbose:
#                     st.log(f"Added pause row after DataFrame {i} at {pause_row['Testtime[s]'].iloc[0]}s")
#
#                 time_offset = last_time + time_between_tests_seconds
#             else:
#                 time_offset = last_time
#
#     # Merge all DataFrames safely
#     if not all_dfs:
#         return pd.DataFrame()
#
#     with StepTimer(verbose) as st:
#         dfs_merged = pd.concat(all_dfs, ignore_index=True)
#         st.log(f"Final merged DataFrame shape: {dfs_merged.shape}")
#
#     return dfs_merged


def _sort_dfs(df_list, verbose=True):
    """
    Sorts a list of DataFrames by their 'Absolute Time[yyyy-mm-dd hh:mm:ss]' column.
    Falls back to filename order if no valid absolute time is found.

    Parameters
    ----------
    df_list : list of pandas.DataFrame or list of (DataFrame, str)
        List of DataFrames to be sorted. Optionally, pass (df, filename) tuples
        so filenames can be used as a fallback sorting key.

    Returns
    -------
    list of pandas.DataFrame
        Sorted list of DataFrames.
    """
    if not df_list:
        return []

    time_col = 'Absolute Time[yyyy-mm-dd hh:mm:ss]'

    # ensure df_list always work with (df, filename) pairs
    if isinstance(df_list[0], (tuple, list)) and len(df_list[0]) == 2:
        pairs = [(df, fn) for df, fn in df_list if df is not None and not df.empty]
    else:
        pairs = [(df, None) for df in df_list if df is not None and not df.empty]

    if not pairs:
        logging.warning("No valid DataFrames found.")
        return []

    # Check if at least one DF has a valid absolute time column
    has_abs_time = all(
        time_col in df.columns and df[time_col].notna().any()
        for df, _ in pairs
    )

    if has_abs_time:
        if verbose:
            logging.info("Sorting DataFrames by absolute time...")
        sorted_pairs = sorted(
            pairs,
            key=lambda x: (
                pd.to_datetime(x[0][time_col].dropna().iloc[0])
                if time_col in x[0].columns and x[0][time_col].notna().any()
                else pd.Timestamp.min
            )
        )
    else:
        if any(fn is not None for _, fn in pairs):
            if verbose:
                logging.info("No valid absolute time found, sorting by filename...")
            sorted_pairs = sorted(pairs, key=lambda x: x[1] or "")
        else:
            if verbose:
                logging.info("No valid absolute time found, keeping original order...")
            sorted_pairs = pairs

    if verbose:
        logging.info("Sorting complete.")

    # Return just the DataFrames
    return [df for df, _ in sorted_pairs]




def campaign(test_series_list: List[List[pd.DataFrame]], verbose=True):
    """
    Execute a list of test series and return a list of merged DataFrames.

    Parameters:
    -----------
    test_series_list : List[List[pandas.DataFrame]]
        List of lists of DataFrames, where each DataFrame represents a single test.
    verbose : bool, optional
        If True, log debug messages.

    Returns:
    --------
    List of pandas.DataFrame
        List of DataFrames, where each DataFrame represents a merged test series.
    """
    test_campaigns = []
    for test in test_series_list:
        with StepTimer(verbose) as st:
            test_campaign = run_series(test, verbose=verbose)
            st.log("Executed one test series")
        test_campaigns.append(test_campaign)

    if verbose:
        logging.info(f"Completed campaign with {len(test_campaigns)} test series.")

    return test_campaigns


def add_pause_values(df, column='Current[A]', multiply_value=3, verbose=True):
    """
    Adds pause values into a new column 'PauseValues' for plotting.
    Original data remains unchanged.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing the 'TestIndex' column with values -1 for pause blocks
        and optionally 'Current[A]' and 'Testtime[s]' columns.
    column : str, optional
        Name of the column containing numeric values to be used as a base. Defaults to 'Current[A]'.
    multiply_value : float, optional
        Value to multiply the max and min values of the specified column by. Defaults to 3.

    Returns:
    -------
    pandas.DataFrame
        DataFrame with an added 'PauseValues' column containing pause markers.
        The 'Testtime[s]' column is sorted in ascending order.
    """
    test_index_column = 'TestIndex'
    testtime_column = 'Testtime[s]'
    pause_column = 'PauseValues'

    if column not in df.columns:
        raise ValueError(f"Column {column} not found in DataFrame.")
    if test_index_column not in df.columns:
        raise ValueError(f"Column {test_index_column} not found in DataFrame.")

    if verbose:
        logging.info("Adding pause values into new column 'PauseValues'...")

    pause_indices = np.where(df[test_index_column].to_numpy() == -1)[0]
    if pause_indices.size == 0:
        if verbose:
            logging.info("No pause rows found. Skipping add_pause_values.")
        df[pause_column] = np.nan
        return df

    max_val = df[column].max()
    min_val = df[column].min()

    new_rows = np.repeat(df.iloc[pause_indices].to_numpy(), 2, axis=0)
    new_testtime = new_rows[:, df.columns.get_loc(testtime_column)].astype(float)

    # pause values only in the new column
    new_pause_values = np.empty_like(new_testtime, dtype=float)
    new_pause_values[::2] = multiply_value * max_val
    new_pause_values[1::2] = multiply_value * min_val

    # shift test times
    new_testtime[::2] -= 0.1
    new_testtime[1::2] += 0.1

    # build new DataFrame with PauseValues only
    df_extra = pd.DataFrame(new_rows, columns=df.columns)
    df_extra[testtime_column] = new_testtime
    df_extra[pause_column] = new_pause_values

    # mark original rows with NaN in PauseValues
    df[pause_column] = np.nan

    with StepTimer(verbose) as st:
        df_new = pd.concat([df, df_extra], ignore_index=True)
        df_new[testtime_column] = df_new[testtime_column].astype(float)
        df_new.sort_values(by=testtime_column, inplace=True)
        df_new.reset_index(drop=True, inplace=True)
        st.log("Added pause values (in 'PauseValues') and sorted DataFrame")

    return df_new
