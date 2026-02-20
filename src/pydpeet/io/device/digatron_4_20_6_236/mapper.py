# Define the mapping from current names to standardized names
# digatron LiVsBlei
COLUMN_MAP = {
    "Schritt Zeit": "Testtime[s]",
    "Spannung": "Voltage[V]",
    "Strom": "Current[A]",
    "Schritt Nr.": "StepID",
    "Zeitstempel": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "T_Batt": "Temperature[°C]"
}

MISSING_REQUIRED_COLUMNS = [
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]"
]
