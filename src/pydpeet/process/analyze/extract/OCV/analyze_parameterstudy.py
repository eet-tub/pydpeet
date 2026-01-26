import pandas as pd
# This file is for Analysing (with debugger) the results of the parameter study


# results_df = pd.read_parquet(
#     r"C:\python projekte\BA_Repo\pydpeet\src\Alex_BA\res\BA\Parameter_studie\06_Results\result_df.parquet")

results_df = pd.read_parquet(
    r"/pydpeet/src/Alex_BA/res/BA/Parameter_studie/06_Results/result_df_with_correct_segments_rmse_2.parquet")
#results_df = pd.read_parquet(r"C:\python projekte\BA_Repo\pydpeet\src\Alex_BA\res\BA\Parameter_studie\Temp\all_parameter_search_results.parquet")

# # Select parameters and area
#results_df = results_df[['rmseDataset', 'extrapolated_pause_length', 'min_pause_length','Area','Area_norm']]
results_df = results_df[['Dataset', 'extrapolated_pause_length', 'min_pause_length','rmse','Area','Area_norm', 'corr_coeff']]

# # Find row with lowest area for every Dataset
min_row_area = results_df.groupby('Dataset').apply(lambda x: x.nsmallest(1, ['Area'])).reset_index(drop=True)
min_row_area = min_row_area.groupby('Dataset').min().reset_index()
#
min_row_area_norm = results_df.groupby('Dataset').apply(lambda x: x.nsmallest(1, ['Area_norm'])).reset_index(drop=True)
min_row_area_norm = min_row_area_norm.groupby('Dataset').min().reset_index()

min_row_rmse = results_df.groupby('Dataset').apply(lambda x: x.nsmallest(1, ['rmse'])).reset_index(drop=True)
min_row_rmse = min_row_rmse.groupby('Dataset').min().reset_index()

min_row_corr = results_df.groupby('Dataset').apply(lambda x: x.nlargest(1, ['corr_coeff'])).reset_index(drop=True)
min_row_corr = min_row_corr.groupby('Dataset').max().reset_index()

#results_df = results_df[['Dataset', 'extrapolated_pause_length','min_pause_length', 'rmse_weighted']]
#min_row_rmse = results_df.groupby('Dataset').apply(lambda x: x.nsmallest(1, ['rmse_weighted'])).reset_index(drop=True)
#min_row_rmse = min_row_rmse.groupby('Dataset').min().reset_index()
print(min_row[['Dataset', 'extrapolated_pause_length', 'min_pause_length', 'Area','Area_norm']])

# Save parameters and area in dataframe
min_row_df = min_row[['Dataset', 'extrapolated_pause_length', 'min_pause_length', 'Area', 'Area_norm']]
print(results_df)