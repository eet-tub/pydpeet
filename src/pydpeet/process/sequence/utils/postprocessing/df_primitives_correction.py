import pandas as pd

from pydpeet.citations import citeme
from pydpeet.process.sequence.utils.annotate.annotate_primitives import _merged_annotations


def df_primitives_correction(
        df_primitives: pd.DataFrame,
        correction_config: dict,
        data_columns: dict[str, str],
        thresholds: dict[str, float],
        reindex: bool = True,
        reannotate: bool = True
) -> pd.DataFrame:
    """
    Corrects the primitives in the dataframe based on the given configuration.

    Parameters:
    df_primitives (pd.DataFrame): Input dataframe containing the primitives.
    correction_config (dict): Configuration for the correction, containing the following keys:
        - replace_ID (dict): Mapping of old IDs to new IDs.
        - replace_time (dict): Mapping of time ranges and the new labels for variable.
        - replace_time_and_merge (dict): Mapping of time ranges  and the new labels for variable + merges all into one segment.
        - merge_left (list): List of IDs to merge with the previous segment.
        - merge_right (list): List of IDs to merge with the next segment.
        - merge_range (list): List of tuples of start and end IDs to merge. Keeping left Variable
        Example: {'replace_time': {(0.0, 10.0): 'I', (10.0, 20.0): 'P'}, ...}
    data_columns (dict): Mapping of column names to their respective short names.
        Example: data_columns = {"I": "Current[A]", "P": "Power[W]", "V": "Voltage[V]"}
    thresholds (dict): Threshold values for each type of annotation.
        Example: {"V": 0.1, "I": 0.1, "P": 0.1}
    reindex (bool): Whether to reindex the IDs to be consecutive, by default True.
    reannotate (bool): Whether to reannotate the primitives after the correction, by default True.

    Returns:
    pd.DataFrame: The corrected dataframe with the added columns for annotated primitives.
    """




    df = df_primitives.copy()
    max_id = df["ID"].max() + 1  # for new IDs

    # --- REPLACE by ID ---
    if "replace_ID" in correction_config:
        for id_, new_label in correction_config["replace_ID"].items():
            df.loc[df["ID"] == id_, "Variable"] = new_label

    # --- REPLACE by TIME with splitting ---
    if "replace_time" in correction_config:
        for (start, end), new_label in correction_config["replace_time"].items():
            overlapping_idx = df[(df["Testtime[s]"] >= start) & (df["Testtime[s]"] <= end)].index
            if overlapping_idx.empty:
                continue

            overlapping_ids = df.loc[overlapping_idx, "ID"].unique()
            for seg_id in overlapping_ids:
                segment_rows = df[df["ID"] == seg_id]
                seg_start_time = segment_rows["Testtime[s]"].min()
                seg_end_time = segment_rows["Testtime[s]"].max()

                if start <= seg_start_time and end >= seg_end_time:
                    mask = (df["ID"] == seg_id)
                    df.loc[mask, "Variable"] = new_label
                else:
                    if seg_start_time < start:
                        mask_before = (df["ID"] == seg_id) & (df["Testtime[s]"] < start)
                        df.loc[mask_before, "ID"] = max_id
                        max_id += 1

                    mask_overlap = (df["ID"] == seg_id) & (df["Testtime[s]"] >= start) & (df["Testtime[s]"] <= end)
                    df.loc[mask_overlap, "Variable"] = new_label
                    df.loc[mask_overlap, "ID"] = max_id
                    max_id += 1

                    if seg_end_time > end:
                        mask_after = (df["ID"] == seg_id) & (df["Testtime[s]"] > end)
                        df.loc[mask_after, "ID"] = max_id
                        max_id += 1

    # --- REPLACE by TIME and MERGE ---
    if "replace_time_and_merge" in correction_config:
        for (start, end), new_label in correction_config["replace_time_and_merge"].items():
            overlapping_idx = df[(df["Testtime[s]"] >= start) & (df["Testtime[s]"] <= end)].index
            if overlapping_idx.empty:
                continue

            overlapping_ids = df.loc[overlapping_idx, "ID"].unique()
            new_id_for_merge = max_id
            max_id += 1

            for seg_id in overlapping_ids:
                segment_rows = df[df["ID"] == seg_id]
                seg_start_time = segment_rows["Testtime[s]"].min()
                seg_end_time = segment_rows["Testtime[s]"].max()

                if start <= seg_start_time and end >= seg_end_time:
                    mask = (df["ID"] == seg_id)
                    df.loc[mask, "Variable"] = new_label
                    df.loc[mask, "ID"] = new_id_for_merge
                else:
                    if seg_start_time < start:
                        mask_before = (df["ID"] == seg_id) & (df["Testtime[s]"] < start)
                        df.loc[mask_before, "ID"] = max_id
                        max_id += 1

                    mask_overlap = (df["ID"] == seg_id) & (df["Testtime[s]"] >= start) & (df["Testtime[s]"] <= end)
                    df.loc[mask_overlap, "Variable"] = new_label
                    df.loc[mask_overlap, "ID"] = new_id_for_merge

                    if seg_end_time > end:
                        mask_after = (df["ID"] == seg_id) & (df["Testtime[s]"] > end)
                        df.loc[mask_after, "ID"] = max_id
                        max_id += 1

    # --- MERGE LEFT ---
    if "merge_left" in correction_config:
        for id_ in correction_config["merge_left"]:
            segment_rows = df[df["ID"] == id_]
            if segment_rows.empty:
                continue
            first_pos = df.index.get_loc(segment_rows.index[0])
            if first_pos == 0:
                continue
            left_id = df.iloc[first_pos - 1]["ID"]
            left_variable = df.iloc[first_pos - 1]["Variable"]
            df.loc[segment_rows.index, "ID"] = left_id
            df.loc[segment_rows.index, "Variable"] = left_variable

    # --- MERGE RIGHT ---
    if "merge_right" in correction_config:
        for id_ in correction_config["merge_right"]:
            segment_rows = df[df["ID"] == id_]
            if segment_rows.empty:
                continue

            first_pos = df.index.get_loc(segment_rows.index[0])
            last_pos = df.index.get_loc(segment_rows.index[-1])

            right_pos = last_pos + 1
            if right_pos >= len(df):
                continue

            right_id = df.iloc[right_pos]["ID"]
            right_variable = df.iloc[right_pos]["Variable"]
            df.loc[segment_rows.index, "ID"] = right_id
            df.loc[segment_rows.index, "Variable"] = right_variable

    # --- MERGE RANGES ---
    if "merge_range" in correction_config:
        for (start_id, end_id) in correction_config["merge_range"]:
            mask = (df["ID"] >= start_id) & (df["ID"] <= end_id)
            if not mask.any():
                continue
            target_id = start_id
            target_variable = df.loc[df["ID"] == target_id, "Variable"].iloc[0]
            df.loc[mask, "ID"] = target_id
            df.loc[mask, "Variable"] = target_variable

    # --- REINDEX IDs to be consecutive ---
    if reindex:
        unique_ids = df["ID"].drop_duplicates().reset_index(drop=True)
        id_mapping = {old_id: new_id for new_id, old_id in enumerate(unique_ids, start=1)}
        df["ID"] = df["ID"].map(id_mapping)

    if reannotate:
        df = _merged_annotations(df, data_columns, thresholds)

    return df

