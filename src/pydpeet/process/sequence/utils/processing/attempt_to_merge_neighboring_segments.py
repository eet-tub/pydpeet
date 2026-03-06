import numpy as np
import pandas as pd
from numba import njit


@njit(cache=True)
def _merge_segments_1d_optimized(
    ids: np.array,
    data: np.array,
    threshold: float,
) -> np.array:
    """
    Merge adjacent segments in a 1D array if the mean of the adjacent segments is within a threshold.

    Parameters:
    ids : numpy array of int
        The array of segment IDs
    data : numpy array of float
        The array of data values
    threshold : float
        The maximum difference between adjacent segment means

    Returns:
    merged_ids : numpy array of int
        The array of merged segment IDs

    Notes:
    This function uses a prefix sum to quickly compute the mean of each segment. It then checks each pair of adjacent segments if their mean difference is within the threshold. If so, it merges the two segments by replacing the IDs of the right segment with those of the left segment.

    """
    n = len(ids)
    merged_ids = ids.copy()

    # Build prefix sum of data
    cumsum = np.empty(n + 1, dtype=np.float64)
    cumsum[0] = 0.0
    for i in range(n):
        cumsum[i + 1] = cumsum[i] + data[i]

    segments = []
    start = -1
    prev_id = -2

    # Compute segments
    for i in range(n):
        cid = ids[i]
        if cid != -1:
            if cid != prev_id:
                if start != -1:
                    segments.append((start, i - 1, prev_id))
                start = i
        else:
            if start != -1:
                segments.append((start, i - 1, prev_id))
                start = -1
        prev_id = cid
    if start != -1:
        segments.append((start, n - 1, prev_id))

    # Merge adjacent segments if mean check passes
    for seg_idx in range(len(segments) - 1):
        start_left, end_left, id_left = segments[seg_idx]
        start_right, end_right, id_right = segments[seg_idx + 1]

        if end_left + 1 != start_right:
            continue

        total = cumsum[end_right + 1] - cumsum[start_left]
        count = end_right - start_left + 1
        mean_val = total / count

        ok = True
        for j in range(start_left, end_right + 1):
            if abs(data[j] - mean_val) > threshold:
                ok = False
                break

        if ok:
            for j in range(start_right, end_right + 1):
                merged_ids[j] = id_left

    return merged_ids


def _attempt_to_merge_neighboring_segments(
    df: pd.DataFrame,
    adjust_segments_config: list[tuple[str, float]],
) -> pd.DataFrame:
    """
    Attempt to merge neighboring segments in the DataFrame if they're within the specified thresholds.

    Parameters:
    df (pd.DataFrame): Input DataFrame with Segment columns.
    adjust_segments_config (list of tuples): List of tuples containing column name and threshold value.

    Returns:
    pd.DataFrame: The original DataFrame with merged segments.

    Notes:
    This function assumes that the Segment columns are named as Segment_<column_name>.
    """
    Data_columns_name_list = [name for name, _ in adjust_segments_config]
    thresholds = np.array([thresh for _, thresh in adjust_segments_config])
    ID_columns_name_list = ["Segment_" + name for name in Data_columns_name_list]

    df = df.copy()
    ID_arr = df[ID_columns_name_list].to_numpy(dtype=np.int64)
    Data_arr = df[Data_columns_name_list].to_numpy(dtype=np.float64)

    n_rows, n_cols = ID_arr.shape
    new_ID_arr = ID_arr.copy()

    for col_idx in range(n_cols):
        ids = ID_arr[:, col_idx]
        data = Data_arr[:, col_idx]
        thresh = thresholds[col_idx]
        new_ID_arr[:, col_idx] = _merge_segments_1d_optimized(ids, data, thresh)

    for idx, col in enumerate(ID_columns_name_list):
        df[col] = new_ID_arr[:, idx]

    return df
