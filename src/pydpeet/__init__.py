"""
Auto-generated __init__ file.
Created: 2026-03-06 15:11:49
"""

# Re-export selected names from source modules

from pydpeet.citations.citeme import print_references, write_to_bibtex
from pydpeet.io.configs.config import DataOutputFiletype, ReadConfig
from pydpeet.io.metadata import Metadata, extract_metadata
from pydpeet.io.read import convert, read
from pydpeet.io.utils import load_custom_module
from pydpeet.io.write import write
from pydpeet.process.analyze.capacity import add_capacity, add_charge_throughput
from pydpeet.process.analyze.configs.battery_config import BatteryConfig, battery_config_wrapper
from pydpeet.process.analyze.cycle import add_equivalent_full_cycles
from pydpeet.process.analyze.efficiency import add_efficiency_coulomb
from pydpeet.process.analyze.energy import add_cumulative_energy
from pydpeet.process.analyze.extract.dva_ica import extract_ocv_dva_ica
from pydpeet.process.analyze.extract.ocv import extract_ocv_iocv
from pydpeet.process.analyze.power import add_power
from pydpeet.process.analyze.resistance import add_resistance_internal
from pydpeet.process.analyze.soc import SocMethod, add_soc
from pydpeet.process.analyze.soh import add_soh
from pydpeet.process.merge.series import merge_into_campaign, merge_into_series
from pydpeet.process.sequence.configs.config import (
    DeviceConfig,
    PrimitiveConfig,
    SequenceOverviewConfig,
    VisualizationConfig,
    primitive_config_wrapper,
    sequence_overview_config_wrapper,
    visualization_config_wrapper,
)
from pydpeet.process.sequence.step_analyzer import add_primitive_segments, extract_sequence_overview
from pydpeet.process.sequence.utils.postprocessing.df_primitives_correction import df_primitives_correction
from pydpeet.process.sequence.utils.postprocessing.filter_df import (
    filter_and_split_df_by_blocks,
    filter_df,
    return_or_print_blocks,
    split_df_by_blocks,
)
from pydpeet.process.sequence.utils.postprocessing.generate_instructions import extract_instructions
from pydpeet.process.sequence.utils.preprocessing.calculate_thresholds import calculate_minimum_definitive_differences
from pydpeet.process.sequence.utils.visualize.visualize_data import visualize_phases
from pydpeet.utils.logging_style import set_logging_style

# Public API for this package
__all__ = [
    # Tutorial 01
    "ReadConfig",
    "read",
    "Metadata",
    "extract_metadata",
    "DataOutputFiletype",
    "load_custom_module",
    "merge_into_series",
    "write",
    "set_logging_style",
    "print_references",
    "write_to_bibtex",
    # Tutorial 02
    "add_primitive_segments",
    "PrimitiveConfig",
    "primitive_config_wrapper",
    "DeviceConfig",
    "calculate_minimum_definitive_differences",
    "visualize_phases",
    "VisualizationConfig",
    "visualization_config_wrapper",
    "df_primitives_correction",  # TODO Tut 2
    # "print_references",
    # "write_to_bibtex",
    # Tutorial 03
    "extract_sequence_overview",
    "SequenceOverviewConfig",
    "sequence_overview_config_wrapper",
    "extract_instructions",
    # "print_references",
    # "write_to_bibtex",
    # Tutorial 04
    "filter_and_split_df_by_blocks",  # TODO why 3 variants?
    "split_df_by_blocks",  # TODO why 3 variants?
    "filter_df",  # TODO why 3 variants?
    "return_or_print_blocks",
    "extract_ocv_iocv",
    "extract_ocv_dva_ica",
    # "print_references",
    # "write_to_bibtex",
    # Tutorial 05
    "SocMethod",
    "add_capacity",
    "BatteryConfig",
    "battery_config_wrapper",
    "add_charge_throughput",
    "add_cumulative_energy",
    "add_efficiency_coulomb",
    "add_equivalent_full_cycles",
    "add_power",
    "add_resistance_internal",
    "add_soc",
    "add_soh",
    # "print_references",
    # "write_to_bibtex",
    # TODO what / why is this?
    "merge_into_campaign",
    # TODO discuss if still needed, due to read()
    "convert",
]
