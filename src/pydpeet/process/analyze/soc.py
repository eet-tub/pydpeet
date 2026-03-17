import gc
import logging
from enum import Enum

import numpy as np
import pandas as pd
from numba import njit

from pydpeet.process.analyze.capacity import add_capacity
from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.analyze.utils import (
    StepTimer,
    precompute_block_arrays_soc_methods,
)


class SocMethod(Enum):
    WITHOUT_RESET = "withoutReset"
    WITH_RESET_WHEN_FULL = "withResetWhenFull"
    WITH_RESET_WHEN_EMPTY = "withResetWhenEmpty"
    WITH_RESET_WHEN_FULL_AND_EMPTY = "withResetWhenFullAndEmpty"


# Map method names to integers expected by numba function
SOC_METHOD_MAP = {
    "WITHOUT_RESET": 0,
    "WITH_RESET_WHEN_FULL": 1,
    "WITH_RESET_WHEN_EMPTY": 2,
    "WITH_RESET_WHEN_FULL_AND_EMPTY": 3,
}


# numba compiled multi-method function: compute SOC arrays for all methods in one call, writing into preallocated output
@njit(cache=True)
def _compute_soc_multi_methods_out(
    delta_soc: list[float],
    current: list[float],
    abs_current: list[float],
    voltage: list[float],
    soc_start: float,
    lower_soc: float,
    upper_soc: float,
    threshold_current: float,
    max_voltage: float,
    min_voltage: float,
    method_ints: list[int],
    socs_out: list[int, float],
    reset_buf: list[float],
) -> None:
    """
    Compute State of Charge (SOC) arrays for all methods in one call, writing into preallocated output.

    Params:
    - delta_soc (n): array of delta SOC values
    - current (n): array of current values
    - abs_current (n): array of absolute current values
    - voltage (n): array of voltage values
    - SOC_start (float): starting SOC value
    - lower_soc (float): lowerSOC value for reset
    - upper_soc (float): upperSOC value for reset
    - threshold_current (float): current threshold value for reset
    - max_voltage (float): maximum voltage value for reset
    - min_voltage (float): minimum voltage value for reset
    - method_ints (nm): array of integers representing SOC methods (0: without reset, 1: with reset when full, 2: with reset when empty, 3: with reset when full and empty)
    - socs_out (nm, n): preallocated array to writeSOC values into
    - reset_buf (n): preallocated array to store reset points
    """
    n = len(delta_soc)
    nm = len(method_ints)

    for m in range(nm):
        method_int = method_ints[m]

        # Use reset_buf as the reset_points storage (preallocated in Python)
        # initialize reset_buf to sentinel -1.0 for this method
        for ii in range(n):
            reset_buf[ii] = -1.0

        charge_sign = 1.0

        # Method flags
        is_full_method = method_int == 1 or method_int == 3
        is_empty_method = method_int == 2 or method_int == 3

        # Minimum run length for reset
        min_run_length = 3

        # detect runs for resets
        i = 0
        while i < n:
            # Skip NaN points
            if np.isnan(voltage[i]) or np.isnan(abs_current[i]):
                i += 1
                continue

            # Full-Rest Runs
            if is_full_method and (voltage[i] >= max_voltage and abs_current[i] < threshold_current):
                start = i
                while (
                    i + 1 < n
                    and not np.isnan(voltage[i + 1])
                    and not np.isnan(abs_current[i + 1])
                    and voltage[i + 1] >= max_voltage
                    and abs_current[i + 1] < threshold_current
                ):
                    i += 1
                run_length = i - start + 1
                if run_length >= min_run_length:
                    reset_buf[i] = upper_soc
                i += 1
                continue

            # Empty-Rest Runs
            if is_empty_method and (voltage[i] <= min_voltage and abs_current[i] < threshold_current):
                start = i
                while (
                    i + 1 < n
                    and not np.isnan(voltage[i + 1])
                    and not np.isnan(abs_current[i + 1])
                    and voltage[i + 1] <= min_voltage
                    and abs_current[i + 1] < threshold_current
                ):
                    i += 1
                run_length = i - start + 1
                if run_length >= min_run_length and reset_buf[i] < 0.0:
                    reset_buf[i] = lower_soc
                i += 1
                continue

            i += 1

        # Transitions: mark previous index on current direction change after limit
        for i in range(1, n):
            if np.isnan(voltage[i - 1]) or np.isnan(current[i]):
                continue
            prev_v = voltage[i - 1]
            if is_full_method and prev_v >= max_voltage and current[i] * charge_sign < 0.0:
                idx = i - 1
                if reset_buf[idx] < 0.0:
                    reset_buf[idx] = upper_soc
            if is_empty_method and prev_v <= min_voltage and current[i] * charge_sign > 0.0:
                idx = i - 1
                if reset_buf[idx] < 0.0:
                    reset_buf[idx] = lower_soc

        # accumulate SOC and write into the output row
        # start value
        # read previous value into prev variable for faster local use
        if reset_buf[0] >= 0.0:
            prev = reset_buf[0]
        else:
            prev = soc_start
        socs_out[m, 0] = prev
        first_reset = False

        for i in range(1, n):
            d = delta_soc[i]
            if np.isnan(d):
                d = 0.0
            cur = prev + d
            if reset_buf[i] >= 0.0:
                if not first_reset:
                    difference = reset_buf[i] - cur
                    # shift previous values in output row
                    for j in range(i):
                        socs_out[m, j] = socs_out[m, j] + difference
                    first_reset = True
                cur = reset_buf[i]
            socs_out[m, i] = cur
            prev = cur

    # function writes into socs_out and uses/reset_buf (both preallocated), returns None
    return


