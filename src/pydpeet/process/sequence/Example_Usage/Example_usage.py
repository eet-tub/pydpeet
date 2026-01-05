#######################################################################################################################
def run_import_df(FILE_IDENTIFIER, remove_duplicate_absolute_time_values):
    # Import the DataFrame (examples created using ppb24)
    from pydpeet.process.sequence.BA.TEMP_load_and_preprocess_file import (
        load_file)

    file_name_options = {
        "Neware": '20240307170835-Cyc_2C_1C_100DOD_50_SOC-2-1-AM23NMC00041_Neware_2025-04-24_20-36-56_Data.parquet',
        "Arbin": 'Arbin_Pack_Test_240009-1-1-816_Arbin_2025-05-05_14-45-14_Data.parquet',
        "ArbinOLD": 'ArbinOLD_QUEEN_Test_ProtC_C-011_55_Arbin_Old_2025-05-05_14-46-13_Data.parquet',
        "Basytec": 'Basytec145_TC23LFP01_CU_25deg_BaSyTec_2025-05-05_14-47-23_Data.parquet',
        "Daniel": 'additional_20250429153146-Daniel_Steperkennung-1-2-AM23NMC00063.parquet',
        "DanielTEST": "TEST_INPUT_Daniel_sampled_every_60s_with_first_last.parquet",
        "NewareTEST": "TEST_INPUT_Neware_sampled_every_60s_with_first_last.parquet",
        "BigBoi": "AM23NMC00012.parquet",
        "Jan": "AM23NMC037.parquet",
    }
    df_file = load_file(file_name_options[FILE_IDENTIFIER])

    # Preprocess the file
    if remove_duplicate_absolute_time_values:
        if "Absolute Time[yyyy-mm-dd hh:mm:ss]" in df_file.columns:
           df_file = df_file.drop_duplicates(subset=["Absolute Time[yyyy-mm-dd hh:mm:ss]"], keep="first")

    return df_file


#######################################################################################################################
def run_precompilation():
    # You can precompile beforehand if you want
    from pydpeet.process.sequence.step_analyzer import precompilation_step_analyzer
    from pydpeet.process.sequence.utils.console_prints.log_time import log_time

    with log_time("precompiling step_analyzer"):
        _ = precompilation_step_analyzer()


#######################################################################################################################
def run_step_analyzer_primitives(df_file):
    # Run step analyzer primitives using a (standard/example) Config or with own parameters
    from pydpeet.process.sequence.step_analyzer import step_analyzer_primitives
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import STEP_ANALYZER_PRIMITIVES_CONFIG

    df_primitives = step_analyzer_primitives(df=df_file,
                                             STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
                                             # you can add a config with combined parameters or your own parameters (own parameters have higher priority)
                                             # STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG
                                             # SEGMENTS_TO_DETECT_CONFIG= ...,
                                             # ...
                                             )
    return df_primitives

#######################################################################################################################
def run_df_primitives_correction(df_primitives):
    # Manually correct dataframe if there is anything detected wrong
    from pydpeet.process.sequence.utils.console_prints.log_time import log_time
    from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import SHOW_RUNTIME, DATA_COLUMNS, THRESHOLDS_PRIMITIVE_ANNOTATION

    correction_config = {
        "replace_ID": {
            # 1: "V",
        },
        "replace_time": {
            # (5000.0, 15000.0): "P",
        },
        "replace_time_and_merge": {
            (5000.0, 15000.0): "P",
            # (df_primitives['Testtime[s]'].min(), df_primitives['Testtime[s]'].max()): "I",
        },
        "merge_left": [
            # 1,
        ],
        "merge_right": [
            # 1,
        ],
        "merge_range": [
            # (1, 10),
        ]
    }
    if SHOW_RUNTIME: print("cleaning up segments...")
    with log_time("cleaning up segments", SHOW_RUNTIME=SHOW_RUNTIME):
        df_primitives = df_primitives_correction(df_primitives=df_primitives,
                                                 correction_config=correction_config,
                                                 data_columns=DATA_COLUMNS,
                                                 thresholds=THRESHOLDS_PRIMITIVE_ANNOTATION)

    return df_primitives

#######################################################################################################################
def run_step_analyzer_seqments_and_sequences(df_primitives):
    # Run step analyzer sequences using a (standard/example) Config or with own parameters
    from pydpeet.process.sequence.step_analyzer import step_analyzer_seqments_and_sequences
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import SEGMENT_SEQUENCE_CONFIG

    df_segments_and_sequences = step_analyzer_seqments_and_sequences(df_primitives,
                                                                     SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG)

    return df_segments_and_sequences

