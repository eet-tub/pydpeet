"""
Auto-generated __init__ file.
Created: 2026-03-05 15:28:07
"""

# Re-export selected names from source modules

from pydpeet.citations.citeme import print_references, write_to_bibtex
from pydpeet.io.convert import convert
from pydpeet.io.map import mapping
from pydpeet.io.read import read
from pydpeet.io.write import write
from pydpeet.process.analyze.capacity import add_capacity
from pydpeet.process.analyze.configs.battery_config import BatteryConfig, battery_config_default, hakadi_nmc_1500, lgm50lt_nmc_4800
from pydpeet.process.analyze.extract.ocv import extract_ocv_iocv
from pydpeet.process.analyze.resistance import add_resistance_internal
from pydpeet.process.analyze.soc import SocMethod, add_soc
from pydpeet.process.merge.series import merge_into_series
from pydpeet.process.sequence.step_analyzer import add_primitive_segments, extract_sequence_overview
from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction
from pydpeet.process.sequence.utils.postprocessing.filter_df import filter_and_split_df_by_blocks
from pydpeet.process.sequence.utils.postprocessing.generate_instructions import generate_instructions
from pydpeet.process.sequence.utils.visualize.visualize_data import visualize_phases
from pydpeet.utils.logging_style import set_logging_style

# Public API for this package
__all__ = [
    "BatteryConfig",
    "SocMethod",
    "add_capacity",
    "add_primitive_segments",
    "add_resistance_internal",
    "add_soc",
    "battery_config_default",
    "convert",
    "df_primitives_correction",
    "extract_ocv_iocv",
    "extract_sequence_overview",
    "filter_and_split_df_by_blocks",
    "generate_instructions",
    "hakadi_nmc_1500",
    "lgm50lt_nmc_4800",
    "mapping",
    "merge_into_series",
    "print_references",
    "read",
    "set_logging_style",
    "visualize_phases",
    "write",
    "write_to_bibtex",
]
