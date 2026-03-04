# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP_1 = {
    r"Frequency/Hz": "EIS_f[Hz]",
    "Number": "Step_Count",
}

COLUMN_MAP_2 = {
    "step": "Step_Count",
    "voltage V": "Voltage[V]",
    "time s": "Test_Time[s]",
    "current A": "Current[A]",
}

COLUMN_MAP_3 = {
    "Number": "Step_Count",
    "Voltage/V": "Voltage[V]",
    "Current/A": "Current[A]",
    "Time/s": "Test_Time[s]",
    "Frequency/Hz": "EIS_f[Hz]",
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
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
]

MISSING_REQUIRED_COLUMNS_2 = [
    "EIS_DC[A]",
    "Temperature[°C]",
    "Date_Time",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
]

MISSING_REQUIRED_COLUMNS_3 = [
    "Temperature[°C]",
    "Date_Time",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]",
]
