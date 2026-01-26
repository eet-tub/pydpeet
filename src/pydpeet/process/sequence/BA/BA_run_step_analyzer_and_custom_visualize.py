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
# 'Discharge at 9.600A until 2.498V',
# ...
# ]













# from pydpeet.process.sequence.utils.postprocessing.filter_df import *
# from pydpeet.process.sequence.step_analyzer import *
#
# df_primitives = step_analyzer_primitives(
#     #...
# )
# df_segments_and_sequences = step_analyzer_seqments_and_sequences(
#     #...
# )
#
# rules = [
#     "Charge_iOCV",
#     "Discharge_iOCV",
# ]
# _, df_filtered = filter_and_split_df_by_blocks(
#     df_segments_and_sequences=df_segments_and_sequences,
#     df_primitives=df_primitives,
#     rules=rules,
#     combine_op='or'
# )
#
# rules = [
#     "Pause",
# ]
# dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
#     df_segments_and_sequences=df_segments_and_sequences,
#     df_primitives=df_filtered,
#     rules=rules,
#     combine_op='or'
# )













from numba import njit


def factorial(n):
   result = 1.0
   for i in range(1,n+1):
       result *= i
   return result

@njit
def factorial_njit(n):
   result = 1.0
   for i in range(1,n+1):
       result *= i
   return result




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


df_file = load_file(FILE_NAME)
#df_file.drop_duplicates(subset=["Testtime[s]"], inplace=True)

#df_file = pandas.read_parquet("D:\Downloads\AM23NMC00012.parquet")
#df_file = df_file[["Voltage[V]", "Current[A]", "Testtime[s]"]]
#df_file.to_parquet("D:\Downloads\AM23NMC00012.parquet")
#df_file = df_file.head(68291)

def thin_df_by_min_interval(df, time_col='Testtime[s]', min_interval=60):
    """
    Return a dataframe keeping only rows where time_col is at least
    `min_interval` greater than the previously kept row.
    """
    # Work on a sorted copy
    df_sorted = df.sort_values(time_col).copy()
    # Ensure numeric and drop rows with NaN times
    times = pd.to_numeric(df_sorted[time_col], errors='coerce')
    valid = times.notna()
    df_sorted = df_sorted[valid].reset_index(drop=True)
    times = times[valid].to_numpy()

    keep_positions = []
    last_time = -1e18  # very small sentinel so first row is kept
    for i, t in enumerate(times):
        if t >= last_time + min_interval:
            keep_positions.append(i)
            last_time = t

    result = df_sorted.iloc[keep_positions].reset_index(drop=True)
    return result

# Usage: replace df_file with the thinned dataframe
#df_file = thin_df_by_min_interval(df_file, time_col='Testtime[s]', min_interval=60)

#df_primitives_all = step_analyzer_primitives(df=df_file,
#                                         STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG)
#df_file['Current[A]'] = np.nan



#df_file['Current[A]'] = np.NAN
df_primitives = step_analyzer_primitives(df=df_file,
                                         STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
                                         check_CV_0Aend_segments_bool=True,
                                         check_zero_length_segments_bool=False,
                                         PRECOMPILE=True,
                                         FORCE_PRECOMPILATION=True)
#df_primitives["Current[A]"] = df_primitives_all["Current[A]"]

# can be used to correct dataframe or to know the min, max, avg, type, direction or slope of each segment
correction_config = {
    "replace_ID": {

    },
    "replace_time": {
        #(5000.0, 15000.0): "P",
    },
    "replace_time_and_merge": {
        #(5000.0, 15000.0): "P",
        #(df_primitives['Testtime[s]'].min(), df_primitives['Testtime[s]'].max()): "I",
    },
    "merge_left": [
        #2,
    ],
    "merge_right": [
        #1,
    ],
    "merge_range": [
        #(1, 10),
    ]
}


