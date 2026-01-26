from pydpeet.process.sequence.utils.postprocessing.filter_df import *
from pydpeet.process.sequence.step_analyzer import *


SEGMENT_CONFIG = {
    "CC_Charge":      {"rules": {"variable": "I", "type": "Constant", "direction": "Charge"}},
    "CC_Discharge":   {"rules": {"variable": "I", "type": "Constant", "direction": "Discharge"}},
    "Pause":          {"rules": {"type": "Rest"}},
}
SEQUENCE_CONFIG = {
    "Discharge_iOCV": {"loop": True, "sequence": ["CC_Discharge", "Pause"]},
    "Charge_iOCV":    {"loop": True, "sequence": ["Pause", "CC_Charge"]},
}
SEGMENT_SEQUENCE_CONFIG = {
    **SEQUENCE_CONFIG,
    **SEGMENT_CONFIG
}

#...

rules = [
    "Charge_iOCV",
    "Discharge_iOCV"
]

dfs_per_block = filter_and_split_df_by_blocks(
    rules=rules
    #...
)

# Beispielhafte Parameter
min_loops = 4
min_pause_length = 30

# Weitere Filterfunktionen
dfs_per_block = [df[df["Type"] == "Rest"] for df in dfs_per_block]
dfs_per_block = [df.loc[df.groupby("ID")["Testtime[s]"].idxmax()] for df in dfs_per_block]
dfs_per_block = [df for df in dfs_per_block if df["ID"].nunique() >= min_loops]
dfs_per_block = [df for df in dfs_per_block if df["Duration"].min() >= min_pause_length]












df_primitives = step_analyzer_primitives(
    #...
)
df_segments_and_sequences = step_analyzer_seqments_and_sequences(
    #...
)

rules = [
    "Charge_iOCV",
    "Discharge_iOCV",
]
_, df_filtered = filter_and_split_df_by_blocks(
    df_segments_and_sequences=df_segments_and_sequences,
    df_primitives=df_primitives,
    rules=rules,
    standard_columns=["Testtime[s]", "Voltage[V]", "Current[A]", "Power[W]"],
    combine_op='or'
)
rules = [
    "Pause",
]
dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
    df_segments_and_sequences=df_segments_and_sequences,
    df_primitives=df_filtered,
    rules=rules,
    standard_columns=["Testtime[s]", "Voltage[V]", "Current[A]", "Power[W]"],
    combine_op='or'
)






from pydpeet.process.sequence.utils.postprocessing.generate_instructions import generate_instructions

#...

instructions = [
    *generate_instructions(
        #...
    )
]

print(instructions)
# Beispielhafte Ausgabe:
# ['Charge at 1.438A until 4.1999V',
# 'Hold at 4.200V until 0.05A',
# 'Discharge at 0.960A until 2.5033V',
# 'Hold at 2.500V until 0.0501A',
# 'Charge at 4.800A until 4.2V',
# 'Discharge at 9.600A until 2.4984V',
# ...
# ]













SEGMENT_CONFIG = {
    "CC_Charge":      {"rules": {"variable": "I", "type": "Constant", "direction": "Charge"}},
    "CC_Discharge":   {"rules": {"variable": "I", "type": "Constant", "direction": "Discharge"}},
    "Pause":          {"rules": {"type": "Rest"}},
    #...
}
SEQUENCE_CONFIG = {
    "Discharge_iOCV": {"loop": True, "sequence": ["CC_Discharge", "Pause"]},
    "Charge_iOCV":    {"loop": True, "sequence": ["Pause", "CC_Charge"]},
    #...
}
SEGMENT_SEQUENCE_CONFIG = {
    **SEQUENCE_CONFIG,
    **SEGMENT_CONFIG
}
































import pandas as pd
from matplotlib import pyplot as plt

from pydpeet.process.sequence.step_analyzer import step_analyzer_primitives, step_analyzer_seqments_and_sequences
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks



file_name_options = {
    "Neware": '20240307170835-Cyc_2C_1C_100DOD_50_SOC-2-1-AM23NMC00041_Neware_2025-04-24_20-36-56_Data.parquet',
    "Daniel": 'additional_20250429153146-Daniel_Steperkennung-1-2-AM23NMC00063.parquet',
    "BigBoi": "AM23NMC00012.parquet"
}

FILE_IDENTIFIER = "Daniel"
FILE_NAME = file_name_options[FILE_IDENTIFIER]
from pydpeet.process.sequence.BA.TEMP_load_and_preprocess_file import load_file
df_file = load_file(FILE_NAME, FILE_IDENTIFIER, [
        "Testtime[s]",
        "Voltage[V]",
        "Current[A]"
    ])






df_primitives = step_analyzer_primitives(df=df_file)
df_segments_and_sequences = step_analyzer_seqments_and_sequences(
    df_primitives=df_primitives,
    SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG
)

dfs = filter_and_split_df_by_blocks(
    df_segments_and_sequences=df_segments_and_sequences,
    df_primitives=df_primitives,
    rules=["Discharge_iOCV", "Charge_iOCV"],
    combine_op='or',
    also_return_filtered_df=False
)

dfs = [df[df["Type"] == "Rest"] for df in dfs]
dfs = [df.loc[df.groupby("ID")["Testtime[s]"].idxmax()] for df in dfs]
dfs = [df for df in dfs if df["ID"].nunique() >= 4]
dfs = [df for df in dfs if df["Duration"].min() >= 30]

df_merged = pd.concat(dfs, ignore_index=True)
df_merged = df_merged.rename(columns={"Voltage[V]": "iOCV-Voltage[V]"})

plt.plot(df_merged['Testtime[s]'], df_merged['iOCV-Voltage[V]'], marker='s', linestyle='None', markersize=8, label='iOCV-Voltage[V]')
plt.xlabel("Time [s]", fontsize=15)
plt.ylabel("Voltage [V]", fontsize=15)
plt.show()

















