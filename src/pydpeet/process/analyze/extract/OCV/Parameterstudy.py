import pandas
import pandas as pd
from pathlib import Path
from sklearn.metrics import r2_score
import numpy as np
from joblib import Parallel, delayed, cpu_count
from pydpeet.Analysis.AgeingDataAna import add_soc
from FUDS_extrapolated import process_fuds_extrapolation

from tsmoothie.smoother import *

# Files for segments, iocv_discharge and FUDS dataframes
base_dir_seg = Path(r"C:\python projekte\BA_Repo\pydpeet\src\Alex_BA\res\BA\Parameter_studie\03_StepAnalyzerSeg")
seg_1 = pd.read_parquet(
    base_dir_seg / "20231027183923-CheckUp-1-2-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_2 = pd.read_parquet(
    base_dir_seg / "20231129133302-CheckUp-3-7-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_3 = pd.read_parquet(
    base_dir_seg / "20231212150550-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_4 = pd.read_parquet(
    base_dir_seg / "20240216101054-CheckUp-3-8-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_5 = pd.read_parquet(
    base_dir_seg / "20240321173721-CheckUp-1-6-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_6 = pd.read_parquet(
    base_dir_seg / "20240503100606-CheckUp-3-8-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_7 = pd.read_parquet(
    base_dir_seg / "20240513115019-CheckUp-1-6-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_8 = pd.read_parquet(
    base_dir_seg / "20240930093255-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_9 = pd.read_parquet(
    base_dir_seg / "20241203204228-CheckUp-1-4-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_Segments.parquet")
seg_10 = pd.read_parquet(
    base_dir_seg / "20250224132359-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_Segments.parquet")

