# Map raw-data column names (left) to standardized column names (right).
# Raw names follow the BDF naming convention (preferred labels).
_COLUMN_MAP = {
    "Test Time / s": "Test_Time[s]",
    "Voltage / V": "Voltage[V]",
    "Current / A": "Current[A]",
    "Ambient Temperature / degC": "Temperature[°C]",
    "Step Count / 1": "Step_Count",
    "Unix Time / s": "Date_Time",
    "Frequency / Hz": "EIS_f[Hz]",  # TODO discuss if it's the correct one
    "Real Impedance / ohm": "EIS_Z_Real[Ohm]",
    "Imaginary Impedance / ohm": "EIS_Z_Imag[Ohm]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
# Note: EIS_DC[A] has no equivalent quantity in the BDF specification.
_MISSING_REQUIRED_COLUMNS = [
    "EIS_DC[A]",
]
