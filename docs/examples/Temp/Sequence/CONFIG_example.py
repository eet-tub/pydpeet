from pydpeet.process.sequence.utils.preprocessing.calculate_thresholds import calculate_minimum_definitive_differences
from pydpeet.process.sequence.threshold_dictonaries import THRESHOLD_DICT_NEWARE, THRESHOLD_DICT_BaSyTec_custom_fit_to_known_data
from typing import Dict

THRESHOLD_DICT_Custom = [  # BaSyTec
    0.001,  # ACCURACY_VOLTAGE_SIGNAL
    0.001,  # ACCURACY_CURRENT_SIGNAL
    0.001,  # ACCURACY_VOLTAGE_MEASUREMENT
    0.001,  # ACCURACY_CURRENT_MEASUREMENT
    5,  # FS_VOLTAGE
    5  # FS_CURRENT
]
# use THRESHOLD_DICT = THRESHOLD_DICT_Custom if you don't want to use a predefined dictionary
THRESHOLD_DICT = THRESHOLD_DICT_NEWARE.threshold_dict_neware
#THRESHOLD_DICT = THRESHOLD_DICT_BaSyTec_custom_fit_to_known_data.THRESHOLD_DICT_BaSyTec_custom_fit_to_known_data
MIN_DEFINITIVE_VOLTAGE_DIFFERENCE, MIN_DEFINITIVE_CURRENT_DIFFERENCE = calculate_minimum_definitive_differences(*THRESHOLD_DICT)
####### depending on the Noise needs to be adjusted even for measurements of the same device #######
SEGMENTS_TO_DETECT_CONFIG = [
    # lower threshold makes it more likely that noisy/non-constant parts get correctly suppressed, due to their smaller lengths
    ("Voltage[V]", MIN_DEFINITIVE_VOLTAGE_DIFFERENCE/2),
    ("Current[A]", MIN_DEFINITIVE_CURRENT_DIFFERENCE/2),
    ("Power[W]", (MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE)/2),
]
####### depending on the Noise needs to be adjusted even for measurements of the same device #######
#ORDER IS IMPORTANT!
ADJUST_SEGMENTS_CONFIG = [
    ("Voltage[V]", MIN_DEFINITIVE_VOLTAGE_DIFFERENCE),
    ("Current[A]", MIN_DEFINITIVE_CURRENT_DIFFERENCE),
    ("Power[W]", (MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE)),
]

THRESHOLD_CV_SEGMENTS_0A_END = MIN_DEFINITIVE_CURRENT_DIFFERENCE

####### HAS TO USE SAME KEY AS DATA_COLUMNS! only change the values of thresholds! ########
THRESHOLDS_PRIMITIVE_ANNOTATION = {
    "V": MIN_DEFINITIVE_VOLTAGE_DIFFERENCE,
    "I": MIN_DEFINITIVE_CURRENT_DIFFERENCE,
    "P": MIN_DEFINITIVE_VOLTAGE_DIFFERENCE + MIN_DEFINITIVE_CURRENT_DIFFERENCE
}

