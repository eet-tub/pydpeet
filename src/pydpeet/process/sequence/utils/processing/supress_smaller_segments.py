import numpy as np
from numba import njit


@njit(cache=True)
def _compute_segment_lengths_numba(segment_ids, times, max_id):
    """
    Compute the length (time) of each segment in the given DataFrame.

    Parameters:
        segment_ids (np.ndarray): Array of segment IDs.
        times (np.ndarray): Array of corresponding times.
        max_id (int): Maximum segment ID.

    Returns:
        np.ndarray: Array of segment durations.

    """
    first_time = np.full(max_id + 1, -1.0)
    last_time = np.full(max_id + 1, -1.0)

    n = len(segment_ids)
    for i in range(n):
        seg_id = segment_ids[i]
        t = times[i]
        if seg_id == -1:
            continue
        if first_time[seg_id] == -1.0:
            first_time[seg_id] = t
        last_time[seg_id] = t

    durations = last_time - first_time

    result = np.full(n, 0.0)
    valid = segment_ids != -1
    result[valid] = durations[segment_ids[valid]]
    return result


def _add_segment_lengths(df, column_name):
    """
    Compute the length (time) of each segment in the given DataFrame.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing 'Testtime[s]' and 'Segment_<column_name>' columns.
        column_name (str): Name of the column containing the signal values.

    Returns:
        pd.DataFrame: Modified DataFrame with an added column 'Length_Segment_<column_name>' containing segment durations.
    """
    segment_name = f"Segment_{column_name}"
    segment_ids = df[segment_name].to_numpy(dtype=np.int32)
    times = df["Test_Time[s]"].to_numpy(dtype=np.float64)

    max_id = segment_ids.max()
    durations = _compute_segment_lengths_numba(segment_ids, times, max_id)

    df[f"Length_{segment_name}"] = durations
    return df


def _keep_max_segment_id(df, keep_max_segment_id_config):
    """
    For each row in the DataFrame, retain the segment ID in the Segment column that has the
    maximum associated length. Set all other segment IDs to -1.

    Parameters:
    df (pd.DataFrame): The input DataFrame.
    length_segment_pairs (list of tuples): List of (length_column, segment_column) pairs.

    Returns:
    pd.DataFrame: Modified DataFrame with updated Segment columns.
    """
    # Extract the length columns into a NumPy array for fast comparison
    length_data = np.stack([df[length_col].values for length_col, _ in keep_max_segment_id_config], axis=1)

    # Determine the index of the max length column per row
    max_indices = np.argmax(length_data, axis=1)

    # Set all segment columns to -1 where not the max, retain value otherwise
    for i, (length_col, segment_col) in enumerate(keep_max_segment_id_config):
        segment_data = df[segment_col].values.copy()
        segment_data[max_indices != i] = -1
        df[segment_col] = segment_data

    return df
