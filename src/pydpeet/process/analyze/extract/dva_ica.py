import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import integrate
from scipy.signal import savgol_filter

from pydpeet.process.analyze.configs.ocv_config import *
from pydpeet.process.analyze.extract.ocv import extract_ocv_iocv
from pydpeet.process.analyze.soc import add_soc
from pydpeet.process.sequence.step_analyzer import add_primitives, extract_sequences
from pydpeet.process.sequence.utils.visualize.visualize_data import *


def compute_ocv_dva_ica(
        df_primitives=None,
        df=None,
        min_pause_lenght: float = 120.0,
        min_loops: float = 70,
        soc_max_voltage: float = 4.21,
        soc_min_voltage: float = 2.49,
        soc_c_ref: float = 4.8,
        savgol: bool = False,
        savgol_window_lenght_percentage: float = 0.07,
        visualize: bool = False) -> pd.DataFrame:
    """
    Compute DVA and ICA curves from given data.

    Parameters
    ----------
    df_primitives : pandas.DataFrame or None
        DataFrame containing the primitives of the data.
    df : pandas.DataFrame or None
        DataFrame containing the original data.
    min_pause_lenght : float
        Minimum length of a pause in seconds.
    min_loops : float
        Minimum number of unique IDs.
    soc_max_voltage : float
        Maximum voltage of the battery.
    soc_min_voltage : float
        Minimum voltage of the battery.
    soc_c_ref : float
        Reference capacity of the battery.
    savgol : bool
        Whether to apply Savitzky-Golay filter to smooth the data.
    savgol_window_lenght_percentage : float
        Percentage of the window length for the Savitzky-Golay filter.
    visualize : bool
        Whether to visualize the DVA and ICA curves over SOC.

    Returns
    -------
    pd.DataFrame
        DataFrame containing all DVA and ICA curves.
    """
    logging.info("Executing DVA and ICA computation...")
    # falls nur ein df übergeben wird:
    if df is not None and df_primitives is not None:
        raise ValueError("Please provide either df or df_primitives, not both!")

    if df is not None:
        df.drop_duplicates(subset=["Test_Time[s]"], inplace=True)
        df.dropna(subset=["Test_Time[s]"], inplace=True)
        df = df.sort_values("Test_Time[s]")

        df_primitives = add_primitives(
            df=df,
            STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
            SHOW_RUNTIME=False,
            check_CV_0Aend_segments_bool=False,
            check_zero_length_segments_bool=False,
            supress_IO_warnings=True
        )

    if df_primitives is not None:
        if df_primitives["Test_Time[s]"].duplicated().any():
            raise ValueError("Duplicated 'Testtime[s]' values found!")

        if df_primitives["Test_Time[s]"].isna().any():
            raise ValueError("NaN values found in 'Testtime[s]'")

        if not np.all(np.diff(df_primitives["Test_Time[s]"]) > 0):
            raise ValueError("'Testtime[s]' is not monotonically increasing!")

        logging.info("Checking if SOC exists in dataframe...")
        if "SOC" in df_primitives.columns:
            logging.info("SOC already exists in df_primitives, skipping SOC calculation...")
        else:
            logging.info("SOC column does not exist in df_primitives, adding it...")
            df_primitives = add_soc(
                df_primitives,
                method="withResetWhenFullAndEmpty",
                max_Voltage=soc_max_voltage,
                min_Voltage=soc_min_voltage,
                C_ref=soc_c_ref
            )

        df_segments_and_sequences = extract_sequences(df_primitives, SEGMENT_SEQUENCE_CONFIG)

    else:
        raise ValueError("No df_primitives found!")

    logging.info("Calling iOCV detection...")
    # Get every iocv as df
    dfs_per_block = extract_ocv_iocv(
        min_pause_lenght=min_pause_lenght,
        min_loops=min_loops,
        visualize=False,
        df_primitives=df_primitives
    )

    # Compute SOC
    logging.info("Checking if SOC exists in dataframe...")
    if "SOC" in df_primitives.columns:
        logging.info("SOC already exists in df_primitives, skipping SOC calculation...")
    else:
        logging.info("SOC column does not exist in df_primitives, adding it...")
        df_primitives = add_soc(
            df_primitives.copy(),
            method="withResetWhenFullAndEmpty",
            max_Voltage=soc_max_voltage,
            min_Voltage=soc_min_voltage,
            C_ref=soc_c_ref
        )

    logging.info("Computing Capacity in Ah...")
    capacity_Ah_points = integrate.cumulative_trapezoid((df_primitives["Current[A]"]), x=df_primitives["Test_Time[s]"], initial=0) / 3600
    df_primitives["Capacity_Ah"] = capacity_Ah_points

    logging.info("Labeling DVA/ICA blocks (Charge/Discharge)...")
    dfs_with_type = []
    for df_block in dfs_per_block:
        if df_block.empty:
            continue

        first_id = df_block["ID"].iloc[0]
        matching_row = df_segments_and_sequences[df_segments_and_sequences["ID"] == first_id]

        if matching_row.empty:
            block_type = "Unknown"
        elif matching_row["Charge_iOCV"].iloc[0] != 0:
            block_type = "Charge"
        elif matching_row["Discharge_iOCV"].iloc[0] != 0:
            block_type = "Discharge"

        df_block["DVA_ICA_type"] = block_type
        dfs_with_type.append(df_block)

    dfs_per_block = dfs_with_type

    logging.info("Computing DVA and ICA for every block...")
    all_dva_ica_curves = []
    for idx, block in enumerate(dfs_per_block):
        df_dva_ica = df_primitives.loc[df_primitives["Test_Time[s]"].isin(block["Test_Time[s]"])]

        voltage = df_dva_ica["Voltage[V]"].to_numpy()
        capacity = df_dva_ica["Capacity_Ah"].to_numpy()

        dV = np.diff(voltage, prepend=np.nan)
        dQ = np.diff(capacity, prepend=np.nan)

        dv_dq = np.divide(dV, dQ)
        df_dva_ica["dV_dQ"] = dv_dq
        df_dva_ica["dQ_dV"] = 1 / df_dva_ica["dV_dQ"]

        if savgol:
            logging.info("Applying Savitzky-Golay filter...")
            window_length = int(len(df_dva_ica["dQ_dV"]) * savgol_window_lenght_percentage)
            if window_length % 2 == 0:
                window_length += 1
            window_length = max(window_length, 5)
            df_dva_ica["dQ_dV"] = savgol_filter(df_dva_ica["dQ_dV"], window_length, 2)

        df_dva_ica["DVA_ICA_type"] = block["DVA_ICA_type"].iloc[0]
        all_dva_ica_curves.append(df_dva_ica)

    if visualize:
        logging.info("Plotting DVA and ICA curves...")
        fig, (ax_dva, ax_ica) = plt.subplots(1, 2, figsize=(14, 6))

        charge_blocks = [df for df in all_dva_ica_curves if df["DVA_ICA_type"].iloc[0] == "Charge"]
        discharge_blocks = [df for df in all_dva_ica_curves if df["DVA_ICA_type"].iloc[0] == "Discharge"]

        # Plot charge
        for i, df_c in enumerate(charge_blocks):
            ax_dva.plot(df_c["SOC"], df_c["dV_dQ"], color="blue", label=f"Charge DVA {i + 1}")
            ax_ica.plot(df_c["SOC"], df_c["dQ_dV"], color="blue", label=f"Charge ICA {i + 1}")

        # Plot discharge
        for i, df_d in enumerate(discharge_blocks):
            ax_dva.plot(df_d["SOC"], df_d["dV_dQ"], color="red", label=f"Discharge DVA {i + 1}")
            ax_ica.plot(df_d["SOC"], df_d["dQ_dV"], color="red", label=f"Discharge ICA {i + 1}")

        # Set DVA plot properties
        ax_dva.set_xlabel("SOC", fontsize=15)
        ax_dva.set_ylabel("dV/dQ", fontsize=15, color="blue")
        ax_dva.set_title("Differential Voltage Analysis (DVA)", fontsize=15)
        ax_dva.set_ylim(0, 4.00)
        ax_dva.legend(fontsize=12, loc="upper left")
        ax_dva.grid(True, linestyle="--", alpha=0.7)
        ax_dva.tick_params(axis="both", which="major", labelsize=15)
        ax_dva.tick_params(axis="y", labelcolor="b")

        # Set ICA plot properties
        ax_ica.set_xlabel("SOC", fontsize=15)
        ax_ica.set_ylabel("dQ/dV", fontsize=15, color="blue")
        ax_ica.set_title("Incremental Capacity Analysis (ICA)", fontsize=15)
        ax_ica.legend(fontsize=12, loc="upper left")
        ax_ica.grid(True, linestyle="--", alpha=0.7)
        ax_ica.tick_params(axis="both", which="major", labelsize=15)
        ax_ica.tick_params(axis="y", labelcolor="b")

        plt.tight_layout()
        plt.show()
    logging.info("Returning DataFrame with all DVA and ICA Curves...")
    return pd.concat(all_dva_ica_curves, ignore_index=True)
