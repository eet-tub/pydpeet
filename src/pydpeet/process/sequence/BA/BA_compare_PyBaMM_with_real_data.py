import pandas as pd
import matplotlib.pyplot as plt

import pydpeet.process.sequence.Example_Usage.CONFIG_example
from pydpeet.process.sequence.BA.TEMP_load_and_preprocess_file import load_file
from pydpeet.process.sequence.step_analyzer import step_analyzer_primitives

def benchmark(df_file, df_experiment):
    df_benchmark = step_analyzer_primitives(df=df_experiment,
                                            STEP_ANALYZER_PRIMITIVES_CONFIG=pydpeet.process.sequence.Example_Usage.CONFIG_example.STEP_ANALYZER_PRIMITIVES_CONFIG,
                                            SHOW_RUNTIME=False,
                                            SHOW_RUNTIME_ANNOTATION=False)

    df_reference = step_analyzer_primitives(df=df_file,
                                            STEP_ANALYZER_PRIMITIVES_CONFIG=pydpeet.process.sequence.Example_Usage.CONFIG_example.STEP_ANALYZER_PRIMITIVES_CONFIG,
                                            SHOW_RUNTIME=False,
                                            SHOW_RUNTIME_ANNOTATION=False)


    df_benchmark_min_max_avg = df_benchmark.groupby('ID').agg({'Testtime[s]':['min','max'],
                                                               'Voltage[V]':['min','max','mean'],
                                                               'Current[A]':['min','max','mean'],
                                                               'Power[W]':['min','max','mean']})
    df_benchmark_min_max_avg.columns = ['Min_Time[s]', 'Max_Time[s]', 'Min_Voltage[V]', 'Max_Voltage[V]', 'Avg_Voltage[V]', 'Min_Current[A]', 'Max_Current[A]', 'Avg_Current[A]', 'Min_Power[W]', 'Max_Power[W]', 'Avg_Power[W]']
    df_benchmark_min_max_avg['Duration[s]'] = df_benchmark_min_max_avg['Max_Time[s]'] - df_benchmark_min_max_avg['Min_Time[s]']
    df_benchmark_min_max_avg.reset_index(inplace=True)

    df_reference_min_max_avg = df_reference.groupby('ID').agg({'Testtime[s]':['min','max'],
                                                               'Voltage[V]':['min','max','mean'],
                                                               'Current[A]':['min','max','mean'],
                                                               'Power[W]':['min','max','mean']})
    df_reference_min_max_avg.columns = ['Min_Time[s]', 'Max_Time[s]', 'Min_Voltage[V]', 'Max_Voltage[V]', 'Avg_Voltage[V]', 'Min_Current[A]', 'Max_Current[A]', 'Avg_Current[A]', 'Min_Power[W]', 'Max_Power[W]', 'Avg_Power[W]']
    df_reference_min_max_avg['Duration[s]'] = df_reference_min_max_avg['Max_Time[s]'] - df_reference_min_max_avg['Min_Time[s]']
    df_reference_min_max_avg.reset_index(inplace=True)

    # Merge on ID to align each step
    merged_df = pd.merge(df_reference_min_max_avg, df_benchmark_min_max_avg, on="ID", suffixes=('_ref', '_bench'))

    # Columns to compare
    columns_to_compare = ['Min_Time[s]', 'Max_Time[s]', 'Duration[s]',
                          'Min_Voltage[V]', 'Max_Voltage[V]', 'Avg_Voltage[V]',
                          'Min_Current[A]', 'Max_Current[A]', 'Avg_Current[A]',
                          'Min_Power[W]', 'Max_Power[W]', 'Avg_Power[W]']

    similarity_results = {}

    from sklearn.metrics import mean_absolute_error, r2_score
    from scipy.stats import spearmanr, kendalltau
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    similarity_results = {}

    for col in columns_to_compare:
        ref_col = f"{col}_ref"
        bench_col = f"{col}_bench"

        # Drop any NaNs that might cause issues
        valid_data = merged_df[[ref_col, bench_col]].dropna()

        ref_values = valid_data[ref_col].values.reshape(1, -1)
        bench_values = valid_data[bench_col].values.reshape(1, -1)

        ref_flat = ref_values.flatten()
        bench_flat = bench_values.flatten()

        # Similarity metrics
        cosine_sim = cosine_similarity(ref_values, bench_values)[0][0]
        pearson_corr = np.corrcoef(ref_flat, bench_flat)[0, 1]
        r2 = r2_score(ref_flat, bench_flat)
        spearman_corr, _ = spearmanr(ref_flat, bench_flat)
        kendall_corr, _ = kendalltau(ref_flat, bench_flat)
        #RMSE oder R2 pro ID vom Strom, Spannung und Leistung
        # PYbamm Simulation dann generate instructions und die Beiden dann vergleichen


        similarity_results[col] = {
            "Cosine Similarity": cosine_sim,
            "Pearson Correlation": pearson_corr,
            "R2": r2,
            "Spearman Correlation": spearman_corr,
            "Kendall Tau": kendall_corr
        }

    # Print similarities
    print("\nSimilarity per column:")
    header = f"{'Column':<20} {'Cosine':>8} {'Pearson':>10} {'Spearman':>10} {'Kendall':>10} {'R2':>6}"
    print(header)
    print("-" * (len(header)+2))

    for col, sim in similarity_results.items():
        print(f"{col:<20} {sim['Cosine Similarity']:>8.4f} {sim['Pearson Correlation']:>10.4f} "
              f"{sim['Spearman Correlation']:>10.4f} {sim['Kendall Tau']:>10.4f} "
              f"{sim['R2']:>8.4f}")


    x = False
    if x:
        max_time_ref = df_reference['Testtime[s]'].max()
        max_time_bench = df_benchmark['Testtime[s]'].max()
        diff = max_time_ref - max_time_bench
        print(f"df_reference has max testtime {max_time_ref:.2f}\n"
              f"df_benchmark has max testtime {max_time_bench:.2f}\n"
              f"The difference is {(diff / max_time_ref * 100):.2f}%\n")

    plot = True
    if plot:
        fig, ax = plt.subplots(3, 1, sharex=True)
        ax[0].plot(df_reference['Testtime[s]'], df_reference['Voltage[V]'], label='Reference', alpha=0.9)
        ax[0].plot(df_benchmark['Testtime[s]'], df_benchmark['Voltage[V]'], label='Benchmark', alpha=0.9)
        ax[0].set_ylabel('Voltage [V]')
        ax[0].legend()

        ax[1].plot(df_reference['Testtime[s]'], df_reference['Current[A]'], label='Reference', alpha=0.9)
        ax[1].plot(df_benchmark['Testtime[s]'], df_benchmark['Current[A]'], label='Benchmark', alpha=0.9)
        ax[1].set_ylabel('Current [A]')

        ax[2].plot(df_reference['Testtime[s]'], df_reference['Power[W]'], label='Reference', alpha=0.9)
        ax[2].plot(df_benchmark['Testtime[s]'], df_benchmark['Power[W]'], label='Benchmark', alpha=0.9)
        ax[2].set_ylabel('Power [W]')

        #ax[3].plot(df_reference['Testtime[s]'], df_reference['Testtime[s]'], label='Reference', alpha=0.8)
        #ax[3].plot(df_benchmark['Testtime[s]'], df_benchmark['Testtime[s]'], label='Benchmark', alpha=0.8)



        #ax[3].set_ylabel('Time [s]')
        #ax[3].set_xlabel('Time [s]')
        plt.tight_layout()
        plt.show()
    return



