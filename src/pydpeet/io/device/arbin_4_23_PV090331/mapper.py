# Map raw-data column names (left) to standardized column names (right)
COLUMN_MAP = {
    "Data_Point": "StepID",
    "Voltage(V)": "Voltage[V]",
    "Current(A)": "Current[A]",
    "Test_Time(s)": "Testtime[s]",
    "Date_Time": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "Temperature (C)_1": "Temperature[°C]",
}

# Default columns of the standardized format
# which are not present in the raw data files.
MISSING_REQUIRED_COLUMNS = [
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]",
]