def add_soc(
    df: pd.DataFrame,
    df_primitives: pd.DataFrame,
    neware_bool: bool = True,
    standard_method: SocMethod = None,
    methods: list[SocMethod] = None,
    config: BatteryConfig = None,
    lower_soc_for_voltage: float = 0,
    upper_soc_for_voltage: float = 1,
    lower_voltage_for_soc: float = 0,
    upper_voltage_for_soc: float = 0,
    verbose: bool = True,
    restart_for_testindex: bool = True,
) -> pd.DataFrame:
    """
    Computes the Soc (State of Charge) for a battery cell, from the given dataframe. It therefore integrates the current over time,
    using the trapezoid rule. As a capacity reference value, the first calculated capacity value is used, which is updated once the
    soc reaches a point with a new calculated capacity value.

    The resulting DataFrame has additional 'SOC_<method_name>' columns.

    Parameters:
        df (pandas.DataFrame): Input DataFrame containing battery test data
        standard_method (SocMethod, optional): Standard SOC method to use if no other methods are provided
        methods (list[SocMethod], optional): List of additional SOC methods to use
        config (BatteryConfig, optional): Configuration object containing battery test parameters
        lower_soc_for_voltage (float, optional): Lower SOC value for voltage bounds (default: 0)
        upper_soc_for_voltage (float, optional): UpperSOC value for voltage bounds (default: 1)
        lower_voltage_for_soc (float, optional): Lower voltage bound for SOC computation (default: 0)
        upper_voltage_for_soc (float, optional): Upper voltage bound forSOC computation (default: 0)
        verbose (bool, optional): If True, print debug messages. Defaults to False.
        restart_for_testindex (bool, optional): If True, restart the computation if a new TestIndex block is encountered. Defaults to True.

    Returns:
        pandas.DataFrame: DataFrame with added 'SOC_<method_name>' columns
    """
    if methods is None:
        methods = [standard_method] if standard_method is not None else []
    if not methods:
        raise ValueError("No SOC methods supplied (methods or standard_method).")
    # Required columns check
    for col in ["Test_Time[s]", "Current[A]", "Voltage[V]"]:
        if col not in df.columns:
            raise ValueError(f"Column: {col} is missing! Can't proceed")

    # Add capacity if missing
    if "Capacity[Ah]" not in df.columns:
        # TODO: Assumed stack level for now
        logging.warning("Column 'Capacity[Ah]' missing, adding with function add_capacity.", stacklevel=2)
        with StepTimer(verbose) as st:
            if df_primitives is None:
                logging.info("df_primitives is None, please provide a valid df_primitives for add_capacity function")
            else:
                df = add_capacity(df, df_primitives, neware_bool, config=config, verbose=verbose)
                st.log("added Capacity[Ah] column")

    # Copy df so it can be safely modified
    df_mod = df.copy()

    # Config
    if config is None:
        raise ValueError("config must be provided")
    c_ref = config.c_ref
    soc_start = config.soc_start
    max_voltage = upper_voltage_for_soc or config.max_voltage
    min_voltage = lower_voltage_for_soc or config.min_voltage
    threshold_current = config.threshold_current
    voltage_intervall = config.voltage_intervall
    lower_soc = lower_soc_for_voltage or 0
    upper_soc = upper_soc_for_voltage or 1

    logging.info(f"Starting SOC computation on dataframe of size {len(df_mod)}...")

    # precompile numba functions to be faster with first big block
    with StepTimer(verbose) as st:
        warmup_numba()
        st.log("warmed up numba")

    logging.info("Pre-creating SOC columns...")
    # Pre-create SOC columns
    with StepTimer(verbose) as st:
        for m in methods:
            colname = "SOC_" + (m.name if hasattr(m, "name") else str(m))
            if colname not in df_mod.columns:
                df_mod[colname] = np.nan
                st.log(f"created column {colname}")

    # Helper to adjust voltages
    def _adj_voltages(max_v, min_v, intervall):
        return max_v * (1 - intervall), min_v * (1 + intervall)

    # Either process per TestIndex block or the whole df
    if "TestIndex" in df_mod.columns and restart_for_testindex:
        unique_indices = df_mod.loc[df_mod["TestIndex"] >= 0, "TestIndex"].dropna().unique()
        for idx in unique_indices:
            logging.info(f"Processing TestIndex {idx} with {df_mod['TestIndex'].eq(idx).sum()} rows...")
            block_mask = df_mod["TestIndex"] == idx
            block = df_mod.loc[block_mask]

            if block.empty:
                continue
            # ensure deterministic order for precomputation
            block_sorted = block.sort_values("Test_Time[s]")  # keep original index values

            # Precompute arrays on the sorted block
            with StepTimer(verbose) as st:
                if block_sorted["Capacity[Ah]"].notna().any():
                    capacity_values = block_sorted["Capacity[Ah]"].values.astype(np.float64)
                else:
                    # pass an array of NaNs with same length (numba-friendly)
                    capacity_values = np.full(len(block_sorted), np.nan, dtype=np.float64)

                delta_soc, current_arr, abs_current, voltage_arr, c_ref_as = precompute_block_arrays_soc_methods(
                    block_sorted["Test_Time[s]"].values,
                    block_sorted["Current[A]"].values,
                    block_sorted["Voltage[V]"].values,
                    capacity_values,
                    c_ref,
                )
                st.log("precomputed block arrays")

            # Using sorted block length for allocations (important!)
            max_voltage_adj, min_voltage_adj = _adj_voltages(max_voltage, min_voltage, voltage_intervall)
            method_ints = np.array([SOC_METHOD_MAP[m.name] for m in methods], dtype=np.int64)

            n_points = len(block_sorted)  # <<< use block_sorted, not block
            socs_matrix = np.empty((len(methods), n_points), dtype=np.float64)
            reset_buf = np.empty(n_points, dtype=np.float64)

            with StepTimer(verbose) as st:
                _compute_soc_multi_methods_out(
                    delta_soc,
                    current_arr,
                    abs_current,
                    voltage_arr,
                    soc_start,
                    lower_soc,
                    upper_soc,
                    threshold_current,
                    max_voltage_adj,
                    min_voltage_adj,
                    method_ints,
                    socs_matrix,
                    reset_buf,
                )
                st.log("computed SOC values")

            # sanity check
            assert socs_matrix.shape[1] == len(block_sorted), "SOC length mismatch vs block_sorted!"

            # Assign back using the sorted block's index so the row mapping is exact
            for idx_method, method in enumerate(methods):
                colname = "SOC_" + (method.name if hasattr(method, "name") else str(method))
                df_mod.loc[block_sorted.index, colname] = socs_matrix[idx_method]

            del socs_matrix, reset_buf
            gc.collect()

    else:
        logging.info(f"Processing whole dataframe ({len(df_mod)} rows)...")

        with StepTimer(verbose) as st:
            delta_soc, current_arr, abs_current, voltage_arr, c_ref_as = precompute_block_arrays_soc_methods(
                df_mod["Test_Time[s]"].values,
                df_mod["Current[A]"].values,
                df_mod["Voltage[V]"].values,
                df_mod["Capacity[Ah]"].values,
                c_ref,
            )
            st.log("precomputed arrays")

        max_voltage_adj, min_voltage_adj = _adj_voltages(max_voltage, min_voltage, voltage_intervall)
        method_ints = np.array([SOC_METHOD_MAP[m.name] for m in methods], dtype=np.int64)

        n_points = len(df_mod)
        socs_matrix = np.empty((len(methods), n_points), dtype=np.float64)
        reset_buf = np.empty(n_points, dtype=np.float64)

        with StepTimer(verbose) as st:
            _compute_soc_multi_methods_out(
                delta_soc,
                current_arr,
                abs_current,
                voltage_arr,
                soc_start,
                lower_soc,
                upper_soc,
                threshold_current,
                max_voltage_adj,
                min_voltage_adj,
                method_ints,
                socs_matrix,
                reset_buf,
            )
            st.log("computed SOC values")

        for idx_method, method in enumerate(methods):
            colname = "SOC_" + (method.name if hasattr(method, "name") else str(method))
            df_mod[colname] = socs_matrix[idx_method]

        del socs_matrix, reset_buf
        gc.collect()

    # Rename standard SOC column
    if standard_method is not None:
        std_name = standard_method.name if hasattr(standard_method, "name") else str(standard_method)
        if "SOC_" + std_name in df_mod.columns:
            # overwrite existing "SOC" if present, avoiding duplicate column labels
            df_mod["SOC"] = df_mod.pop("SOC_" + std_name)

    return df_mod


def warmup_numba():
    """
    Warm up numba by calling the expensive functions with dummy data.

    This ensures that subsequent calls to these functions are faster.
    """
    n = 10
    t = np.zeros(n, dtype=np.float64)
    c = np.zeros(n, dtype=np.float64)
    v = np.zeros(n, dtype=np.float64)
    cap = np.ones(n, dtype=np.float64)
    precompute_block_arrays_soc_methods(t, c, v, cap, 1.0)
    dummy_methods = np.array([0], dtype=np.int64)
    socs_out = np.zeros((1, n), dtype=np.float64)
    reset_buf = np.zeros(n, dtype=np.float64)
    _compute_soc_multi_methods_out(
        np.zeros(n),
        np.zeros(n),
        np.zeros(n),
        np.zeros(n),
        0.0,
        0.0,
        1.0,
        0.01,
        4.2,
        3.0,
        dummy_methods,
        socs_out,
        reset_buf,
    )
