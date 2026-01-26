import numpy as np
import pandas as pd
import pybamm
from matplotlib import pyplot as plt

from TEMP_load_and_preprocess_file import load_file
from pydpeet.process.sequence.BA.BA_compare_PyBaMM_with_real_data import benchmark
from pydpeet.process.sequence.step_analyzer import step_analyzer_seqments_and_sequences, step_analyzer_primitives
from pydpeet.process.sequence.utils.console_prints.log_time import log_time
from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
from pydpeet.process.sequence.utils.postprocessing.generate_instructions import generate_instructions
from pydpeet.process.sequence.BA.BA_custom_visualize_phases import visualize_phases

file_name_options = {
    "Neware": '20240307170835-Cyc_2C_1C_100DOD_50_SOC-2-1-AM23NMC00041_Neware_2025-04-24_20-36-56_Data.parquet',
    "Arbin": 'Arbin_Pack_Test_240009-1-1-816_Arbin_2025-05-05_14-45-14_Data.parquet',
    "ArbinOLD": 'ArbinOLD_QUEEN_Test_ProtC_C-011_55_Arbin_Old_2025-05-05_14-46-13_Data.parquet',
    "Basytec": 'Basytec145_TC23LFP01_CU_25deg_BaSyTec_2025-05-05_14-47-23_Data.parquet',
    "Daniel": 'additional_20250429153146-Daniel_Steperkennung-1-2-AM23NMC00063.parquet',
    "DanielTEST": "TEST_INPUT_Daniel_sampled_every_60s_with_first_last.parquet",
}

FILE_IDENTIFIER = "Daniel"
FILE_NAME = file_name_options[FILE_IDENTIFIER]

from pydpeet.process.sequence.BA.BA_CONFIG import *


df_file = load_file(FILE_NAME, FILE_IDENTIFIER, STANDARD_COLUMNS)

df_primitives = step_analyzer_primitives(df=df_file,
                                         STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
                                         PRECOMPILE=False)

df_primitives['dV/dt'] = df_primitives['Voltage[V]'].diff() / df_primitives['Testtime[s]'].diff()
df_primitives['dI/dt'] = df_primitives['Current[A]'].diff() / df_primitives['Testtime[s]'].diff()
df_primitives_DS = df_primitives.iloc[::5, :].reset_index(drop=True)
df_primitives_DS['dV/dt downsampled'] = df_primitives_DS['Voltage[V]'].diff() / df_primitives_DS['Testtime[s]'].diff()
df_primitives_DS['dI/dt downsampled'] = df_primitives_DS['Current[A]'].diff() / df_primitives_DS['Testtime[s]'].diff()

print("min dI/dt in time range [10400, 10800]:", df_primitives.loc[(df_primitives['Testtime[s]'] >= 10400) & (df_primitives['Testtime[s]'] <= 10800), 'dI/dt'].min())

x = False
if x:
    LINE_VISUALIZATION_CONFIG = [
        ("Voltage[V]", "blue", (4.15, 4.25)),
        ("Current[A]", "red", (1, 1.8)),
        #("dV/dt", "darkblue", (-0.01, 0.01)),
        #("dI/dt", "purple", (-0.02, 0.02)),
    ]
    visualize_phases(
        dataframe=df_primitives,
        start_time=10400,
        end_time=10800,
        visualize_phases_config=VISUALIZE_PHASES_CONFIG,
        segment_alpha=SEGMENT_ALPHA,
        line_visualization_config=LINE_VISUALIZATION_CONFIG,
        use_lines_for_segments=USE_LINES_FOR_SEGMENTS,
        show_column_names=SHOW_COLUMN_NAMES,
        show_time=SHOW_TIME,
        show_id=SHOW_ID,
        width_height_ratio=WIDTH_HEIGHT_RATIO,
        show_runtime=SHOW_RUNTIME_VISUALIZATION and SHOW_RUNTIME
    )
x = False
if x:
    LINE_VISUALIZATION_CONFIG = [
        #("Voltage[V]", "blue", (2.4, 4.4)),
        #("Current[A]", "red", (-15, 5)),
        #("dV/dt downsampled", "darkblue", (-0.01, 0.01)),
        ("dI/dt downsampled", "purple", (-0.02, 0.02)),
    ]
    visualize_phases(
        dataframe=df_primitives_DS,
        start_time=10400,
        end_time=10800,
        visualize_phases_config=VISUALIZE_PHASES_CONFIG,
        segment_alpha=SEGMENT_ALPHA,
        line_visualization_config=LINE_VISUALIZATION_CONFIG,
        use_lines_for_segments=USE_LINES_FOR_SEGMENTS,
        show_column_names=SHOW_COLUMN_NAMES,
        show_time=SHOW_TIME,
        show_id=SHOW_ID,
        width_height_ratio=WIDTH_HEIGHT_RATIO,
        show_runtime=SHOW_RUNTIME_VISUALIZATION and SHOW_RUNTIME
    )

x = True
if x:
    df_primitives_DS.drop("dI/dt", axis=1, inplace=True)
    df_primitives_DS.drop("dV/dt", axis=1, inplace=True)
    df_primitives_DS = df_primitives_DS[df_primitives_DS['Testtime[s]'] <= 10630].reset_index(drop=True)
    df_primitives = df_primitives[df_primitives['Testtime[s]'] > 10630].reset_index(drop=True)
    df_merged = pd.concat([df_primitives, df_primitives_DS], ignore_index=True)

    LINE_VISUALIZATION_CONFIG = [
        ("dI/dt downsampled", "darkblue", (-0.0051, 0.0051)),
        ("dI/dt", "purple", (-0.0051, 0.0051)),
    ]
    visualize_phases(
        dataframe=df_merged,
        start_time=10400,
        end_time=10800,
        visualize_phases_config=VISUALIZE_PHASES_CONFIG,
        segment_alpha=SEGMENT_ALPHA,
        line_visualization_config=LINE_VISUALIZATION_CONFIG,
        use_lines_for_segments=USE_LINES_FOR_SEGMENTS,
        show_column_names=SHOW_COLUMN_NAMES,
        show_time=SHOW_TIME,
        show_id=SHOW_ID,
        width_height_ratio=WIDTH_HEIGHT_RATIO,
        show_runtime=SHOW_RUNTIME_VISUALIZATION and SHOW_RUNTIME
    )
mngr = plt.get_current_fig_manager()
mngr.window.wm_geometry("+0+0")
mngr.set_window_title('detect_segments + filter')
plt.show()