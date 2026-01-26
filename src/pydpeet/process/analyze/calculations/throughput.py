import logging

import numpy as np
from scipy import integrate

from pydpeet.process.analyze.calculations.utils import StepTimer

# ** Charge / Discharge and Absolute Throughput calculation logic **

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
    time_col = 'Testtime[s]'
    current_col = 'Current[A]'
    testindex_col = 'TestIndex'

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
