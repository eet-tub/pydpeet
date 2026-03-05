# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Elapsed Time (s)": "Test_Time[s]",
    "Potential (V)": "Voltage[V]",
    "Current (A)": "Current[A]",
    "Point": "Step_Count",
    "Frequency (Hz)": "EIS_f[Hz]",
    "Zre (ohms)": "EIS_Z_Real[Ohm]",
    "Zim (ohms)": "EIS_Z_Imag[Ohm]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "Date_Time",
    "EIS_DC[A]",
]
