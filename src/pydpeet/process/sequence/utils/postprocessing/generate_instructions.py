import logging
from typing import Optional

import pandas as pd

from pydpeet.process.sequence.step_analyzer import extract_sequence_overview

SEGMENTS_CONFIG_STANDARD: dict[str, dict] = {
    "Pause": {
        "rules": {
            "type": "Rest",
        }
    },
    "CC_Charge": {
        "rules": {
            "variable": "I",
            "type": "Constant",
            "direction": "Charge",
        }
    },
    "CV_Charge": {
        "rules": {
            "variable": "V",
            "type": "Constant",
            "direction": "Charge",
        }
    },
    "CP_Charge": {
        "rules": {
            "variable": "P",
            "type": "Constant",
            "direction": "Charge",
        }
    },
    "CC_Discharge": {
        "rules": {
            "variable": "I",
            "type": "Constant",
            "direction": "Discharge",
        }
    },
    "CV_Discharge": {
        "rules": {
            "variable": "V",
            "type": "Constant",
            "direction": "Discharge",
        }
    },
    "CP_Discharge": {
        "rules": {
            "variable": "P",
            "type": "Constant",
            "direction": "Discharge",
        }
    },
    "CRamp_Charge": {
        "rules": {
            "variable": "I",
            "type": "Ramp",
            "direction": "Up",
        }
    },
    "VRamp_Charge": {
        "rules": {
            "variable": "V",
            "type": "Ramp",
            "direction": "Up",
        }
    },
    "PRamp_Charge": {
        "rules": {
            "variable": "P",
            "type": "Ramp",
            "direction": "Up",
        }
    },
    "CRamp_Discharge": {
        "rules": {
            "variable": "I",
            "type": "Ramp",
            "direction": "Down",
        }
    },
    "VRamp_Discharge": {
        "rules": {
            "variable": "V",
            "type": "Ramp",
            "direction": "Down",
        }
    },
    "PRamp_Discharge": {
        "rules": {
            "variable": "P",
            "type": "Ramp",
            "direction": "Down",
        }
    },
}


def _parse_segment_type(seg_type: str) -> tuple[str, str | None]:
    """
    Parse a segment type string into its base and direction.

    Parameters:
    seg_type (str): segment type string

    Returns:
    tuple: (base, direction)

    base (str): base of the segment type (e.g. CC, CV, CP, CRamp, VRamp, PRamp)
    direction (str): direction of the segment type (e.g. Charge, Discharge)

    Example:
    _parse_segment_type("CC_Charge") -> ("CC", "Charge")
    _parse_segment_type("Ramp_Current_Charge") -> ("CRamp", "Charge")
    """
    if seg_type in ("Pause", "Rest"):
        return "Pause", None

    # Case 1: already in the form CC_Charge, CRamp_Discharge, etc.
    if "_" in seg_type and seg_type.split("_")[0] in {"CC", "CV", "CP", "CRamp", "VRamp", "PRamp"}:
        base, *tail = seg_type.split("_")
        direction = tail[-1] if tail else None

        return base, direction

    # Case 2: new naming scheme ► Ramp_{Current|Voltage|Power}_{Charge|Discharge}
    if seg_type.startswith("Ramp_"):
        _, signal, *tail = seg_type.split("_")
        mapping = {"Current": "CRamp", "Voltage": "VRamp", "Power": "PRamp"}
        base = mapping.get(signal, "UNKNOWN")
        direction = tail[-1] if tail else None

        return base, direction

    # Fallback
    return "UNKNOWN", None


def _get_important_entries_per_segment(
    df_primitives: pd.DataFrame, df_segments_and_sequences: pd.DataFrame
) -> pd.DataFrame:
    """
    Get the last entries per segment from a primitives dataframe and a segments_and_sequences dataframe.

    Parameters:
    df_primitives (pd.DataFrame): primitives dataframe
    df_segments_and_sequences (pd.DataFrame): segments_and_sequences dataframe

    Returns:
    pd.DataFrame: dataframe with the last entries per segment (ID, Segment_Type, End_Value_Voltage[V],
                  End_Value_Current[A], End_Value_Power[W], End_Value_Length, Type, Direction, AVG_Current)

    """
    segment_type_cols = [c for c in df_segments_and_sequences.columns if c not in ["ID", "Sequence"]]

    records = []
    for _, row in df_segments_and_sequences.iterrows():
        seg_id = row["ID"]
        segment_type = row[segment_type_cols].idxmax()

        segment_df = df_primitives[df_primitives["ID"] == seg_id]
        last_row = segment_df.iloc[-1]

        records.append(
            {
                "ID": seg_id,
                "Segment_Type": segment_type,
                "End_Value_Voltage[V]": last_row["Voltage[V]"],
                "End_Value_Current[A]": last_row["Current[A]"],
                "End_Value_Power[W]": last_row["Power[W]"],
                "End_Value_Length": last_row["Length"],
                "Type": last_row["Type"],
                "Direction": last_row["Direction"],
                "AVG_Current": segment_df["Current[A]"].mean(),
                # "AVG_Voltage": segment_df["Voltage[V]"].mean(),
                # "AVG_Power":   segment_df["Power[W]"].mean(),
            }
        )

    dataframe_records = pd.DataFrame(records)

    return dataframe_records


