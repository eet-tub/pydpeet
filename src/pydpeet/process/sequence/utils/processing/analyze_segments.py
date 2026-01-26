from typing import Dict
import pandas as pd
from pydpeet.process.sequence.utils.console_prints.log_time import log_time


def _match_rules(df: pd.DataFrame, rules: Dict) -> pd.Series:
    """
    Match segments in a DataFrame according to rules to create a mask that matches these rules.

    The rules dictionary can contain the following keys:
    - "min_length_sec": minimum length of the segment in seconds
    - "max_length_sec": maximum length of the segment in seconds
    - "min_avg_abs": minimum average absolute value of the segment
    - "max_slope": maximum slope of the segment
    - "min_abs_slope": minimum absolute slope of the segment
    - "direction": direction of the segment
    - "variable": variable name of the segment
    - "type": type of the segment

    Parameters:
    df (pd.DataFrame): DataFrame to be matched
    rules (Dict): Dict containing matching rules
        Example: {'direction': 'Charge', 'type': 'Constant', 'variable': 'I'}
    Returns:
    pd.Series: Mask of True and False values where the segment matches the rules

    """
    mask = pd.Series(True, index=df.index)

    if "min_length_sec" in rules:
        mask &= df["Length"] >= rules["min_length_sec"]
    if "max_length_sec" in rules:
        mask &= df["Length"] <= rules["max_length_sec"]
    if "min_avg_abs" in rules:
        mask &= df["Avg"].abs() >= rules["min_avg_abs"]
    if "max_slope" in rules:
        mask &= df["Slope"].abs() <= rules["max_slope"]
    if "min_abs_slope" in rules:
        slope_abs = df["Slope"].abs()
        mask &= slope_abs >= rules["min_abs_slope"]
        if "direction" in rules:
            if rules["direction"] == "Up":
                mask &= df["Slope"] > 0
            elif rules["direction"] == "Down":
                mask &= df["Slope"] < 0
    if "variable" in rules:
        mask &= df["Variable"] == rules["variable"]
    if "type" in rules:
        mask &= df["Type"] == rules["type"]
    if "direction" in rules:
        mask &= df["Direction"] == rules["direction"]
    return mask


def _get_step_mask(df, step_name, SEGMENT_SEQUENCE_CONFIG):
    """
    Get a mask for a step in a DataFrame based on its found segments that fit the SEGMENT_SEQUENCE_CONFIG.

    Parameters:
    df (pd.DataFrame): DataFrame to be matched
    step_name (str): Name of the step in SEGMENT_SEQUENCE_CONFIG
    SEGMENT_SEQUENCE_CONFIG (dict): Dict containing sequence names and rule dicts

    Returns:
    pd.Series: Mask of True and False values where the segment matches the rules
    """
    step_cfg = SEGMENT_SEQUENCE_CONFIG[step_name]
    if "rules" in step_cfg:
        return _match_rules(df, step_cfg["rules"])
    elif "sequence" in step_cfg:
        if step_name not in df.columns:
            _tag_sequences(df, SEGMENT_SEQUENCE_CONFIG)
        return df[step_name] != 0
    else:
        # fallback empty mask
        return pd.Series(False, index=df.index)


def _match_merged_sequence(df, subsequences, SEGMENT_SEQUENCE_CONFIG):
    """
    Match a merged sequence of subsequences or segments in a DataFrame with incremental IDs.

    Parameters:
    df (pd.DataFrame): DataFrame to be matched
    subsequences (list): List of sequence names that are merged
        Example:  ["Discharge_iOCV", "CC_Discharge", "CV_Discharge", "CC_Charge", "Charge_iOCV"]
    SEGMENT_SEQUENCE_CONFIG (dict): Dict containing sequence names and rule dicts
        Example:{"Discharge_iOCV": {"loop": True, "minimum_IDs": 4, "sequence": ["CC_Discharge","Pause"]}, ...}

    Returns:
    pd.Series: Mask of True and False values where the segment matches the rules
    """
    masks_list = []
    lengths = []
    for sub_seq in subsequences:
        mask = _get_step_mask(df, sub_seq, SEGMENT_SEQUENCE_CONFIG).values
        masks_list.append(mask)
        # Count length of the subsequence pattern:
        # We get the max consecutive segment length in the mask for this sub_seq
        max_len = 0
        current_len = 0
        for val in mask:
            if val:
                current_len += 1
                max_len = max(max_len, current_len)
            else:
                current_len = 0
        lengths.append(max_len if max_len > 0 else 1)
    total_length = sum(lengths)

    n = len(df)
    seg_id = 1
    col_name = "_".join(subsequences)  # dummy name if needed
    if col_name not in df.columns:
        df[col_name] = 0

    i = 0
    while i <= n - total_length:
        # Check if concatenation of subsequences matches at i
        match = True
        offset = 0
        for idx, mask in enumerate(masks_list):
            length = lengths[idx]
            if not all(mask[i+offset:i+offset+length]):
                match = False
                break
            offset += length
        if match:
            # Assign segment ID
            for k in range(i, i + total_length):
                df.iat[k, df.columns.get_loc(col_name)] = seg_id
            seg_id += 1
            i += total_length
        else:
            i += 1
    return df[col_name] != 0


