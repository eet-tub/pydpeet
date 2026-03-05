# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Data_Point": "Step_Count",
    "Voltage(V)": "Voltage[V]",
    "Current(A)": "Current[A]",
    "Test_Time(s)": "Test_Time[s]",
    "Date_Time": "Date_Time",
    "Temperature (C)_1": "Temperature[°C]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]",
]