def generate_instructions(
    df_primitives: pd.DataFrame,
    end_condition_map: Optional[dict] = None,
    threshold_warnings: int = 5,
) -> list[str]:
    """
    Generate PyBaMM instructions based on the given primitives dataframe and end condition map.
    Replaces Ramps with AVG Current for time.

    Parameters:
    df_primitives (pd.DataFrame): primitives dataframe
    end_condition_map (dict): end condition map (key: segment type, value: end condition)
        Example: {"CC": "voltage", "CV": "current", "CP": "voltage","Pause": "time"}

    Returns:
    list: list of instructions
    """
    # Set default values for mutable data structures
    if end_condition_map is None:
        end_condition_map = {
            "CC": "voltage",
            "CV": "current",
            "CP": "voltage",
            "Pause": "time",
        }
    df_segments_and_sequences = extract_sequence_overview(
        df_primitives, SEGMENT_SEQUENCE_CONFIG=SEGMENTS_CONFIG_STANDARD
    )
    results = _get_important_entries_per_segment(df_primitives, df_segments_and_sequences)
    instructions = []
    unknown_seen = False

    too_many_warnings = 0
    for _, row in results.iterrows():
        raw_seg_type = row["Segment_Type"]
        base_type, direction = _parse_segment_type(raw_seg_type)

        if base_type == "UNKNOWN":
            instructions.append(
                f"\033[91mUnknown segment type '{raw_seg_type}' " f"for {row['End_Value_Length']}s encountered\033[0m"
            )
            unknown_seen = True
            continue

        current = row["AVG_Current"] if "Ramp" in base_type else row["End_Value_Current[A]"]
        length = row["End_Value_Length"]

        # Determine end condition
        end_condition = end_condition_map.get(base_type.replace("Ramp", ""), "time")

        # TODO: Docstring
        def build_instruction(
            action: str,
            value_str: str,
            current: float = current,
            row: pd.Series = row,
            length: int = length,
            end_condition: str = end_condition,
        ) -> str:
            if end_condition == "time":
                return f"{action} at {value_str} for {length} seconds"

            cond_val, units = {
                "current": (abs(current), "A"),
                "voltage": (abs(row["End_Value_Voltage[V]"]), "V"),
                "power": (abs(row["End_Value_Power[W]"]), "W"),
            }.get(end_condition, (length, "seconds"))

            return f"{action} at {value_str} until {cond_val}{units}"

        # Handle Ramp replacements with current-based logic
        if base_type in {"CRamp", "VRamp", "PRamp"}:
            if too_many_warnings < threshold_warnings:
                logging.warning(f"{base_type} segment (ID: {row['ID']}) replaced by CC with Average Current")
                too_many_warnings += 1
            if direction == "Charge" or (direction is None and current > 0):
                instructions.append(build_instruction("Charge", f"{abs(current):.3f}A"))
            elif direction == "Discharge" or (direction is None and current < 0):
                instructions.append(build_instruction("Discharge", f"{abs(current):.3f}A"))

        # Standard CC (non-ramp current)
        elif base_type == "CC":
            if direction == "Charge" or (direction is None and current > 0):
                instructions.append(build_instruction("Charge", f"{abs(current):.3f}A"))
            elif direction == "Discharge" or (direction is None and current < 0):
                instructions.append(build_instruction("Discharge", f"{abs(current):.3f}A"))

        # Constant voltage (CV)
        elif base_type == "CV":
            voltage = row["End_Value_Voltage[V]"]
            if direction == "Charge" or (direction is None and current > 0):
                instructions.append(build_instruction("Hold", f"{abs(voltage):.3f}V"))
            elif direction == "Discharge" or (direction is None and current < 0):
                instructions.append(build_instruction("Hold", f"{abs(voltage):.3f}V"))

        # Constant power (CP)
        elif base_type == "CP":
            power = row["End_Value_Power[W]"]
            if direction == "Charge" or (direction is None and power > 0):
                instructions.append(build_instruction("Charge", f"{abs(power):.2f}W"))
            elif direction == "Discharge" or (direction is None and power < 0):
                instructions.append(build_instruction("Discharge", f"{abs(power):.2f}W"))

        # Pause/Rest
        elif base_type == "Pause":
            instructions.append(f"Rest for {length} seconds")
    if too_many_warnings > threshold_warnings:
        logging.warning("...")
    if unknown_seen:
        logging.warning("Unknown segment types encountered. " "Instructions may be incomplete!")

    return instructions