if __name__ == "__main__":
    x = True
    if x:
        file_name_options = {
            "Neware": '20240307170835-Cyc_2C_1C_100DOD_50_SOC-2-1-AM23NMC00041_Neware_2025-04-24_20-36-56_Data.parquet',
            "Arbin": 'Arbin_Pack_Test_240009-1-1-816_Arbin_2025-05-05_14-45-14_Data.parquet',
            "ArbinOLD": 'ArbinOLD_QUEEN_Test_ProtC_C-011_55_Arbin_Old_2025-05-05_14-46-13_Data.parquet',
            "Basytec": 'Basytec145_TC23LFP01_CU_25deg_BaSyTec_2025-05-05_14-47-23_Data.parquet',
            "Daniel": 'additional_20250429153146-Daniel_Steperkennung-1-2-AM23NMC00063.parquet',
            "DanielTEST": "TEST_INPUT_Daniel_sampled_every_60s_with_first_last.parquet",
            "Benchmark": "BENCHMARK_Daniel_df_experiment.parquet"
        }

        FILE_IDENTIFIER = "Benchmark"
        FILE_NAME = file_name_options[FILE_IDENTIFIER]
        df_benchmark = load_file(FILE_NAME, FILE_IDENTIFIER, STANDARD_COLUMNS)
        FILE_IDENTIFIER = "Daniel"
        FILE_NAME = file_name_options[FILE_IDENTIFIER]
        df_reference = load_file(FILE_NAME, FILE_IDENTIFIER, STANDARD_COLUMNS)

        benchmark(df_file=df_reference, df_experiment=df_benchmark)