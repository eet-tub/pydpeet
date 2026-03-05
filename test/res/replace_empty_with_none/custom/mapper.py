# Define the mapping from current names to standardized names
# digatron LiVsBlei
COLUMN_MAP = {
    "Zreal1": "EIS_Z_Real[Ohm]",
    "Zimg1": "EIS_Z_Imag[Ohm]",
    "Zeitstempel": "Date_Time",
    "Schritt Nr.": "Step_Count",
    "Spannung": "Voltage[V]",
    "Strom": "Current[A]",
    "Progr. Zeit": "Test_Time[s]"
}

MISSING_REQUIRED_COLUMNS = [
    "Temperature[°C]",
    "EIS_f[Hz]",
    "EIS_DC[A]"
]

