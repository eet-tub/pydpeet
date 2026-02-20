import inspect
import logging

import numpy as np

from pydpeet.process.analyze.capacity import add_capacity
from pydpeet.process.analyze.configs.battery_config import BatteryConfig
from pydpeet.process.analyze.utils import StepTimer


def add_soh(df, neware_bool=True, df_primitives=None, config: BatteryConfig = None, verbose=True):
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

    if "Capacity[Ah]" not in df.columns:
        logging.info("Capacity[Ah] not found, adding Capacity column with add_capacity function...")
        with StepTimer(verbose) as st:
            if df_primitives is None:
                logging.info("df_primitives is None, please provide a valid df_primitives for add_capacity function")
            else:
                df = add_capacity(df, neware_bool, df_primitives, config, verbose=verbose)
                st.log("added capacity column to df")
                first_valid_idx = df["Capacity[Ah]"].first_valid_index()
                if first_valid_idx is None:
                    logging.warning("No valid capacity values found — returning DataFrame with empty SOH column")
                    df["SOH"] = np.nan  # or whatever column you intend to fill
                    return df

    c_ref = config.c_ref

    if c_ref is None:
        logging.info("c_ref is None, attempting to use first valid capacity value as reference")

        first_valid_idx = df["Capacity[Ah]"].first_valid_index()

        if first_valid_idx is None:
            logging.warning("No valid capacity values found — returning DataFrame with empty SOH column")
            df["SOH"] = np.nan  # or whatever column you intend to fill
            return df
        else:
            c_ref = df.at[first_valid_idx, "Capacity[Ah]"]
            logging.info(f"Using first valid capacity value ({c_ref:.4f} Ah) as reference")

    with StepTimer(verbose) as st:
        df["SOH"] = df["Capacity[Ah]"].dropna() / c_ref
        st.log("computed SOH values")

    return df
