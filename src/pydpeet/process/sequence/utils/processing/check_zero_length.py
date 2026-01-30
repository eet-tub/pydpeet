import numpy as np

from pydpeet.process.sequence.utils.console_prints.log_time import log_time
from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction
import logging

def _check_zero_length_segments(df_primitives,
                                SHOW_RUNTIME,
                                DATA_COLUMNS,
                                THRESHOLDS_PRIMITIVE_ANNOTATION,
                                supress_IO_warnings,
                                THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK):

    """
    Checks all segments in the dataframe for zero length segments and correct them by merging with the closest neighbor segment.

    Parameters:
    df_primitives (pd.DataFrame): DataFrame containing the primitives
    SHOW_RUNTIME (bool): whether to print runtime information
    DATA_COLUMNS (dict): dictionary of column names to be kept in the DataFrame
        Example: {"I": "Current[A]", "P": "Power[W]", "V": "Voltage[V]"}
    THRESHOLDS_PRIMITIVE_ANNOTATION (dict): dictionary of threshold values for primitive annotation
        Example: {"I": 0.1, "P": 0.1, "V": 0.1}
    supress_IO_warnings (bool): whether to suppress runtime warnings
    THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK (int): threshold for the number of corrected segments to print

    Returns:
    pd.DataFrame: Dataframe with added columns for annotated primitives
    """
    with log_time("checking zero length segments", SHOW_RUNTIME=SHOW_RUNTIME):
        zero_length_ids = df_primitives[df_primitives['Length'] == 0]['ID'].unique().tolist()

        zero_length_ids_left_merge = []
        zero_length_ids_right_merge = []

        for zero_id in zero_length_ids:
            # Get the first row where this ID appears
            zero_rows = df_primitives[df_primitives['ID'] == zero_id]
            if zero_rows.empty:
                continue

            zero_idx = zero_rows.index[0]
            try:
                idx_pos = df_primitives.index.get_loc(zero_idx)
            except KeyError:
                continue

            # Get the row's Voltage, Current, Power
            zero_vals = df_primitives.iloc[idx_pos][['Voltage[V]', 'Current[A]', 'Power[W]']].values

            # Initialize distances
            dist_left = np.inf
            dist_right = np.inf

            # Compare with left neighbor if available and different ID
            if idx_pos > 0:
                left_row = df_primitives.iloc[idx_pos - 1]
                if left_row['ID'] != zero_id:
                    left_vals = left_row[['Voltage[V]', 'Current[A]', 'Power[W]']].values
                    dist_left = np.linalg.norm(zero_vals - left_vals)

            # Compare with right neighbor if available and different ID
            if idx_pos < len(df_primitives) - 1:
                right_row = df_primitives.iloc[idx_pos + 1]
                if right_row['ID'] != zero_id:
                    right_vals = right_row[['Voltage[V]', 'Current[A]', 'Power[W]']].values
                    dist_right = np.linalg.norm(zero_vals - right_vals)

            # Pick closer neighbor
            if dist_left < dist_right:
                zero_length_ids_left_merge.append(zero_id)
            else:
                zero_length_ids_right_merge.append(zero_id)

    with log_time("correcting zero length segments", SHOW_RUNTIME=SHOW_RUNTIME):
        correction_config = {
            "merge_left": [
                *zero_length_ids_left_merge
            ],
            "merge_right": [
                *zero_length_ids_right_merge
            ],
        }

        df_primitives = df_primitives_correction(df_primitives=df_primitives,
                                                 correction_config=correction_config,
                                                 data_columns=DATA_COLUMNS,
                                                 thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION,
                                                 reindex=False,
                                                 reannotate=False)

        if not supress_IO_warnings:
            if zero_length_ids_left_merge or zero_length_ids_right_merge:
                logging.warning("Segments with duration of 1 sample found.")
            if THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK:
                if zero_length_ids_left_merge:
                    if len(zero_length_ids_left_merge) > THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK:
                        logging.warning(f"Merged with left neighbor: {zero_length_ids_left_merge[:THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK]}, ...")
                    else:
                        logging.warning(f"Merged with left neighbor: {zero_length_ids_left_merge[:THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK]}")
                if zero_length_ids_right_merge:
                    if len(zero_length_ids_right_merge) > THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK:
                        logging.warning(f"Merged with right neighbor: {zero_length_ids_right_merge[:THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK]}, ...")
                    else:
                        logging.warning(f"Merged with right neighbor: {zero_length_ids_right_merge[:THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK]}")

    return df_primitives
