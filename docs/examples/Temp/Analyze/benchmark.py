"""
benchmark_end_to_end.py

End-to-end benchmark:
 - Stage A: group-by-cell -> read many parquet chunks -> _sort_dfs -> run_series -> write merged parquet
 - Stage B: read merged parquet -> full add_new_columns pipeline (CampaignBuilder, step_analyzer_primitives, etc.) -> write final parquet

Metrics captured per cell/run:
 - total_time_s (per stage)
 - memory_delta_MB (per stage)
 - read_MB, write_MB (per stage)
 - success flag and optional error message

Outputs:
 - benchmark_results_raw.csv (all runs)
 - benchmark_results_summary.csv (averaged over repeats)
 - benchmark_summary.png (visual)
"""

import os
import re
import time
import gc
import psutil
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import List, Tuple, Dict

# ------------------- CONFIG -------------------

# Input folders (your provided structure)
PATHS = {
    "big": r"D:\Daten_BA\Benchmark\Basytec_Raw_Parquet\big",
    "medium": r"D:\Daten_BA\Benchmark\Basytec_Raw_Parquet\medium",
    "small": r"D:\Daten_BA\Benchmark\Basytec_Raw_Parquet\small",
}

# Where to write merged & final outputs
MERGED_OUTPUT_ROOT = r"D:\Daten_BA\Benchmark\Merged_Output"
EXTRA_OUTPUT_ROOT = r"D:\Daten_BA\Benchmark\Extra_Columns_Output"

os.makedirs(MERGED_OUTPUT_ROOT, exist_ok=True)
os.makedirs(EXTRA_OUTPUT_ROOT, exist_ok=True)

REPEATS = 3                # number of repeated runs per cell
CELLS_PER_GROUP = 2        # how many cells to pick from each group (2 big, 2 medium, 2 small)
FORCE_RECREATE_MERGED = True   # if True, always re-run merge instead of skipping existing merged files
FORCE_RECREATE_EXTRA = True    # if True, always re-run add_new_columns instead of skipping existing outputs

# Behavior toggles used by add_new_columns stage
neware_bool = False                  # set True if your data is Neware type (affects thresholds)

# -------------------------------------------------
# Replace this import line with the module that contains your pipeline functions / constants.
# Example: "from my_battery_pipeline import _sort_dfs, run_series, CampaignBuilder, ..."
# -------------------------------------------------
import gc
import os
import re

import pandas as pd

import logging

import pyarrow

from pydpeet.process.analyze.calculations.efficiency import add_internal_resistance, add_coulomb_efficiency
from pydpeet.process.analyze.calculations.throughput import calculate_average_positive_chargeThroughput, calculate_average_negative_charge_throughput
from pydpeet.process.analyze.calculations.utils import plot_columns, ColumnName, plot_single_column_all_files
from pydpeet.process.analyze.configs.step_analyzer_config import STEP_ANALYZER_PRIMITIVES_CONFIG, SEGMENT_SEQUENCE_CONFIG, \
    THRESHOLD_DICT
from pydpeet.process.analyze.calculations.campaign import CampaignBuilder
from pydpeet.process.merge.series import run_series, _sort_dfs
from pydpeet.process.analyze.calculations.soc_methods import SocMethod
from pydpeet.process.analyze.configs.battery_config import am23nmc


from pydpeet.convert.configs.config import Config
from pydpeet.convert.convert import convert
from pydpeet.convert.directory_standardization import directory_standardization
from pydpeet.convert.export import export
from pydpeet.process.sequence.old_utils.CONFIG_function_calls import THRESHOLD_DICT_NEWARE
from pydpeet.process.sequence.step_analyzer import step_analyzer_primitives, step_analyzer_seqments_and_sequences
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
from collections import defaultdict

from pydpeet.process.sequence.utils.preprocessing.calculate_thresholds import calculate_minimum_definitive_differences
# -------------------------------------------------
# Ensure you replace 'your_module' with the real module name before running.
# -------------------------------------------------

CELL_REGEX = re.compile(r"(AM\d+NMC\d+)")

