import logging
import pandas as pd
import numpy as np

from pydpeet.process.analyze.capacity import add_charge_throughput
from pydpeet.process.analyze.utils import _check_columns, StepTimer


def calculate_average_temperature(df, verbose=True):
    if 'Temperature[°C]' not in df.columns:
        raise ValueError("Temperature[°C] column not found in DataFrame.")

    average_temperature = df['Temperature[°C]'].mean()

    return average_temperature

def calculate_average_voltage(df, verbose=True):
    if 'Voltage[V]' not in df.columns:
        raise ValueError("Voltage[V] column not found in DataFrame.")

    average_voltage = df['Voltage[V]'].mean()

    return average_voltage

def calculate_average_loading_voltage(df, verbose=True):
    if 'Voltage[V]' not in df.columns:
        raise ValueError("Voltage[V] column not found in DataFrame.")

    positive_charges = df[df['Voltage[V]'].diff() > 0]['Voltage[V]']
    average_charge = positive_charges.mean()

    # Select only positive values (charging)
    return average_charge

def calculate_average_charge(df):
    """
    Calculate the average charge current [A] over all charging phases (Current > 0) efficiently.
    """
    if 'Current[A]' not in df.columns:
        return np.nan

    currents = df['Current[A]'].to_numpy()
    positive = currents[currents > 0]

    if positive.size == 0:
        return np.nan
    return positive.mean()

def calculate_average_discharge(df):
    """
    Calculate the average discharge current [A] over all discharging phases (Current < 0) efficiently.
    """
    if 'Current[A]' not in df.columns:
        return np.nan

    currents = df['Current[A]'].to_numpy()
    negative = currents[currents < 0]

    if negative.size == 0:
        return np.nan
    return negative.mean()


def calculate_soh_loss(df, verbose=True):
    """
    Calculate the total SOH loss for a dataset.
    Returns a single scalar value:
        soh_loss = 1 - min(valid SOH)
    """
    _check_columns(df, ['SOH'])

    soh = df['SOH'].astype(float).dropna()

    if soh.empty:
        if verbose:
            logging.warning("No valid SOH values found.")
        return np.nan

    with StepTimer(verbose) as st:
        soh_loss = 1 - soh.min()
        st.log("computed SOH loss")

    return soh_loss


def calculate_soh_loss_per_cycle(df, verbose=True):
    """
    Calculate the SOH loss per equivalent full cycle.
    Returns a single scalar value:
        soh_loss_per_cycle = (1 - min(SOH)) / max(EquivalentFullCycles)
    """
    _check_columns(df, ['SOH', 'EquivalentFullCycles'])

    soh_loss = calculate_soh_loss(df, verbose=False)
    cycles = df['EquivalentFullCycles'].astype(float).dropna()

    if cycles.empty:
        if verbose:
            logging.warning("No valid EquivalentFullCycles values found. returning np.nan")
        return np.nan

    max_cycles = cycles.max()
    if max_cycles <= 0:
        if verbose:
            logging.warning("Max EquivalentFullCycles <= 0, cannot compute loss per cycle. returning np.nan")
        return np.nan

    with StepTimer(verbose) as st:
        soh_loss_per_cycle = soh_loss / max_cycles
        st.log("computed SOH loss per cycle")

    return soh_loss_per_cycle


def add_soh_loss_over_charging(df, verbose=True):
    """
    Calculate SOH loss per unit of charging current.

    Parameters:
        df (pd.DataFrame): Must contain 'SOH' and 'ChargingCurrent' columns.
        verbose (bool): If True, prints intermediate steps.

    Returns:
        pd.DataFrame: Original df with a new column 'SohLossPerAh'.
    """
    df = df.sort_index().copy()
    soh_indices = df.index[~df['SOH'].isna()]
    df['SohLossPerAh'] = np.nan

    for i in range(1, len(soh_indices)):
        start_idx = soh_indices[i - 1]
        end_idx = soh_indices[i]

        soh_diff = df.at[end_idx, 'SOH'] - df.at[start_idx, 'SOH']

        # Slice the dataframe between two SOH measurements
        df_slice = df.loc[start_idx:end_idx]

        # Calculate average charging current (make sure function exists)
        avg_current = calculate_average_positive_chargeThroughput(df_slice)

        # Compute SOH loss per Ah
        loss_per_current = soh_diff / avg_current if avg_current != 0 else np.nan
        df.at[end_idx, 'SohLossPerAh'] = loss_per_current

        if verbose:
            logging.info(f"From index {start_idx} to {end_idx}: SOH diff = {soh_diff}, "
                  f"Avg current = {avg_current}, Loss/current = {loss_per_current}")

    return df


