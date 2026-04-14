import logging

import numpy as np
import pandas as pd
from numba import njit

from pydpeet.process.sequence.utils.console_prints.log_time import log_time
from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction


@njit(cache=True)
def _find_zero_segments(
    times: np.ndarray,
    currents: np.ndarray,
    tolerance: float,
) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Find segments where the absolute value of the current is less than or equal to the given tolerance.

    Parameters:
        times (np.ndarray): Array of timestamps.
        currents (np.ndarray): Array of current values.
        tolerance (float): Maximum absolute value of the current. [-tol,tol] is accepted

    Returns:
        list: List of tuples of start and end times for each zero segment.
    """
    n = len(currents)
    mask = (~np.isnan(currents)) & (np.abs(currents) <= tolerance)

    zero_segments = []
    in_seg = False
    start_idx = 0

    for i in range(n):
        if mask[i]:
            if not in_seg:
                start_idx = i
                in_seg = True
        else:
            if in_seg:
                zero_segments.append((times[start_idx], times[i - 1]))
                in_seg = False

    if in_seg:  # ended inside a segment
        zero_segments.append((times[start_idx], times[n - 1]))

    return zero_segments


@njit(cache=True)
def _get_id_tol_range(
    times: np.ndarray,
    currents: np.ndarray,
    tolerance: float,
) -> tuple[float, float]:
    """
    Return (tmin, tmax) where tmin and tmax are the minimum and maximum times, respectively,
    where the absolute value of the current is less than or equal to the given tolerance.

    Parameters:
        times (np.ndarray): Array of timestamps.
        currents (np.ndarray): Array of current values.
        tolerance (float): Maximum absolute value of the current. [-tol,tol] is accepted

    Returns:
        tuple: (tmin, tmax)
    """
    n = len(currents)
    found = False
    tmin = 0.0
    tmax = 0.0

    for i in range(n):
        if np.abs(currents[i]) <= tolerance and not np.isnan(currents[i]):
            if not found:
                tmin = times[i]
                tmax = times[i]
                found = True
            else:
                if times[i] < tmin:
                    tmin = times[i]
                if times[i] > tmax:
                    tmax = times[i]

    if not found:
        return np.nan, np.nan

    return tmin, tmax


@njit(cache=True)
def _compute_new_ids(ids) -> np.ndarray:
    """
    Compute a new array of IDs based on the input array to have contiguous IDs
    after inserting the falsely suppressed CC segment back in.

    Parameters:
        ids (np.ndarray): Input array of IDs.

    Returns:
        np.ndarray: New array of IDs.
    """
    n = len(ids)
    new_ids = np.ones(n, dtype=np.int64)
    for i in range(1, n):
        if ids[i] > ids[i - 1]:
            new_ids[i] = new_ids[i - 1] + 1
        elif ids[i] == -2 and ids[i - 1] != -2:
            new_ids[i] = new_ids[i - 1] + 1
        else:
            new_ids[i] = new_ids[i - 1]
    return new_ids


def _check_CV_0Aend_segments(
    df_primitives: pd.DataFrame,
    tolerance: float,
    SHOW_RUNTIME: bool,
    DATA_COLUMNS: dict[str, str],
    THRESHOLDS_PRIMITIVE_ANNOTATION: dict[str, float],
    supress_IO_warnings: bool,
    THRESHOLD_CONSOLE_PRINTS_CV_CHECK: int,
    THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK: int,
) -> pd.DataFrame:
    """
    Check CV Segments that end with 0A to identify and correct falsely suppressed CC segment at the end,
    that happen due to the slow sloping of the CV.

    Parameters:
    df_primitives (pd.DataFrame): DataFrame containing the primitives
    tolerance (float): maximum absolute value of current that is allowed in the CV segment
    SHOW_RUNTIME (bool): whether to print runtime information
    DATA_COLUMNS (dict): dictionary of column names to be kept in the DataFrame
        Example: {"I": "Current", "P": "Power", "V": "Voltage"}
    THRESHOLDS_PRIMITIVE_ANNOTATION (dict): dictionary of threshold values for primitive annotation
        Example: {"I": 0.1, "P": 0.1, "V": 0.1}
    supress_IO_warnings (bool): whether to suppress runtime warnings
    THRESHOLD_CONSOLE_PRINTS_CV_CHECK (int): threshold for the number of corrected segments to print
    THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK (int): threshold for the number of segments to print

    Returns:
    pd.DataFrame: Dataframe with added columns for annotated primitives
    """

    with log_time("checking CV Segments that end with 0A", SHOW_RUNTIME=SHOW_RUNTIME):
        # convert once to numpy
        times = df_primitives["Test_Time[s]"].to_numpy(np.float64)
        currents = df_primitives["Current[A]"].to_numpy(np.float64)

        # 1) compute global zero-current segments
        zero_segments = _find_zero_segments(times, currents, tolerance)

        # 2) get last entry per ID, restricted to Variable=='V' and ~0 current
        last_entries = df_primitives.groupby("ID", sort=False).tail(1)
        mask_V = last_entries["Variable"].to_numpy() == "V"
        mask_tol = np.abs(last_entries["Current[A]"].to_numpy(np.float64)) <= tolerance
        candidate_ids = last_entries.loc[mask_V & mask_tol, "ID"].to_numpy()

        expanded_ranges = {}

        # 3) process each candidate ID with numba-accelerated range finder
        for id_val in candidate_ids:
            sub = df_primitives[df_primitives["ID"] == id_val]
            sub_times = sub["Test_Time[s]"].to_numpy(np.float64)
            sub_currents = sub["Current[A]"].to_numpy(np.float64)

            seg_min, seg_max = _get_id_tol_range(sub_times, sub_currents, tolerance)
            if np.isnan(seg_min):
                continue

            # expand by global zero_segments
            for zero_segments_start, zero_segments_end in zero_segments:
                if zero_segments_end >= seg_min and zero_segments_start <= seg_max:  # overlap
                    seg_min = min(seg_min, zero_segments_start)
                    seg_max = max(seg_max, zero_segments_end)

            expanded_ranges[id_val] = (float(seg_min), float(seg_max))

    with log_time("correcting CV Segments that end with 0A", SHOW_RUNTIME=SHOW_RUNTIME):
        correction_config = {
            "replace_time_and_merge": {(start, end): "I" for _, (start, end) in expanded_ranges.items()},
        }
        starts = np.array([s for s, e in expanded_ranges.values()])
        ends = np.array([e for s, e in expanded_ranges.values()])
        times = df_primitives["Test_Time[s]"].to_numpy(np.float64)

        # single mask: True if time is inside any (start, end)
        mask = np.zeros(len(times), dtype=bool)
        for s, e in zip(starts, ends, strict=False):
            mask |= (times >= s) & (times <= e)

        df_CV_0Aend_segments = df_primitives.loc[mask]

        if not df_CV_0Aend_segments.empty:
            df_CV_0Aend_segments = df_primitives_correction(
                df_primitives=df_CV_0Aend_segments,
                correction_config=correction_config,
                data_columns=DATA_COLUMNS,
                thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION,
                reindex=False,
                reannotate=False,
            )

            # Update df_primitives with df_CV_0Aend_segments
            df_CV_0Aend_segments["ID"] = -2
            cols_to_update = ["ID", "Variable", "Duration", "Length", "Min", "Max", "Avg", "Type", "Direction", "Slope"]
            df_primitives.loc[df_CV_0Aend_segments.index, cols_to_update] = df_CV_0Aend_segments[cols_to_update]

        # Extract as numpy arrays
        ids = df_primitives["ID"].to_numpy(dtype=np.int64)

        # Run with numba
        df_primitives["ID"] = _compute_new_ids(ids)

        if not supress_IO_warnings:
            if expanded_ranges:
                logging.warning("Suspicious Voltage Segments that end with Current[A] = 0.0 found.")
            if THRESHOLD_CONSOLE_PRINTS_CV_CHECK:
                expanded_ranges_items = list(expanded_ranges.items())
                if len(expanded_ranges_items) > THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK:
                    preview = expanded_ranges_items[:THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK]
                    logging.warning(f"Turned into CC segments: {preview}, ...")
                else:
                    logging.warning(f"Turned into CC segments: {expanded_ranges_items}")

    return df_primitives
