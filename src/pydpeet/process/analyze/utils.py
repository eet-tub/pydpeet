import gc
import logging
import os
import re
import time
from enum import Enum

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numba import njit


class StepTimer:
    """Helper to log elapsed time for sub-steps inside a method."""
    def __init__(self, verbose=True, indent="    "):
        self.verbose = verbose
        self.indent = indent
        self.start = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def log(self, msg: str):
        if self.verbose:
            elapsed = time.perf_counter() - self.start
            logging.info(f"{self.indent}{elapsed:0.4f}s {msg}")


def _check_columns(df, required_columns):
    """Checks if the required columns are present in the DataFrame, allowing for 'Segment_' prefixes."""
    columns = set(df.columns)
    mapped_columns = {col.replace("Segment_", "") for col in columns}

    missing_columns = [col for col in required_columns if col not in columns and col not in mapped_columns]
    if missing_columns:
        raise KeyError(f"The following required columns are missing: {', '.join(missing_columns)}")



# Precompute arrays that are independent of chosen SOC reset method

@njit(cache=True)
def precompute_block_arrays_soc_methods(time, current, voltage, capacity_values, c_ref):
    """
    Numba-optimized version of precompute_block_arrays_soc_methods.
    Returns: (delta_soc, current_arr, abs_current, voltage_arr, c_ref_as)
    """
    n = len(time)

    # Ensure arrays are float64 contiguous
    delta_t = np.zeros(n, dtype=np.float64)
    if n > 1:
        for i in range(1, n):
            if np.isnan(time[i]) or np.isnan(time[i-1]):
                delta_t[i] = 0.0
            else:
                delta_t[i] = time[i] - time[i-1]

    # delta_Q = current * delta_t
    delta_Q = np.zeros(n, dtype=np.float64)
    for i in range(n):
        if np.isnan(current[i]):
            delta_Q[i] = 0.0
        else:
            delta_Q[i] = current[i] * delta_t[i]

    # c_ref_as forward-fill
    c_ref_as = np.empty(n, dtype=np.float64)
    local = c_ref if c_ref is not None else 1e-9
    for i in range(n):
        value = capacity_values[i]
        if not np.isnan(value):
            local = value
        if local <= 0.0 or np.isnan(local):
            local = 1e-9
        c_ref_as[i] = local * 3600.0  # convert Ah → As

    # delta_soc = delta_Q / c_ref_as
    delta_soc = np.zeros(n, dtype=np.float64)
    for i in range(n):
        if c_ref_as[i] != 0.0:
            delta_soc[i] = delta_Q[i] / c_ref_as[i]
        else:
            delta_soc[i] = 0.0

    # abs_current
    abs_current = np.empty(n, dtype=np.float64)
    for i in range(n):
        ci = current[i]
        if np.isnan(ci):
            abs_current[i] = 0.0
        else:
            abs_current[i] = ci if ci >= 0.0 else -ci

    # voltage_arr
    voltage_arr = np.empty(n, dtype=np.float64)
    for i in range(n):
        voltage_arr[i] = voltage[i] if not np.isnan(voltage[i]) else 0.0

    return delta_soc, current, abs_current, voltage_arr, c_ref_as

def drop_duplicate_testtime(df, keep="first"):
    """
    Drop duplicate rows based on Testtime[s].
    keep='first' keeps the first occurrence,
    keep='last' keeps the last,
    keep=False removes all duplicates entirely.
    """
    if "Testtime[s]" not in df.columns:
        raise ValueError("No 'Testtime[s]' column in DataFrame")

    n_before = len(df)
    df_clean = df.drop_duplicates(subset=["Testtime[s]"], keep=keep).copy()
    n_after = len(df_clean)

    logging.warning(f"Dropped {n_before - n_after} duplicate rows (kept={keep}).")

    return df_clean.sort_values("Testtime[s]").reset_index(drop=True)