#######################################################################################################################
def run_generate_instructions(df_primitives):
    # Run generate instructions
    from pydpeet.process.sequence.utils.console_prints.log_time import log_time
    from pydpeet.process.sequence.utils.postprocessing.generate_instructions import generate_instructions
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import END_CONDITION_MAP_GENERATE_INSTRUCTIONS, SHOW_RUNTIME

    with log_time("generating instructions", SHOW_RUNTIME=SHOW_RUNTIME):
        instructions = generate_instructions(
            df_primitives=df_primitives,
            # .loc[(df_primitives['Testtime[s]'] >= 58500) & (df_primitives['Testtime[s]'] <= 91000)]
            end_condition_map=END_CONDITION_MAP_GENERATE_INSTRUCTIONS,
            threshold_warnings=10
        )
        print_instructions = True
        print_instructions_limit = 1000000
        if print_instructions:
            for i, row in enumerate(instructions[:print_instructions_limit]):
                print(f"{i + 1}: {row}")
        print(instructions)

    return instructions

#######################################################################################################################
def run_pybamm_simulation(instructions):

    # Run pybamm simulation using instructions
    from pydpeet.process.sequence.utils.console_prints.log_time import log_time
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import SHOW_RUNTIME
    import pybamm

    with log_time("running pybamm simulation", SHOW_RUNTIME=SHOW_RUNTIME):
        sim = pybamm.Simulation(
            pybamm.lithium_ion.SPM(),
            experiment=pybamm.Experiment(instructions),
            parameter_values=pybamm.ParameterValues("Chen2020")
        )

        sim.solve(initial_soc=0)
        sim.plot()

########################################################################################################################

def run_filter_and_split_df_by_blocks(df_segments_and_sequences, df_primitives):
    # Filter Data using rules
    from pydpeet.process.sequence.utils.console_prints.log_time import log_time
    from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import SHOW_RUNTIME
    if SHOW_RUNTIME: print("filtering IDs...")
    with log_time("filtering IDs", SHOW_RUNTIME=SHOW_RUNTIME):
        rules = [
            "Charge_iOCV",
            "Discharge_iOCV",
        ]

        _, df_filtered = filter_and_split_df_by_blocks(
            df_segments_and_sequences=df_segments_and_sequences,
            df_primitives=df_primitives,
            rules=rules,
            combine_op='or'
        )
    return df_filtered

def run_filter_and_split_df_by_blocks_2(df_segments_and_sequences, df_filtered):
    # Filter Data using rules
    from pydpeet.process.sequence.utils.console_prints.log_time import log_time
    from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import SHOW_RUNTIME
    if SHOW_RUNTIME: print("filtering IDs...")
    with log_time("filtering IDs", SHOW_RUNTIME=SHOW_RUNTIME):
        rules = [
            "Pause",
        ]

        dfs_per_block, df_filtered = filter_and_split_df_by_blocks(
            df_segments_and_sequences=df_segments_and_sequences,
            df_primitives=df_filtered,
            rules=rules,
            combine_op='or'
        )

    return dfs_per_block, df_filtered

def run_filter_and_split_df_by_blocks3(df_segments_and_sequences, df_primitives):
    # Filter Data using rules
    from pydpeet.process.sequence.utils.console_prints.log_time import log_time
    from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import SHOW_RUNTIME
    if SHOW_RUNTIME: print("filtering IDs...")
    with log_time("filtering IDs", SHOW_RUNTIME=SHOW_RUNTIME):
        rules = [
            "Merged_Subsequences",
        ]

        _, df_filtered = filter_and_split_df_by_blocks(
            df_segments_and_sequences=df_segments_and_sequences,
            df_primitives=df_primitives,
            rules=rules,
            combine_op='or'
        )
    return df_filtered

########################################################################################################################
def run_visualize_phases(df_filtered):
    # Visualize Data
    from pydpeet.process.sequence.utils.visualize.visualize_data import visualize_phases
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import (SHOW_RUNTIME, START, END, VISUALIZE_PHASES_CONFIG, SEGMENT_ALPHA,
                                                                        LINE_VISUALIZATION_CONFIG, USE_LINES_FOR_SEGMENTS,
                                                                        SHOW_COLUMN_NAMES, SHOW_TIME, SHOW_ID, WIDTH_HEIGHT_RATIO)
    from matplotlib import pyplot as plt

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
        show_runtime=SHOW_RUNTIME
    )

    # mngr = plt.get_current_fig_manager()
    # mngr.window.wm_geometry("+0+0")
    plt.show()

