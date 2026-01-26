from pydpeet.process.sequence.BA.TEMP_load_and_preprocess_file import load_file
from pydpeet.process.sequence.step_analyzer import step_analyzer_primitives
from pydpeet.process.sequence.Example_Usage.CONFIG_example import *
from pydpeet.process.sequence.step_analyzer import step_analyzer_seqments_and_sequences
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
from pydpeet.process.sequence.utils.visualize.visualize_data import visualize_phases
from matplotlib import pyplot as plt

df_file = load_file('additional_20250429153146-Daniel_Steperkennung-1-2-AM23NMC00063.parquet',base_path=__file__)
if "Absolute Time[yyyy-mm-dd hh:mm:ss]" in df_file.columns:
    df_file = df_file.drop_duplicates(subset=["Absolute Time[yyyy-mm-dd hh:mm:ss]"], keep="first")
df_file = df_file[["Voltage[V]", "Current[A]", "Testtime[s]"]]
df_primitives = step_analyzer_primitives(df=df_file, STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG)
visualize_phases(dataframe=df_primitives)
df_segments_and_sequences = step_analyzer_seqments_and_sequences(df_primitives, SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG)

########################################################################################################################
# Visualisierung der primitiven Segmente
plt.show()

# Filtern nach iOCV Sequenzen
_, df_filtered_1 = filter_and_split_df_by_blocks(
    df_primitives=df_primitives,
    df_segments_and_sequences=df_segments_and_sequences,
    rules=["Charge_iOCV", "Discharge_iOCV"],
    combine_op='or'
)
visualize_phases(dataframe=df_filtered_1)
plt.show()

# Filtern nach Pausen in den iOCV Sequenzen
_, df_filtered_2 = filter_and_split_df_by_blocks(
    df_primitives=df_filtered_1,
    df_segments_and_sequences=df_segments_and_sequences,
    rules=["Pause"],
    combine_op='or'
)
visualize_phases(dataframe=df_filtered_2)
plt.show()


