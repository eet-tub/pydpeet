import numpy as np
import pandas as pd
from numba import njit

from pydpeet.process.sequence.utils.console_prints.log_time import log_time


def _annotate_primitives(
    df: pd.DataFrame,
    data_columns: dict[str, str],
    thresholds: dict[str, float],
    show_runtime: bool = False,
) -> pd.DataFrame:
    """
    Annotates the primitives in the dataframe with ID, variable, duration, length, min, max, avg, type, direction, slope.

    Parameters:
    df (pd.DataFrame):Dataframe containing the primitives
    data_columns (dict[str, str]): Mapping of column names to their respective short names
    thresholds (dict[str, float]) : Threshold values for each type of annotation
    show_runtime (bool) : Whether to show the runtime of this function, by default False

    Returns
    -------
    df (pd.DataFrame): Dataframe with added columns for annotated primitives
    """
    df = _annotate_id(df, data_columns, show_runtime)
    df = _annotate_variable(df, data_columns, show_runtime)
    with log_time("adding duration, length, min, max, avg, type, direction, slope annotation", show_runtime):
        df = _merged_annotations(df, data_columns, thresholds)

    return df


@njit(cache=True)
def _compute_segment_id(ID_arrays) -> np.array:
    """
    Compute segment ID array using the ID arrays.

    Parameters:
    ID_arrays (numpy.ndarray): input arrays to compute segment ID
        Example: ID_arrays = np.array([[-1, -1, 1], [-1, -1, 1], [3, -1, -1], [-1, 10, -1]])

    Returns:
    segment_id (numpy.ndarray): segment ID array with the same shape as the input array
        Example: segment_id = np.array([1, 1, 2, 3])

    Notes:
    - The segment ID is computed by checking if each row differs from the previous row.
    - If all columns in a row are -1, the segment ID for that row is -1.
    - The segment ID is incremented for each row that differs from the previous row.
    """
    n_rows, n_cols = ID_arrays.shape
    segment_id = np.empty(n_rows, dtype=np.int64)
    segment_id[:] = -1  # default -1

    # Check mask_all_minus1 per row: all columns == -1
    mask_all_minus1 = np.ones(n_rows, dtype=np.bool_)
    for i in range(n_rows):
        for j in range(n_cols):
            if ID_arrays[i, j] != -1:
                mask_all_minus1[i] = False
                break

    # Initialize segment counter and track previous row
    segment_counter = 0
    segment_id[0] = segment_counter if not mask_all_minus1[0] else -1

    for i in range(1, n_rows):
        if mask_all_minus1[i]:
            segment_id[i] = -1
        else:
            # Check if row differs from previous row
            changed = False
            for j in range(n_cols):
                if ID_arrays[i, j] != ID_arrays[i - 1, j]:
                    changed = True
                    break
            if changed:
                segment_counter += 1
            segment_id[i] = segment_counter

    return segment_id


def _annotate_id(
    df: pd.DataFrame,
    data_columns: dict[str, str],
    show_runtime: bool,
) -> pd.DataFrame:
    """
    Adds a column 'ID' to the dataframe df based on the values of the columns specified in data_columns.

    The 'ID' column is computed by checking if each row differs from the previous row.
    If all columns in a row are -1, the 'ID' for that row is -1.
    The 'ID' is incremented for each row that differs from the previous row.

    Parameters:
    df (pd.DataFrame): Input dataframe.
    data_columns (dict[str, str]): Mapping of column names to their respective short names.
        Example: data_columns = {"I": "Current", "P": "Power", "V": "Voltage"}
    show_runtime (bool): Whether to show the runtime of this function, by default False.

    Returns:
    pd.DataFrame: The original dataframe with an added column named 'ID'.
    """
    with log_time("adding ID annotation", show_runtime):
        cols = [f"Segment_{v}" for v in data_columns.values()]
        arr = df[cols].to_numpy()
        segment_id = _compute_segment_id(arr)
        df["ID"] = segment_id

    return df