# ------------------- HELPERS -------------------

def bytes_to_mb(b: int) -> float:
    return b / (1024 ** 2)

def safe_concat_if_needed(result_df, dfs_sorted: List[pd.DataFrame], cell_id: str):
    """If run_series returned None or empty, fall back to concatenating the sorted dfs."""
    if result_df is None or (hasattr(result_df, "empty") and result_df.empty):
        print(f"[WARN] run_series returned empty/None for {cell_id} — falling back to pd.concat of chunks")
        try:
            fallback = pd.concat(dfs_sorted, ignore_index=True)
        except Exception as e:
            raise RuntimeError(f"Fallback concat failed for {cell_id}: {e}")
        return fallback
    return result_df

# ------------------- STAGE A: Merge per cell -------------------

def merge_cell(file_list: List[str], output_path: str, cell_id: str) -> Dict:
    """Read many parquet files, sort/process with your functions, write merged parquet.
       Returns metrics dict.
    """
    metrics = {
        "stage": "merge",
        "cell": cell_id,
        "success": False,
        "error": None,
        "time_s": None,
        "mem_delta_MB": None,
        "read_MB": None,
        "write_MB": None,
    }

    # compute read size
    try:
        read_bytes = sum(os.path.getsize(p) for p in file_list)
    except Exception as e:
        read_bytes = 0
    read_MB = bytes_to_mb(read_bytes)

    proc = psutil.Process(os.getpid())
    mem_before = proc.memory_info().rss / (1024 ** 2)
    t0 = time.time()

    try:
        # Step 4: Read list of DataFrames
        dfs = [pd.read_parquet(f) for f in file_list]

        # Step 5: sort + process
        dfs_sorted = _sort_dfs(dfs)

        # allow run_series to operate
        merged_df = run_series(dfs_sorted)

        # fallback if run_series returns Nothing/empty
        merged_df = safe_concat_if_needed(merged_df, dfs_sorted, cell_id)

        # Step 6: Save merged DataFrame
        merged_df.to_parquet(output_path, index=False)

        # gather write size after saving
        write_MB = bytes_to_mb(os.path.getsize(output_path)) if os.path.exists(output_path) else 0.0

        t1 = time.time()
        mem_after = proc.memory_info().rss / (1024 ** 2)

        metrics.update({
            "success": True,
            "time_s": t1 - t0,
            "mem_delta_MB": mem_after - mem_before,
            "read_MB": read_MB,
            "write_MB": write_MB,
        })

        # cleanup
        del dfs, dfs_sorted, merged_df
        gc.collect()

    except Exception as e:
        metrics.update({
            "success": False,
            "error": str(e),
            "time_s": time.time() - t0,
            "mem_delta_MB": (proc.memory_info().rss / (1024 ** 2)) - mem_before,
            "read_MB": read_MB,
            "write_MB": 0.0,
        })
        print(f"[ERROR] merge_cell {cell_id}: {e}")

    return metrics

# ------------------- STAGE B: Add new columns (your full pipeline) -------------------

