import gc
import logging
import os
import re
import time
from enum import Enum

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from numba import njit

# ** small generic helper functions **


# Decorator for timing + logging
def log_time(func):
    def wrapper(self, *args, **kwargs):
        rows_before, cols_before = self.df.shape
        start = time.perf_counter()

        result = func(self, *args, **kwargs)

        end = time.perf_counter()
        elapsed = end - start
        rows_after, cols_after = self.df.shape

        new_cols = cols_after - cols_before
        msg = (
            f"{func.__name__} took {elapsed:.2f} sec | "
            f"rows: {rows_before} → {rows_after}, "
            f"cols: {cols_before} → {cols_after}"
        )
        if new_cols > 0:
            msg += f" (+{new_cols} new cols)"
        logging.info(msg)

        return result
    return wrapper


class StepTimer:
    """Helper to log elapsed time for sub-steps inside a method."""
    def __init__(self, verbose=True, indent="    "):
        self.verbose = verbose
        self.indent = indent
        self.start = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def log(self, msg: str):
        if self.verbose:
            elapsed = time.perf_counter() - self.start
            logging.info(f"{self.indent}{elapsed:0.4f}s {msg}")


def _check_columns(df, required_columns):
    """Checks if the required columns are present in the DataFrame, allowing for 'Segment_' prefixes."""
    columns = set(df.columns)
    mapped_columns = {col.replace("Segment_", "") for col in columns}

    missing_columns = [col for col in required_columns if col not in columns and col not in mapped_columns]
    if missing_columns:
        raise KeyError(f"The following required columns are missing: {', '.join(missing_columns)}")



# Precompute arrays that are independent of chosen SOC reset method

@njit(cache=True)
def precompute_block_arrays_soc_methods(time, current, voltage, capacity_values, c_ref):
    """
    Numba-optimized version of precompute_block_arrays_soc_methods.
    Returns: (delta_soc, current_arr, abs_current, voltage_arr, c_ref_as)
    """
    n = len(time)

    # Ensure arrays are float64 contiguous
    delta_t = np.zeros(n, dtype=np.float64)
    if n > 1:
        for i in range(1, n):
            if np.isnan(time[i]) or np.isnan(time[i-1]):
                delta_t[i] = 0.0
            else:
                delta_t[i] = time[i] - time[i-1]

    # delta_Q = current * delta_t
    delta_Q = np.zeros(n, dtype=np.float64)
    for i in range(n):
        if np.isnan(current[i]):
            delta_Q[i] = 0.0
        else:
            delta_Q[i] = current[i] * delta_t[i]

    # c_ref_as forward-fill
    c_ref_as = np.empty(n, dtype=np.float64)
    local = c_ref if c_ref is not None else 1e-9
    for i in range(n):
        value = capacity_values[i]
        if not np.isnan(value):
            local = value
        if local <= 0.0 or np.isnan(local):
            local = 1e-9
        c_ref_as[i] = local * 3600.0  # convert Ah → As

    # delta_soc = delta_Q / c_ref_as
    delta_soc = np.zeros(n, dtype=np.float64)
    for i in range(n):
        if c_ref_as[i] != 0.0:
            delta_soc[i] = delta_Q[i] / c_ref_as[i]
        else:
            delta_soc[i] = 0.0

    # abs_current
    abs_current = np.empty(n, dtype=np.float64)
    for i in range(n):
        ci = current[i]
        if np.isnan(ci):
            abs_current[i] = 0.0
        else:
            abs_current[i] = ci if ci >= 0.0 else -ci

    # voltage_arr
    voltage_arr = np.empty(n, dtype=np.float64)
    for i in range(n):
        voltage_arr[i] = voltage[i] if not np.isnan(voltage[i]) else 0.0

    return delta_soc, current, abs_current, voltage_arr, c_ref_as

def drop_duplicate_testtime(df, keep="first"):
    """
    Drop duplicate rows based on Testtime[s].
    keep='first' keeps the first occurrence,
    keep='last' keeps the last,
    keep=False removes all duplicates entirely.
    """
    if "Testtime[s]" not in df.columns:
        raise ValueError("No 'Testtime[s]' column in DataFrame")

    n_before = len(df)
    df_clean = df.drop_duplicates(subset=["Testtime[s]"], keep=keep).copy()
    n_after = len(df_clean)

    print(f"Dropped {n_before - n_after} duplicate rows (kept={keep}).")

    return df_clean.sort_values("Testtime[s]").reset_index(drop=True)


