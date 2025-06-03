from enum import Enum, auto
from typing import Callable

from pandas import DataFrame
# arbin
import ppb.zyklisierer.arbin.reader as arbin_reader
import ppb.zyklisierer.arbin.formatter as arbin_formatter
import ppb.zyklisierer.arbin.mapper as arbin_mapper
# arbin_old
import ppb.zyklisierer.arbin_old.formatter as arbin_old_formatter
import ppb.zyklisierer.arbin_old.mapper as arbin_old_mapper
import ppb.zyklisierer.arbin_old.reader as arbin_old_reader
# basytec
import ppb.zyklisierer.basytec.formatter as basytec_formatter
import ppb.zyklisierer.basytec.mapper as basytec_mapper
import ppb.zyklisierer.basytec.reader as basytec_reader
# digatron
import ppb.zyklisierer.digatron.formatter as digatron_formatter
import ppb.zyklisierer.digatron.mapper as digatron_mapper
import ppb.zyklisierer.digatron.reader as digatron_reader
# digatron_eis
import ppb.zyklisierer.digatron_eis.formatter as digatron_eis_formatter
import ppb.zyklisierer.digatron_eis.mapper as digatron_eis_mapper
import ppb.zyklisierer.digatron_eis.reader as digatron_eis_reader
# neware
import ppb.zyklisierer.neware.formatter as neware_formatter
import ppb.zyklisierer.neware.mapper as neware_mapper
import ppb.zyklisierer.neware.reader as neware_reader
# parstat
import ppb.zyklisierer.parstat.formatter as parstat_formatter
import ppb.zyklisierer.parstat.mapper as parstat_mapper
import ppb.zyklisierer.parstat.reader as parstat_reader
# safion
import ppb.zyklisierer.safion.formatter as safion_formatter
import ppb.zyklisierer.safion.mapper as safion_mapper
import ppb.zyklisierer.safion.reader as safion_reader
# zahner
import ppb.zyklisierer.zahner.formatter as zahner_formatter
import ppb.zyklisierer.zahner.mapper as zahner_mapper
import ppb.zyklisierer.zahner.reader as zahner_reader
# zahner_new
import ppb.zyklisierer.zahner_new.formatter as zahner_new_formatter
import ppb.zyklisierer.zahner_new.mapper as zahner_new_mapper
import ppb.zyklisierer.zahner_new.reader as zahner_new_reader


class Config(Enum):
    Zahner_1 = auto()
    Zahner_2 = auto()
    Zahner_new_1 = auto()
    Zahner_new_2 = auto()
    Zahner_new_3 = auto()
    Safion = auto()
    Parstat = auto()
    Neware = auto()
    Digatron = auto()
    Digatron_EIS = auto()
    BaSyTec = auto()
    Arbin = auto()
    Arbin_Old = auto()
    Custom = auto()

    @staticmethod
    def exists(maybe_config: any) -> bool:
        """
        Checks if a given configuration is a member of the Config enum.

        Args:
            maybe_config (any): The configuration to check, which can be an enum member or its value.

        Returns:
            bool: True if maybe_config is a member of the Config enum or its value; False otherwise.
        """
        try:
            return maybe_config in Config.__members__ or maybe_config.value in {config.value for config in Config}
        except Exception:
            return False

    @staticmethod
    def not_exists(value: any) -> bool:
        """
        Checks if a given configuration does not exist.

        Args:
            value (any): The configuration to check, which can be an enum member or its value.

        Returns:
            bool: True if maybe_config is not a member of the Config enum or its value; False otherwise.
        """
        return not Config.exists(value)


STANDARD_COLUMNS = [
    "Metadata",
    "StepID",
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Testtime[s]",
    "Absolute Time[yyyy-mm-dd hh:mm:ss]",
    "EISFreq[Hz]",
    "Zre[Ohm]",
    "Zim[Ohm]",
    "DC_Current[A]"
]

