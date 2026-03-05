# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Schritt Zeit": "Test_Time[s]",
    "Spannung": "Voltage[V]",
    "Strom": "Current[A]",
    "Schritt Nr.": "Step_Count",
    "Zeitstempel": "Date_Time",
    "T_Batt": "Temperature[°C]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]",
]