def add_columns_cell(merged_input_path: str, output_path: str, cell_id: str) -> Dict:
    """Run the full add_new_columns pipeline for one merged file.
       Returns metrics dict (time, memory, read/write MB).
    """
    metrics = {
        "stage": "add_columns",
        "cell": cell_id,
        "success": False,
        "error": None,
        "time_s": None,
        "mem_delta_MB": None,
        "read_MB": None,
        "write_MB": None,
    }

    if not os.path.exists(merged_input_path):
        metrics.update({"error": "merged input does not exist", "read_MB": 0.0, "write_MB": 0.0})
        print(f"[ERROR] add_columns_cell: merged input missing for {cell_id}: {merged_input_path}")
        return metrics

    read_MB = bytes_to_mb(os.path.getsize(merged_input_path))

    proc = psutil.Process(os.getpid())
    mem_before = proc.memory_info().rss / (1024 ** 2)
    t0 = time.time()

    try:
        # Load merged parquet
        df_merged = pd.read_parquet(merged_input_path, engine="pyarrow")

        # Initialize builder
        builder = (
            CampaignBuilder(df_merged, verbose=False)
            .set_config(config=am23nmc)
            .set_cell_name(name=cell_id)
        )

        # Build campaign base
        campaign = builder.build()

        # free original df_merged
        del df_merged
        gc.collect()

        # compute thresholds
        if neware_bool:
            MIN_DEFINITIVE_VOLTAGE_DIFFERENCE, MIN_DEFINITIVE_CURRENT_DIFFERENCE = \
                calculate_minimum_definitive_differences(*THRESHOLD_DICT)
        else:
            MIN_DEFINITIVE_VOLTAGE_DIFFERENCE = 0.001
            MIN_DEFINITIVE_CURRENT_DIFFERENCE = 0.001

        SEGMENTS_TO_DETECT_CONFIG = [
            ("Voltage[V]", MIN_DEFINITIVE_VOLTAGE_DIFFERENCE / 2),
            ("Current[A]", MIN_DEFINITIVE_CURRENT_DIFFERENCE / 2),
            ("Power[W]", (MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE) / 2),
        ]
        ADJUST_SEGMENTS_CONFIG = [
            ("Voltage[V]", MIN_DEFINITIVE_VOLTAGE_DIFFERENCE),
            ("Current[A]", MIN_DEFINITIVE_CURRENT_DIFFERENCE),
            ("Power[W]", (MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE)),
        ]

        THRESHOLD_CV_SEGMENTS_0A_END = MIN_DEFINITIVE_CURRENT_DIFFERENCE

        # run step analyzer primitive
        df_primitives = step_analyzer_primitives(
            campaign,
            STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
            SEGMENTS_TO_DETECT_CONFIG=SEGMENTS_TO_DETECT_CONFIG,
            ADJUST_SEGMENTS_CONFIG=ADJUST_SEGMENTS_CONFIG,
            check_CV_0Aend_segments_bool=neware_bool,
            WIDEN_CONSTANT_SEGMENTS_BOOL=neware_bool,
            check_zero_length_segments_bool=neware_bool
        )

        df_segments_and_sequences = step_analyzer_seqments_and_sequences(
            df_primitives,
            SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG
        )

        # Filter for charge/discharge blocks
        dfs_per_block_charge, _ = filter_and_split_df_by_blocks(
            df_segments_and_sequences=df_segments_and_sequences,
            df_primitives=df_primitives,
            rules=['CCCV_Charge'],
            combine_op='or',
            also_return_filtered_df=True
        )

        dfs_per_block_Discharge, _ = filter_and_split_df_by_blocks(
            df_segments_and_sequences=df_segments_and_sequences,
            df_primitives=df_primitives,
            rules=['CCCV_Discharge'],
            combine_op='or',
            also_return_filtered_df=True
        )

        dfs_per_block_charge = _sort_dfs(dfs_per_block_charge)
        dfs_per_block_Discharge = _sort_dfs(dfs_per_block_Discharge)

        # Run the builder column additions
        builder.set_df(campaign)

        # Columns requiring df_primitives
        builder.add_capacity(df_primitives, neware_bool)
        builder.add_soh(df_primitives, neware_bool)
        builder.add_soc(
            df_primitives, neware_bool,
            standard_method=SocMethod.WITH_RESET_WHEN_FULL_AND_EMPTY,
            methods=[SocMethod.WITH_RESET_WHEN_FULL_AND_EMPTY, SocMethod.WITHOUT_RESET],
            restart_for_testindex=True
        )

        # free heavy primitives and segment structures
        del df_primitives, df_segments_and_sequences
        gc.collect()

        # add columns using charge/discharge splits
        builder.add_charge_throughput()
        builder.add_coulomb_efficiency(dfs_per_block_charge, dfs_per_block_Discharge)
        builder.add_power()
        builder.add_cumulative_energy()
        builder.add_equivalent_full_cycles()
        builder.add_internal_resistance(ignore_negative_resistance_values=False)

        del dfs_per_block_charge, dfs_per_block_Discharge
        gc.collect()

        # Save processed DataFrame
        final_df = builder.build()
        final_df.to_parquet(output_path, index=False)
        write_MB = bytes_to_mb(os.path.getsize(output_path)) if os.path.exists(output_path) else 0.0

        t1 = time.time()
        mem_after = proc.memory_info().rss / (1024 ** 2)

        metrics.update({
            "success": True,
            "time_s": t1 - t0,
            "mem_delta_MB": mem_after - mem_before,
            "read_MB": read_MB,
            "write_MB": write_MB,
        })

        # cleanup
        del final_df
        gc.collect()

    except Exception as e:
        metrics.update({
            "success": False,
            "error": str(e),
            "time_s": time.time() - t0,
            "mem_delta_MB": (psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)) - mem_before,
            "read_MB": read_MB,
            "write_MB": 0.0,
        })
        print(f"[ERROR] add_columns_cell {cell_id}: {e}")

    return metrics

