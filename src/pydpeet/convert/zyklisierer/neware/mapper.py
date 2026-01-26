# Define the mapping from current names to standardized names
COLUMN_MAP = {
    "step_id": "StepID",
    'Voltage(V)': "Voltage[V]",
    "Current[A] - record": "Current[A]",
    "T1": "Temperature[°C]",
    "Total Time": "Testtime[s]",
    "Date": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
}

MISSING_REQUIRED_COLUMNS = ["EISFreq[Hz]", "Zre[Ohm]", "Zim[Ohm]", "DC_Current[A]"]
