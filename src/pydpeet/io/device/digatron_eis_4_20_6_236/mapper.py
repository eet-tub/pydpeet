# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Zreal1": "EIS_Z_Real[Ohm]",
    "Zimg1": "EIS_Z_Imag[Ohm]",
    "Zeitstempel": "Date_Time",
    "Schritt Nr.": "Step_Count",
    "Spannung": "Voltage[V]",
    "Strom": "Current[A]",
    "Progr. Zeit": "Test_Time[s]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "EIS_f[Hz]",
    "EIS_DC[A]",
]