# ------------------- DRIVER: full end-to-end benchmark -------------------

def collect_cell_files_from_folder(folder: str) -> Dict[str, List[str]]:
    """Group files by regex cell id in a given folder"""
    grouped = defaultdict(list)
    for fname in os.listdir(folder):
        if not fname.endswith(".parquet"):
            continue
        match = CELL_REGEX.search(fname)
        if match:
            cell = match.group(1)
            grouped[cell].append(os.path.join(folder, fname))
    # sort lists for deterministic ordering
    for k in grouped:
        grouped[k].sort()
    return grouped

def run_benchmark():
    results = []
    for group_name, input_folder in PATHS.items():
        if not os.path.isdir(input_folder):
            print(f"[WARN] input folder not found for group {group_name}: {input_folder} — skipping")
            continue

        print(f"\n=== Group: {group_name} | input: {input_folder} ===")
        grouped = collect_cell_files_from_folder(input_folder)
        if not grouped:
            print(f"[WARN] no parquet files found in {input_folder}")
            continue

        # pick up to CELLS_PER_GROUP distinct cells
        picked_cells = list(grouped.items())[:CELLS_PER_GROUP]

        merged_group_out = os.path.join(MERGED_OUTPUT_ROOT, group_name)
        extra_group_out = os.path.join(EXTRA_OUTPUT_ROOT, group_name)
        os.makedirs(merged_group_out, exist_ok=True)
        os.makedirs(extra_group_out, exist_ok=True)

        for cell_id, files in picked_cells:
            print(f"\n--- Benchmarking cell {cell_id} with {len(files)} chunk files ---")

            merged_path = os.path.join(merged_group_out, f"{cell_id}_series.parquet")
            extra_path = os.path.join(extra_group_out, f"{cell_id}_with_extra_columns.parquet")

            for run_idx in range(REPEATS):
                print(f"\nRun {run_idx + 1}/{REPEATS} — cell {cell_id}")

                # Merge stage: optionally recreate merged each run
                if FORCE_RECREATE_MERGED or not os.path.exists(merged_path):
                    m_metrics = merge_cell(files, merged_path, cell_id)
                else:
                    print(f"[SKIP] merge already exists: {merged_path}")
                    # if skipping, set dummy metrics with zeros
                    m_metrics = {
                        "stage": "merge",
                        "cell": cell_id,
                        "success": True,
                        "error": None,
                        "time_s": 0.0,
                        "mem_delta_MB": 0.0,
                        "read_MB": sum(bytes_to_mb(os.path.getsize(p)) for p in files),
                        "write_MB": bytes_to_mb(os.path.getsize(merged_path)) if os.path.exists(merged_path) else 0.0,
                    }
                # Add-columns stage: optionally recreate
                if FORCE_RECREATE_EXTRA or not os.path.exists(extra_path):
                    a_metrics = add_columns_cell(merged_path, extra_path, cell_id)
                else:
                    print(f"[SKIP] add_columns already exists: {extra_path}")
                    a_metrics = {
                        "stage": "add_columns",
                        "cell": cell_id,
                        "success": True,
                        "error": None,
                        "time_s": 0.0,
                        "mem_delta_MB": 0.0,
                        "read_MB": bytes_to_mb(os.path.getsize(merged_path)) if os.path.exists(merged_path) else 0.0,
                        "write_MB": bytes_to_mb(os.path.getsize(extra_path)) if os.path.exists(extra_path) else 0.0,
                    }

                # stamp metadata
                for d in (m_metrics, a_metrics):
                    d.update({
                        "group": group_name,
                        "run": run_idx + 1,
                        "files_count": len(files),
                        "merged_path": merged_path,
                        "extra_path": extra_path
                    })
                    results.append(d)

    return results

