import logging

import numpy as np
import pandas as pd
from numba import njit


# TODO: Typing correct?
@njit(cache=True)
def _widen_segments_numba(
    Data_arr: np.ndarray,
    ID_arr: np.ndarray,
    thresholds: np.array,
) -> np.array:
    """
    Widen constant segments in a DataFrame by identifying contiguous segments in each column,
    and then widening each segment by extending it to the left and right until the
    average of the segment exceeds the threshold.

    Parameters:
    Data_arr (numpy array): Input DataFrame with Segment columns.
    ID_arr (numpy array): IDs of the segments in the DataFrame.
    thresholds (numpy array): Threshold values per column.

    Returns:
    numpy array: The original DataFrame with widened segments.
    """
    n_rows, n_cols = Data_arr.shape
    new_ID_arr = ID_arr.copy()

    for col_idx in range(n_cols):
        thresh = thresholds[col_idx]
        col_data = Data_arr[:, col_idx]
        col_ids = new_ID_arr[:, col_idx]

        i = 0
        while i < n_rows:
            col_id = col_ids[i]
            if col_id == -1:
                i += 1
                continue

            # Identify start and end of contiguous segment
            start = i
            while i + 1 < n_rows and col_ids[i + 1] == col_id:
                i += 1
            end = i

            # Compute mean and check validity in one pass
            seg_sum = 0.0
            segment_length = end - start + 1
            is_valid = True
            for j in range(start, end + 1):
                seg_sum += col_data[j]
            avg = seg_sum / segment_length

            for j in range(start, end + 1):
                if abs(col_data[j] - avg) > thresh:
                    is_valid = False
                    break
            if not is_valid:
                i += 1
                continue

            # Extend to the right
            extend_r = end
            j = end + 1
            while j < n_rows:
                v = col_data[j]
                cid_j = new_ID_arr[j, col_idx]
                if abs(v - avg) > thresh or (cid_j != -1 and cid_j != col_id):
                    break
                extend_r = j
                j += 1

            # Extend to the left
            extend_l = start
            j = start - 1
            while j >= 0:
                v = col_data[j]
                cid_j = new_ID_arr[j, col_idx]
                if abs(v - avg) > thresh or (cid_j != -1 and cid_j != col_id):
                    break
                extend_l = j
                j -= 1

            # Assign widened ID to extended ranges
            for j in range(extend_l, start):
                new_ID_arr[j, col_idx] = col_id
            for j in range(end + 1, extend_r + 1):
                new_ID_arr[j, col_idx] = col_id

            # Invalidate other columns only once for the widened areas
            if extend_l < start or extend_r > end:
                for other_col_idx in range(n_cols):
                    if other_col_idx == col_idx:
                        continue
                    for j in range(extend_l, start):
                        new_ID_arr[j, other_col_idx] = -1
                    for j in range(end + 1, extend_r + 1):
                        new_ID_arr[j, other_col_idx] = -1

            i += 1

    return new_ID_arr


def _widen_constant_segments(
    df: pd.DataFrame,
    adjust_segments_config: list[tuple[str, float]],
    Threshold_segments_to_print: int,
    supress_IO_warnings: bool,
) -> pd.DataFrame:
    """
    Widen constant segments in a DataFrame by identifying contiguous segments in each column,
    and then widening each segment by extending it to the left and right until the
    average of the segment exceeds the threshold.

    Parameters:
    df (pd.DataFrame): Input DataFrame with Segment columns.
    adjust_segments_config (list of tuples): List of tuples containing column name and threshold value.
        Example: [("Voltage[V]", 0.1), ("Current[A]", 0.1), ("Power[W]", 0.1)]
    Threshold_segments_to_print (int): The maximum number of removed segments to print in the warning message.
    supress_IO_warnings (bool): Whether to suppress warning messages.

    Returns:
    pd.DataFrame: The original DataFrame with widened segments.
    """
    Data_columns_name_list = [name for name, _ in adjust_segments_config]
    thresholds = np.array([thresh for _, thresh in adjust_segments_config], dtype=np.float64)
    ID_columns_name_list = ["Segment_" + name for name, _ in adjust_segments_config]

    Data_arr = df[Data_columns_name_list].to_numpy(dtype=np.float64)
    ID_arr = df[ID_columns_name_list].to_numpy(dtype=np.int32)

    n_rows = ID_arr.shape[0]

    # Store start and end indices of original segments per column
    original_segments = {col: [] for col in ID_columns_name_list}
    for i, col in enumerate(ID_columns_name_list):
        ids = ID_arr[:, i]
        current_id = ids[0]
        start_idx = 0 if current_id != -1 else None
        for row in range(1, n_rows):
            if ids[row] != current_id:
                if current_id != -1:
                    original_segments[col].append((start_idx, row - 1))
                current_id = ids[row]
                start_idx = row if current_id != -1 else None
        if current_id != -1:
            original_segments[col].append((start_idx, n_rows - 1))

    # Run widening
    new_ID_arr = _widen_segments_numba(Data_arr, ID_arr, thresholds)

    # Check removed segments and print one-line warning
    for i, col in enumerate(ID_columns_name_list):
        updated_ids = new_ID_arr[:, i]
        removed_ranges = [
            f"{start}:{end}" for start, end in original_segments[col] if np.all(updated_ids[start : end + 1] == -1)
        ]
        if removed_ranges:
            if not supress_IO_warnings:
                if Threshold_segments_to_print:
                    if Threshold_segments_to_print < len(removed_ranges):
                        logging.warning(
                            f"Removed segments during finetuning of the width in '{col}': "
                            + ", ".join(removed_ranges[:Threshold_segments_to_print])
                            + " ..."
                        )
                    else:
                        logging.warning(
                            f"Removed segments during finetuning of the width in '{col}': "
                            + ", ".join(removed_ranges[:Threshold_segments_to_print])
                        )
                else:
                    logging.warning(
                        f"Removed segments during finetuning of the width in '{col}': " + ", ".join(removed_ranges)
                    )

    # Update DataFrame
    for i, col in enumerate(ID_columns_name_list):
        df[col] = new_ID_arr[:, i]

    return df
