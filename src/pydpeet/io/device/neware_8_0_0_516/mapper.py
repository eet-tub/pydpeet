# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "step_id": "StepID",
    "Voltage(V)": "Voltage[V]",
    "Current[A] - record": "Current[A]",
    "T1": "Temperature[°C]",
    "Total Time": "Testtime[s]",
    "Date": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]",
]