def calculate_total_charge(df, verbose=True):
    """
    Calculate the total charge (in Ah) from the ChargeThroughput column.

    Parameters:
    -----------
    df : pandas.DataFrame
        Input DataFrame containing 'ChargeThroughput[Ah]' column

    Returns:
    -------
    float
        Total charge (in Ah)
    """
    if 'ChargeThroughput[Ah]' not in df.columns:
        if verbose:
            logging.info("ChargeThroughput column missing, computing via add_charge_throughput...")
        df = add_charge_throughput(df, verbose=verbose)

    delta_load = df['ChargeThroughput[Ah]'].diff().fillna(0)
    total_charge = delta_load[delta_load > 0].sum()

    if verbose:
        logging.info(f"Total charge computed: {total_charge:.4f} Ah")

    return total_charge


def calculate_total_discharge(df, verbose=True):
    """
    Calculate the total discharge (in Ah) from the ChargeThroughput column.

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing 'ChargeThroughput[Ah]' column

    Returns:
    float: Total discharge (in Ah)

    Notes:
    The total discharge is calculated as the sum of negative differences in the ChargeThroughput column.
    """
    if 'ChargeThroughput[Ah]' not in df.columns:
        logging.info("ChargeThroughput column missing, computing via add_charge_throughput...")
        df = add_charge_throughput(df, verbose=verbose)

    delta_load = df['ChargeThroughput[Ah]'].diff().fillna(0)
    total_discharge = -delta_load[delta_load < 0].sum()

    if verbose:
        logging.info(f"Total discharge computed: {total_discharge:.4f} Ah")

    return total_discharge


def calculate_average_positive_chargeThroughput(df, verbose=True):
    """
    Calculate the average charge (in Ah) from the ChargeThroughput column.

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing 'ChargeThroughput[Ah]' column
    verbose (bool, optional): If True, print debug messages

    Returns:
    float: Average charge (in Ah)

    Notes:
    The average charge is calculated as the mean of only positive values in the ChargeThroughput column.
    """
    if 'ChargeThroughput[Ah]' not in df.columns:
        logging.info("ChargeThroughput column missing, computing via add_charge_throughput...")
        df = add_charge_throughput(df, verbose=verbose)

    positive_charges = df[df['ChargeThroughput[Ah]'] > 0]['ChargeThroughput[Ah]']
    average_charge = positive_charges.mean()

    # Select only positive values (charging)
    return average_charge


def calculate_average_negative_charge_throughput(df, verbose=True):
    """
    Calculate the average discharge (in Ah) from the ChargeThroughput column.

    Parameters:
    df (pandas.DataFrame): Input DataFrame containing 'ChargeThroughput[Ah]' column
    verbose (bool, optional): If True, print debug messages

    Returns:
    float: Average discharge (in Ah)

    Notes:
    The average discharge is calculated as the mean of only negative values in the ChargeThroughput column.
    """
    if 'ChargeThroughput[Ah]' not in df.columns:
        logging.info("ChargeThroughput column missing, computing via add_charge_throughput...")
        df = add_charge_throughput(df, verbose=verbose)

    negative_charges = df[df['ChargeThroughput[Ah]'] < 0]['ChargeThroughput[Ah]']
    average_discharge = negative_charges.mean()

    # Select only negative values (discharging)
    return average_discharge