def _annotate_variable(
    df: pd.DataFrame,
    data_columns: dict[str, str],
    show_runtime: bool,
) -> pd.DataFrame:
    """
    Adds a column 'Variable' to the dataframe df based on the values of the columns specified in data_columns.

    Parameters:
    df (pd.DataFrame): Input dataframe.
    data_columns (dict[str, str]): Mapping of column names to their respective short names.
        Example: data_columns = {"I": "Current", "P": "Power", "V": "Voltage"}
    show_runtime (bool): Whether to show the runtime of this function, by default False.

    Returns:
    pd.DataFrame: The original dataframe with an added column named 'Variable'.
    """
    with log_time("adding variable annotation", show_runtime):
        cols = [f"Segment_{v}" for v in data_columns.values()]
        short_names = list(data_columns.keys())
        data = df[cols].to_numpy()
        variable_array = np.full(len(df), None, dtype=object)
        for i, name in enumerate(short_names):
            mask = (data[:, i] != -1) & (variable_array == np.array(None))
            variable_array[mask] = name
        df["Variable"] = variable_array

    return df


@njit(cache=True)
def _merged_annotations_njit(
    group_of_row: np.array,
    group_var_vals: np.array,
    values_matrix: np.array,
    testtime_s: np.array,
    current_mean_per_group: np.array,
    thresholds_array: np.array,
) -> tuple[np.array, np.array, np.array, np.array, np.array, np.array, np.array]:
    """
    Compute the following annotations for each row in the input dataframe:
    - min value
    - max value
    - average value
    - slope
    - length (time range)
    - type (Rest, Constant, Ramp)
    - direction (Neutral, Charge, Discharge, Up, Down)

    Parameters:
    group_of_row (numpy.array): An array of length n, where each element is the group ID of the corresponding row.
    group_var_vals (numpy.array): An array of length G, where each element is the variable index of the corresponding group.
    values_matrix (numpy.array): A matrix of shape (n, num_vars), where each row is a set of measurements for the corresponding row in the input dataframe.
    testtime_s (numpy.array): An array of length n, where each element is the test time for the corresponding row.
    current_mean_per_group (numpy.array): An array of length G, where each element is the current mean of the corresponding group.
    thresholds_array (numpy.array): An array of length num_vars, where each element is the threshold value for the corresponding variable.

    Returns:
    min_vals (numpy.array): An array of length n, where each element is the minimum value of the corresponding row of the Variable.
    max_vals (numpy.array): An array of length n, where each element is the maximum value of the corresponding row of the Variable.
    avg_vals (numpy.array): An array of length n, where each element is the average value of the corresponding row of the Variable.
    slope_vals (numpy.array): An array of length n, where each element is the slope of the corresponding row of the Variable.
    length_vals (numpy.array): An array of length n, where each element is the length (time range) of the corresponding row of the Variable.
    type_codes (numpy.array): An array of length n, where each element is the type code of the corresponding row of the Variable.
    dir_codes (numpy.array): An array of length n, where each element is the direction code of the corresponding row of the Variable.
    """
    n = group_of_row.shape[0]
    G = group_var_vals.shape[0]

    # Group accumulators (typed, fixed-size)
    group_count = np.zeros(G, dtype=np.int64)
    group_sum = np.zeros(G, dtype=np.float64)
    group_min = np.full(G, np.nan, dtype=np.float64)
    group_max = np.full(G, np.nan, dtype=np.float64)
    first_val = np.full(G, np.nan, dtype=np.float64)
    last_val = np.full(G, np.nan, dtype=np.float64)
    init_flag = np.zeros(G, dtype=np.int8)  # initialization flag
    time_min = np.full(G, np.nan, dtype=np.float64)
    time_max = np.full(G, np.nan, dtype=np.float64)

    for i in range(n):
        gid = group_of_row[i]
        if gid == -1:
            continue
        var_idx = group_var_vals[gid]
        val = values_matrix[i, var_idx]
        t = testtime_s[i]

        if init_flag[gid] == 0:
            # initialize group (first encountered row for this group)
            first_val[gid] = val
            last_val[gid] = val
            group_min[gid] = val
            group_max[gid] = val
            if not np.isnan(val):
                group_sum[gid] = val
                group_count[gid] = 1
            else:
                group_sum[gid] = 0.0
                group_count[gid] = 0
            time_min[gid] = t
            time_max[gid] = t
            init_flag[gid] = 1
        else:
            # update last (df order)
            last_val[gid] = val
            # update min/max/sum/count only for non-nan values
            if not np.isnan(val):
                if np.isnan(group_min[gid]) or val < group_min[gid]:
                    group_min[gid] = val
                if np.isnan(group_max[gid]) or val > group_max[gid]:
                    group_max[gid] = val
                group_sum[gid] += val
                group_count[gid] += 1
            # update time range
            if t < time_min[gid]:
                time_min[gid] = t
            if t > time_max[gid]:
                time_max[gid] = t

    min_vals = np.full(n, np.nan, dtype=np.float64)
    max_vals = np.full(n, np.nan, dtype=np.float64)
    avg_vals = np.full(n, np.nan, dtype=np.float64)
    slope_vals = np.full(n, np.nan, dtype=np.float64)
    length_vals = np.full(n, np.nan, dtype=np.float64)
    type_codes = np.full(n, -1, dtype=np.int64)  # -1=None, 0=Rest,1=Constant,2=Ramp
    dir_codes = np.full(n, -1, dtype=np.int64)  # -1=None, 0=Neutral,1=Charge,2=Discharge,3=Up,4=Down

    for i in range(n):
        gid = group_of_row[i]
        if gid == -1:
            continue

        vmin = group_min[gid]
        vmax = group_max[gid]
        cnt = group_count[gid]
        s = group_sum[gid]
        first = first_val[gid]
        last = last_val[gid]
        tmn = time_min[gid]
        tmx = time_max[gid]

        # avg
        if cnt > 0:
            avg = s / cnt
        else:
            avg = np.nan

        # length (time range) using np.isnan checks
        if np.isnan(tmn) or np.isnan(tmx):
            length_val = np.nan
        else:
            length_val = tmx - tmn

        # slope — denom = max(cnt - 1, 1)
        denom = cnt - 1
        if denom < 1:
            denom = 1
        slope_val = (last - first) / denom

        # Type & Direction
        thr = thresholds_array[group_var_vals[gid]]
        curr_mean = current_mean_per_group[gid] if gid < current_mean_per_group.shape[0] else 0.0

        if cnt == 0 or np.isnan(vmin) or np.isnan(vmax):
            type_code = -1
            dir_code = -1
        else:
            diff = vmax - vmin
            if diff <= thr and abs(curr_mean) <= thr:
                type_code = 0  # Rest
                dir_code = 0  # Neutral
            elif diff <= thr:
                type_code = 1  # Constant
                dir_code = 1 if curr_mean >= 0 else 2  # Charge / Discharge
            else:
                type_code = 2  # Ramp
                dir_code = 3 if last > first else 4  # Up / Down

        min_vals[i] = vmin
        max_vals[i] = vmax
        avg_vals[i] = avg
        slope_vals[i] = slope_val
        length_vals[i] = length_val
        type_codes[i] = type_code
        dir_codes[i] = dir_code

    return min_vals, max_vals, avg_vals, slope_vals, length_vals, type_codes, dir_codes


