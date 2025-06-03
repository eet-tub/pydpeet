# Define the mapping from current names to standardized names
COLUMN_MAP = {
    "Record number": "StepID",
    "Voltage(V)": "Voltage[V]",
    "Current(A)": "Current[A]",
    "Relative Time(h:min:s.ms)": "Testtime[s]",
    "Real Time(h:min:s.ms)": "Absolute Time[yyyy-mm-dd hh:mm:ss]"
}


MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]"
]
