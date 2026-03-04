# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Elapsed Time (s)": "Testtime[s]",
    "Potential (V)": "Voltage[V]",
    "Current (A)": "Current[A]",
    "Point": "StepID",
    "Frequency (Hz)": "EISFreq[Hz]",
    "Zre (ohms)": "Zre[Ohm]",
    "Zim (ohms)": "Zim[Ohm]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "DC_Current[A]",
]
