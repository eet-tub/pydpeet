import logging

import pandas as pd
import matplotlib.pyplot as plt

from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks

def fuds_ocv_by_pause(
    fuds_df : pd.DataFrame = None,
    iocv_discharge_df: pd.DataFrame = None,
    segments_sequence_df: pd.DataFrame = None,
    min_pause_length=0,
    plot_results: bool = False
    ) -> pd.DataFrame:
    """
       Extract OCV (open-circuit voltage) points from pause segments in a FUDS dataset and optionally
       compare them against a reference iOCV discharge curve.

       Parameters
       ----------
       fuds_df : pandas.DataFrame, optional
           Raw FUDS primitive dataframe containing at least the standard columns:
           ["Testtime[s]", "Voltage[V]", "Current[A]", "Power[W]"] and additional columns used by the
           block splitting logic (e.g., "ID", "Length", and typically "SOC" for plotting).
       iocv_discharge_df : pandas.DataFrame, optional
           Reference iOCV discharge curve dataframe used only for plotting. Must contain "SOC" and
           "Voltage[V]" if `plot_results=True`.
       segments_sequence_df : pandas.DataFrame, optional
           Segment/sequence mapping dataframe consumed by `filter_and_split_df_by_blocks` to identify
           "Pause" blocks.
       min_pause_length : int or float, default 0
           Minimum required pause duration/length. Blocks with a minimum "Length" value below this
           threshold are discarded.
       plot_results : bool, default False
           If True, generates a Matplotlib plot comparing the iOCV discharge curve against the
           extracted pause-based OCV points.

       Returns
       -------
       pandas.DataFrame
           Concatenated dataframe containing the extracted pause-based OCV points (last sample per ID
           within each qualifying pause block). Includes the columns present in the selected rows
    """


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
            df_segments_and_sequences=segments_sequence_df,
            df_primitives=fuds_df,
            rules=_rules,
            standard_columns=_STANDARD_COLUMNS,
            combine_op='or',
            print_blocks=False,
            also_return_filtered_df=False
        )

    logging.info("Filtering iOCV Points...")

    # Filter blocks with minimum Duration
    dfs_per_block = [df for df in dfs_per_block if df["Length"].min() >= min_pause_length]

    # Keep only rows with maximum Testtime[s] per ID
    dfs_per_block = [
        df.loc[df.groupby("ID")["Testtime[s]"].idxmax()] for df in dfs_per_block
    ]
    #filter and merge to one dataframe
    result_df = [df for df in dfs_per_block if df["Length"].min() >= min_pause_length]
    result_df = pd.concat([df for df in result_df], ignore_index=True)

    # Only process plotting if needed
    if plot_results:
        # Create figure and axes
        fig, ax1 = plt.subplots(1, 1, figsize=(12, 8))

        # Plot iOCV curve
        ax1.plot(iocv_discharge_df['SOC'], iocv_discharge_df['Voltage[V]'], color='red', label='iOCV Discharge', linewidth=2,
                 alpha=0.8)
        ax1.plot(result_df['SOC'], result_df['Voltage[V]'], color='blue', label='OCV by Pause', linewidth=2,
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

    return result_df