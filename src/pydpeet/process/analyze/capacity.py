import inspect
import logging

import numpy as np
import pandas as pd
from scipy import integrate

from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.analyze.configs.step_analyzer_config import SEGMENT_SEQUENCE_CONFIG
from pydpeet.process.analyze.utils import (
    StepTimer,
    _check_columns,
)
from pydpeet.process.sequence.step_analyzer import extract_sequence_overview
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
from pydpeet.utils.guardrails import _guardrail_dataframe


def add_capacity(
    df: pd.DataFrame,
    df_primitives: pd.DataFrame,
    config: BatteryConfig = None,
    neware_bool: bool = True,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Compute the capacity of a battery cell from its discharge data.

    The capacity computation is a multistep process. First, the discharge blocks
    are filtered from the data. Then, the blocks with a full discharge (from max to min)
    are searched. For each of these blocks, the cumulative capacity is computed by
    integrating the absolute current over time.

    The resulting DataFrame has an additional 'Capacity[Ah]' column.

    Parameters:
        df (pandas.DataFrame): Input DataFrame containing battery test data
        df_primitives (pandas.DataFrame): Input DataFrame containing primitive segments
        neware_bool (bool, optional): If True, use Neware-specific filtering rules. Defaults to True.
        config (BatteryConfig, optional): Configuration object containing battery test parameters
        verbose (bool, optional): If True, print debug messages. Defaults to False.

    Returns:
        pandas.DataFrame: DataFrame with added 'Capacity[Ah]' column
    """
    required_columns_df = ["Voltage[V]", "Current[A]", "Test_Time[s]"]
    required_column_dtypes_df = [("Voltage[V]", float), ("Current[A]", float), ("Test_Time[s]", float)]
    required_columns_df_primitives = ["PLACEHOLDER", "PLACEHOLDER", "PLACEHOLDER"]
    required_column_dtypes_df_primitives = [("PLACEHOLDER", float), ("PLACEHOLDER", float), ("PLACEHOLDER", float)]
    _guardrail_dataframe(
        df,
        hard_fail_missing_required_columns=(True, required_columns_df),
        hard_fail_wrong_column_dtypes=(True, required_column_dtypes_df),
        hard_fail_inf_values=(False, required_columns_df),
        hard_fail_nan_values=(False, required_columns_df),
        hard_fail_none_values=(False, required_columns_df)
    )
    #TODO
    # _guardrail_dataframe(
    #     df_primitives,
    #     hard_fail_missing_required_columns=(True, required_columns_df_primitives),
    #     hard_fail_wrong_column_dtypes=(True, required_column_dtypes_df_primitives),
    #     hard_fail_inf_values=(False, required_columns_df_primitives),
    #     hard_fail_nan_values=(False, required_columns_df_primitives),
    #     hard_fail_none_values=(False, required_columns_df_primitives)
    # )

    if config is None:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}!")

    minimal_current = config.minimal_current_for_capacity
    maximal_current = config.maximal_current_for_capacity

    df_mod = df.copy()
    max_voltage = config.max_voltage
    min_voltage = config.min_voltage
    voltage_intervall = config.voltage_intervall

    logging.info(f"Starting capacity computation on dataframe of size {len(df_mod)}...")

    # Step 2: Segments and sequences
    with StepTimer(verbose) as st:
        df_segments_and_sequences = extract_sequence_overview(
            df_primitives, SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG
        )
        st.log("computed segments and sequences")

    if neware_bool:
        # Step 3: Filter discharge blocks
        rules = [
            "CC_Discharge_after_CC_Charge",
            "CC_Discharge_after_CCCV_Charge",
            "CC_Discharge_after_CV_Charge",
            "CC_Discharge_after_CCCV_Charge_with_Pause",
            "CC_Discharge_after_CC_Charge_with_Pause",
            "CC_Discharge_after_CV_Charge_with_Pause",
        ]
        with StepTimer(verbose) as st:
            dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
                df_segments_and_sequences=df_segments_and_sequences,
                df_primitives=df_primitives,
                rules=rules,
                combine_op="or",
                also_return_filtered_df=True,
            )
            st.log("filtered initial discharge blocks")

    rules = ["CC_Discharge"]
    with StepTimer(verbose) as st:
        dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
            df_segments_and_sequences=df_segments_and_sequences,
            df_primitives=df_primitives,
            rules=rules,
            combine_op="or",
            also_return_filtered_df=True,
        )
        st.log("filtered CC_Discharge blocks")

    discharge_dfs = []
    # search for the blocks with a full discharge (from max to min)
    for i, block in enumerate(dfs_per_block):
        avg_current = block["Current[A]"].mean()
        voltage_range = (block["Voltage[V]"].max(), block["Voltage[V]"].min())

        if not (minimal_current < avg_current < maximal_current) or not (
            voltage_range[0] >= max_voltage * (1 - voltage_intervall)
            and voltage_range[1] <= min_voltage * (1 + voltage_intervall)
        ):
            continue

        block = block.copy()
        time_diff = block["Test_Time[s]"].diff() / 3600
        block["Capacity[Ah]"] = (block["Current[A]"] * time_diff).cumsum()

        if len(block) > 0:
            time_seconds = block["Test_Time[s]"].values
            current = block["Current[A]"].values
            with StepTimer(verbose) as st:
                capacity_ah = integrate.cumulative_trapezoid(abs(current), time_seconds, initial=0) / 3600
                st.log(f"computed cumulative capacity for block {i}")
            block["Capacity[Ah]"] = float("NaN")
            block.loc[block.index[-1], "Capacity[Ah]"] = capacity_ah[-1]

        discharge_dfs.append(block)

    if len(discharge_dfs) > 0:
        for block in discharge_dfs:
            df_mod.loc[block.index[0] : block.index[-1], "Capacity[Ah]"] = block["Capacity[Ah]"]
    else:
        logging.info("No valid discharge blocks found, returning DataFrame with Capacity as nans")
        df_mod["Capacity[Ah]"] = np.full(len(df_mod), np.nan, dtype=np.float64)

    return df_mod


def add_charge_throughput(
    df: pd.DataFrame,
    calculate_tests_individually: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Calculate charge throughput and absolute charge throughput from a given DataFrame.

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing 'Test_Time[s]' and 'Current[A]' columns

    Returns:
    pandas.DataFrame: DataFrame with added 'ChargeThroughput[Ah]' and 'AbsoluteChargeThroughput[Ah]' columns

    Notes:
    The 'ChargeThroughput[Ah]' column represents the cumulative charge (in Ah) with sign (i.e., loaded + / unloaded -)
    The 'AbsoluteChargeThroughput[Ah]' column represents the cumulative absolute charge (in Ah)
    """
    time_col = "Test_Time[s]"
    current_col = "Current[A]"
    testindex_col = "TestIndex"

    # quick checks
    if time_col not in df.columns or current_col not in df.columns:
        raise KeyError(f"Missing required columns: {time_col}, {current_col}")

    n = len(df)
    if n == 0:
        if verbose:
            logging.info("Empty DataFrame, returning.")
        return df.copy()

    time = df[time_col].to_numpy(dtype=float)
    current = df[current_col].to_numpy(dtype=float)

    charge_throughput = np.full(n, np.nan, dtype=float)
    abs_charge_throughput = np.full(n, np.nan, dtype=float)

    def _process_slice(start_slice: int, end_slice: int):
        slice_time = time[start_slice:end_slice]
        slice_current = current[start_slice:end_slice]

        mask = ~np.isnan(slice_time) & ~np.isnan(slice_current)
        if np.sum(mask) <= 1:
            return

        charge = integrate.cumulative_trapezoid(slice_current[mask], slice_time[mask], initial=0) / 3600.0
        abs_charge = integrate.cumulative_trapezoid(np.abs(slice_current[mask]), slice_time[mask], initial=0) / 3600.0

        valid_indices = np.nonzero(mask)[0] + start_slice
        charge_throughput[valid_indices] = charge
        abs_charge_throughput[valid_indices] = abs_charge

    with StepTimer(verbose) as st:
        if calculate_tests_individually and (testindex_col in df.columns):
            testvalues = df[testindex_col].to_numpy()
            starts = np.nonzero(np.concatenate(([True], testvalues[1:] != testvalues[:-1])))[0]
            starts = np.append(starts, n)
            for i in range(len(starts) - 1):
                start = int(starts[i])
                end = int(starts[i + 1])
                _process_slice(start, end)
            st.log("Processed charge throughput per individual test blocks")
        else:
            _process_slice(0, n)
            st.log("Processed charge throughput for whole DataFrame")

    df_mod = df.copy()
    df_mod["ChargeThroughput[Ah]"] = charge_throughput
    df_mod["AbsoluteChargeThroughput[Ah]"] = abs_charge_throughput

    return df_mod