def _tag_simple(df: pd.DataFrame, SEGMENT_SEQUENCE_CONFIG):
    """
    Tag simple segments in a DataFrame with incremental IDs

    Parameters:
    df (pd.DataFrame): DataFrame to be tagged
    SEGMENT_SEQUENCE_CONFIG (dict): Dict containing sequence names and rule dicts
        Example:{"Current": {"rules": {"variable": "I", ...}}, ...}

    Returns:
    df (pd.DataFrame): DataFrame with tagged segments
    """
    for name, cfg in SEGMENT_SEQUENCE_CONFIG.items():
        if "rules" not in cfg:
            continue
        mask = _match_rules(df, cfg["rules"])
        # Assign incremental segment IDs to True rows in mask, else 0
        df[name] = 0
        # Find indices where mask is True
        true_indices = df.index[mask]
        # Assign incremental IDs for those rows
        df.loc[true_indices, name] = range(1, len(true_indices) + 1)

    return df


def _tag_sequences(df, SEGMENT_SEQUENCE_CONFIG):
    """
    Tag sequences in a DataFrame with incremental IDs (sequences spanning multiple rows use the same value for each row)

    "merge": True - If you want to use subsequences in the definition of you sequence (e.g. "merge": True, "sequence": ["sequence1","sequence2"])
    "loop": True - If you want to detect a looping definition (e.g. "loop": True, "sequence": ["CC_Discharge","Pause"])

    Parameters:
    df (pd.DataFrame): DataFrame to be tagged
    SEGMENT_SEQUENCE_CONFIG (dict): Dict containing sequence names and rule dicts
        Example:{"Discharge_iOCV": {"loop": True, "minimum_IDs": 4, "sequence": ["CC_Discharge","Pause"]}, ...}

    Returns:
    df (pd.DataFrame): DataFrame with tagged sequences
    """
    for name, cfg in SEGMENT_SEQUENCE_CONFIG.items():
        if "sequence" not in cfg:
            continue

        df[name] = 0

        if cfg.get("merge", False):
            subsequences = cfg["sequence"]
            for subseq in subsequences:
                if subseq not in df.columns:
                    _tag_sequences(df, SEGMENT_SEQUENCE_CONFIG)
            _ = _match_merged_sequence(df, subsequences, SEGMENT_SEQUENCE_CONFIG)
            temp_col = "_".join(subsequences)
            df[name] = df[temp_col]
            df.drop(columns=[temp_col], inplace=True)
        else:
            seq = cfg["sequence"]
            loop = cfg.get("loop", False)

            step_masks = []
            for step in seq:
                mask = _get_step_mask(df, step, SEGMENT_SEQUENCE_CONFIG).values
                step_masks.append(mask)

            len_df = len(df)
            len_sequence = len(seq)
            seg_id = 1
            i = 0

            while i <= len_df - len_sequence:
                if all(step_masks[j][i + j] for j in range(len_sequence)):
                    if not loop:
                        for j in range(len_sequence):
                            df.iat[i + j, df.columns.get_loc(name)] = seg_id
                        seg_id += 1
                        i += len_sequence
                    else:
                        start = i
                        loop_count = 0
                        while i <= len_df - len_sequence and all(step_masks[j][i + j] for j in range(len_sequence)):
                            loop_count += 1
                            i += len_sequence

                        total_ids = loop_count * len_sequence
                        valid = True

                        # Check constraints
                        if "minimum_IDs" in cfg:
                            valid &= total_ids >= cfg["minimum_IDs"]
                        if "min_loops" in cfg:
                            valid &= loop_count >= cfg["min_loops"]
                        if "max_loops" in cfg:
                            valid &= loop_count <= cfg["max_loops"]
                        if "exact_loops" in cfg:
                            # Prevent conflict with other loop constraints
                            if any(k in cfg for k in ["min_loops", "max_loops", "minimum_IDs"]):
                                raise ValueError(
                                    f"'exact_loops' cannot be combined with other loop constraints in {name}"
                                )
                            valid &= loop_count == cfg["exact_loops"]

                        if valid:
                            for k in range(start, i):
                                df.iat[k, df.columns.get_loc(name)] = seg_id
                            seg_id += 1
                        # If not valid, rewind index to skip just one step
                        else:
                            i = start + 1
                else:
                    i += 1

    return df


