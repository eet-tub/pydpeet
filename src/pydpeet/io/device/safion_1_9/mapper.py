# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "step": "StepID",
    "impedance_frequency": "EISFreq[Hz]",
    "real impedance": "Zre[Ohm]",
    "imaginary impedance": "Zim[Ohm]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Testtime[s]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "DC_Current[A]",
]
