from pydpeet.process.sequence.configs.config import NEWARE_CT_4008Q_5V12A_S1
from pydpeet.process.sequence.utils.preprocessing.calculate_thresholds import calculate_minimum_definitive_differences

THRESHOLD_DICT_Custom = [  # ARBIN_OLD
    0.0005,  # ACCURACY_VOLTAGE_SIGNAL
    0.01,  # ACCURACY_CURRENT_SIGNAL
    0.0005,  # ACCURACY_VOLTAGE_MEASUREMENT
    0.01,  # ACCURACY_CURRENT_MEASUREMENT
    5,  # FS_VOLTAGE
    3,  # FS_CURRENT
]
# use THRESHOLD_DICT = THRESHOLD_DICT_Custom if you don't want to use a predefined dictionary
THRESHOLD_DICT = NEWARE_CT_4008Q_5V12A_S1.threshold_dict_neware
MIN_DEFINITIVE_VOLTAGE_DIFFERENCE, MIN_DEFINITIVE_CURRENT_DIFFERENCE = calculate_minimum_definitive_differences(*THRESHOLD_DICT)

####### depending on the Noise needs to be adjusted even for measurements of the same device #######
SEGMENTS_TO_DETECT_CONFIG = [
    # devide threshold by 2 because it's looking above and below the target line
    ("Voltage[V]", MIN_DEFINITIVE_VOLTAGE_DIFFERENCE / 2),
    ("Current[A]", MIN_DEFINITIVE_CURRENT_DIFFERENCE / 2),
    ("Power[W]", (MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE) / 2),
]
####### depending on the Noise needs to be adjusted even for measurements of the same device #######
# ORDER IS IMPORTANT!
ADJUST_SEGMENTS_CONFIG = [
    ("Voltage[V]", MIN_DEFINITIVE_VOLTAGE_DIFFERENCE),
    ("Current[A]", MIN_DEFINITIVE_CURRENT_DIFFERENCE),
    ("Power[W]", (MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE)),
]

####### HAS TO USE SAME KEY AS DATA_COLUMNS! only change the values of thresholds! ########
THRESHOLDS_PRIMITIVE_ANNOTATION = {
    "V": MIN_DEFINITIVE_VOLTAGE_DIFFERENCE,
    "I": MIN_DEFINITIVE_CURRENT_DIFFERENCE,
    "P": MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE
}

########################################################################################################################
SHOW_RUNTIME = True
SHOW_RUNTIME_ANNOTATION = True
SHOW_RUNTIME_ANALYZE = True
SHOW_RUNTIME_VISUALIZATION = True
THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK = 2
THRESHOLD_CONSOLE_PRINTS_CV_CHECK = 2
########################################################################################################################
# Visualize Data
VISUALIZE_PHASES_CONFIG = [
    ("V", "blue"),
    ("I", "red"),
    ("P", "green"),
]
LINE_VISUALIZATION_CONFIG = [
    ("Voltage[V]", "blue", (2.4, 4.3)),
    ("Current[A]", "red", (-10, 10)),
    # ("Power[W]", "green", (-40, 20)),
]
# Bilder Bachelorarbeit Text
# ("Voltage[V]", "blue", (2.4, 4.3)),
# ("Current[A]", "red", (-10, 10)),
START = 0  # 55000.0
END = 1e10  # 90000
USE_LINES_FOR_SEGMENTS = True
SHOW_COLUMN_NAMES = False
SHOW_TIME = False
SHOW_ID = False
SEGMENT_ALPHA = 0.3
WIDTH_HEIGHT_RATIO = [1.0, 0.3]
########################################################################################################################
# Generate Instructions
END_CONDITION_MAP_GENERATE_INSTRUCTIONS = {
    "CC": "voltage",
    "CV": "current",
    "CP": "voltage",
    "Pause": "time",
}
########################################################################################################################
SEQUENCES_CONFIG: dict[str, dict] = {
    # Complex Sequences
    # Loop rules: "loop": True, "exact_loops": 2, "min_loops": 2, "max_loops": 2, "minimum_IDs": 6
    "Discharge_iOCV": {"loop": True, "sequence": ["Pause", "CC_Discharge"]},
    "Charge_iOCV": {"loop": True, "sequence": ["Pause", "CC_Charge"]},
    # "Discharge_iOCV": {"sequence": ["Discharge_iOCV_correction", "CC_Discharge","CV_Discharge"]},
}

SEGMENTS_CONFIG_STANDARD: dict[str, dict] = {
    # Primitive segments
    # Pause
    # CC_Charge, CV_Charge, CP_Charge
    # CC_Discharge, CV_Discharge, CP_Discharge
    # Ramp_Current_Charge, Ramp_Voltage_Charge, Ramp_Power_Charge
    # Ramp_Current_Discharge, Ramp_Voltage_Discharge, Ramp_Power_Discharge
    "Pause": {
        "rules": {
            "type": "Rest",
        }
    },
    "CC_Charge": {
        "rules": {
            "variable": "I",
            "type": "Constant",
            "direction": "Charge",
        }
    },
    "CV_Charge": {
        "rules": {
            "variable": "V",
            "type": "Constant",
            "direction": "Charge",
        }
    },
    "CC_Discharge": {
        "rules": {
            "variable": "I",
            "type": "Constant",
            "direction": "Discharge",
        }
    },
    "CV_Discharge": {
        "rules": {
            "variable": "V",
            "type": "Constant",
            "direction": "Discharge",
        }
    },
    "Ramp": {
        "rules": {
            "type": "Ramp",
        }
    },
    "C_Charge": {
        "rules": {
            "variable": "I",
            "direction": "Charge",
        }
    },
    "C_Discharge": {
        "rules": {
            "variable": "I",
            "direction": "Discharge",
        }
    },
    "Discharge": {
        "rules": {
            "direction": "Charge",
        }
    },
}


SEGMENT_SEQUENCE_CONFIG = {
    **SEQUENCES_CONFIG,
    **SEGMENTS_CONFIG_STANDARD,
}

########################################################################################################################
#### These shouldn't be changed when using ppb Dataframes ####
DATA_COLUMNS = {
    "V": "Voltage[V]",
    "I": "Current[A]",
    "P": "Power[W]",
}
STANDARD_COLUMNS = [
    "Testtime[s]",
    "Voltage[V]",
    "Current[A]"
]
#### These shouldn't be changed when using ppb Dataframes ####

STEP_ANALYZER_PRIMITIVES_CONFIG = {
    "SEGMENTS_TO_DETECT_CONFIG": SEGMENTS_TO_DETECT_CONFIG,
    "ADJUST_SEGMENTS_CONFIG": ADJUST_SEGMENTS_CONFIG,
    "THRESHOLDS_PRIMITIVE_ANNOTATION": THRESHOLDS_PRIMITIVE_ANNOTATION,
    "SHOW_RUNTIME": SHOW_RUNTIME,
    "SHOW_RUNTIME_ANNOTATION": SHOW_RUNTIME_ANNOTATION,
    "DATA_COLUMNS": DATA_COLUMNS,
    "MIN_DEFINITIVE_CURRENT_DIFFERENCE": MIN_DEFINITIVE_CURRENT_DIFFERENCE,
    "THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK": THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK,
    "THRESHOLD_CONSOLE_PRINTS_CV_CHECK": THRESHOLD_CONSOLE_PRINTS_CV_CHECK,
}
