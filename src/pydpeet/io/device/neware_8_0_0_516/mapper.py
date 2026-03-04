# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "step_id": "Step_Count",
    "Voltage(V)": "Voltage[V]",
    "Current[A] - record": "Current[A]",
    "T1": "Temperature[°C]",
    "Total Time": "Test_Time[s]",
    "Date": "Date_Time",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]",
]