# ------------------- RUN + SAVE + PLOT -------------------

if __name__ == "__main__":
    print("Starting end-to-end benchmark (merge -> add_columns)...")
    bench_results = run_benchmark()

    if not bench_results:
        print("No results collected — check input folders and module imports.")
    else:
        df_raw = pd.DataFrame(bench_results)
        raw_csv = "benchmark_results_raw.csv"
        summary_csv = "benchmark_results_summary.csv"
        df_raw.to_csv(raw_csv, index=False)
        print(f"Saved raw results -> {raw_csv}")

        # compute averages grouped by (group, stage)
        df_summary = (
            df_raw.groupby(["group", "stage"], as_index=False)
            .agg({
                "time_s": "mean",
                "mem_delta_MB": "mean",
                "read_MB": "mean",
                "write_MB": "mean",
                "success": "all"
            })
            .rename(columns={
                "time_s": "avg_time_s",
                "mem_delta_MB": "avg_mem_MB",
                "read_MB": "avg_read_MB",
                "write_MB": "avg_write_MB"
            })
        )
        df_summary.to_csv(summary_csv, index=False)
        print(f"Saved summary -> {summary_csv}")

        # Simple visual: two subplots: avg time & avg memory per group/stage
        pivot_time = df_summary.pivot(index="group", columns="stage", values="avg_time_s").fillna(0)
        pivot_mem = df_summary.pivot(index="group", columns="stage", values="avg_mem_MB").fillna(0)

        fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)

        # Common style parameters
        bar_kwargs = dict(rot=0, edgecolor="black", width=0.8)
        title_fontsize = 30
        label_fontsize = 30
        tick_fontsize = 18

        # --- Time Plot ---
        pivot_time.plot(kind="bar", ax=axes[0], **bar_kwargs)
        axes[0].set_title("Average Time (s) by Group and Stage", fontsize=title_fontsize, weight="bold")
        axes[0].set_ylabel("Seconds", fontsize=label_fontsize)
        axes[0].set_xlabel("Group", fontsize=label_fontsize)
        axes[0].tick_params(axis="x", labelsize=tick_fontsize)
        axes[0].tick_params(axis="y", labelsize=tick_fontsize)
        axes[0].grid(True, which="major", linestyle="--", linewidth=0.7, alpha=0.7)
        axes[0].legend(title="Stage", fontsize=11, title_fontsize=12)

        # --- Memory Plot ---
        pivot_mem.plot(kind="bar", ax=axes[1], **bar_kwargs)
        axes[1].set_title("Average Memory Delta (MB) by Group and Stage", fontsize=title_fontsize, weight="bold")
        axes[1].set_ylabel("MB", fontsize=label_fontsize)
        axes[1].set_xlabel("Group", fontsize=label_fontsize)
        axes[1].tick_params(axis="x", labelsize=tick_fontsize)
        axes[1].tick_params(axis="y", labelsize=tick_fontsize)
        axes[1].grid(True, which="major", linestyle="--", linewidth=0.7, alpha=0.7)
        axes[1].legend(title="Stage", fontsize=11, title_fontsize=12)

        # --- Save and Show ---
        out_png = "benchmark_summary.png"
        plt.savefig(out_png, dpi=200, bbox_inches="tight")
        plt.show()
        print(f"Saved figure -> {out_png}")

    print("Benchmark finished.")
