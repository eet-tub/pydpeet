import logging

import numpy as np

from pydpeet.process.analyze.calculations.throughput import calculate_average_positive_chargeThroughput
from pydpeet.process.analyze.calculations.utils import _check_columns, StepTimer
from numba import njit




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

# @njit(cache=True)
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

# @njit(cache=True)
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
            print("No valid SOH values found.")
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
            print("No valid EquivalentFullCycles values found.")
        return np.nan

    max_cycles = cycles.max()
    if max_cycles <= 0:
        if verbose:
            print("Max EquivalentFullCycles <= 0, cannot compute loss per cycle.")
        return np.nan

    with StepTimer(verbose) as st:
        soh_loss_per_cycle = soh_loss / max_cycles
        st.log("computed SOH loss per cycle")

    return soh_loss_per_cycle


import pandas as pd
import numpy as np


def calculate_soh_loss_over_charging(df, verbose=True):
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
            print(f"From index {start_idx} to {end_idx}: SOH diff = {soh_diff}, "
                  f"Avg current = {avg_current}, Loss/current = {loss_per_current}")

    return df

