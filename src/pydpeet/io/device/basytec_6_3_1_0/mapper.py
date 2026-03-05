# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Time[h]": "Test_Time[s]",
    "U[V]": "Voltage[V]",
    "I[A]": "Current[A]",
    "T1[°C]": "Temperature[°C]",
    "Line": "Step_Count",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Date_Time",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]",
]