if SHOW_RUNTIME: print("cleaning up segments...")
with log_time("cleaning up segments", SHOW_RUNTIME=SHOW_RUNTIME):
    df_primitives = df_primitives_correction(df_primitives=df_primitives,
                                             correction_config=correction_config,
                                             data_columns=DATA_COLUMNS,
                                             thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION)

df_segments_and_sequences = step_analyzer_seqments_and_sequences(df_primitives,
                                                                 SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG,
                                                                 SHOW_RUNTIME=True)

x = False
if x:
    with log_time("generating instructions", SHOW_RUNTIME=SHOW_RUNTIME):
        instructions = [
            *generate_instructions(
                df_primitives=df_primitives,
                end_condition_map=END_CONDITION_MAP_GENERATE_INSTRUCTIONS
            )
        ]
        instructions = [
            (
            'Charge at 2A for 60s',
            'Rest for 360.0 seconds'
            ) *10,
            "Rest for 3600 seconds"
        ]


x = False
print_instructions = True
print_instructions_limit = 1000000
if x:
    with log_time("running pybamm simulation", SHOW_RUNTIME=SHOW_RUNTIME):
        if print_instructions:
            for i, row in enumerate(instructions[:print_instructions_limit]):
                print(f"{i+1}: {row}")
        experiment = pybamm.Experiment(instructions)
        parameter_values = pybamm.ParameterValues("Chen2020")

        sim = pybamm.Simulation(
            pybamm.lithium_ion.SPM(),
            experiment=experiment,
            parameter_values=parameter_values
        )

        solution = sim.solve(initial_soc=0)
        y = False
        if y:
            t = solution["Time [s]"]
            I = solution["Current [A]"]
            V = solution["Voltage [V]"]
            df_experiment = pd.DataFrame({
                "Testtime[s]": t.entries,
                "Voltage[V]": V.entries,
                "Current[A]": I.entries,

            })
            df_experiment["Current[A]"] = -df_experiment["Current[A]"] #invert cause pybamm uses other direction
            df_experiment["Testtime[s]"] = df_experiment["Testtime[s]"] # convert to seconds?

            import os
            base_path = os.path.dirname(os.path.abspath(__file__))
            res_path = os.path.join(base_path, "res")
            df_experiment.to_parquet(os.path.join(res_path, "BENCHMARK_Daniel_df_experiment.parquet"))

    y = False
    if y:
        benchmark(df_file=df_file, df_experiment=df_experiment)

x = False
if x:
    with log_time("plotting pybamm simulation", SHOW_RUNTIME=SHOW_RUNTIME):
        sim.plot(output_variables=["Current [A]", "Voltage [V]"])

rules = [
    #"V",
    #"Charge_iOCV",
    #"Discharge_iOCV",
    #"CCCV_Charge"
    #"CRamp_Charge",
    #"CC_Charge",
    #"Pause"
]

if SHOW_RUNTIME: print("filtering IDs and splitting into DataFrames per block...")
with log_time("filtering IDs", SHOW_RUNTIME=SHOW_RUNTIME):
    dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
        df_segments_and_sequences=df_segments_and_sequences,
        df_primitives=df_primitives,
        rules=rules,
        combine_op='or',
        print_blocks=False,
        also_return_filtered_df=True
    )
    rules = [
        #"Pause"
    ]
    dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
        df_segments_and_sequences=df_segments_and_sequences,
        df_primitives=df_filtered,
        rules=rules,
        combine_op='or',
        print_blocks=False,
        also_return_filtered_df=True
    )



# Calculate first derivative of Voltage[V] over time
#df_filtered["dV/dt"] = df_filtered["Voltage[V]"].diff() / df_filtered["Testtime[s]"].diff()
#df_filtered["dI/dt"] = df_filtered["Current[A]"].diff() / df_filtered["Testtime[s]"].diff()
#df_filtered["dW/dV"] = df_filtered["Power[W]"].diff() / df_filtered["Testtime[s]"].diff()





if SHOW_RUNTIME: print("starting visualization process...")
visualize_phases(
    dataframe=df_filtered,
    start_time=START,
    end_time=END,
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
