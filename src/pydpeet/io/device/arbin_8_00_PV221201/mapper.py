# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Record number": "Step_Count",
    "Voltage(V)": "Voltage[V]",
    "Current(A)": "Current[A]",
    "Relative Time(h:min:s.ms)": "Test_Time[s]",
    "Real Time(h:min:s.ms)": "Date_Time",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]",
]