class ColumnName(Enum):
    # --- Electrical measurements ---
    VOLTAGE = "Voltage[V]"
    CURRENT = "Current[A]"
    POWER = "Power[W]"
    INTERNAL_RESISTANCE = "InternalResistance[ohm]"
    DC_CURRENT = "DC Current[A]"

    # --- Capacity & throughput ---
    CAPACITY = "Capacity[Ah]"
    CAPACITY_THROUGHPUT = "CapacityThroughput[Ah]"
    CHARGE_THROUGHPUT = "ChargeThroughput[Ah]"
    ABSOLUTE_CHARGE_THROUGHPUT = "AbsoluteChargeThroughput[Ah]"

    # --- Energy ---
    CUMULATIVE_ENERGY = "CumulativeEnergy[Wh]"

    # --- Ageing metrics ---
    SOH = "SOH"
    SOH_LOSS_PER_AH = "SohLossPerAh"
    SOC = "SOC"
    COULOMB_EFFICIENCY = "CoulombEfficiency"
    EQUIVALENT_FULL_CYCLES = "EquivalentFullCycles"

    # --- Time information ---
    TESTTIME = "Testtime[s]"
    ABSOLUTE_TIME = "Absolute Time[yyyy-mm-dd hh:mm:ss]"
    TEST_INDEX = "TestIndex"
    STEPID = "StepID"

    # --- Environmental ---
    TEMPERATURE = "Temperature[°C]"

    # --- EIS (Electrochemical Impedance Spectroscopy) ---
    EISFREQ = "EISFreq[Hz]"
    ZRE = "Zre[Ohm]"
    ZIM = "Zim[Ohm]"

    # helper method
    @classmethod
    def to_list(cls, group: str = None):

        """
        Return a list of the specified groups columns.

        Parameters:
        group (str, optional): Filter column names by group. Must be one of
            "electrical", "capacity", "energy", "calculations", "time", "environment", "eis".
            If None, returns all available column names.

        Returns:
        list[str]: A list of column names as strings.

        Raises:
        ValueError: If group is not one of the available groups.
        """
        groups = {
            "electrical": [
                cls.VOLTAGE, cls.CURRENT, cls.POWER, cls.RESISTANCE,
                cls.INTERNAL_RESISTANCE, cls.DC_CURRENT
            ],
            "capacity": [
                cls.CAPACITY, cls.CUMULATIVE_CAPACITY, cls.CAPACITY_THROUGHPUT,
                cls.CHARGE_THROUGHPUT, cls.ABSOLUTE_CHARGE_THROUGHPUT
            ],
            "energy": [cls.CUMULATIVE_ENERGY],
            "calculations": [
                cls.SOH, cls.SOC, cls.COULOMB_EFFICIENCY, cls.EQUIVALENT_FULL_CYCLES
            ],
            "time": [cls.TEST_INDEX, cls.STEPID,
                       # cls.TESTTIME, cls.ABSOLUTE_TIME
                       ],
            "environment": [cls.TEMPERATURE],
            "eis": [cls.EISFREQ, cls.ZRE, cls.ZIM],
            "custom": [] # add preferences
        }

        if group is None:
            return [col.value for col in cls]
        if group not in groups:
            raise ValueError(f"Unknown group '{group}'. Must be one of {list(groups.keys())}.")
        return [col.value for col in groups[group]]