def _assign_longest_sequence(df: pd.DataFrame, SEGMENT_SEQUENCE_CONFIG) -> pd.DataFrame:

    """
    Assigns the longest sequence found in the DataFrame to each row in the column 'Sequence' using the format "<Occurrence>_<TestName>".

    Parameters:
        df (pd.DataFrame): The DataFrame to be analyzed.
        SEGMENT_SEQUENCE_CONFIG (dict): A dictionary containing the configuration for the analysis.
            Example:{"Discharge_iOCV": {"loop": True, "minimum_IDs": 4, "sequence": ["CC_Discharge","Pause"]}, ...}

    Returns:
        df (pd.DataFrame): A DataFrame containing the columns 'ID', 'Sequence', and all columns specified in SEGMENT_SEQUENCE_CONFIG.
    """
    test_names = list(SEGMENT_SEQUENCE_CONFIG.keys())
    #df = df.copy() #  is this needed
    df['Sequence'] = None
    counters = {name: 0 for name in test_names}
    n = len(df)
    i = 0

    # Pre-extract the relevant columns for faster access
    columns_data = {name: df[name].values if name in df.columns else None for name in test_names}
    index = df.index

    for _ in range(n):
        if i >= n:
            break  # safeguard, since we'll manually advance i

        best_len = 0
        best_name = None

        for name in test_names:
            col = columns_data[name]
            if col is None or not col[i]:
                continue
            seg_id = col[i]

            length = 0
            for j in range(i, n):
                if col[j] == seg_id:
                    length += 1
                else:
                    break

            if length > best_len:
                best_len = length
                best_name = name

        if best_name:
            counters[best_name] += 1
            label = f"{counters[best_name]}_{best_name}"
            df.loc[index[i:i + best_len], 'Sequence'] = label
            i += best_len
        else:
            i += 1

    return df


def _analyze_segments(df: pd.DataFrame, SHOW_RUNTIME: bool, SEGMENT_SEQUENCE_CONFIG):
    """
    Analyzes a DataFrame and returns a DataFrame with the columns 'ID', 'Sequence', and
    all columns specified in SEGMENT_SEQUENCE_CONFIG.

    The function first tags simple segments in the DataFrame, then tags sequences
    (each segment/sequence got the same value during it's ID(s)),
    assigns the longest sequence found to each row in the column 'Sequence' using the format "<Occurrence>_<TestName>",

    Parameters:
        df (pd.DataFrame): The DataFrame to be analyzed.
        SHOW_RUNTIME (bool): If True, the function logs the time taken to perform each step.
        SEGMENT_SEQUENCE_CONFIG (dict): A dictionary containing the configuration for the analysis.
            Example:{"Current": {"rules": {"variable": "I", ...}}, ...}

    Returns:
        df_segments_and_sequences (pd.DataFrame): A DataFrame containing the columns 'ID', 'Sequence', and all columns
                                                  specified in SEGMENT_SEQUENCE_CONFIG.
    """
    with log_time("tag simple segments", SHOW_RUNTIME):
        df = _tag_simple(df, SEGMENT_SEQUENCE_CONFIG)
    with log_time("tag sequences", SHOW_RUNTIME):
        df = _tag_sequences(df, SEGMENT_SEQUENCE_CONFIG)
    with log_time("assign longest sequence", SHOW_RUNTIME):
        df = _assign_longest_sequence(df, SEGMENT_SEQUENCE_CONFIG)
    with log_time("separate sequences and df_with_segments", SHOW_RUNTIME):
        segment_keys = [key for key in SEGMENT_SEQUENCE_CONFIG.keys() if key in df.columns]
        df_segments_and_sequences = df[["ID", "Sequence"] + segment_keys]
    return df_segments_and_sequences

