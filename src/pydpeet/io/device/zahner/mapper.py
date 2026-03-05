# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP_1 = {
    "Frequency/Hz": "EIS_f[Hz]",
    "Number": "Step_Count",
    r"R/": "EIS_Z_Real[Ohm]",
    r"I/": "EIS_Z_Imag[Ohm]",
}

COLUMN_MAP_2 = {
    "step": "Step_Count",
    "voltage V": "Voltage[V]",
    "time s": "Test_Time[s]",
    "current A": "Current[A]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS_1 = [
    "Test_Time[s]",
    "Voltage[V]",
    "Current[A]",
    "Date_Time",
    "Temperature[°C]",
    "EIS_DC[A]",
]

MISSING_REQUIRED_COLUMNS_2 = [
    "EIS_DC[A]",
    "Temperature[°C]",
    "Date_Time",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
]
