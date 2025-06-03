# Define the mapping from current names to standardized names
COLUMN_MAP = {
    "Time[h]": "Testtime[s]",
    "U[V]": "Voltage[V]",
    "I[A]": "Current[A]",
    "T1[°C]": "Temperature[°C]",
    "Line": "StepID"
}

MISSING_REQUIRED_COLUMNS = [
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]"
]
