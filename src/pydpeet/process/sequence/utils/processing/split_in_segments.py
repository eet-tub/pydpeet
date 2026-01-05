import numpy as np
from numba import njit


@njit(cache=True)
def _assign_segments_with_fit(times, values, threshold):
    """
    Assign segment IDs to each point in a time series by incrementally fitting linear
    segments using least squares. A new segment is started when either the current
    point OR the starting point of the segment deviates from the fitted line beyond
    the threshold.

    Parameters:
    times (np.ndarray): Array of time values in seconds.
    values (np.ndarray): Array of corresponding signal values.
    threshold (float): Maximum allowed deviation from the fitted line to continue the segment.

    Returns:
    np.ndarray: Array of segment IDs assigned to each point.
    """
    n = times.shape[0]
    seg_ids = np.empty(n, dtype=np.int32)
    seg_ids[0] = 0

    start = 0
    sum_x = times[0]
    sum_y = values[0]
    sum_xx = times[0] ** 2
    sum_xy = times[0] * values[0]
    count = 1

    for i in range(1, n):
        sum_x += times[i]
        sum_y += values[i]
        sum_xx += times[i] ** 2
        sum_xy += times[i] * values[i]
        count += 1

        denom = count * sum_xx - sum_x ** 2
        if denom == 0:
            slope = 0.0
            intercept = values[start]
        else:
            slope = (count * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / count

        # Check deviation for current point and first point in segment
        expected_current = slope * times[i] + intercept
        deviation_current = abs(values[i] - expected_current)

        expected_start = slope * times[start] + intercept
        deviation_start = abs(values[start] - expected_start)

        if deviation_current <= threshold and deviation_start <= threshold:
            seg_ids[i] = seg_ids[i - 1]
        else:
            start = i
            seg_ids[i] = seg_ids[i - 1] + 1
            sum_x = times[i]
            sum_y = values[i]
            sum_xx = times[i] ** 2
            sum_xy = times[i] * values[i]
            count = 1

    return seg_ids


def _split_in_segments_using_incremental_linear_fit(df, column_name, threshold):
    """
    Detect near-linear segments in columns of a DataFrame using incremental least squares fitting.

    Parameters:
    df (pd.DataFrame): Input DataFrame with a datetime index and a numeric column.
    column_name (str): Name of the column containing the signal values.
    threshold (float): Maximum deviation allowed from the fitted line to consider a point as part of the current segment.

    Returns:
    pd.DataFrame: The original DataFrame with an added column 'Segment_<column_name>' indicating segment IDs.

    Assumes:
    Column "Testtime[s]" exists and is in seconds and a float
    """
    times = df["Testtime[s]"].to_numpy()
    values = df[column_name].to_numpy()
    seg_ids = _assign_segments_with_fit(times, values, threshold)
    df[f"Segment_{column_name}"] = seg_ids
    return df
