# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Time[h]": "Testtime[s]",
    "U[V]": "Voltage[V]",
    "I[A]": "Current[A]",
    "T1[°C]": "Temperature[°C]",
    "Line": "StepID",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]",
]
