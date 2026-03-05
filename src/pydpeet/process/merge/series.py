import logging

import numpy as np
import pandas as pd

from pydpeet.process.analyze.utils import (
    StepTimer,
    drop_duplicate_testtime,
)


def merge_into_series(
    dfs: list[pd.DataFrame],
    time_between_tests_seconds: float = 60.0,
    verbose: bool = True,
    sort_dfs: bool = True,
) -> pd.DataFrame:
    """
    Run a list of DataFrames as a single aging test series.

    Each DataFrame is treated as a single test in the series. The 'Test_Time[s]' column of each DataFrame is adjusted to create a continuous time axis. A pause row is added after each DataFrame (except the last one) to indicate a pause in the test series.

    The function returns a single DataFrame with the merged test series.

    Parameters:
    df_list (List[List[pandas.DataFrame]]): List of DataFrames (or list of (df, filename) pairs).
    time_between_tests_seconds (float, optional): Time between tests in seconds. Defaults to 60.0.
    verbose (bool, optional): If True, log debug messages. Defaults to True.
    sort_dfs (bool, optional): If True, sort the DataFrames by their 'Date_Time' column. Defaults to True.

    Returns:
    pandas.DataFrame: Merged DataFrame with a single test series.
    """
    if not dfs:
        logging.info("No DataFrames provided.")
        return pd.DataFrame()

    if time_between_tests_seconds <= 0:
        raise ValueError("time_between_tests_seconds must be > 0")

    first_item = dfs[0]
    if isinstance(first_item, (tuple, list)) and len(first_item) == 2:
        # Already (df, filename) pairs
        input_pairs = dfs
    else:
        # Wrap plain DataFrames with None as filename
        input_pairs = [(df, None) for df in dfs]

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
            if raw_df is None or raw_df.empty or "Test_Time[s]" not in raw_df.columns:
                continue

            df = raw_df.copy()

            # Skip battery description files (existing behavior)
            if "Step_Count" in df.columns:
                first_val = df["Step_Count"].iloc[0]
                if isinstance(first_val, str) and first_val.lower() == "test":
                    logging.warning(f"Skipping DataFrame {i} because Step_Count starts with 'Test'")
                    continue

            last_valid_idx = df["Test_Time[s]"].last_valid_index()
            if last_valid_idx is None:
                logging.info(f"DataFrame {i} skipped: 'Test_Time[s]' is all NaN")
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

            # Convert Step_Count to int64
            if "Step_Count" in df.columns:
                df["Step_Count"] = pd.to_numeric(df["Step_Count"], errors="coerce").fillna(0).astype(np.int64)

            # Ensure Test_Time[s] is numeric and safe for addition
            df["Test_Time[s]"] = pd.to_numeric(df["Test_Time[s]"], errors="coerce").fillna(0.0)

            # --- Apply the current cumulative offset to this DataFrame ---
            df["Test_Time[s]"] = df["Test_Time[s]"] + time_offset

            # Assign sequential TestIndex
            df["TestIndex"] = valid_index
            valid_index += 1

            # Ensure TestIndex is tracked in numeric columns / col_order
            if "TestIndex" not in numeric_cols:
                numeric_cols.append("TestIndex")
            if "TestIndex" not in col_order:
                col_order.append("TestIndex")

            # Store numeric and other columns
            numeric_storage.append(df[numeric_cols].to_numpy())
            for column in datetime_cols + object_cols:
                other_storage[column].extend(df[column].tolist())

            # Compute the maximum Testtime after offset (this is the basis for next offset)
            df_max = df["Test_Time[s]"].dropna().max()

            # If not the last DataFrame, add a pause row placed at df_max + time_between_tests_seconds
            if i < len(sorted_dfs) - 1:
                pause_value = float(df_max + time_between_tests_seconds)
                pause_numeric = []
                for column in numeric_cols:
                    if column == "Test_Time[s]":
                        pause_numeric.append(pause_value)
                    elif column == "TestIndex":
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
        dfs_merged["Test_Time[s]"] = dfs_merged["Test_Time[s]"].astype(float)
        st.log(f"Final merged DataFrame shape: {dfs_merged.shape}")

    dfs_merged = drop_duplicate_testtime(dfs_merged)

    return dfs_merged


def _sort_dfs(
    dfs: list[pd.DataFrame],
    verbose: bool = True,
) -> list[pd.DataFrame]:
    """
    Sorts a list of DataFrames by their 'Date_Time' column.
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
    if not dfs:
        return []

    time_col = "Date_Time"

    # ensure df_list always work with (df, filename) pairs
    if isinstance(dfs[0], (tuple, list)) and len(dfs[0]) == 2:
        pairs = [(df, fn) for df, fn in dfs if df is not None and not df.empty]
    else:
        pairs = [(df, None) for df in dfs if df is not None and not df.empty]

    if not pairs:
        logging.warning("No valid DataFrames found.")
        return []

    # Check if at least one DF has a valid absolute time column
    has_abs_time = all(time_col in df.columns and df[time_col].notna().any() for df, _ in pairs)

    if has_abs_time:
        if verbose:
            logging.info("Sorting DataFrames by absolute time...")
        sorted_pairs = sorted(
            pairs,
            key=lambda x: (
                pd.to_datetime(x[0][time_col].dropna().iloc[0])
                if time_col in x[0].columns and x[0][time_col].notna().any()
                else pd.Timestamp.min
            ),
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

    return [df for df, _ in sorted_pairs]


def merge_into_campaign(
    dfs_list: list[list[pd.DataFrame]],
    verbose: bool = True,
) -> list[pd.DataFrame]:
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
    for test in dfs_list:
        with StepTimer(verbose) as st:
            test_campaign = merge_into_series(test, verbose=verbose)
            st.log("Executed one test series")
        test_campaigns.append(test_campaign)

    if verbose:
        logging.info(f"Completed campaign with {len(test_campaigns)} test series.")

    return test_campaigns
