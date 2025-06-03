# Define the mapping from current names to standardized names
COLUMN_MAP_1 = {
    "Frequency/Hz": "EISFreq[Hz]",
    "Number": "StepID",
    r"R/": "Zre[Ohm]",
    r"I/": "Zim[Ohm]"
}

COLUMN_MAP_2 = {
    "step": "StepID",
    "voltage V": "Voltage[V]",
    "time s": "Testtime[s]",
    "current A": "Current[A]"
}

MISSING_REQUIRED_COLUMNS_1 = [
    "Testtime[s]",
    "Voltage[V]",
    "Current[A]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "Temperature[°C]",
    "DC_Current[A]"
]

MISSING_REQUIRED_COLUMNS_2 = [
    "DC_Current[A]",
    "Temperature[°C]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",

]