# Define the mapping from current names to standardized names
COLUMN_MAP_1 = {
    r"Frequency/Hz": "EISFreq[Hz]",
    "Number": "StepID"
}

COLUMN_MAP_2 = {
    "step": "StepID",
    "voltage V": "Voltage[V]",
    "time s": "Testtime[s]",
    "current A": "Current[A]"
}

COLUMN_MAP_3 = {
    "Number": "StepID",
    "Voltage/V": "Voltage[V]",
    "Current/A": "Current[A]",
    "Time/s": "Testtime[s]",
    "Frequency/Hz": "EISFreq[Hz]"
}

MISSING_REQUIRED_COLUMNS_1 = [
    "Testtime[s]",
    "Voltage[V]",
    "Current[A]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "Temperature[°C]",
    "DC_Current[A]",
    "Zre[Ohm]",
    "Zim[Ohm]"
]

MISSING_REQUIRED_COLUMNS_2 = [
    "DC_Current[A]",
    "Temperature[°C]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]"
]

MISSING_REQUIRED_COLUMNS_3 = [
    "Temperature[°C]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]"
]
