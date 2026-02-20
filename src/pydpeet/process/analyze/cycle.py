import logging
import inspect

import numpy as np
from matplotlib import pyplot as plt
from scipy import integrate

from pydpeet.process.analyze.configs.step_analyzer_config import SEGMENT_SEQUENCE_CONFIG
from pydpeet.process.analyze.capacity import add_charge_throughput
from pydpeet.process.analyze.utils import StepTimer, _check_columns
from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.sequence.step_analyzer import extract_sequences
from pydpeet.process.sequence.configs import config
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks


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
