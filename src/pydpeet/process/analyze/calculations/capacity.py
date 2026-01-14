import logging
import inspect

import numpy as np
from matplotlib import pyplot as plt
from scipy import integrate

from pydpeet.process.analyze.configs.step_analyzer_config import SEGMENT_SEQUENCE_CONFIG
from pydpeet.process.analyze.calculations.throughput import add_charge_throughput
from pydpeet.process.analyze.calculations.utils import StepTimer, _check_columns
from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.sequence.step_analyzer import step_analyzer_seqments_and_sequences
from pydpeet.process.sequence.threshold_dictonaries import THRESHOLD_DICT_NEWARE
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks


# ** Capacity and Degradation metrics **

def add_capacity(df, df_primitives, neware_bool = True, config: BatteryConfig = None, verbose=True):
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
    required_cols = ['Testtime[s]', 'Current[A]', 'Voltage[V]']
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
        df_segments_and_sequences = step_analyzer_seqments_and_sequences(df_primitives, SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG)
        st.log("computed segments and sequences")

    if neware_bool:
        # Step 3: Filter discharge blocks
        rules = [
            'CC_Discharge_after_CC_Charge',
            'CC_Discharge_after_CCCV_Charge',
            'CC_Discharge_after_CV_Charge',
            'CC_Discharge_after_CCCV_Charge_with_Pause',
            'CC_Discharge_after_CC_Charge_with_Pause',
            'CC_Discharge_after_CV_Charge_with_Pause'
        ]
        with StepTimer(verbose) as st:
            dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
                df_segments_and_sequences=df_segments_and_sequences,
                df_primitives=df_primitives,
                rules=rules,
                combine_op='or',
                also_return_filtered_df=True
            )
            st.log("filtered initial discharge blocks")

    rules = ['CC_Discharge']
    with StepTimer(verbose) as st:
        dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
            df_segments_and_sequences=df_segments_and_sequences,
            df_primitives=df_primitives,
            rules=rules,
            combine_op='or',
            also_return_filtered_df=True
        )
        st.log("filtered CC_Discharge blocks")

    discharge_dfs = []
    # search for the blocks with a full discharge (from max to min)
    for i, block in enumerate(dfs_per_block):
        avg_current = block['Current[A]'].mean()
        voltage_range = (block['Voltage[V]'].max(), block['Voltage[V]'].min())

        if not (minimal_current < avg_current < maximal_current) or \
                not (voltage_range[0] >= max_voltage * (1 - voltage_intervall) and
                     voltage_range[1] <= min_voltage * (1 + voltage_intervall)):
            continue

        block = block.copy()
        time_diff = block['Testtime[s]'].diff() / 3600
        block['Capacity[Ah]'] = (block['Current[A]'] * time_diff).cumsum()

        if len(block) > 0:
            time_seconds = block['Testtime[s]'].values
            current = block['Current[A]'].values
            with StepTimer(verbose) as st:
                capacity_ah = integrate.cumulative_trapezoid(abs(current), time_seconds, initial=0) / 3600
                st.log(f"computed cumulative capacity for block {i}")
            block['Capacity[Ah]'] = float('NaN')
            block.loc[block.index[-1], 'Capacity[Ah]'] = capacity_ah[-1]

        discharge_dfs.append(block)

    df_with_capacity = df.copy()
    if len(discharge_dfs) > 0:
        for block in discharge_dfs:
            df_with_capacity.loc[block.index[0]:block.index[-1], 'Capacity[Ah]'] = block['Capacity[Ah]']
    else:
        logging.info("No valid discharge blocks found, returning DataFrame with Capacity as nans")
        df_with_capacity['Capacity[Ah]'] = np.full(len(df_with_capacity), np.nan, dtype=np.float64)

    return df_with_capacity


