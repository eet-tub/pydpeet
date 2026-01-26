import timeit

import pandas
from matplotlib import pyplot as plt

from pydpeet.process.sequence.BA.BA_custom_visualize_phases import visualize_phases
from pydpeet.process.sequence.BA.TEMP_load_and_preprocess_file import load_file
from pydpeet.process.sequence.step_analyzer import step_analyzer_seqments_and_sequences, step_analyzer_primitives

from pydpeet.process.sequence.BA.Config_Benchmark import *
from pydpeet.process.sequence.utils.postprocessing.generate_instructions import generate_instructions

file_name_options = {
    "BigBoi": "AM23NMC00012.parquet"
}
FILE_IDENTIFIER = "BigBoi"
FILE_NAME = file_name_options[FILE_IDENTIFIER]
df_file = load_file(FILE_NAME, FILE_IDENTIFIER, STANDARD_COLUMNS)

# df_file.dropna(subset=['Testtime[s]'], inplace=True)
# df_file.drop_duplicates(subset=['Testtime[s]'], inplace=True)
# df_file.sort_values(by=['Testtime[s]'], inplace=True)

def benchmark_runtime(df_input):
    # df_primitives = step_analyzer_primitives(df=df_input,
    #                                          STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
    #                                          check_CV_0Aend_segments_bool=False,
    #                                          check_zero_length_segments_bool=False,
    #                                          check_Power_zero_W_segments_bool=False,
    #                                          PRECOMPILE=True,
    #                                          FORCE_PRECOMPILATION=True,
    #                                          supress_IO_warnings=True,
    #                                          SHOW_RUNTIME=False)
    df_primitives = step_analyzer_primitives(df=df_input,
                                            STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
                                            check_CV_0Aend_segments_bool=True,
                                            check_zero_length_segments_bool=True,
                                            check_Power_zero_W_segments_bool=True,
                                            PRECOMPILE=False,
                                            FORCE_PRECOMPILATION=False,
                                            supress_IO_warnings=True,
                                            SHOW_RUNTIME=False)
    # df_segments_and_sequences = step_analyzer_seqments_and_sequences(df_input,
    #                                                                 SEGMENT_SEQUENCE_CONFIG=SEGMENT_SEQUENCE_CONFIG,
    #                                                                 SHOW_RUNTIME_ANALYZE=True,
    #                                                                 SHOW_RUNTIME=False)
    # generate_instructions(
    #    df_primitives=df_input,
    #    end_condition_map=END_CONDITION_MAP_GENERATE_INSTRUCTIONS
    # )
    # df_primitives = step_analyzer_primitives(df=df_input,
    #                                          STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
    #                                          check_CV_0Aend_segments_bool=True,
    #                                          check_zero_length_segments_bool=True,
    #                                          check_Power_zero_W_segments_bool=True,
    #                                          PRECOMPILE=False,
    #                                          FORCE_PRECOMPILATION=False,
    #                                          supress_IO_warnings=True,
    #                                          SHOW_RUNTIME=False)

x = False
if x:
    df_file = load_file(FILE_NAME, FILE_IDENTIFIER, STANDARD_COLUMNS)
    df_primitives = step_analyzer_primitives(df=df_file,
                                             STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
                                             check_CV_0Aend_segments_bool=True,
                                             check_zero_length_segments_bool=True,
                                             check_Power_zero_W_segments_bool=True,
                                             PRECOMPILE=True,
                                             FORCE_PRECOMPILATION=True,
                                             supress_IO_warnings=True,
                                             SHOW_RUNTIME=False)

    tested_df = df_file
    segmente = True
    if segmente:
        print(10000)
        print(1000)
        print(100)
        print(10)
        times = timeit.repeat(lambda: benchmark_runtime(tested_df.head(1543414)), number=1, repeat=5)
        print(str(times) + ",")
        times = timeit.repeat(lambda: benchmark_runtime(tested_df.head(555688)), number=1, repeat=5)
        print(str(times) + ",")
        times = timeit.repeat(lambda: benchmark_runtime(tested_df.head(64422)), number=1, repeat=5)
        print(str(times) + ",")
        times = timeit.repeat(lambda: benchmark_runtime(tested_df.head(44249)), number=1, repeat=5)
        print(str(times) + ",")

    zeilen = True
    if zeilen:
        print(5000000)
        print(500000)
        print(50000)
        print(5000)
        times = timeit.repeat(lambda: benchmark_runtime(tested_df.head(5000000)), number=1, repeat=5)
        print(str(times) + ",")
        times = timeit.repeat(lambda: benchmark_runtime(tested_df.head(500000)), number=1, repeat=5)
        print(str(times) + ",")
        times = timeit.repeat(lambda: benchmark_runtime(tested_df.head(50000)), number=1, repeat=5)
        print(str(times) + ",")
        times = timeit.repeat(lambda: benchmark_runtime(tested_df.head(5000)), number=1, repeat=5)
        print(str(times) + ",")




