from dataclasses import dataclass

@dataclass
class BatteryConfig:
    cell_name: str = "Default"
    c_ref: float = None
    soc_start: float = 0
    max_voltage: float = 4.2
    min_voltage: float = 2.5
    threshold_current: float = 0.075
    voltage_intervall: float = 0.04
    # ----- values for capacity calculation -----
    minimal_current_for_capacity: float = -1.2
    maximal_current_for_capacity: float = -0.8
    # ----- values for internal resistance calculation -----
    min_current_diff: float = 1
    max_time_diff: float = 0.5
    min_voltage_diff: float = 0
    ignore_negative_resistance_values: bool = False # ignores negative values in internal resistance calculation,
                                                    # should only appear in Neware Cells because of a bug

battery_default = BatteryConfig()

# Configs for different Cells
am23nmc = BatteryConfig(
    c_ref=4.8,
    max_voltage=4.2,
    min_voltage=2.5,
    min_current_diff = 1,
    max_time_diff = 0.5,
    min_voltage_diff = 0,
    ignore_negative_resistance_values = True
)

tc23nmc = BatteryConfig(
    c_ref=2.5,
    max_voltage=3.6,
    min_voltage=2.0
)