########################################################################################################################
SHOW_RUNTIME = True
THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK = 2
THRESHOLD_CONSOLE_PRINTS_CV_CHECK = 2
THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH = 2
THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK = 10
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
    #("Power[W]", "green", (-40, 20)),
]
START = 0
END = 1e100
USE_LINES_FOR_SEGMENTS = True
SHOW_COLUMN_NAMES = True
SHOW_TIME = True
SHOW_ID = True
SEGMENT_ALPHA = 0.3
WIDTH_HEIGHT_RATIO = [1, 0.3]
########################################################################################################################
# Generate Instructions
END_CONDITION_MAP_GENERATE_INSTRUCTIONS = {
    "CC": "voltage",
    "CV": "current",
    "CP": "voltage",
    "Pause": "time",
}
########################################################################################################################
SEQUENCES_CONFIG: Dict[str, Dict] = {
    # Complex Sequences
    # Loop rules: "loop": True, "exact_loops": 2, "min_loops": 2, "max_loops": 2, "minimum_IDs": 6
    "Discharge_iOCV": {"loop": True, "minimum_IDs": 4, "sequence": ["CC_Discharge","Pause"]},
    "Charge_iOCV": {"loop": True, "min_loops": 2, "sequence": ["Pause", "CC_Charge"]},

    "CCCV_Charge": {"loop": False, "sequence": ["CC_Charge", "CV_Charge"]},
    "CCCV_Discharge": {"loop": False, "sequence": ["CC_Discharge", "CV_Discharge"]},

    # Since Noise might create additional Segments during the pulses is this not possible in a single rule
    "HPPC_Pulse_Pause": {"loop": True, "sequence": ["less_then_15s", "Pause"]},
    "HPPC_Charge": {"sequence": ["HPPC_Pulse_Pause", "CC_Charge_longer_then_60s", "Pause"]},
    "HPPC_Discharge": {"sequence": ["HPPC_Pulse_Pause", "CC_Discharge_longer_then_60s", "Pause"]},


}
SEGMENTS_CONFIG_SIMPLE: Dict[str, Dict] = {
    # Primitive segments
    # I, V, P,
    # Charging, Discharging
    "I": {
        "rules": {
            "variable": "I",
        }
    },
    "V": {
        "rules": {
            "variable": "V",
        }
    },
    "P": {
        "rules": {
            "variable": "P",
        }
    },
    "Charging": {
        "rules": {
            "direction": "Charge",
        }
    },
    "Discharging": {
        "rules": {
            "direction": "Discharge",
        }
    },

}
SEGMENTS_CONFIG_STANDARD: Dict[str, Dict] = {
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
    "CP_Charge": {
        "rules": {
            "variable": "P",
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
    "CP_Discharge": {
        "rules": {
            "variable": "P",
            "type": "Constant",
            "direction": "Discharge",
        }
    },
    "CRamp_Charge": {
        "rules": {
            "variable": "I",
            "type": "Ramp",
            "direction": "Up",
        }
    },
    "VRamp_Charge": {
        "rules": {
            "variable": "V",
            "type": "Ramp",
            "direction": "Up",
        }
    },
    "PRamp_Charge": {
        "rules": {
            "variable": "P",
            "type": "Ramp",
            "direction": "Up",
        }
    },
    "CRamp_Discharge": {
        "rules": {
            "variable": "I",
            "type": "Ramp",
            "direction": "Down",
        }
    },
    "VRamp_Discharge": {
        "rules": {
            "variable": "V",
            "type": "Ramp",
            "direction": "Down",
        }
    },
    "PRamp_Discharge": {
        "rules": {
            "variable": "P",
            "type": "Ramp",
            "direction": "Down",
        }
    },
}

SEGMENTS_CONFIG_LENGTHS: Dict[str, Dict] = {
    "less_then_15s": {
        "rules": {
            "max_length_sec": 15,
        }
    },

    "I_Burst_less_then_15s": {
        "rules": {
            "variable": "I",
            "max_length_sec": 15,
        }
    },
    "V_Burst_less_then_15s": {
        "rules": {
            "variable": "V",
            "max_length_sec": 15,
        }
    },
    "P_Burst_less_then_15s": {
        "rules": {
            "variable": "P",
            "max_length_sec": 15,
        }
    },

    "CC_Charge_longer_then_60s": {
        "rules": {
            "variable": "I",
            "direction": "Charge",
            "min_length_sec": 60,
        }
    },
    "CC_Discharge_longer_then_60s": {
        "rules": {
            "variable": "I",
            "direction": "Discharge",
            "min_length_sec": 60,
        }
    },

}


SEGMENT_SEQUENCE_CONFIG = {
    **SEQUENCES_CONFIG,
    **SEGMENTS_CONFIG_LENGTHS,
    **SEGMENTS_CONFIG_STANDARD,
    **SEGMENTS_CONFIG_SIMPLE,
}
########################################################################################################################
#### These shouldn't be changed when using ppb Dataframes ####
DATA_COLUMNS = {
    "V": "Voltage[V]",
    "I": "Current[A]",
    "P": "Power[W]",
}
#### These shouldn't be changed when using ppb Dataframes ####


STEP_ANALYZER_PRIMITIVES_CONFIG = {
    "SEGMENTS_TO_DETECT_CONFIG": SEGMENTS_TO_DETECT_CONFIG,
    "ADJUST_SEGMENTS_CONFIG": ADJUST_SEGMENTS_CONFIG,
    "THRESHOLDS_PRIMITIVE_ANNOTATION": THRESHOLDS_PRIMITIVE_ANNOTATION,
    "SHOW_RUNTIME": SHOW_RUNTIME,
    "DATA_COLUMNS": DATA_COLUMNS,
    "MIN_DEFINITIVE_CURRENT_DIFFERENCE": MIN_DEFINITIVE_CURRENT_DIFFERENCE,
    "THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK": THRESHOLD_CONSOLE_PRINTS_ZERO_LENGTH_CHECK,
    "THRESHOLD_CONSOLE_PRINTS_CV_CHECK": THRESHOLD_CONSOLE_PRINTS_CV_CHECK,
    "THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH": THRESHOLD_CONSOLE_PRINTS_FINETUNING_WIDTH,
    "THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK": THRESHOLD_CONSOLE_PRINTS_POWER_ZERO_WATT_CHECK,
    "THRESHOLD_CV_SEGMENTS_0A_END": THRESHOLD_CV_SEGMENTS_0A_END
    # you could also add the bools to this config, but they will likely be changed often in the actual function calls
}