def plot_columns(df, columns=None, x_column=None, verbose=True):
    """
    Plot selected columns from a DataFrame using ColumnName enums.
    X-axis will be `x_column` if provided, otherwise Testtime in days if available.

    Parameters:
    - df: pandas DataFrame
    - columns: list of ColumnName enums to plot
    - x_column: str, optional, name of column to use for X-axis
    - verbose: bool, log info messages
    """

    if columns is None:
        # default: all defined columns that exist in df
        columns = [col for col in ColumnName if col.value in df.columns]

    special_cols = [ColumnName.SOH, ColumnName.SOH_LOSS_PER_AH, ColumnName.CAPACITY, ColumnName.COULOMB_EFFICIENCY]

    if not columns:
        logging.warning("No matching columns found in dataframe to plot.")
        return
    if verbose:
        logging.info(f"Plotting {len(columns)} columns...")

        # Determine X-axis
        if isinstance(x_column, ColumnName):
            x_column_name = x_column.value
        else:
            x_column_name = x_column  # str or None

        if x_column_name is not None and x_column_name in df.columns:
            x = df[x_column_name]
            x_label = x_column_name
        elif ColumnName.TESTTIME.value in df.columns:
            x = df[ColumnName.TESTTIME.value] / (24 * 3600)  # convert seconds → days
            x_label = "Testtime [days]"
        else:
            x = df.index
            x_label = "Index"

    fig, axes = plt.subplots(len(columns), 1, figsize=(18, 6 * len(columns)))

    if len(columns) == 1:
        axes = [axes]  # make iterable

    for ax, col in zip(axes, columns):
        col_name = col.value
        if col_name not in df.columns:
            logging.warning(f"Column {col_name} not in dataframe, skipping this column.")
            continue

        data = df[col_name]

        if col in special_cols:
            valid_data = data.dropna()
            ax.plot(x.loc[valid_data.index], valid_data.values, linestyle=":", marker="o", linewidth=4, markersize = 12)

            # Ensure the x-axis always covers the full testtime range
            ax.set_xlim(x.iloc[0], x.iloc[-1])
        elif col == ColumnName.INTERNAL_RESISTANCE:
            valid_data = data.dropna()
            ax.scatter(x.loc[valid_data.index], valid_data.values, marker="o", s = 6)
            ax.set_xlim(x.iloc[0], x.iloc[-1])
        elif col == ColumnName.TEST_INDEX:
            valid_data = data[data >= 0]
            ax.plot(x.loc[valid_data.index], valid_data.values, linewidth=4)
            ax.set_xlim(x.iloc[0], x.iloc[-1])
        else:
            ax.plot(x, data, linewidth=2)
            ax.set_xlim(x.iloc[0], x.iloc[-1])

        ax.tick_params(axis='both', which='major', labelsize=20)
        # --- Instead of set_title(), add text below the x-axis ---
        ax.text(
            0.5, -0.15,  # position (x, y) in axes coordinates
            f"{col_name} over {x_label}",
            fontsize=30,
            ha="center",
            va="top",
            transform=ax.transAxes
        )
        ax.set_ylabel(col_name, fontsize=30)
        # ax.set_xlabel(x_label, fontsize=12)

        ax.grid(True)

    plt.tight_layout(h_pad=2.0)  # default is ~1.2; increase to add more vertical gap

    plt.show()




