from pydpeet.process.sequence.BA.TEMP_load_and_preprocess_file import load_file
from pydpeet.process.sequence.step_analyzer import step_analyzer_primitives
from pydpeet.process.sequence.Example_Usage.CONFIG_example import *
from pydpeet.process.sequence.utils.visualize.visualize_data import visualize_phases
from matplotlib import pyplot as plt
import pandas as pd

# Einlesen der Datei von einem Dateipfad
# df_file = load_file(r'res/additional_20250429153146-Daniel_Steperkennung-1-2-AM23NMC00063.parquet')
# load_file("data.parquet", base_path=__file__)
df_file = load_file("additional_20250429153146-Daniel_Steperkennung-1-2-AM23NMC00063.parquet",
                    base_path=__file__)

# Vorverarbeitung (Wahl der Spalten) + z.B. Fehlerkorrektur
if "Absolute Time[yyyy-mm-dd hh:mm:ss]" in df_file.columns:
    df_file = df_file.drop_duplicates(subset=["Absolute Time[yyyy-mm-dd hh:mm:ss]"], keep="first")
df_file = df_file[["Voltage[V]", "Current[A]", "Testtime[s]"]]

# Aufrufen des step_analyzer (Primitive Segmente)
df_primitives = step_analyzer_primitives(df=df_file,
                                         STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG,
                                         #...
                                         )

# Visualisierung
print("starting visualization process...")
visualize_phases(dataframe=df_primitives,
                 #...
                 )
plt.show()