def run_visualize_phases_no_ID_varible_or_length(df_filtered):
    # Visualize Data
    from pydpeet.process.sequence.utils.visualize.visualize_data import visualize_phases
    from pydpeet.process.sequence.Example_Usage.CONFIG_example import (SHOW_RUNTIME, START, END, VISUALIZE_PHASES_CONFIG, SEGMENT_ALPHA,
                                                                        LINE_VISUALIZATION_CONFIG, USE_LINES_FOR_SEGMENTS,
                                                                        WIDTH_HEIGHT_RATIO)
    from matplotlib import pyplot as plt

    if SHOW_RUNTIME: print("starting visualization process...")

    visualize_phases(
        dataframe=df_filtered,
        start_time=START,
        end_time=END,
        visualize_phases_config=VISUALIZE_PHASES_CONFIG,
        segment_alpha=SEGMENT_ALPHA,
        line_visualization_config=LINE_VISUALIZATION_CONFIG,
        use_lines_for_segments=USE_LINES_FOR_SEGMENTS,
        show_column_names=False,
        show_time=False,
        show_id=False,
        width_height_ratio=WIDTH_HEIGHT_RATIO,
        show_runtime=SHOW_RUNTIME
    )

    # mngr = plt.get_current_fig_manager()
    # mngr.window.wm_geometry("+0+0")
    plt.show()

########################################################################################################################

if __name__ == "__main__":

    # 1. Segmentation in primitive segments (125254 lines)
    df_file = run_import_df(FILE_IDENTIFIER="Daniel", remove_duplicate_absolute_time_values=True)
    df_primitives_input = run_step_analyzer_primitives(df_file=df_file)
    run_visualize_phases(df_primitives_input)

    # 2. Segmentation in primitive segments (604405 lines)
    df_file_bigger = run_import_df(FILE_IDENTIFIER="Neware", remove_duplicate_absolute_time_values=True)
    df_primitives_bigger = run_step_analyzer_primitives(df_file=df_file_bigger)
    run_visualize_phases_no_ID_varible_or_length(df_primitives_bigger)

    # 3. Applying corrections to primitive segments (just example, not a useful correction in this case)
    df_primitives_output = run_df_primitives_correction(df_primitives_input)
    run_visualize_phases(df_primitives_output)

    # 4. Filtering data by (Dis-)Charge-iOCV Sequences ((Dis-)Charge, Pause, (Dis-)Charge, ...)
    #    and Pauses inside Sequences
    df_segments_and_sequences = run_step_analyzer_seqments_and_sequences(df_primitives_input)
    df_primitives_output = run_filter_and_split_df_by_blocks(df_segments_and_sequences, df_primitives_input)
    run_visualize_phases_no_ID_varible_or_length(df_primitives_output)
    _, df_primitives_output = run_filter_and_split_df_by_blocks_2(df_segments_and_sequences, df_primitives_output)
    run_visualize_phases_no_ID_varible_or_length(df_primitives_output)

    #5. Generating instructions & PyBaMM simulation
    instructions = run_generate_instructions(df_primitives_input)
    run_pybamm_simulation(instructions)




    # df_file = run_import_df(FILE_IDENTIFIER="Neware", remove_duplicate_absolute_time_values=False)
    # df_primitives_input = run_step_analyzer_primitives(df_file=df_file)
    # df_segments_and_sequences = run_step_analyzer_seqments_and_sequences(df_primitives_input)
    #
    #
    # from pydpeet.process.sequence.utils.console_prints.log_time import log_time
    # from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
    # from pydpeet.process.sequence.CONFIG_example import SHOW_RUNTIME
    #
    # # Since Noise might create additional Segments during the pulses is this not a single df per HPPC test
    # # Manual correction of pulses is needed beforehand for better automation
    # rules = [
    #     "HPPC_Pulse_Pause",
    #     "HPPC_Charge",
    #     "HPPC_Discharge",
    # ]
    #
    # _, df_filtered = filter_and_split_df_by_blocks(
    #     df_segments_and_sequences=df_segments_and_sequences,
    #     df_primitives=df_primitives_input,
    #     rules=rules,
    #     combine_op='or'
    # )
    #
    # run_visualize_phases_no_ID_varible_or_length(df_filtered)