step_analyzer_primitives_mit_precompile_ohne_optionale_korrektur = {
    "Segments": [10000, 1000, 100, 10, 76291, 971, 38, 1],
    "Rows": [1543414, 555688, 64422, 44249, 5000000, 500000, 50000, 5000],
    "Runtimes": [
        [1.611920299998019, 1.3947689000051469, 1.3834340000030352, 1.3765635000017937, 1.3813309999968624],
        [0.5268469000002369, 0.5192637000000104, 0.51869880000595, 0.5274081000097794, 0.5188669000053778],
        [0.10705999999481719, 0.10314750000543427, 0.10244349999993574, 0.10570919999736361, 0.1027139000070747],
        [0.08714669999608304, 0.08551679999800399, 0.08683699999528471, 0.08714529999997467, 0.08714430000691209],

        [4.634127299999818, 4.699943300001905, 4.808816999997362, 4.723149700002978, 4.91748559998814],
        [0.4825944000040181, 0.4859701999957906, 0.48264249999192543, 0.4894873000012012, 0.49075189999712165],
        [0.0931072000093991, 0.09286649999557994, 0.095137700001942, 0.09253920000628568, 0.0936717000004137],
        [0.05329160000837874, 0.05195520000415854, 0.052429599993047304, 0.052539700001943856, 0.0529065000009723],
    ]
}
step_analyzer_primitives_mit_precompile_mit_optionale_korrektur = {
    "Segments": [10000, 1000, 100, 10, 76291, 971, 38, 1],
    "Rows": [1543414, 555688, 64422, 44249, 5000000, 500000, 50000, 5000],
    "Runtimes": [
        [2.717439400003059, 2.5258414999989327, 2.5591144999925746, 2.511984600001597, 2.491843299998436],
        [0.9005332000087947, 0.8969934999913676, 0.9036186000012094, 0.8927000999974553, 0.8971586999978172],
        [0.15707050000492018, 0.15691940000397153, 0.1559854999941308, 0.15573420000146143, 0.15671399999700952],
        [0.12673390000418294, 0.12857960000110324, 0.12589260000095237, 0.12816680000105407, 0.12697189999744296],

        [10.173901800008025, 9.90636490000179, 9.891080900008092, 9.875331999995979, 9.880594400005066],
        [0.810610499989707, 0.8094752999895718, 0.8164765999972587, 0.820134199995664, 0.827124500006903],
        [0.136100699994131, 0.13385500000731554, 0.13370829999621492, 0.13592590000189375, 0.13557530000980478],
        [0.06666650000261143, 0.06578750000335276, 0.06673749999026768, 0.06821689999196678, 0.06624010000086855],
    ]
}

step_analyzer_segments_and_sequences = {
    "Segments": [10000, 1000, 100, 10, 76291, 971, 38, 1],
    "Rows": [1543414, 555688, 64422, 44249, 5000000, 500000, 50000, 5000],
    "Runtimes": [
        [0.30679930000042077, 0.30382809998991434, 0.3042676000040956, 0.3013963999983389, 0.30237650001072325],
        [0.034266399990883656, 0.03386820000014268, 0.03482990000338759, 0.034003400010988116, 0.033644299997831695],
        [0.01005779999832157, 0.009759099993971176, 0.0097719000041252, 0.009692799998447299, 0.009827200003201142],
        [0.008278599998448044, 0.008396599994739518, 0.008396600009291433, 0.008154399998602457, 0.008251000006566755],

        [2.1976468000066234, 2.2093098999903305, 2.2406751999951666, 2.3035659000015585, 2.2234992000012426],
        [0.033176700002513826, 0.03297460000612773, 0.03322820000175852, 0.03300980001222342, 0.03338199999416247],
        [0.008878599997842684, 0.008538299996871501, 0.008402600011322647, 0.008396799996262416, 0.008614100006525405],
        [0.007067099999403581, 0.006192100001499057, 0.006214900000486523, 0.006184700003359467, 0.006528099998831749],
    ]
}

