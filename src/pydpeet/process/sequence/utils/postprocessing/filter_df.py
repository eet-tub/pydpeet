import logging
import operator
from functools import reduce

import pandas as pd
from pandas import DataFrame


def filter_df(df_segments_and_sequences,
              df_primitives,
              rules,
              standard_columns,
              combine_op='xor'):

    # Map string to actual function
    comb_funcs = {
        'and': operator.and_,
        'or': operator.or_,
        'xor': operator.xor,
        'not': operator.not_
    }
    if combine_op not in comb_funcs:
        raise ValueError(f"combine_op must be one of {list(comb_funcs)}")

    if not rules:
        # No filtering, use all IDs
        df_filtered_IDs = df_segments_and_sequences["ID"].values
    else:
        # build list of boolean Series for each rule
        masks = []
        for col in rules:
            if col not in df_segments_and_sequences:
                raise KeyError(f"column {col!r} not in DataFrame")
            masks.append(operator.ne(df_segments_and_sequences[col], 0))

        # combine masks with selected operator
        combined_mask = reduce(comb_funcs[combine_op], masks)
        df_filtered_IDs = df_segments_and_sequences[combined_mask]["ID"].values

    # Create standard and non-standard dataframes
    df_standard = df_primitives[standard_columns + ["ID", "Power[W]"]]
    df_non_standard = df_primitives[[col for col in df_primitives.columns if col not in standard_columns + ["Power[W]"]]]

    # Nullify non-standard rows not in filtered IDs
    mask = ~df_non_standard["ID"].isin(df_filtered_IDs)
    cols_to_null = [col for col in df_non_standard.columns if col != "ID"]
    df_non_standard.loc[mask, cols_to_null] = None
    df_non_standard.loc[mask, "Variable"] = "Filtered"

    # Combine standard and non-standard
    df_filtered = pd.concat([df_standard, df_non_standard.drop(columns="ID")], axis=1)

    return df_filtered, df_filtered_IDs


def return_or_print_blocks(df_filtered: pd.DataFrame,
                           filtered_IDs: pd.Series | list | set, tuple,
                           print_blocks: bool = True) -> None | list[dict]:

    import numpy as np

    # Ensure IDs are in a fast lookup structure
    filtered_IDs_set = set(filtered_IDs)

    # Convert necessary columns to arrays
    ids = df_filtered["ID"].values
    testtimes = df_filtered["Test_Time[s]"].values
    is_filtered = df_filtered["Variable"].values == "Filtered"

    # Boolean mask for unfiltered rows
    unfiltered_mask = np.isin(ids, list(filtered_IDs_set)) & ~is_filtered

    # Find block boundaries (diff between 0/1 in mask)
    block_edges = np.diff(unfiltered_mask.astype(int))
    starts = np.where(block_edges == 1)[0] + 1
    ends = np.where(block_edges == -1)[0]

    # Edge case: starts/ends at beginning or end
    if unfiltered_mask[0]:
        starts = np.insert(starts, 0, 0)
    if unfiltered_mask[-1]:
        ends = np.append(ends, len(unfiltered_mask) - 1)

    blocks = []
    for i, (start_idx, end_idx) in enumerate(zip(starts, ends, strict=False), start=-1):
        start_id = ids[start_idx]
        end_id = ids[end_idx]
        start_time = testtimes[start_idx]
        end_time = testtimes[end_idx]
        if print_blocks:
            logging.info("-" * 40)
            logging.info(f"Block {i + 1}:")
            logging.info(f"  Start ID: {start_id}, Test_Time[s]: {start_time}")
            logging.info(f"  End ID:   {end_id}, Test_Time[s]: {end_time}")
            logging.info("-" * 40)

        blocks.append(
            {
                "start_id": start_id,
                "end_id": end_id,
                "start_time": start_time,
                "end_time": end_time,
            }
        )

    return blocks


def split_df_by_blocks(df_filtered: pd.DataFrame, blocks: list[dict]) -> list[pd.DataFrame]:
    """
    Split df_filtered into multiple DataFrames per block.
    Each block includes all rows from start_id to end_id (inclusive), even if IDs repeat.
    """
    dfs_per_block = []
    ids = df_filtered["ID"].values

    for block in blocks:
        start_id = block["start_id"]
        end_id = block["end_id"]

        # Find ALL positions of start_id and end_id
        start_positions = (ids == start_id).nonzero()[0]
        end_positions = (ids == end_id).nonzero()[0]

        if len(start_positions) == 0 or len(end_positions) == 0:
            continue  # skip if not found

        start_idx = start_positions[0]
        end_idx = end_positions[-1]

        df_block = df_filtered.iloc[start_idx : end_idx + 1].copy()
        dfs_per_block.append(df_block)

    return dfs_per_block

def filter_and_split_df_by_blocks(df_segments_and_sequences: pd.DataFrame,
                                  df_primitives: pd.DataFrame,
                                  rules: list[str],
                                  combine_op: str = 'or',
                                  print_blocks: bool = False,
                                  also_return_filtered_df: bool = True
                                  ) -> tuple[list[DataFrame], DataFrame] | list[DataFrame]:


    standard_columns = ["Test_Time[s]", "Voltage[V]", "Current[A]", "Power[W]"]
    logging.warning("Using default standard columns:")
    logging.warning(standard_columns)

    df_filtered, df_filtered_IDs = filter_df(
        df_segments_and_sequences=df_segments_and_sequences,
        df_primitives=df_primitives,
        rules=rules,
        combine_op=combine_op,
        standard_columns=standard_columns
    )

    blocks = return_or_print_blocks(
        df_filtered=df_filtered,
        filtered_IDs=df_filtered_IDs,
        print_blocks=print_blocks
    )

    dfs_per_block = split_df_by_blocks(
        df_filtered=df_filtered,
        blocks=blocks
    )

    if also_return_filtered_df:
        return dfs_per_block, df_filtered
    return dfs_per_block
