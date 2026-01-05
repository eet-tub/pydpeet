from pydpeet.process.sequence.BA.TEMP_load_and_preprocess_file import load_file
from pydpeet.process.sequence.step_analyzer import step_analyzer_primitives
from pydpeet.process.sequence.Example_Usage.CONFIG_example import *
from pydpeet.process.sequence.utils.postprocessing.generate_instructions import generate_instructions
import pybamm

df_file = load_file('additional_20250429153146-Daniel_Steperkennung-1-2-AM23NMC00063.parquet',base_path=__file__)
if "Absolute Time[yyyy-mm-dd hh:mm:ss]" in df_file.columns:
    df_file = df_file.drop_duplicates(subset=["Absolute Time[yyyy-mm-dd hh:mm:ss]"], keep="first")
df_file = df_file[["Voltage[V]", "Current[A]", "Testtime[s]"]]
df_primitives = step_analyzer_primitives(df=df_file, STEP_ANALYZER_PRIMITIVES_CONFIG=STEP_ANALYZER_PRIMITIVES_CONFIG)

# Generieren der Instruktionen
instructions = generate_instructions(df_primitives=df_primitives)

# Ausgabe der Instruktionen in der Konsole
print("Instructions:")
for row in instructions:
    print(row)

# Simulation via pybamm mit Instruktionen
sim = pybamm.Simulation(
    pybamm.lithium_ion.SPM(),
    experiment=pybamm.Experiment(instructions),
    parameter_values=pybamm.ParameterValues("Chen2020")
)
sim.solve(initial_soc=0)
sim.plot()