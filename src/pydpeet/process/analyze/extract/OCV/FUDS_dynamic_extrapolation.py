import logging

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks


def apply_variable_pause_thresholds(time_col: str,
                                    thresholds_pct_tuples=None,
                                    fuds_df: pd.DataFrame = None,
                                    df_segments_and_sequences: pd.DataFrame = None,
                                    iocv_discharge_df: pd.DataFrame = None,
                                    plot_results: bool = False
                                    ) -> pd.DataFrame:
    """
    Parameters
    ----------
    time_col : str
        Name of the time column in `fuds_df` (e.g., "Testtime[s]"). Must be numeric and sortable.
    thresholds_pct_tuples : list[tuple[float, float, float]]
        List of tuples `(start_pct, end_pct, threshold_seconds)` defining piecewise thresholds over
        the total test-time span:
          - `start_pct`, `end_pct` are percentages in [0, 100]
          - `threshold_seconds` is the extrapolationduration`
        If no tuple matches (including edge cases near 100%), the last tuple's threshold is used.
    fuds_df : pandas.DataFrame
        Input dataframe containing time-series primitives. Must include `time_col`. For plotting
        and pause extraction, it is expected to also include columns like "SOC" and "Voltage[V]".
    df_segments_and_sequences : pandas.DataFrame, optional
        Segment/sequence dataframe used by `filter_and_split_df_by_blocks` to identify pause blocks.)
    iocv_discharge_df : pandas.DataFrame, optional
        Reference iOCV discharge dataframe used only when `plot_results=True`. Must contain "SOC"
        and "Voltage[V]" for plotting.
    plot_results : bool, default False
        If True, generates a Matplotlib plot comparing:
          - `iocv_discharge_df` (SOC vs Voltage[V]) and
          - merged pause-block OCV points (`df_merged_blocks`, SOC vs Voltage[V])

    Returns
    -------
    pandas.DataFrame
    which contains the dynamic extrapolated OCV points

    Raises
    ------
    ValueError
        If `thresholds_pct_tuples` is None or if `fuds_df` is None.

    """
    if thresholds_pct_tuples is None:
        raise ValueError("thresholds_pct_tuples must be provided")

    if fuds_df is None:
        raise ValueError("Dataframe is Empty! please provide a Dataframe.")

    logging.info("Applying rules and standard columns...")
    _rules = [
        "Pause"
    ]
    _STANDARD_COLUMNS = [
        "Testtime[s]",
        "Voltage[V]",
        "Current[A]",
        "Power[W]",
    ]

    dfs_per_block = filter_and_split_df_by_blocks(
        df_segments_and_sequences=df_segments_and_sequences,
        df_primitives=fuds_df,
        rules=_rules,
        standard_columns=_STANDARD_COLUMNS,
        combine_op='or',
        print_blocks=False,
        also_return_filtered_df=False
    )

    df_merged_blocks = pd.concat([df for df in dfs_per_block], ignore_index=True)
    # sort by time to be safe
    fuds_df = fuds_df.sort_values(time_col).reset_index(drop=True)

    t_min = fuds_df[time_col].min()
    t_max = fuds_df[time_col].max()
    total_span = float(t_max - t_min)

    # If total_span == 0, fallback to last threshold (or raise) — here we fallback.
    if total_span == 0:
        def get_threshold_for_midpoint(_mid):
            return thresholds_pct_tuples[-1][2]
    else:
        def get_threshold_for_midpoint(mid_time):
            pct = ((mid_time - t_min) / total_span) * 100.0  # percent 0..100
            for start_pct, end_pct, thr in thresholds_pct_tuples:
                if start_pct <= pct < end_pct:
                    return thr
            # if no match, try inclusive end for 100%
            for start_pct, end_pct, thr in thresholds_pct_tuples:
                if np.isclose(pct, end_pct) and end_pct == 100:
                    return thr
            # fallback to last tuple threshold
            return thresholds_pct_tuples[-1][2]

    # compute diff to previous and midpoint
    prev_time = fuds_df[time_col].shift(1)
    diff = fuds_df[time_col] - prev_time
    midpoint = (fuds_df[time_col] + prev_time) / 2.0

    # build boolean keep array
    keep = np.zeros(len(fuds_df), dtype=bool)
    # always keep first candidate (no previous row to compare)
    keep[0] = True
    for i in range(1, len(fuds_df)):
        mid = midpoint.iat[i]
        if pd.isna(mid):
            # if somehow NaN, keep weird behavior: require last threshold (or keep)
            keep[i] = True
            continue
        thr = get_threshold_for_midpoint(mid)
        keep[i] = (diff.iat[i] >= thr)

    # Only process plotting if needed
    if plot_results:
        # Create figure and axes
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 8))

        # Plot iOCV curve
        ax1.plot(iocv_discharge_df['SOC'], iocv_discharge_df['Voltage[V]'], color='red', label='iOCV Discharge',
                 linewidth=2,
                 alpha=0.8)
        ax1.plot(df_merged_blocks['SOC'], df_merged_blocks['Voltage[V]'], color='blue', label='OCV Extrapolated dynamicly',
                 linewidth=2,
                 alpha=0.8)

        # Configure iOCV plot
        ax1.set_title('iOCV Curves', fontsize=15)
        ax1.set_xlabel('SOC', fontsize=15)
        ax1.set_ylabel('Voltage [V]', fontsize=15, color='blue')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend(fontsize=12, loc='lower right')
        ax1.tick_params(axis='y', which='major', labelsize=15, labelcolor='blue')
        ax1.tick_params(axis='x', which='major', labelsize=15)
        plt.show()

    return fuds_df[keep].reset_index(drop=True)