READER_CONFIGS: dict[Config, Callable[[str], DataFrame]] = \
    {
        # zahner readers
        Config.Zahner_1: zahner_reader.to_DataFrame,
        Config.Zahner_2: zahner_reader.to_DataFrame,

        # zahner New readers
        Config.Zahner_new_1: zahner_new_reader.to_DataFrame,
        Config.Zahner_new_2: zahner_new_reader.to_DataFrame,
        Config.Zahner_new_3: zahner_new_reader.to_DataFrame,

        # Other readers
        Config.Safion: safion_reader.to_DataFrame,
        Config.Parstat: parstat_reader.to_DataFrame,
        Config.Neware: neware_reader.to_DataFrame,
        Config.Digatron: digatron_reader.to_DataFrame,
        Config.Digatron_EIS: digatron_eis_reader.to_DataFrame,
        Config.BaSyTec: basytec_reader.to_DataFrame,
        Config.Arbin: arbin_reader.to_DataFrame,
        Config.Arbin_Old: arbin_old_reader.to_DataFrame,
    }

MAPPER_CONFIGS: dict[Config, tuple[dict[str, str], list[str]]] = \
    {
        # zahner mappers
        Config.Zahner_1: (zahner_mapper.COLUMN_MAP_1, zahner_mapper.MISSING_REQUIRED_COLUMNS_1),
        Config.Zahner_2: (zahner_mapper.COLUMN_MAP_2, zahner_mapper.MISSING_REQUIRED_COLUMNS_2),

        # zahner New mappers
        Config.Zahner_new_1: (zahner_new_mapper.COLUMN_MAP_1, zahner_new_mapper.MISSING_REQUIRED_COLUMNS_1),
        Config.Zahner_new_2: (zahner_new_mapper.COLUMN_MAP_2, zahner_new_mapper.MISSING_REQUIRED_COLUMNS_2),
        Config.Zahner_new_3: (zahner_new_mapper.COLUMN_MAP_3, zahner_new_mapper.MISSING_REQUIRED_COLUMNS_3),

        # Other mappers
        Config.Safion: (safion_mapper.COLUMN_MAP, safion_mapper.MISSING_REQUIRED_COLUMNS),
        Config.Parstat: (parstat_mapper.COLUMN_MAP, parstat_mapper.MISSING_REQUIRED_COLUMNS),
        Config.Neware: (neware_mapper.COLUMN_MAP, neware_mapper.MISSING_REQUIRED_COLUMNS),
        Config.Digatron: (digatron_mapper.COLUMN_MAP, digatron_mapper.MISSING_REQUIRED_COLUMNS),
        Config.Digatron_EIS: (digatron_eis_mapper.COLUMN_MAP, digatron_eis_mapper.MISSING_REQUIRED_COLUMNS),
        Config.BaSyTec: (basytec_mapper.COLUMN_MAP, basytec_mapper.MISSING_REQUIRED_COLUMNS),
        Config.Arbin: (arbin_mapper.COLUMN_MAP, arbin_mapper.MISSING_REQUIRED_COLUMNS),
        Config.Arbin_Old: (arbin_old_mapper.COLUMN_MAP, arbin_old_mapper.MISSING_REQUIRED_COLUMNS),
    }

FORMATTER_CONFIGS: dict[Config, Callable[[DataFrame], DataFrame]] = \
    {
        # zahner formatters
        Config.Zahner_1: zahner_formatter.get_data_into_format_zahner_1,
        Config.Zahner_2: zahner_formatter.get_data_into_format_zahner_2,

        # zahner New formatters
        Config.Zahner_new_1: zahner_new_formatter.get_data_into_format_zahner_1,
        Config.Zahner_new_2: zahner_new_formatter.get_data_into_format_zahner_2,
        Config.Zahner_new_3: zahner_new_formatter.get_data_into_format_zahner_3,

        # Other formatters
        Config.Safion: safion_formatter.get_data_into_format,
        Config.Parstat: parstat_formatter.get_data_into_format,
        Config.Neware: neware_formatter.get_data_into_format,
        Config.Digatron: digatron_formatter.get_data_into_format,
        Config.Digatron_EIS: digatron_eis_formatter.get_data_into_format,
        Config.BaSyTec: basytec_formatter.get_data_into_format,
        Config.Arbin: arbin_formatter.get_data_into_format,
        Config.Arbin_Old: arbin_old_formatter.get_data_into_format,
    }


class DataOutputFiletype(Enum):
    parquet = auto()
    csv = auto()
    xlsx = auto()
