# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Zreal1": "Zre[Ohm]",
    "Zimg1": "Zim[Ohm]",
    "Zeitstempel": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "Schritt Nr.": "StepID",
    "Spannung": "Voltage[V]",
    "Strom": "Current[A]",
    "Progr. Zeit": "Testtime[s]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "EISFreq[Hz]",
    "DC_Current[A]",
]