def add_soh(df, neware_bool = True, df_primitives = None, config: BatteryConfig = None, verbose=True):
    """
    Calculate State of Health (SOH) for the given battery test data.

    The State of Health is calculated as the ratio of the current capacity to the reference capacity (C_ref).

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing battery test data
    df_primitives (pandas.DataFrame, optional): DataFrame containing primitive battery test data
    config (BatteryConfig, optional): Configuration object containing battery test parameters

    Returns:
    pandas.DataFrame: DataFrame with added 'SOH' column
    """
    if config is None:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}")

    df = df.copy()
    logging.info(f"Starting SOH computation on dataframe of size {len(df)}...")

    if 'Capacity[Ah]' not in df.columns:
        logging.info("Capacity[Ah] not found, adding Capacity column with add_capacity function...")
        with StepTimer(verbose) as st:
            if df_primitives is None:
                logging.info("df_primitives is None, please provide a valid df_primitives for add_capacity function")
            else:
                df = add_capacity(df, neware_bool, df_primitives, config, verbose=verbose)
                st.log("added capacity column to df")
                first_valid_idx = df['Capacity[Ah]'].first_valid_index()
                if first_valid_idx is None:
                    logging.warning("No valid capacity values found — returning DataFrame with empty SOH column")
                    df['SOH'] = np.nan  # or whatever column you intend to fill
                    return df

    c_ref = config.c_ref

    if c_ref is None:
        logging.info("c_ref is None, attempting to use first valid capacity value as reference")

        first_valid_idx = df['Capacity[Ah]'].first_valid_index()

        if first_valid_idx is None:
            logging.warning("No valid capacity values found — returning DataFrame with empty SOH column")
            df['SOH'] = np.nan  # or whatever column you intend to fill
            return df
        else:
            c_ref = df.at[first_valid_idx, 'Capacity[Ah]']
            logging.info(f"Using first valid capacity value ({c_ref:.4f} Ah) as reference")

    with StepTimer(verbose) as st:
        df['SOH'] = df['Capacity[Ah]'].dropna() / c_ref
        st.log("computed SOH values")

    return df


def add_equivalent_full_cycles(df, config: BatteryConfig = None, verbose=True):
    """
    Calculate equivalent full cycles from absolute charge throughput and capacity reference.

    Equivalent full cycles are calculated as the absolute charge throughput divided by two times the capacity reference,
    so that every full cycle is counted as one cycle.

    Parameters:
        df (pandas.DataFrame): Input DataFrame containing battery test data
        config (BatteryConfig, optional): Configuration for the battery. Defaults to BATTERY_DEFAULT

    Returns:
        pandas.DataFrame: DataFrame with added 'EquivalentFullCycles' column
    """
    if config is None:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}")

    df = df.copy()
    logging.info(f"Starting Equivalent Full Cycles computation on dataframe of size {len(df)}...")

    c_ref = config.c_ref
    if c_ref is None:
        logging.info("c_ref is None, attempting to use first valid capacity value as reference")

        first_valid_idx = df['Capacity[Ah]'].first_valid_index()

        if first_valid_idx is None:
            logging.warning("No valid capacity values found — returning DataFrame with empty SOH column")
            df['SOH'] = np.nan  # or whatever column you intend to fill
            return df
        else:
            c_ref = df.at[first_valid_idx, 'Capacity[Ah]']
            logging.info(f"Using first valid capacity value ({c_ref:.4f} Ah) as reference")

    if 'AbsoluteChargeThroughput[Ah]' not in df.columns:
        logging.info("AbsoluteChargeThroughput[Ah] not found, adding AbsoluteChargeThroughput[Ah] column with add_charge_throughput function...")
        with StepTimer(verbose) as st:
            df = add_charge_throughput(df)
            st.log("added charge throughput column to df")

    with StepTimer(verbose) as st:
        df['EquivalentFullCycles'] = df['AbsoluteChargeThroughput[Ah]'] / (c_ref * 2)
        st.log("computed Equivalent Full Cycles")

    return df
