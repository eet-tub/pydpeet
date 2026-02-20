import inspect
import logging
import warnings

import numpy as np
import pandas as pd

from pydpeet.process.analyze.average import calculate_total_charge, calculate_total_discharge
from pydpeet.process.analyze.utils import _check_columns, StepTimer
from pydpeet.process.analyze.configs.battery_config import BatteryConfig

# ** Battery performance metrics **

def add_efficiency_coulomb(df, df_blocks_charge, df_blocks_discharge, config: BatteryConfig = None,
                           max_time_diff_in_secs: int = 300, ignore_threshold_values: bool = False, verbose=True):
    """
    Calculate the Coulomb Efficiency of a battery based on the given data.

    The Coulomb efficiency is calculated as the total discharge divided by the total charge.
    The time difference between a charge block and the subsequent discharge block is taken into account.
    If a charge block does not have a corresponding discharge block within the given time difference,
    it is ignored. Similarly, if a discharge block does not have a corresponding charge block within
    the given time difference, it is ignored.

    Parameters:
        df (pandas.DataFrame): Input DataFrame containing battery test data
        df_blocks_charge (list[pandas.DataFrame] or pandas.DataFrame): List of DataFrames containing charge blocks
        df_blocks_discharge (list[pandas.DataFrame] or pandas.DataFrame): List of DataFrames containing discharge blocks
        config (BatteryConfig, optional): Configuration object containing battery test parameters
        max_time_diff_in_secs (int, optional): Maximum time difference in seconds between charge and discharge blocks
        ignore_threshold_values (bool, optional): Whether to ignore voltage thresholds when computing Coulomb efficiency
        verbose (bool, optional): If True, print debug messages

    Returns:
        pandas.DataFrame: DataFrame with added 'CoulombEfficiency' column
    """
    if config is None:
        func_name = inspect.currentframe().f_code.co_name
        raise ValueError(f"config is None, please provide a valid config for {func_name}")

    logging.info(f"Starting Coulomb Efficiency computation on dataframe of size {len(df)}...")

    # Ensure blocks are lists
    if isinstance(df_blocks_charge, pd.DataFrame):
        df_blocks_charge = [df_blocks_charge]
    if isinstance(df_blocks_discharge, pd.DataFrame):
        df_blocks_discharge = [df_blocks_discharge]


    # Determine which time column to use
    if 'Testtime[s]' in df.columns:
        time_col = 'Testtime[s]'
        parse_time = False
        tolerance_val = max_time_diff_in_secs  # already seconds
    elif 'Absolute Time[yyyy-mm-dd hh:mm:ss]' in df.columns:
        warnings.warn("Absolute Time[yyyy-mm-dd hh:mm:ss] is used as time column, because there is no 'Testtime[s]' given.")
        time_col = 'Absolute Time[yyyy-mm-dd hh:mm:ss]'
        parse_time = True
        tolerance_val = pd.Timedelta(seconds=max_time_diff_in_secs)
    else:
        raise ValueError("No suitable time column found. Provide 'Absolute Time[yyyy-mm-dd hh:mm:ss]' or 'Testtime[s]'.")

    max_voltage = config.max_voltage
    min_voltage = config.min_voltage

    # Voltage thresholds
    max_v_adj_down = max_voltage * (1 - config.voltage_intervall)
    max_v_adj_up   = max_voltage * (1 + config.voltage_intervall)
    min_v_adj_up   = min_voltage * (1 + config.voltage_intervall)
    min_v_adj_down = min_voltage * (1 - config.voltage_intervall)

    df['CoulombEfficiency'] = np.nan  # numeric NaN

    # Helper to summarize blocks safely
    def summarize_blocks(blocks, total_col_name):
        summary = []
        for block in blocks:
            if block.empty:
                continue
            block_max = block['Voltage[V]'].max()
            block_min = block['Voltage[V]'].min()
            if ignore_threshold_values or (max_v_adj_down <= block_max <= max_v_adj_up and min_v_adj_down <= block_min <= min_v_adj_up):
                start_time = pd.to_datetime(block[time_col].iloc[0]) if parse_time else block[time_col].iloc[0]
                end_time   = pd.to_datetime(block[time_col].iloc[-1]) if parse_time else block[time_col].iloc[-1]
                with StepTimer(verbose) as timer:
                    total = calculate_total_charge(block) if total_col_name == 'total_charge' else calculate_total_discharge(block)
                    timer.log(f"calculated {total_col_name} for one block")
                summary.append({
                    'start_time': start_time,
                    'end_time': end_time,
                    total_col_name: total,
                    'last_index': block.index[-1]
                })
        if not summary:
            return pd.DataFrame(columns=['start_time', 'end_time', total_col_name, 'last_index'])
        return pd.DataFrame(summary).sort_values('start_time')

    # Helper to find matching blocks
    with StepTimer(verbose) as st:
        charge_df = summarize_blocks(df_blocks_charge, 'total_charge')
        discharge_df = summarize_blocks(df_blocks_discharge, 'total_discharge')
        st.log("summarized all charge/discharge blocks")

    if charge_df.empty or discharge_df.empty:
        logging.info("No valid charge/discharge blocks found. Skipping Coulomb Efficiency computation.")
        return df

    if parse_time:
        # Ensure datetime dtype
        charge_df['start_time'] = pd.to_datetime(charge_df['start_time'])
        charge_df['end_time']   = pd.to_datetime(charge_df['end_time'])
        discharge_df['start_time'] = pd.to_datetime(discharge_df['start_time'])
        discharge_df['end_time']   = pd.to_datetime(discharge_df['end_time'])

    # Sort before merge_asof
    charge_df = charge_df.sort_values('start_time').reset_index(drop=True)
    discharge_df = discharge_df.sort_values('start_time').reset_index(drop=True)

    # Forward merge: discharge after charge
    with StepTimer(verbose) as st:
        paired_forward = pd.merge_asof(
            charge_df,
            discharge_df,
            left_on='end_time',
            right_on='start_time',
            direction='forward',
            tolerance=tolerance_val
        )
        st.log("performed forward merge of charge/discharge blocks")

    # Backward merge: discharge before charge
    with StepTimer(verbose) as st:
        paired_backward = pd.merge_asof(
            charge_df,
            discharge_df,
            left_on='start_time',
            right_on='end_time',
            direction='backward',
            tolerance=tolerance_val
        )
        st.log("performed backward merge of charge/discharge blocks")

    # Combine forward/backward and pick closest in absolute time
    with StepTimer(verbose) as st:
        combined = pd.concat([paired_forward, paired_backward], ignore_index=True, sort=False)
        combined['time_diff'] = (pd.to_datetime(combined['start_time_y']) - pd.to_datetime(combined['end_time_x'])).abs()
        combined = combined.dropna(subset=['total_discharge'])
        combined = combined.sort_values('time_diff').drop_duplicates(subset=['start_time_x', 'end_time_x'])

        # Assign Coulomb Efficiency to last index of the later block
        for _, row in combined.iterrows():
            total_charge = row.get('total_charge', np.nan)
            total_discharge = row.get('total_discharge', np.nan)
            if pd.isna(total_charge) or total_charge == 0:
                ce = np.nan
            else:
                ce = total_discharge / total_charge
            # Use nan-safe max and cast to int to avoid type checker complaints about comparing Series
            last_index = int(np.nanmax([row.get('last_index_x', np.nan), row.get('last_index_y', np.nan)]))
            df.loc[last_index, 'CoulombEfficiency'] = ce
        st.log("assigned Coulomb Efficiency to dataframe")

    return df