def plot_single_column_all_files(input_dir, column = ColumnName.CAPACITY, title = "Capacity", cycler = None, cell_pattern=r"(AM\d+NMC\d+)", verbose=True):
    """
    Plotte ein bestimmtes ColumnName-Attribut für alle Dateien im Ordner in EINEM Diagramm.

    Parameters
    ----------
    input_dir : str
        Pfad zum Ordner mit den .parquet-Dateien.
    column : ColumnName
        Das zu plottende Spalten-Enum (z.B. ColumnName.VOLTAGE).
    cell_pattern : str, optional
        Regex zum Extrahieren der Zell-ID aus dem Dateinamen.
    verbose : bool, optional
        Ob Statusmeldungen ausgegeben werden sollen.
    """
    cell_regex = re.compile(cell_pattern)
    fig, ax = plt.subplots(figsize=(8, 6))

    found_any = False
    special_cols = [ColumnName.SOH, ColumnName.CAPACITY, ColumnName.COULOMB_EFFICIENCY]

    for filename in os.listdir(input_dir):
        if not filename.endswith(".parquet"):
            continue

        match = cell_regex.search(filename)
        if not match:
            if verbose:
                print(f"Skipping {filename}: no valid cell ID found.")
            continue

        cell_id = match.group(1)
        path = os.path.join(input_dir, filename)

        try:
            df = pd.read_parquet(path)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        if column.value not in df.columns:
            if verbose:
                print(f"{filename}: column '{column.value}' not found, skipping.")
            continue

        data = df[column.value]
        # Indizes mit gültigen (nicht-NaN) Werten
        valid_index = data.dropna().index
        if len(valid_index) == 0:
            if verbose:
                print(f"{cell_id}: no valid (non-NaN) values for {column.value}, skipping.")
            continue

        first_valid_idx = valid_index[0]  # Label des ersten gültigen Eintrags

        # --- X bestimmen und so verschieben, dass first_valid -> 0 ---
        if "Testtime[s]" in df.columns:
            x_seconds = df["Testtime[s]"].copy()
            # X-baseline: Testtime-Wert an der Position des ersten gültigen Eintrags
        if "EquivalentFullCycles" in df.columns:
            x_EFC = df["EquivalentFullCycles"].copy()
            # X-baseline: Testtime-Wert an der Position des ersten gültigen Eintrags
            try:
                x0 = x_seconds.loc[first_valid_idx]
            except KeyError:
                # Falls loc mit Label fehlschlägt (selten), per Position abgreifen:
                pos0 = df.index.get_loc(first_valid_idx)
                x0 = x_seconds.iloc[pos0]


            # verschieben und in Tage umrechnen
            x_shifted = (x_seconds - x0) / (24 * 3600)
            x_days = x_seconds / (24*3600)
            x_to_plot = x_days.loc[valid_index]
            x_label = f"Testtime [days]"
            x_to_plot_EFC = x_EFC.loc[valid_index]
            x_label_EFC = f"Equivalent Full Cycles"
        else:
            # Keine Testtime-Spalte -> benutze numerische Positionen und offset auf first_valid
            pos0 = df.index.get_loc(first_valid_idx)
            positions = np.arange(len(df))
            shifted_positions = positions - pos0
            x_series = pd.Series(shifted_positions, index=df.index)
            x_to_plot = x_series.loc[valid_index]
            x_label = f"Index (offset so first {column.value} → 0)"

        y_to_plot = data.loc[valid_index]

        # --- Zeichnen (Spezialfälle berücksichtigen) ---
        if column in special_cols:
            ax.plot(x_to_plot_EFC, y_to_plot.values, linestyle=":", marker="o", label=cell_id, linewidth = 4, markersize = 12)
        elif column == ColumnName.INTERNAL_RESISTANCE:
            ax.scatter(x_to_plot_EFC, y_to_plot.values, marker="o", label=cell_id)
        else:
            ax.plot(x_to_plot_EFC, y_to_plot.values, label=cell_id, scalex= 16)

        found_any = True
        del df
        gc.collect()

    if not found_any:
        print(f"Keine gültigen Daten für Spalte '{column.value}' in '{input_dir}' gefunden.")
        return None, None

    ax.set_title(f"{column.value} über {x_label_EFC} ({cycler})", fontsize=30)
    ax.set_xlabel(x_label_EFC, fontsize=24)
    ax.set_ylabel(column.value, fontsize=24)
    ax.grid(True)
    # ax.legend(title= title, fontsize=12, loc="upper right", frameon=True)

    # Increase tick label size
    ax.tick_params(axis='both', which='major', labelsize=18)  # adjust 18 as needed

    plt.tight_layout()
    plt.show()

    return fig, ax


import matplotlib.pyplot as plt

def plot_axis_with_color(x_axis, y_axis, colour_column,
                         title: str = "", xlabel=None, ylabel=None,
                         colourlabel=None, s=40, alpha=0.8, edgecolour='None', plot_colourbar=True):
    import matplotlib.colors as mcolors

    fig, ax = plt.subplots(figsize=(24, 6))
    norm = mcolors.PowerNorm(gamma=2)
    sc = ax.scatter(
        x_axis,
        y_axis,
        c=colour_column,
        cmap="viridis",
        norm = norm,
        s=s,
        alpha=alpha,
        edgecolor=edgecolour,
    )

    ax.set_xlabel(xlabel, fontsize=30)
    ax.set_ylabel(ylabel, fontsize=30)
    ax.grid(True, alpha=0.3)

    if plot_colourbar:
        cbar = plt.colorbar(sc, ax=ax)
        cbar.set_label("Equivalent Full Cycles", fontsize=30)  # bigger label
        cbar.ax.tick_params(labelsize=18)  # bigger tick font size

    ax.tick_params(axis='both', which='major', labelsize=18)

    ax.text(
        0.5, -0.15,
        s=title,
        ha='center', va='center',
        fontsize=30,
        transform=ax.transAxes
    )

    fig.tight_layout()
    plt.show()

