# Define the mapping from current names to standardized names
# digatron LiVsBlei
COLUMN_MAP = {
    "Zreal1": "Zre[Ohm]",
    "Zimg1": "Zim[Ohm]",
    "Zeitstempel": "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "Schritt Nr.": "StepID",
    "Spannung": "Voltage[V]",
    "Strom": "Current[A]",
    "Progr. Zeit": "Testtime[s]"
}

MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "EISFreq[Hz]",
    "DC_Current[A]"
]

