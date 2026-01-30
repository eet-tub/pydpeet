import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression as SkLinearRegression
from tsmoothie.smoother import *

from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks

def process_fuds_extrapolation(
    fuds_df: pd.DataFrame,
    iocv_discharge_df: pd.DataFrame,
    segments_sequence_df: pd.DataFrame,
    extrapolated_pause_length: float = 0,
    min_pause_length: int = 0,
    plot_results: bool = False
) -> pd.DataFrame:
    """
    Process FUDS extrapolation data and optionally plot alongside iOCV curves.

    Parameters:
    -----------
    fuds_df : pd.DataFrame
        DataFrame containing FUDS data
    iocv_discharge_df : pd.DataFrame
        DataFrame containing iOCV Discharge data
    segments_sequence_df : pd.DataFrame
        DataFrame containing segments and sequences data
    extrapolated_pause_length : float, optional
        Time offset for extrapolation in seconds (default: 0)
    min_pause_length : int, optional
        Minimum length of blocks to consider (default: 0)
    plot_results : bool, optional
        Whether to generate and show the plot (default: False)

    Returns:
    --------
    pd.DataFrame
        DataFrame containing extrapolated data
        If plot_results=True: Returns (fig, axes, results_df)
    """

    if fuds_df is None:
        raise ValueError("Please provide a Dataframe which contains the FUDS data!")

    if iocv_discharge_df is None:
        raise ValueError("Please provide a Dataframe which contains the iOCV Discharge data!")

    logging.info("Applying rules and standard columns...")
    _rules = ["Pause"]
    _STANDARD_COLUMNS = ["Testtime[s]", "Voltage[V]", "Current[A]", "Power[W]"]

    # Process FUDS data
    dfs_per_block = filter_and_split_df_by_blocks(
        df_segments_and_sequences=segments_sequence_df,
        df_primitives=fuds_df,
        rules=_rules,
        standard_columns=_STANDARD_COLUMNS,
        combine_op='or',
        print_blocks=False,
        also_return_filtered_df=False
    )
    dfs_per_block = [df for df in dfs_per_block if df["Length"].min() >= min_pause_length]

    # Perform linear regression for voltage extrapolation
    results_voltage = []
    results_time = []
    results_soc = []

    for df in dfs_per_block:
        X = df["Testtime[s]"].values.reshape(-1, 1)
        y = df["Voltage[V]"].values

        log_y = np.log(y)
        model = SkLinearRegression()
        model.fit(X, log_y)
        b = model.coef_[0]
        a = np.exp(model.intercept_)

        shifted_time = df["Testtime[s]"].iloc[0] + extrapolated_pause_length

        y_pred = a * np.exp(b * shifted_time)

        results_time.append(shifted_time)
        results_voltage.append(y_pred)

        idx_nearest = (df["Testtime[s]"] - shifted_time).abs().idxmin()
        results_soc.append(df.loc[idx_nearest, "SOC"])


    results_df = pd.DataFrame({
        "SOC": results_soc,
        "Voltage[V]": results_voltage,
        "Testtime[s]": results_time
    })

    results_df.dropna(subset=['Voltage[V]'], inplace=True)

    # Only process plotting if needed
    if plot_results:
        # Create figure and axes
        fig, ax1 = plt.subplots(1, 1, figsize=(12,8))

        # Plot iOCV curve
        ax1.plot(iocv_discharge_df['SOC'], iocv_discharge_df['Voltage[V]'], color='red', label='iOCV', linewidth=2, alpha=0.8)
        ax1.plot(results_df['SOC'], results_df['Voltage[V]'], color='blue', label='Pause Extrapolated', linewidth=2,
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


    return results_df