def _merged_annotations(
    df: pd.DataFrame,
    data_columns: dict[str, str],
    thresholds: dict[str, float],
) -> pd.DataFrame:
    # map variable names to integer var indices
    """
    Compute duration, length, min, max, avg, type, direction, slope for each group of (ID, Variable).

    Parameters:
    df (pd.DataFrame): DataFrame containing the primitives
    data_columns (dict[str, str]): Mapping of column names to their respective short names
    thresholds (dict[str, float]): Threshold values for each type of annotation

    Returns:
    pd.DataFrame: Dataframe with added columns for annotated primitives
    """
    var_names = list(data_columns.keys())
    num_vars = len(var_names)
    var_map = {name: idx for idx, name in enumerate(var_names)}

    n = len(df)
    ids = df["ID"].to_numpy(np.int64)

    # map variables column (strings) to integer indices (-1 if not in var_map)
    # use pandas.map for speed & clarity
    variables = df["Variable"].map(lambda x: var_map.get(x, -1)).to_numpy(np.int64)

    # Build values_matrix (n x num_vars) where column j is the measurement for var j
    values_matrix = np.full((n, num_vars), np.nan, dtype=np.float64)
    for var_name, col_name in data_columns.items():
        var_idx = var_map[var_name]
        values_matrix[:, var_idx] = df[col_name].to_numpy(np.float64)

    testtime_s = df["Test_Time[s]"].to_numpy(np.float64)
    current_a = df["Current[A]"].to_numpy(np.float64)

    # Compute duration per row: count of rows per ID (original annotate_duration_length)
    duration = np.zeros(n, dtype=np.float64)
    valid_mask = ids != -1
    if np.any(valid_mask):
        ids_valid = ids[valid_mask]
        unique_ids, inv_ids = np.unique(ids_valid, return_inverse=True)
        counts_per_id = np.bincount(inv_ids)
        duration_valid = counts_per_id[inv_ids]
        duration[valid_mask] = duration_valid

        # current_mean per ID (global, used by Type/Direction logic)
        sums_per_id = np.bincount(inv_ids, weights=current_a[valid_mask])
        mean_current_per_id = sums_per_id / counts_per_id
    else:
        unique_ids = np.array([], dtype=np.int64)
        mean_current_per_id = np.array([], dtype=np.float64)

    # Build groups for (ID, Variable) only for valid rows
    K = num_vars + 1
    mask_valid_var_and_id = (ids != -1) & (variables != -1)
    if np.any(mask_valid_var_and_id):
        keys_valid = ids[mask_valid_var_and_id].astype(np.int64) * K + variables[mask_valid_var_and_id]
        unique_keys, inv_keys = np.unique(keys_valid, return_inverse=True)
        # group_id_vals and group_var_vals
        group_id_vals = unique_keys // K
        group_var_vals = unique_keys % K

        # group_of_row: map each row to group index (or -1)
        group_of_row = np.full(n, -1, dtype=np.int64)
        group_of_row[mask_valid_var_and_id] = inv_keys

        # map group_id_vals to positions in unique_ids (unique_ids sorted)
        group_id_pos = np.searchsorted(unique_ids, group_id_vals)
        current_mean_per_group = mean_current_per_id[group_id_pos]
    else:
        group_of_row = np.full(n, -1, dtype=np.int64)
        group_var_vals = np.zeros(0, dtype=np.int64)
        current_mean_per_group = np.zeros(0, dtype=np.float64)

    # thresholds array by var index
    thresholds_array = np.zeros(num_vars, dtype=np.float64)
    for var_name, thr in thresholds.items():
        if var_name in var_map:
            thresholds_array[var_map[var_name]] = thr

    # Call Numba worker
    min_vals, max_vals, avg_vals, slope_vals, length_vals, type_codes, dir_codes = _merged_annotations_njit(
        group_of_row,
        group_var_vals,
        values_matrix,
        testtime_s,
        current_mean_per_group,
        thresholds_array,
    )

    # Map type & direction codes to strings (or None)
    type_map = np.array(["Rest", "Constant", "Ramp"], dtype=object)
    dir_map = np.array(["Neutral", "Charge", "Discharge", "Up", "Down"], dtype=object)

    type_col = np.empty(n, dtype=object)
    dir_col = np.empty(n, dtype=object)
    for i in range(n):
        tc = type_codes[i]
        dc = dir_codes[i]
        type_col[i] = None if tc == -1 else type_map[tc]
        dir_col[i] = None if dc == -1 else dir_map[dc]

    df["Duration"] = duration
    df["Length"] = length_vals
    df["Min"] = min_vals
    df["Max"] = max_vals
    df["Avg"] = avg_vals
    df["Type"] = type_col
    df["Direction"] = dir_col
    df["Slope"] = slope_vals

    return df
