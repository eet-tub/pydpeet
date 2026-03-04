# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Record number": "StepID",
    "Voltage(V)": "Voltage[V]",
    "Current(A)": "Current[A]",
    "Relative Time(h:min:s.ms)": "Testtime[s]",
    "Real Time(h:min:s.ms)": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]",
]
