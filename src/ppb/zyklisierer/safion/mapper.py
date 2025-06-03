# Define the mapping from current names to standardized names
COLUMN_MAP = {
    "step": "StepID",
    "impedance_frequency": "EISFreq[Hz]",
    "real impedance": "Zre[Ohm]",
    "imaginary impedance": "Zim[Ohm]"
}

MISSING_REQUIRED_COLUMNS = [
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Testtime[s]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "DC_Current[A]"
]