step_analyzer_generate_instructions = {
    "Segments": [10000, 1000, 100, 10, 76291, 971, 38, 1],
    "Rows": [1543414, 555688, 64422, 44249, 5000000, 500000, 50000, 5000],
    "Runtimes": [
        [3.5567531999986386, 3.5627813000028254, 3.5464673999958904, 3.538204600001336, 3.7457967000082135],
        [0.3879802000010386, 0.38539949999540113, 0.3841123000020161, 0.38557240000227466, 0.384197099992889],
        [0.046795800008112565, 0.04795370000647381, 0.047703100004582666, 0.04712239999207668, 0.04696039999544155],
        [0.01233670000510756, 0.012496299998019822, 0.012299299996811897, 0.012509899999713525, 0.012658999999985099],

        [65.34936459999881, 64.30570880000596, 63.85106169999926, 63.92488150000281, 64.0624714000005],
        [0.3697517999971751, 0.37271410001267213, 0.3721577999967849, 0.37660560000222176, 0.36547910000081174],
        [0.022771699994336814, 0.021734099995228462, 0.022937200003070757, 0.021509900005185045, 0.021568999989540316],
        [0.0058529999951133505, 0.005761699998402037, 0.005100099995615892, 0.0050712999945972115, 0.005069599996204488],
    ]
}

step_analyzer_primitives_ohne_precompile_mit_optionale_korrektur = {
    "Segments": [10000, 1000, 100, 10, 76291, 971, 38, 1],
    "Rows": [1543414, 555688, 64422, 44249, 5000000, 500000, 50000, 5000],
    "Runtimes": [
        [2.4146609000017634, 2.404508599996916, 2.43005730000732, 2.4218602999899304, 2.4134886999963783],
        [0.8403971999941859, 0.834178899996914, 0.8368517999915639, 0.861126100004185, 0.842464999994263],
        [0.11032999999588355, 0.11083740000321995, 0.10956369999621529, 0.10980049999488983, 0.11083869999856688],
        [0.08006699998804834, 0.0799818000086816, 0.08125529999961145, 0.08094889999483712, 0.07937139998830389],

        [9.777939099993091, 9.94559649999428, 9.793762299988884, 9.828389800008154, 9.820841199994902],
        [0.7640308999980334, 0.7630313000117894, 0.7677485000021989, 0.7566539999970701, 0.7582070999924326],
        [0.08861909998813644, 0.08877159999974538, 0.08810549999179784, 0.08945319999475032, 0.08927330000733491],
        [0.021339999992051162, 0.019445600002654828, 0.019237800006521866, 0.0190561999916099, 0.0192691999982344],
    ]
}

step_analyzer_primitives_mit_precompile_mit_optionale_korrektur_ez_precompile = {
    "Segments": [10000, 1000, 100, 10, 76291, 971, 38, 1],
    "Rows": [1543414, 555688, 64422, 44249, 5000000, 500000, 50000, 5000],
    "Runtimes": [
        [2.4030565000139177, 2.3953149000299163, 2.405682999989949, 2.3984655999811366, 2.406436200020835],
        [0.8502006999915466, 0.8400824000127614, 0.8378065999713726, 0.8421520999982022, 0.8424867000430822],
        [0.12317619996611029, 0.12237659998936579, 0.12318450002931058, 0.12156970001524314, 0.12206259998492897],
        [0.09370809997199103, 0.09344279998913407, 0.09375409997301176, 0.0928315999917686, 0.0933538000099361],

        [9.843021999986377, 9.778746499971021, 9.767557599989232, 9.771955400006846, 9.764754100004211],
        [0.764934099977836, 0.7637873000348918, 0.7695315000019036, 0.7603623999748379, 0.764781900041271],
        [0.10132170002907515, 0.10476140002720058, 0.10312099999282509, 0.10190549999242648, 0.10251229995628819],
        [0.03402540000388399, 0.03200299997115508, 0.031843299977481365, 0.03276839997852221, 0.03236260003177449],
    ]
}

step_analyzer_primitives_ohne_precompile_mit_optionale_korrektur_ez_precompile = {
    "Segments": [10000, 1000, 100, 10, 76291, 971, 38, 1],
    "Rows": [1543414, 555688, 64422, 44249, 5000000, 500000, 50000, 5000],
    "Runtimes": [
        [2.4169396000215784, 2.420255000004545, 2.41044609999517, 2.4176592000294477, 2.419871599995531],
        [0.8322865999653004, 0.829090700019151, 0.8348370000021532, 0.8330994000425562, 0.8504191000247374],
        [0.11122529994463548, 0.10983969998778775, 0.1154860999668017, 0.11012899997876957, 0.10952820000238717],
        [0.08112659998005256, 0.08016569999745116, 0.08066000003600493, 0.08253489999333397, 0.0816624999861233],

        [9.95624480000697, 9.980483500054106, 9.847253200015984, 9.858090199995786, 9.836690599971917],
        [0.7556092999875546, 0.7640706000383943, 0.7530773000326008, 0.7627141000120901, 0.7514666999923065],
        [0.08893490000627935, 0.09078300005057827, 0.08982659998582676, 0.09015119995456189, 0.08806300000287592],
        [0.020688000018708408, 0.019907199952285737, 0.019852299999911338, 0.019892499956768006, 0.019601000007241964],
    ]
}


