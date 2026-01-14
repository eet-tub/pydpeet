import gc
import glob
import os
import re

import numpy as np
import pandas as pd

import logging

from pydpeet.process.analyze.calculations.ageing import calculate_soh_loss_per_cycle, calculate_average_charge, \
    calculate_average_discharge, calculate_average_voltage, calculate_average_loading_voltage, \
    calculate_average_temperature
from pydpeet.process.analyze.calculations.capacity import add_soh
from pydpeet.process.merge.series import _sort_dfs, run_series
from pydpeet.process.analyze.calculations.throughput import calculate_average_negative_charge_throughput, calculate_average_positive_chargeThroughput
from pydpeet.process.analyze.calculations.utils import ColumnName, plot_axis_with_color, plot_columns, StepTimer, \
    plot_single_column_all_files
from matplotlib import pyplot as plt
import hvplot.pandas  # auto-registers hvPlot on DataFrames

from pydpeet.process.analyze.configs.battery_config import BatteryConfig, am23nmc

# for logging texts
def plot_soh_and_ce_two_dfs(df1, df2, label1="Cell1", label2="Cell2"):
    """
    Plot SOH (left y-axis) and Coulomb Efficiency (right y-axis) over Equivalent Full Cycles
    for two DataFrames on a single figure.

    Parameters
    ----------
    df1 : pd.DataFrame
        First DataFrame containing columns: 'EquivalentFullCycles', 'CoulombEfficiency', 'SOH'
    df2 : pd.DataFrame
        Second DataFrame with the same columns
    label1 : str
        Label for first DataFrame in legend
    label2 : str
        Label for second DataFrame in legend
    """
    x_column = "EquivalentFullCycles"

    fig, ax_soh = plt.subplots(figsize=(18, 6))
    ax_ce = ax_soh.twinx()  # right y-axis for Coulomb Efficiency

    # Colors and markers
    colors_soh = ["tab:blue", "tab:orange"]
    colors_ce = ["tab:green", "tab:red"]
    markers = ["o", "s"]

    # --- Plot SOH on left axis ---
    for i, df in enumerate([df1, df2]):
        valid = df["SOH"].notna()
        ax_soh.plot(
            df.loc[valid, x_column],
            df.loc[valid, "SOH"],
            linestyle=":",
            marker=markers[i],
            markersize=10,
            linewidth=3,
            color=colors_soh[i],
            label=f"{['SOH'][0]} - {label1 if i == 0 else label2}"
        )

    # --- Plot Coulomb Efficiency on right axis ---
    for i, df in enumerate([df1, df2]):
        valid = df["CoulombEfficiency"].notna()
        ax_ce.plot(
            df.loc[valid, x_column],
            df.loc[valid, "CoulombEfficiency"],
            linestyle="--",
            marker=markers[i],
            markersize=10,
            linewidth=3,
            color=colors_ce[i],
            label=f"{['Coulomb Efficiency'][0]} - {label1 if i == 0 else label2}"
        )

    # X-axis limits
    min_x = min(df1[x_column].min(), df2[x_column].min())
    max_x = max(df1[x_column].max(), df2[x_column].max())
    ax_soh.set_xlim(min_x, max_x)

    # Labels
    ax_soh.set_xlabel(x_column, fontsize=24)
    ax_soh.set_ylabel("SOH", fontsize=24, color="tab:blue")
    ax_ce.set_ylabel("Coulomb Efficiency", fontsize=24, color="tab:green")

    # Make second Y-axis share same ticks as first
    ax_ce.set_yticks(ax_soh.get_yticks())
    ax_ce.set_ylim(ax_soh.get_ylim())  # optional: ensures scales match exactly

    # Tick params
    ax_soh.tick_params(axis='y', labelcolor="tab:blue", labelsize=18)
    ax_ce.tick_params(axis='y', labelcolor="tab:green", labelsize=18)
    ax_soh.tick_params(axis='x', labelsize=18)

    # Grid
    ax_soh.grid(True, alpha=0.3)

    # Combine legends
    lines_soh, labels_soh = ax_soh.get_legend_handles_labels()
    lines_ce, labels_ce = ax_ce.get_legend_handles_labels()
    ax_soh.legend(lines_soh + lines_ce, labels_soh + labels_ce, fontsize=16)

    # Subtitle below plot
    ax_soh.text(
        0.5, -0.15,
        "SOH (left) and Coulomb Efficiency (right) over Equivalent Full Cycles",
        fontsize=28,
        ha="center",
        va="top",
        transform=ax_soh.transAxes
    )

    plt.tight_layout()
    plt.show()
    gc.collect()

    return fig, ax_soh, ax_ce

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
if __name__ == '__main__':

    # --- Load Data ---
    df_summary = pd.read_csv(
        r"D:\Programs\JetBrains\PyCharm Professional\pydpeet_neu\src\analysis\examples\benchmark_results_summary.csv"
    )

    # --- Prepare Data ---
    pivot_time = df_summary.pivot(index="group", columns="stage", values="avg_time_s").fillna(0)
    pivot_mem = df_summary.pivot(index="group", columns="stage", values="avg_mem_MB").fillna(0)

    # --- Create Subplots ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)

    # --- Common Style ---
    bar_kwargs = dict(rot=0, edgecolor="black", width=0.8)
    caption_fontsize = 32
    label_fontsize = 30
    tick_fontsize = 18

    # --- Time Plot ---
    pivot_time.plot(kind="bar", ax=axes[0], **bar_kwargs)
    axes[0].set_ylabel("Seconds", fontsize=label_fontsize)
    axes[0].set_xlabel("Group", fontsize=label_fontsize)
    axes[0].tick_params(axis="x", labelsize=tick_fontsize)
    axes[0].tick_params(axis="y", labelsize=tick_fontsize)
    axes[0].grid(True, which="major", linestyle="--", linewidth=2, alpha=0.7)
    axes[0].legend(title="Stage", fontsize=20, title_fontsize=22)

    # Add caption below the first plot
    axes[0].text(
        0.5, -0.12,
        "Average Time (s) by Group and Stage",
        ha='center', va='center',
        fontsize=caption_fontsize,
        transform=axes[0].transAxes
    )

    # --- Memory Plot ---
    pivot_mem.plot(kind="bar", ax=axes[1], **bar_kwargs)
    axes[1].set_ylabel("MB", fontsize=label_fontsize)
    axes[1].set_xlabel("Group", fontsize=label_fontsize)
    axes[1].tick_params(axis="x", labelsize=tick_fontsize)
    axes[1].tick_params(axis="y", labelsize=tick_fontsize)
    axes[1].grid(True, which="major", linestyle="--", linewidth=2, alpha=0.7)
    axes[1].legend(title="Stage", fontsize=18, title_fontsize=20)

    # Add caption below the second plot
    axes[1].text(
        0.5, -0.12,
        "Average Memory Delta (MB) by Group and Stage",
        ha='center', va='center',
        fontsize=caption_fontsize,
        transform=axes[1].transAxes
    )

    # --- Save and Show ---
    out_png = "benchmark_summary.png"
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.show()
    print(f"Saved figure -> {out_png}")

    # # Path to directory containing Parquet files
    # parquet_dir = r"D:\Programs\JetBrains\PyCharm Professional\pydpeet_neu\src\analysis\res\AM23NMC078"
    # # Get all Parquet files in directory
    # files = glob.glob(os.path.join(parquet_dir, "*.parquet"))
    # # Read each file into a DataFrame and store in a list
    # dfs = [pd.read_parquet(file) for file in files]
    # dfs_sorted = _sort_dfs(dfs)
    # df = run_series(dfs_sorted)
    # df.to_parquet(r"D:\Programs\JetBrains\PyCharm Professional\pydpeet_neu\src\analysis\res\AM23NMC078\AM23NMC078_series.parquet")



    # input_pathh = r"D:\Daten_BA\parquet_neu\Neware_Files_Merged_With_Extra_Columns\parquet_neu\Neware_Files_Merged_With_Extra_Columns\AM23NMC00053_with_extra_columns.parquet"
    #
    # input_pathh_2 = r"D:\Daten_BA\parquet_neu\Neware_Files_Merged_With_Extra_Columns\parquet_neu\Neware_Files_Merged_With_Extra_Columns\AM23NMC00054_with_extra_columns.parquet"
    #
    # cols = ["EquivalentFullCycles", "CoulombEfficiency", "SOH"]
    # df = pd.read_parquet(input_pathh, columns=cols)
    #
    # df_2 = pd.read_parquet(input_pathh_2, columns=cols)
    #
    #
    # plot_soh_and_ce_two_dfs(df, df_2, label1="AM23NMC00053", label2="AM23NMC00054")


    # plot_columns(df, columns=[ColumnName.SOH,ColumnName.INTERNAL_RESISTANCE,ColumnName.TEST_INDEX], x_column=ColumnName.EQUIVALENT_FULL_CYCLES)


    if False:
        input_dir = r"D:\Daten_BA\parquet_neu\Neware_Files_Merged_With_Extra_Columns\parquet_neu\Neware_Files_Extra_Columns_SOH_C_Ref_4.8"
        input_dir_og = r"D:\Daten_BA\parquet_neu\NAS_Basytec\Basytec_Files_Merged_With_Extra_Columns"
        output_dir = r"D:\Daten_BA\parquet_neu\NAS_Basytec\Basytec_Files_Extra_Columns_Added_Absolute_Time"

        os.makedirs(output_dir, exist_ok=True)

        cell_pattern = re.compile(r"(AM\d+NMC\d+)")

        for filename in os.listdir(input_dir):
            if not filename.endswith(".parquet"):
                continue

            match = cell_pattern.search(filename)
            if not match:
                print(f"Skipping {filename}, no valid cell ID found.")
                continue

            cell_id = match.group(1)
            input_path = os.path.join(input_dir, filename)

            # find matching file in input_dir_og by cell_id pattern
            og_matches = glob.glob(os.path.join(input_dir_og, f"*{cell_id}*.parquet"))
            if not og_matches:
                print(f"⚠️ No matching original file found for {cell_id}")
                continue
            input_path_og = og_matches[0]  # take the first match
            output_path = os.path.join(output_dir, f"{cell_id}_with_extra_columns_added_absolute_time.parquet")

            print(f"\nProcessing {filename} -> Cell {cell_id}")

            df = pd.read_parquet(input_path)
            x_axis = df["SOC"]
            y_axis = df["InternalResistance[ohm]"]
            colour_column = df["EquivalentFullCycles"]
            title = f"Internal Resistance [ohm] over SOC, colored by Equivalent Full Cycles (Cell: {cell_id})"

            xlabel = "SOC"
            ylabel = "Internal Resistance [ohm]"
            colour_label = "Equivalent Full Cycles"

            del df
            gc.collect()

            plot_axis_with_color(x_axis, y_axis, colour_column, title, xlabel, ylabel, colour_label)

            # # --- Load files ---
            # cols = ["Testtime[s]", "TestIndex", "Absolute Time[yyyy-mm-dd hh:mm:ss]"]
            # df = pd.read_parquet(input_path, columns=cols)
            # df_og = pd.read_parquet(input_path_og)
            #
            # # --- Print line counts ---
            # print(f"   📄 df (absolute time merged): {len(df):,} rows")
            # print(f"   📄 df_og (original):          {len(df_og):,} rows")
            #
            # # --- Map Absolute Time and Testindex based on Testtime[s] ---
            # # We'll join on "Testtime[s]" to align both DataFrames
            # df_out = df_og.merge(
            #     df[["Testtime[s]", "TestIndex", "Absolute Time[yyyy-mm-dd hh:mm:ss]"]],
            #     on="Testtime[s]",
            #     how="left",  # preserve all rows from df_og
            #     suffixes=("_old", "")
            # )
            #
            # del df, df_og
            # gc.collect()
            #
            # # Optional: drop old columns if you had them before merging
            # if "TestIndex_old" in df_out.columns:
            #     df_out.drop(columns=["TestIndex_old"], inplace=True)
            # if "Absolute Time[yyyy-mm-dd hh:mm:ss]_old" in df_out.columns:
            #     df_out.drop(columns=["Absolute Time[yyyy-mm-dd hh:mm:ss]_old"], inplace=True)
            #
            # # --- Ensure proper datetime format and sort by Absolute Time ---
            # time_col = "Absolute Time[yyyy-mm-dd hh:mm:ss]"
            # if df_out[time_col].dtype == object:
            #     df_out[time_col] = pd.to_datetime(df_out[time_col], errors="coerce")
            #
            # df_out = df_out.sort_values(by=time_col).reset_index(drop=True)
            #
            # # --- Save output ---
            # df_out.to_parquet(output_path, index=False)
            # print(f"✅ Saved: {output_path}")

            # del df_out
            # gc.collect()

    yes = False
    if yes:
        input_dir = r"D:\Daten_BA\parquet_neu\Neware_Files_Merged_With_Extra_Columns\parquet_neu\Neware_Files_Extra_Columns_SOH_C_Ref_4.8"
        output_dir = r"D:\Daten_BA\parquet_neu\Neware_Files_Merged_With_Extra_Columns\parquet_neu\Neware_Files_Extra_Columns_SOH_C_Ref_4.8"

        os.makedirs(output_dir, exist_ok=True)

        # Regex to extract e.g. AM23NMC00002
        cell_pattern = re.compile(r"(AM\d+NMC\d+)")

        for filename in os.listdir(input_dir):
            if not filename.endswith(".parquet"):
                continue

            match = cell_pattern.search(filename)
            if not match:
                print(f"Skipping {filename}, no valid cell ID found.")
                continue

            cell_id = match.group(1)
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{cell_id}_with_extra_columns.parquet")

            print(f"\nProcessing {filename} -> Cell {cell_id}")

            try:
                df = pd.read_parquet(input_path, engine = "pyarrow")
                plot_columns(df, columns=[ColumnName.CHARGE_THROUGHPUT, ColumnName.ABSOLUTE_CHARGE_THROUGHPUT])
                # df.drop('SOH', axis=1, inplace=True)
                # df = add_soh(df, config = am23nmc)
                # df.to_parquet(output_path, engine = "pyarrow")
                del df
                gc.collect()

            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue


    # df = pd.read_parquet(r"D:\Daten_BA\parquet_neu\Neware_Files_Merged_With_Extra_Columns\parquet_neu\Neware_Files_Merged_With_Extra_Columns\AM23NMC00001_with_extra_columns.parquet", engine="pyarrow")
    # plot_columns(df, columns=[ColumnName.CHARGE_THROUGHPUT, ColumnName.ABSOLUTE_CHARGE_THROUGHPUT])

    # df = pd.read_parquet(r"D:\Daten_BA\parquet_neu\NAS_Basytec\Basytec_Files_Extra_Columns_Soh_with_C_ref_4.8\AM23NMC078_with_extra_columns.parquet")
    # plot_columns(df, columns=[ColumnName.CAPACITY,ColumnName.VOLTAGE,ColumnName.INTERNAL_RESISTANCE,ColumnName.TEST_INDEX], x_column=ColumnName.EQUIVALENT_FULL_CYCLES)


    # input_dir = r"D:\Daten_BA\parquet_neu\NAS_Basytec\Basytec_Extra_Columns_with_absolute_Time"
    # plot_single_column_all_files(input_dir,column=ColumnName.SOH, cycler="Basytec",verbose=True)

    # columns = ["Testtime[s]", "ChargeThroughput[Ah]"]
    # df = pd.read_parquet(r"D:\Programs\JetBrains\PyCharm Professional\pydpeet_neu\src\analysis\res\AM23NMC00048_with_extra_columns.parquet", columns = columns)
    #
    # plt.plot(df["Testtime[s]"], df["ChargeThroughput[Ah]"])
    # plt.show()

    # --------------- Example for plotting columns (for whole directory) -------------------

    input_dir = r"D:\Daten_BA\parquet_neu\NAS_Basytec\Basytec_Extra_Columns_with_absolute_Time"
    # Regex to extract e.g. AM23NMC00002
    cell_pattern = re.compile(r"(AM\d+NMC\d+)")

    # Collect metrics for all cells
    results = []

    for filename in os.listdir(input_dir):
        if not filename.endswith(".parquet"):
            continue

        match = cell_pattern.search(filename)
        if not match:
            print(f"Skipping {filename}, no valid cell ID found.")
            continue

        cell_id = match.group(1)
        input_path = os.path.join(input_dir, filename)
        # cols = ["Testtime[s]","ChargeThroughput[Ah]","SOH", "EquivalentFullCycles", "Current[A]", "Temperature[°C]", "Voltage[V]"]
        cols = ["EquivalentFullCycles", "SOH"]
        df = pd.read_parquet(input_path, columns=cols)

        # avg_charge = calculate_average_charge(df)
        # avg_discharge = calculate_average_discharge(df)
        # avg_voltage = calculate_average_voltage(df)
        # avg_loading_voltage = calculate_average_loading_voltage(df)
        # avg_temperature = calculate_average_temperature(df)
        # soh_loss_per_cycle = calculate_soh_loss_per_cycle(df, verbose=False)

        df = df.sort_values("EquivalentFullCycles").reset_index(drop=True)

        dsoh = df["SOH"].diff()
        dcycles = df["EquivalentFullCycles"].diff()
        meansoh = df["SOH"].mean()

        # if avg_charge > 20:
        #     print(filename, avg_charge, soh_loss_per_cycle)
        # if avg_temperature > 26:
        #     print(filename, avg_temperature, soh_loss_per_cycle)

        # if avg_charge is not None and soh_loss_per_cycle is not None and avg_charge < 2.2:
        results.append({
            "CellID": cell_id,
            "dSOH": dsoh,
            "dCycles": dcycles,
            "SOH": df["SOH"].iloc[-1],
            "MeanSOH": meansoh,
            # "AvgChargeCurrent[A]": avg_charge,
            # "AvgDischargeCurrent[A]": avg_discharge,
            # "AvgTemperature[°C]": avg_temperature,
            # "AvgVoltage[V]": avg_voltage,
            # "AvgLoadingVoltage[V]": avg_loading_voltage,
            # "SOH_Loss_per_Cycle": soh_loss_per_cycle
        })
        print(f"result appended for {cell_id}")
        # df = calculate_soh_loss_over_charging(df, verbose=False)
        # plot_columns(df, columns=[ColumnName.VOLTAGE])
        del df
        gc.collect()

    df_plot = pd.DataFrame(results)

    del results
    gc.collect()

    x_axis = pd.concat(df_plot["dCycles"].values).reset_index(drop=True)
    y_axis = pd.concat(df_plot["dSOH"].values).reset_index(drop=True)
    colour_column = pd.concat(
        [pd.Series([soh] * len(d)) for d, soh in zip(df_plot["dCycles"], df_plot["MeanSOH"])]
    ).reset_index(drop=True)
    title = "ΔSOH over ΔCycles (colored by SOH) Basytec"
    x_label = "Δ Equivalent Full Cycles"
    ylabel = "ΔSOH"

    plot_axis_with_color(x_axis=x_axis, y_axis=y_axis, colour_column=colour_column, title=title, xlabel=x_label,
                         ylabel=ylabel)

    # plot_columns(df_merged, columns=[ColumnName.CURRENT, ColumnName.VOLTAGE
    #                                   ,ColumnName.SOC, ColumnName.CAPACITY, ColumnName.SOH
    #                                   ,ColumnName.INTERNAL_RESISTANCE, ColumnName.COULOMB_EFFICIENCY
    #                                   ])
    # print(calculate_average_charge(df_merged))
    # print(calculate_average_discharge(df_merged))
    # print("Soh loss: " + str(calculate_soh_loss(df_merged, verbose=False)))
    # print("Soh loss per Cycle: " + str(calculate_soh_loss_per_cycle(df_merged, verbose = False)))
    #
    # plot_columns(df_merged, columns=[ColumnName.SOH])

    # Convert to DataFrame


    # from sklearn.metrics import r2_score
    # # Plot all cells in one scatter plot
    # fig, ax = plt.subplots(figsize=(18, 8))
    #
    # ax.scatter(
    #     df_metrics["AvgChargeCurrent[A]"],
    #     df_metrics["SOH_Loss_per_Cycle"],
    #     s=80,
    #     alpha=0.8,
    #     edgecolor='k'
    # )
    #
    # # Linear trendline
    # if len(df_metrics) > 1:
    #     x = df_metrics["AvgChargeCurrent[A]"].values
    #     y = df_metrics["SOH_Loss_per_Cycle"].values
    #
    #     z = np.polyfit(x, y, 1)
    #     p = np.poly1d(z)
    #
    #     sort_idx = np.argsort(x)
    #     ax.plot(x[sort_idx], p(x)[sort_idx], "r--", label=f"Trend: y={z[0]:.2e}x+{z[1]:.2e}", linewidth = 4)
    #
    #     # R²
    #     r2 = r2_score(y, p(x))
    #     ax.text(
    #         0.05, 0.95,
    #         f"$R^2$ = {r2:.4f}",
    #         transform=ax.transAxes,
    #         fontsize=30,
    #         verticalalignment='top'
    #     )
    #
    # # Labels and ticks
    # ax.set_xlabel("AvgChargeCurrent [A]", fontsize=30)
    # ax.set_ylabel("SOH Loss per Cycle", fontsize=30)
    # ax.tick_params(axis='both', which='major', labelsize=20)
    #
    # # Subtitle below the plot (instead of title)
    # ax.text(
    #     0.5, -0.15,  # position relative to axes
    #     "SOH Loss per Cycle vs Average Charge Current (Neware)",
    #     fontsize=28,
    #     ha="center",
    #     va="top",
    #     transform=ax.transAxes
    # )
    #
    # # Grid and legend
    # ax.grid(True, alpha=0.3)
    # ax.legend(fontsize=30)
    #
    # # Adjust layout and add more space below for subtitle
    # plt.tight_layout()
    # plt.subplots_adjust(bottom=0.2)
    # plt.show()

    #
    # # plot_single_column_all_files(input_dir, column = ColumnName.SOH, cell_pattern=cell_pattern, verbose=True)


    # ---------------------------------------------------------------------------------------------------------

    # # --- CONFIGURATION ---
    # input_file = r"D:\Daten_BA\parquet_neu\Basytec_Files_Merged_With_Extra_Columns\AM23NMC081_with_extra_columns.parquet"  # path to your original parquet file
    # output_file = r"D:\Daten_BA\parquet_neu\Basytec_Files_Merged_With_Extra_Columns\AM23NMC081_with_extra_columns_cut.parquet"  # path to save the filtered parquet
    # days_to_keep = 68  # number of days you want to keep
    #
    # # --- LOAD PARQUET FILE ---
    # df = pd.read_parquet(input_file)
    #
    # # --- CONVERT DAYS TO SECONDS ---
    # seconds_limit = days_to_keep * 24 * 60 * 60  # 1 day = 86400 seconds
    #
    # # --- FILTER DATA ---
    # df_cut = df[df["Testtime[s]"] <= seconds_limit]
    #
    # # --- SAVE NEW PARQUET FILE ---
    # df_cut.to_parquet(output_file, index=False)
    #
    # print(f"✅ File saved: {output_file}")
    # print(f"Original rows: {len(df)}, kept rows: {len(df_cut)}")
    #
    #
    use = False
    if use:
        import pyarrow as pa
        import pyarrow.parquet as pq
        #
        # # === CONFIG ===
        input_dir = r"D:\Daten_BA\parquet_neu\NAS_Basytec\Basytec_Extra_Columns_with_absolute_Time"
        output_dir = r"D:\Daten_BA\parquet_neu\NAS_Basytec\Analysis"
        output_path = os.path.join(output_dir, "BasytecFiles_with_charge_and_discharge_current_avg.parquet")
        cell_pattern = re.compile(r"(AM\d+NMC\d+)")
        CHUNK_LIMIT = 1_000_000  # how many rows to buffer before writing to disk

        # === SETUP ===
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # remove old output file if it exists
        if os.path.exists(output_path):
            os.remove(output_path)

        results_buffer = []

        # === MAIN LOOP ===
        for filename in os.listdir(input_dir):
            if not filename.endswith(".parquet"):
                continue

            match = cell_pattern.search(filename)
            if not match:
                continue

            cell_id = match.group(1)
            input_path = os.path.join(input_dir, filename)

            with StepTimer(verbose=True) as st:
                cols = ["Current[A]", "InternalResistance[ohm]", "EquivalentFullCycles", "SOH"]
                df = pd.read_parquet(input_path, columns=cols, engine="pyarrow")
                st.log("read parquet")

                if len(df) < 2:
                    continue

                df = df.sort_values("EquivalentFullCycles").reset_index(drop=True)

                soh = df["SOH"]
                dSOH = df["SOH"].diff()
                dCycles = df["EquivalentFullCycles"].diff()

                soh_per_cycle = -dSOH / dCycles
                soh_loss_per_cycle = calculate_soh_loss_per_cycle(df, verbose=False)
                avg_charge = calculate_average_charge(df)
                avg_discharge = calculate_average_discharge(df)

                valid = dCycles > 0
                for i in df[valid].index:
                    results_buffer.append({
                        "CellID": cell_id,
                        "dSoh": dSOH,
                        "dCycles": dCycles,
                        "SOH" : soh
                    })

                st.log(f"calculated results for {filename}")

                # === Incremental flush ===
                if len(results_buffer) >= CHUNK_LIMIT:
                    df_chunk = pd.DataFrame(results_buffer)
                    table = pa.Table.from_pandas(df_chunk, preserve_index=False)
                    pq.write_to_dataset(table, root_path=output_path)
                    print(f"💾 Flushed {len(df_chunk):,} rows to {output_path}")
                    results_buffer.clear()
                    gc.collect()

        # === Final flush ===
        if results_buffer:
            df_chunk = pd.DataFrame(results_buffer)
            table = pa.Table.from_pandas(df_chunk, preserve_index=False)
            pq.write_to_dataset(table, root_path=output_path)
            print(f"💾 Final flush: {len(df_chunk):,} rows written.")
            results_buffer.clear()
            gc.collect()

        print("✅ All files processed and written to disk incrementally.")

        # === Optional: Load the combined parquet back in one go (if small enough)
        df_metrics = pq.read_table(output_path).to_pandas()
        print(f"\nFinal dataset shape: {df_metrics.shape}")



        # # === PLOT ===
        # import matplotlib.pyplot as plt
        #
        # plt.close("all")
        # fig, ax = plt.subplots(figsize=(18, 6))
        #
        # ax.scatter(
        #     df_metrics["avgChargeCurrent"],
        #     df_metrics["soh_loss_per_cycle"],
        #     s=80,
        #     alpha=0.8,
        #     edgecolor='k'
        # )
        #
        # # Optional linear trendline
        # if len(df_metrics) > 1:
        #     z = np.polyfit(df_metrics["avgChargeCurrent"], df_metrics["soh_loss_per_cycle"], 1)
        #     p = np.poly1d(z)
        #     ax.plot(
        #         df_metrics["avgChargeCurrent"],
        #         p(df_metrics["avgChargeCurrent"]),
        #         "r--",
        #         label=f"Trend: y={z[0]:.2e}x+{z[1]:.2e}"
        #     )
        #
        # ax.set_xlabel("Average Charge Current [A]", fontsize=30)
        # ax.set_ylabel("SOH Loss per Cycle", fontsize=30)
        # ax.tick_params(axis='both', which='major', labelsize=20)
        #
        # ax.text(
        #     0.5, -0.18,
        #     "SOH Loss per Cycle over Average Charge Current (Basytec)",
        #     fontsize=28,
        #     ha="center",
        #     va="top",
        #     transform=ax.transAxes
        # )
        #
        # ax.grid(True, alpha=0.3)
        # # ax.legend(fontsize=14)
        # #
        # # fig.tight_layout()
        # fig.subplots_adjust(bottom=0.25)
        #
        # plt.show()

        # import panel as pn
        #
        # pn.extension('bokeh')  # load Bokeh backend
        #
        # # Create interactive Datashader scatter plot
        # plot = df_metrics.hvplot.scatter(
        #     x='avgChargeCurrent',
        #     y='soh_loss_per_cycle',
        #     datashade=True,  # enables Datashader
        #     cmap='viridis',
        #     width=800,
        #     height=600,
        #     title="SOH Loss per Cycle over Average Charge Current (Basytec)",
        #     xlabel="Average Charge Current [A]",
        #     ylabel="SOH Loss per Cycle",
        # )
        #
        # # Serve the interactive plot in a browser window
        # pn.panel(plot).show()
        # ---------------------------------------------------------------------------------------


        # Scatterplot: ΔSOH over ΔCycles
        df_plot = pd.DataFrame(results)

        # Plot delta Soh over delta Cycles
        x_axis = df_plot["dCycles"]
        y_axis = df_plot["dsoh"]
        colour_column = df_plot["MeanSOH"]
        title = "ΔSOH over ΔCycles (colored by SOH) Basytec"
        x_label = "Δ Equivalent Full Cycles"
        ylabel = "ΔSOH"

        plot_axis_with_color(x_axis = x_axis, y_axis = y_axis, colour_column = colour_column, title = title, xlabel = x_label, ylabel = ylabel)


        # x_axis = df_plot["avgChargeCurrent"]
        # y_axis = df_plot["soh_loss_per_cycle"]
        # colour_column = None
        # title = "Soh loss per Cycle over average charge current Basytec"
        # x_label = "Average Charge Current [A]"
        # ylabel = "Soh loss per Cycle"
        #
        # logging.info("")
        # plot_axis_with_color(x_axis=x_axis, y_axis=y_axis, colour_column=colour_column, title=title, xlabel=x_label,
        #                      ylabel=ylabel, plot_colourbar=False)

        # for filename in os.listdir(input_dir):
        #     if not filename.endswith(".parquet"):
        #         continue
        #
        #     match = cell_pattern.search(filename)
        #     if not match:
        #         print(f"Skipping {filename}, no valid cell ID found.")
        #         continue
        #
        #     cell_id = match.group(1)
        #     input_path = os.path.join(input_dir, filename)
        #     cols = ["ChargeThroughput[Ah]","SOH", "EquivalentFullCycles", "Current[A]"]
        #     df = pd.read_parquet(input_path, columns=cols)
        #
        #     avg_charge = calculate_average_charge(df)
        #     avg_discharge = calculate_average_discharge(df)
        #     soh_loss_per_cycle = calculate_soh_loss_per_cycle(df, verbose=False)
        #
        #     print(avg_charge)
        #     if avg_charge > 20:
        #         print(filename, avg_charge, soh_loss_per_cycle)
        #
        #     if avg_charge is not None and soh_loss_per_cycle is not None:
        #         results.append({
        #             "CellID": cell_id,
        #             "AvgChargeCurrent[A]": avg_charge,
        #             "AvgDischargeCurrent[A]": avg_discharge,
        #             "SOH_Loss_per_Cycle": soh_loss_per_cycle
        #         })
        #
        #     df = calculate_soh_loss_over_charging(df, verbose=False)
        #
        #     del df




