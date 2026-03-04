# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Schritt Zeit": "Testtime[s]",
    "Spannung": "Voltage[V]",
    "Strom": "Current[A]",
    "Schritt Nr.": "StepID",
    "Zeitstempel": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "T_Batt": "Temperature[°C]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]",
]
