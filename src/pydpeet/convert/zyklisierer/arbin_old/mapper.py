# Define the mapping from current names to standardized names
COLUMN_MAP = {
    "Data_Point": "StepID",
    "Voltage(V)": "Voltage[V]",
    "Current(A)": "Current[A]",
    "Test_Time(s)": "Testtime[s]",
    "Date_Time": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "Temperature (C)_1": "Temperature[°C]"
}


MISSING_REQUIRED_COLUMNS = [
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]"
]
