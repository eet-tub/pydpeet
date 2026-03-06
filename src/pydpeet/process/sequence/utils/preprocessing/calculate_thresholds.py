def calculate_minimum_definitive_differences(
    accuracy_voltage_signal: float,
    accuracy_current_signal: float,
    accuracy_voltage_measurement: float,
    accuracy_current_measurement: float,
    fs_voltage: float,
    fs_current: float,
) -> tuple[float, float]:
    """
    Calculate minimum definitive differences, that can't be described by noise.

    Parameters:
        accuracy_voltage_signal (float): Accuracy of voltage signal/stimulus.
        accuracy_current_signal (float): Accuracy of current signal/stimulus.
        accuracy_voltage_measurement (float): Accuracy of voltage measurement.
        accuracy_current_measurement (float): Accuracy of current measurement.
        fs_voltage (float): Full-scale voltage value.
        fs_current (float): Full-scale current value.

    Returns:
        minimum_definitive_voltage_difference (float): Minimum definitive voltage difference.
        minimum_definitive_current_difference (float): Minimum definitive current difference.
    """
    minimum_definitive_voltage_difference = (accuracy_voltage_signal + accuracy_voltage_measurement) * fs_voltage
    minimum_definitive_current_difference = (accuracy_current_signal + accuracy_current_measurement) * fs_current

    return minimum_definitive_voltage_difference, minimum_definitive_current_difference
