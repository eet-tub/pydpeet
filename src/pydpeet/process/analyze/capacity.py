import inspect
import logging

import numpy as np
from scipy import integrate

from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.analyze.configs.step_analyzer_config import SEGMENT_SEQUENCE_CONFIG
from pydpeet.process.analyze.utils import StepTimer, _check_columns
from pydpeet.process.sequence.step_analyzer import extract_sequences
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks

# ** Capacity and Degradation metrics **


def add_capacity(df, df_primitives, neware_bool=True, config: BatteryConfig = None, verbose=True):
    """
    Compute the capacity of a battery cell from its discharge data.

    The capacity computation is a multistep process. First, the discharge blocks
    are filtered from the data. Then, the blocks with a full discharge (from max to min)
    are searched. For each of these blocks, the cumulative capacity is computed by
    integrating the absolute current over time.

    The resulting DataFrame has an additional 'Capacity[Ah]' column.

    Parameters:
        df (pandas.DataFrame): Input DataFrame containing battery test data
        config (BatteryConfig, optional): Configuration object containing battery test parameters
        verbose (bool, optional): If True, print debug messages. Defaults to False.

    Returns:
        pandas.DataFrame: DataFrame with added 'Capacity[Ah]' column
        :param THRESHOLD_DICT: threshold dictionary for neware params
    """
    # Check if the required columns are present
    required_cols = ["Test_Time[s]", "Current[A]", "Voltage[V]"]
    _check_columns(df, required_cols)

    if config is None:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}!")

    minimal_current = config.minimal_current_for_capacity
    maximal_current = config.maximal_current_for_capacity

    df = df.copy()
    max_voltage = config.max_voltage
    min_voltage = config.min_voltage
    voltage_intervall = config.voltage_intervall

    logging.info(f"Starting capacity computation on dataframe of size {len(df)}...")

    # Step 2: Segments and sequences
    with StepTimer(verbose) as st:
        df_segments_and_sequences = extract_sequences(df_primitives, SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG)
        st.log("computed segments and sequences")

    if neware_bool:
        # Step 3: Filter discharge blocks
        rules = [
            "CC_Discharge_after_CC_Charge",
            "CC_Discharge_after_CCCV_Charge",
            "CC_Discharge_after_CV_Charge",
            "CC_Discharge_after_CCCV_Charge_with_Pause",
            "CC_Discharge_after_CC_Charge_with_Pause",
            "CC_Discharge_after_CV_Charge_with_Pause"
        ]
        with StepTimer(verbose) as st:
            dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
                df_segments_and_sequences=df_segments_and_sequences,
                df_primitives=df_primitives,
                rules=rules,
                combine_op="or", also_return_filtered_df=True
            )
            st.log("filtered initial discharge blocks")

    rules = ["CC_Discharge"]
    with StepTimer(verbose) as st:
        dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
            df_segments_and_sequences=df_segments_and_sequences,
            df_primitives=df_primitives,
            rules=rules,
            combine_op="or", also_return_filtered_df=True
        )
        st.log("filtered CC_Discharge blocks")

    discharge_dfs = []
    # search for the blocks with a full discharge (from max to min)
    for i, block in enumerate(dfs_per_block):
        avg_current = block["Current[A]"].mean()
        voltage_range = (block["Voltage[V]"].max(), block["Voltage[V]"].min())

        if (not (minimal_current < avg_current < maximal_current)
                or not (voltage_range[0] >= max_voltage * (1 - voltage_intervall)
                        and voltage_range[1] <= min_voltage * (1 + voltage_intervall))):
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

    df_with_capacity = df.copy()
    if len(discharge_dfs) > 0:
        for block in discharge_dfs:
            df_with_capacity.loc[block.index[0] : block.index[-1], "Capacity[Ah]"] = block["Capacity[Ah]"]
    else:
        logging.info("No valid discharge blocks found, returning DataFrame with Capacity as nans")
        df_with_capacity["Capacity[Ah]"] = np.full(len(df_with_capacity), np.nan, dtype=np.float64)

    return df_with_capacity


def add_charge_throughput(df, inplace=False, calculate_tests_individually=False, verbose=True):
    """
    Calculate charge throughput and absolute charge throughput from a given DataFrame.

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing 'Testtime[s]' and 'Current[A]' columns

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
        return df if inplace else df.copy()

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

    out = df if inplace else df.copy()
    out["ChargeThroughput[Ah]"] = charge_throughput
    out["AbsoluteChargeThroughput[Ah]"] = abs_charge_throughput
    return out