base_dir = Path(r"C:\python projekte\BA_Repo\pydpeet\src\Alex_BA\res\BA\Parameter_studie\04_iOCV")
iocv_1 = pandas.read_parquet(base_dir / "20231027183923-CheckUp-1-2-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_2 = pandas.read_parquet(base_dir / "20231129133302-CheckUp-3-7-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_3 = pandas.read_parquet(base_dir / "20231212150550-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_4 = pandas.read_parquet(base_dir / "20240216101054-CheckUp-3-8-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_5 = pandas.read_parquet(base_dir / "20240321173721-CheckUp-1-6-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_6 = pandas.read_parquet(base_dir / "20240503100606-CheckUp-3-8-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_7 = pandas.read_parquet(base_dir / "20240513115019-CheckUp-1-6-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_8 = pandas.read_parquet(base_dir / "20240930093255-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_9 = pandas.read_parquet(base_dir / "20241203204228-CheckUp-1-4-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")
iocv_10 = pandas.read_parquet(base_dir / "20250224132359-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")

filenames = ["20231027183923-CheckUp-1-2-AM23NMC00001_Neware_2025-11-12_16-07-45",
            "20231129133302-CheckUp-3-7-AM23NMC00020_Neware_2025-11-12_16-07-45",
            "20231212150550-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45",
            "20240216101054-CheckUp-3-8-AM23NMC00020_Neware_2025-11-12_16-07-45",
            "20240321173721-CheckUp-1-6-AM23NMC00001_Neware_2025-11-12_16-07-45",
            "20240503100606-CheckUp-3-8-AM23NMC00020_Neware_2025-11-12_16-07-45",
            "20240513115019-CheckUp-1-6-AM23NMC00001_Neware_2025-11-12_16-07-45",
            "20240930093255-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45",
            "20241203204228-CheckUp-1-4-AM23NMC00020_Neware_2025-11-12_16-07-45",
            "20250224132359-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45"]

base_dir = Path(r"C:\python projekte\BA_Repo\pydpeet\src\Alex_BA\res\BA\Parameter_studie\05_FUDS_with_SOC")
fuds_1 = pandas.read_parquet(base_dir / "20231027183923-CheckUp-1-2-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_primitives_fuds_1.parquet")
fuds_2 = pandas.read_parquet(base_dir / "20231129133302-CheckUp-3-7-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_primitives_fuds_2.parquet")
fuds_3 = pandas.read_parquet(base_dir / "20231212150550-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_primitives_fuds_3.parquet")
fuds_4 = pandas.read_parquet(base_dir / "20240216101054-CheckUp-3-8-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_primitives_fuds_4.parquet")
fuds_5 = pandas.read_parquet(base_dir / "20240321173721-CheckUp-1-6-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_primitives_fuds_5.parquet")
fuds_6 = pandas.read_parquet(base_dir / "20240503100606-CheckUp-3-8-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_primitives_fuds_6.parquet")
fuds_7 = pandas.read_parquet(base_dir / "20240513115019-CheckUp-1-6-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_primitives_fuds_7.parquet")
fuds_8 = pandas.read_parquet(base_dir / "20240930093255-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_primitives_fuds_8.parquet")
fuds_9 = pandas.read_parquet(base_dir / "20241203204228-CheckUp-1-4-AM23NMC00020_Neware_2025-11-12_16-07-45_Data_primitives_fuds_9.parquet")
fuds_10 = pandas.read_parquet(base_dir / "20250224132359-CheckUp-1-3-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_primitives_fuds_10.parquet")

fuds_list = [fuds_1, fuds_2, fuds_3, fuds_4, fuds_5, fuds_6, fuds_7, fuds_8, fuds_9, fuds_10]


import matplotlib.pyplot as plt
plt.figure()

#results_df = results_df[results_df['SOC'] >= 0.07]
base_dir = Path(r"C:\python projekte\BA_Repo\pydpeet\src\Alex_BA\res\BA\Parameter_studie\04_iOCV")
iocv_discharge_1 = pandas.read_parquet(
    base_dir / "20231027183923-CheckUp-1-2-AM23NMC00001_Neware_2025-11-12_16-07-45_Data_discharge_iocv.parquet")

datasets = [[fuds_1,iocv_1,seg_1],[fuds_2,iocv_2,seg_2],[fuds_3,iocv_3,seg_3],[fuds_4,iocv_4,seg_4],[fuds_5,iocv_5,seg_5],[fuds_6,iocv_6, seg_6],[fuds_7,iocv_7, seg_7],[fuds_8,iocv_8, seg_8],[fuds_9,iocv_9,seg_9],[fuds_10,iocv_10,seg_10]]

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from multiprocessing import cpu_count
from pathlib import Path

# parameter ranges
Extrapolated_length = range(0, 10*60, 1)
min_pause_length = range(0, 2*60, 1)

def compute_single(dataset_name,
                   fuds_df,
                   iocv_df,
                   seg_df,
                   extrapolation,
                   min_pause,
                   n_grid=500):
    """
    Run one FUDS pause extrapolation configuration and score the resulting OCV curve
    against a reference iOCV discharge curve on a common SOC grid.

    The function calls `process_fuds_extrapolation(...)` to generate pause-based OCV points
    (typically SOC vs Voltage[V]) from `fuds_df`/`seg_df`, using:
      - `extrapolated_pause_length=extrapolation`
      - `min_pause_length=min_pause`

    It then computes a set of similarity/error metrics versus `iocv_df`:
      - `corr_coeff`: Pearson correlation coefficient between the two voltage curves
        interpolated onto a shared SOC grid.
      - `Area`: integral of absolute voltage difference over SOC (L1 area error).
      - `Area_norm`: `Area` normalized by the reference curve voltage span
        (max(V) - min(V)); NaN if the span is 0.
      - `rmse`: root mean squared error over the SOC grid.
      - `pause_count`: number of extrapolated pause OCV points produced (len of df2).

    The scoring is performed only on the SOC overlap region shared by both curves.
    If the extrapolation output is empty/invalid or there is no SOC overlap, the function
    returns NaNs for metrics (and pause_count accordingly).

    Parameters
    ----------
    dataset_name : str
        Identifier for the dataset (used in the returned record under key "Dataset").
    fuds_df : pandas.DataFrame
        FUDS primitives dataframe used as input to `process_fuds_extrapolation`.
        Expected to be compatible with the extrapolation.
    iocv_df : pandas.DataFrame
        Reference iOCV discharge dataframe. Must contain columns "SOC" and "Voltage[V]"
        for metric computation.
    seg_df : pandas.DataFrame
        Segments/sequences dataframe associated with `fuds_df`, used by the extrapolation
        pipeline to locate pause blocks.
    extrapolation : int
        Extrapolated pause length passed to `process_fuds_extrapolation` as
        `extrapolated_pause_length`. Units should match what the extrapolation function
        expects (commonly seconds).
    min_pause : int
        Minimum pause length passed to `process_fuds_extrapolation` as `min_pause_length`.
        Units should match what the extrapolation function expects.
    n_grid : int, default 500
        Number of SOC samples in the uniform overlap grid used for interpolation and
        metric computation.

    Returns
    -------
    dict
        Dictionary with the following keys:
          - 'extrapolated_pause_length' => Interpolated duration in seconds
          - 'min_pause_length' => minimum Pause lenght to be considered for the OCV Curve.
          - 'pause_count' => Number of extrapolated pause OCV points produced (len of df2).
          - 'corr_coeff' => Computationmetric for correlation coeffecient
          - 'Area' => Computationmetric for the Area of both OCV curves
          - 'Area_norm' => Computationmetric for the Normalized Area of both OCV curves
          - 'rmse' => Computationmetric for the Root Mean Square Error of both OCV curves
          - 'Dataset' => Identifier for the dataset (used in the returned record under key "Dataset").

        If inputs are missing required columns, output is too short, or SOC overlap is
        empty, metric values are NaN and pause_count is 0 or the available count.

    Notes
    -----
    - Both curves are sorted by SOC before interpolation.
    - The extrapolated dataframe ("df2") is cleaned by coercing Voltage[V] to numeric,
      replacing inf with NaN, and linearly interpolating missing voltage values.
    - `corr_coeff` is computed via `np.corrcoef(v1, v2)[0, 1]` on the interpolated grid.
    """
    extrapolated_fuds_df = process_fuds_extrapolation(
        fuds_df=fuds_df,
        iocv_discharge_df=iocv_df,
        segments_sequence_df=seg_df,
        extrapolated_pause_length=extrapolation,
        min_pause_length=min_pause,
        plot_results=False
    )

    if extrapolated_fuds_df is None or len(extrapolated_fuds_df) < 2:
        return {
            'extrapolated_pause_length': extrapolation,
            'min_pause_length': min_pause,
            'pause_count': 0,
            'corr_coeff': np.nan,
            'Area': np.nan,
            'Area_norm': np.nan,
            'rmse': np.nan,
            'Dataset': dataset_name
        }

    df1 = iocv_df.sort_values("SOC").reset_index(drop=True)
    df2 = extrapolated_fuds_df.sort_values("SOC").reset_index(drop=True)

    # Basic validation
    needed = {"SOC", "Voltage[V]"}
    if not needed.issubset(df1.columns) or not needed.issubset(df2.columns):
        return {
            'extrapolated_pause_length': extrapolation,
            'min_pause_length': min_pause,
            'pause_count': 0,
            'corr_coeff': np.nan,
            'Area': np.nan,
            'Area_norm': np.nan,
            'rmse': np.nan,
            'Dataset': dataset_name
        }

    # Clean df2 voltage
    df2 = df2[np.isfinite(df2["SOC"])].copy()
    df2["Voltage[V]"] = pd.to_numeric(df2["Voltage[V]"], errors="coerce")
    df2["Voltage[V]"] = df2["Voltage[V]"].replace([np.inf, -np.inf], np.nan)
    df2["Voltage[V]"] = df2["Voltage[V]"].interpolate(method="linear", limit_direction="both")
    df2 = df2[np.isfinite(df2["Voltage[V]"])].copy()

    pause_count = len(df2)
    if pause_count < 2:
        return {
            'extrapolated_pause_length': extrapolation,
            'min_pause_length': min_pause,
            'pause_count': pause_count,
            'corr_coeff': np.nan,
            'Area': np.nan,
            'Area_norm': np.nan,
            'rmse': np.nan,
            'Dataset': dataset_name
        }

    # overlap in SOC
    soc_min = max(df1["SOC"].min(), df2["SOC"].min())
    soc_max = min(df1["SOC"].max(), df2["SOC"].max())
    if soc_max <= soc_min:
        return {
            'extrapolated_pause_length': extrapolation,
            'min_pause_length': min_pause,
            'pause_count': pause_count,
            'corr_coeff': np.nan,
            'Area': np.nan,
            'Area_norm': np.nan,
            'rmse': np.nan,
            'Dataset': dataset_name
        }

    # ensuring same size for df1 & df2
    soc_grid = np.linspace(soc_min, soc_max, n_grid)
    v1 = np.interp(soc_grid, df1["SOC"], df1["Voltage[V]"])
    v2 = np.interp(soc_grid, df2["SOC"], df2["Voltage[V]"])

    # metrics
    area = float(np.trapz(np.abs(v1 - v2), soc_grid))
    # normalization over Voltage
    normalize = float(df1["Voltage[V]"].max() - df1["Voltage[V]"].min())
    if normalize > 0:
        area_norm = area / normalize
    else:
        area_norm = np.nan

    rmse = float(np.sqrt(((v1 - v2) ** 2).mean()))
    corr_coeff = float(np.corrcoef(v1, v2)[0, 1])

    return {
        'extrapolated_pause_length': extrapolation,
        'min_pause_length': min_pause,
        'pause_count': pause_count,
        'corr_coeff': corr_coeff,
        'Area': area,
        'Area_norm': area_norm,
        'rmse': rmse,
        'Dataset': dataset_name
    }


# -----------------------
# PARALLELIZATION (unchanged, aside from using compute_single signature)
# -----------------------

available_cores = cpu_count()
n_jobs = max(1, available_cores - 1)   # keep 1 free

print(f"Using {n_jobs} parallel workers (keeping 1 free).")

tasks = []

# assuming filenames and datasets are iterables of equal length and datasets items are (fuds_df, iocv_df)
for (dataset_name, (fuds_df, iocv_df, seg_df)) in zip(filenames, datasets):
    iocv_df['Voltage[V]'] -= iocv_df['Voltage[V]'].min()
    fuds_df['Voltage[V]'] -= iocv_df['Voltage[V]'].min()
    for extrapolation in Extrapolated_length:
        for min_pause in min_pause_length:
            tasks.append(
                delayed(compute_single)(
                    dataset_name, fuds_df, iocv_df, seg_df, extrapolation, min_pause
                )
            )

results = Parallel(n_jobs=n_jobs, backend="loky", verbose=10)(tasks)

# Convert results to DataFrame
result_df = pd.DataFrame(results)

# Export
export_dir = Path(r"C:\python projekte\BA_Repo\pydpeet\src\Alex_BA\res\BA\Parameter_studie\06_Results\result_df_with_correct_segments_rmse_3.parquet")
result_df.to_parquet(export_dir)