import matplotlib.pyplot as plt
import numpy as np

# Helper function to flatten runtimes into points
def flatten_runtimes(x_values, runtimes):
    xs, ys = [], []
    for x, r_list in zip(x_values, runtimes):
        xs.extend([x] * len(r_list))
        ys.extend(r_list)
    return xs, ys

# Helper function to compute mean runtimes
def mean_runtimes(x_values, runtimes):
    xs = x_values
    ys = [np.mean(r_list) for r_list in runtimes]
    return xs, ys

# Helper function to sort by x-values
def sort_by_x(x_values, runtimes):
    sorted_pairs = sorted(zip(x_values, runtimes), key=lambda pair: pair[0])
    xs_sorted, runtimes_sorted = zip(*sorted_pairs)
    return list(xs_sorted), list(runtimes_sorted)


def plot_runtime_results():
    # Datasets with updated names
    datasets = {
        # "step_analyzer_primitives mit Precompile, ohne optionaler Korrektur": step_analyzer_primitives_mit_precompile_ohne_optionale_korrektur,
        #"step_analyzer_primitives mit Precompile, mit optionaler Korrektur": step_analyzer_primitives_mit_precompile_mit_optionale_korrektur,
        #"step_analyzer_segments_and_sequences": step_analyzer_segments_and_sequences,
        #"step_analyzer_generate_instructions": step_analyzer_generate_instructions,
        # "step_analyzer_primitives ohne Precompile, mit optionaler Korrektur": step_analyzer_primitives_ohne_precompile_mit_optionale_korrektur,
        "step_analyzer_primitives mit Precompile, mit optionaler Korrektur": step_analyzer_primitives_mit_precompile_mit_optionale_korrektur_ez_precompile,
        "step_analyzer_primitives ohne Precompile, mit optionaler Korrektur": step_analyzer_primitives_ohne_precompile_mit_optionale_korrektur_ez_precompile
    }
    selection = [0, 1, 2, 3, 4, 5, 6, 7]
    #selection = [0,1,2,3]
    #selection = [4,5,6,7]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    # Subplot 1: Segments as x-axis
    for name, data in datasets.items():
        xs_sorted, runtimes_sorted = sort_by_x([data["Segments"][i] for i in selection], [data["Runtimes"][i] for i in selection])
        xs_all, ys_all = flatten_runtimes(xs_sorted, runtimes_sorted)
        xs_mean, ys_mean = mean_runtimes(xs_sorted, runtimes_sorted)
        ax1.scatter(xs_all, ys_all, alpha=0.4)
        ax1.plot(xs_mean, ys_mean, marker="o", label=name, linewidth=3)

    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel("Segmente", fontsize=15)
    ax1.set_ylabel("Laufzeit(s)", fontsize=15)
    if selection == [0, 1, 2, 3]:
        ax1.set_xticks([10000, 1000, 100, 10])
        ax1.set_xticklabels(["10.000", "1.000", "100", "10"], fontsize=15)
    elif selection == [4, 5, 6, 7]:
        ax1.set_xticks([76291, 971, 38, 1])
        ax1.set_xticklabels(["76291", "971", "38", "1"], fontsize=15)
    ax1.tick_params(axis='x', labelsize=15)
    ax1.tick_params(axis='y', labelsize=15)
    ax1.grid(True)
    ax1.legend(loc='upper left')

    # Subplot 2: Rows as x-axis
    for name, data in datasets.items():
        xs_sorted, runtimes_sorted = sort_by_x([data["Rows"][i] for i in selection], [data["Runtimes"][i] for i in selection])
        xs_all, ys_all = flatten_runtimes(xs_sorted, runtimes_sorted)
        xs_mean, ys_mean = mean_runtimes(xs_sorted, runtimes_sorted)
        ax2.scatter(xs_all, ys_all, alpha=0.4)
        ax2.plot(xs_mean, ys_mean, marker="o", label=name, linewidth=3)

    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("Zeilen", fontsize=15)
    ax2.tick_params(axis='x', labelsize=15)
    ax2.tick_params(axis='y', labelsize=15)
    if selection == [0, 1, 2, 3]:
        ax2.set_xticks([1543414, 555688, 64422, 44249])
        ax2.set_xticklabels(['1.543.414', '555.688', '64.422', '44.249'], fontsize=15)
    elif selection == [4, 5, 6, 7]:
        ax2.set_xticks([5000000, 500000, 50000, 5000])
        ax2.set_xticklabels(['5.000.000', '500.000', '50.000', '5.000'], fontsize=15)
    ax2.grid(True)
    ax2.legend(loc='upper left')

    plt.tight_layout()
    plt.show()

plot_runtime_results()