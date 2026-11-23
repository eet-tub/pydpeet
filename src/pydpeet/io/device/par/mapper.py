# Map raw-data column names (left) to standardized column names (right).
_COLUMN_MAP = {
    "Elapsed Time(s)": "Test_Time[s]",
    "E(V)": "Voltage[V]",
    "I(A)": "Current[A]",
    "Point #": "Step_Count",
    "Frequency(Hz)": "EIS_f[Hz]",
    "Z Real": "EIS_Z_Real[Ohm]",
    "Z Imag": "EIS_Z_Imag[Ohm]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
_MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "Date_Time",
    "EIS_DC[A]",
]
