from collections.abc import Callable
from enum import Enum, auto

from pandas import DataFrame
# Arbin, MITS Pro v8.00.13 (PV221201)
import pydpeet.io.device.arbin_8_00_PV221201.reader as arbin_8_00_PV221201_reader
import pydpeet.io.device.arbin_8_00_PV221201.formatter as arbin_8_00_PV221201_formatter
import pydpeet.io.device.arbin_8_00_PV221201.mapper as arbin_8_00_PV221201_mapper
# arbin_old
import pydpeet.io.device.arbin_4_23_PV090331.formatter as arbin_4_23_PV090331_formatter
import pydpeet.io.device.arbin_4_23_PV090331.mapper as arbin_4_23_PV090331_mapper
import pydpeet.io.device.arbin_4_23_PV090331.reader as arbin_4_23_PV090331_reader
# basytec
import pydpeet.io.device.basytec_6_3_1_0.formatter as basytec_6_3_1_0_formatter
import pydpeet.io.device.basytec_6_3_1_0.mapper as basytec_6_3_1_0_mapper
import pydpeet.io.device.basytec_6_3_1_0.reader as basytec_6_3_1_0_reader
# digatron
import pydpeet.io.device.digatron_4_20_6_236.formatter as digatron_4_20_6_236_formatter
import pydpeet.io.device.digatron_4_20_6_236.mapper as digatron_4_20_6_236_mapper
import pydpeet.io.device.digatron_4_20_6_236.reader as digatron_4_20_6_236_reader
# digatron_eis
import pydpeet.io.device.digatron_eis_4_20_6_236.formatter as digatron_eis_4_20_6_236_formatter
import pydpeet.io.device.digatron_eis_4_20_6_236.mapper as digatron_eis_4_20_6_236_mapper
import pydpeet.io.device.digatron_eis_4_20_6_236.reader as digatron_eis_4_20_6_236_reader
# neware
import pydpeet.io.device.neware_8_0_0_516.formatter as neware_8_0_0_516_formatter
import pydpeet.io.device.neware_8_0_0_516.mapper as neware_8_0_0_516_mapper
import pydpeet.io.device.neware_8_0_0_516.reader as neware_8_0_0_516_reader
# parstat
import pydpeet.io.device.parstat_2_63_3.formatter as parstat_2_63_3_formatter
import pydpeet.io.device.parstat_2_63_3.mapper as parstat_2_63_3_mapper
import pydpeet.io.device.parstat_2_63_3.reader as parstat_2_63_3_reader
# safion
import pydpeet.io.device.safion_1_9.formatter as safion_1_9_formatter
import pydpeet.io.device.safion_1_9.mapper as safion_1_9_mapper
import pydpeet.io.device.safion_1_9.reader as safion_1_9_reader
# zahner
import pydpeet.io.device.zahner.formatter as zahner_formatter
import pydpeet.io.device.zahner.mapper as zahner_mapper
import pydpeet.io.device.zahner.reader as zahner_reader
# zahner_new
import pydpeet.io.device.zahner_new.formatter as zahner_new_formatter
import pydpeet.io.device.zahner_new.mapper as zahner_new_mapper
import pydpeet.io.device.zahner_new.reader as zahner_new_reader


class Config(Enum):
    Zahner_1 = auto()
    Zahner_2 = auto()
    Zahner_new_1 = auto()
    Zahner_new_2 = auto()
    Zahner_new_3 = auto()
    Safion_1_9 = auto()
    Parstat_2_63_3 = auto()
    Neware_8_0_0_516 = auto()
    Digatron_4_20_6_236 = auto()
    Digatron_EIS_4_20_6_236 = auto()
    BaSyTec_6_3_1_0 = auto()
    Arbin_8_00_PV221201 = auto()
    Arbin_4_23_PV090331 = auto()
    Custom = auto()

    @classmethod
    def from_string(cls, value: str) -> "Config":
        if not isinstance(value, str):
            raise TypeError("Config must be str or Config enum")

        key = value.strip().lower()

        aliases = {
            "arbin_4_23_pv090331": cls.Arbin_4_23_PV090331,
            "arbin_8_00_pv221201": cls.Arbin_8_00_PV221201,
            "basytec_6_3_1_0": cls.BaSyTec_6_3_1_0,
            "digatron_4_20_6_236": cls.Digatron_4_20_6_236,
            "digatron_eis_4_20_6_236": cls.Digatron_EIS_4_20_6_236,
            "neware_8_0_0_516": cls.Neware_8_0_0_516,
            "parstat_2_63_3": cls.Parstat_2_63_3,
            "safion_1_9": cls.Safion_1_9,
            "zahner1": cls.Zahner_1,
            "zahner2": cls.Zahner_2,
            "zahner_new_1": cls.Zahner_new_1,
        }

        try:
            return aliases[key]
        except KeyError:
            known = ", ".join(aliases.keys())
            raise ValueError(f"Unknown config '{value}'. Known: {known}")
    
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
    "Meta_Data",
    "Step_Count",
    "Voltage[V]",
    "Current[A]",
    "Temperature[°C]",
    "Test_Time[s]",
    "Date_Time",
    "EIS_f[Hz]",
    "EIS_Z_Real[Ohm]",
    "EIS_Z_Imag[Ohm]",
    "EIS_DC[A]"
]

READER_CONFIGS: dict[Config, Callable[[str], DataFrame]] = {
    # zahner readers
    Config.Zahner_1: zahner_reader.to_dataframe,
    Config.Zahner_2: zahner_reader.to_dataframe,
    # zahner New readers
    Config.Zahner_new_1: zahner_new_reader.to_dataframe,
    Config.Zahner_new_2: zahner_new_reader.to_dataframe,
    Config.Zahner_new_3: zahner_new_reader.to_dataframe,
    # Other readers
    Config.Safion_1_9: safion_1_9_reader.to_dataframe,
    Config.Parstat_2_63_3: parstat_2_63_3_reader.to_dataframe,
    Config.Neware_8_0_0_516: neware_8_0_0_516_reader.to_dataframe,
    Config.Digatron_4_20_6_236: digatron_4_20_6_236_reader.to_dataframe,
    Config.Digatron_EIS_4_20_6_236: digatron_eis_4_20_6_236_reader.to_dataframe,
    Config.BaSyTec_6_3_1_0: basytec_6_3_1_0_reader.to_dataframe,
    Config.Arbin_8_00_PV221201: arbin_8_00_PV221201_reader.to_dataframe,
    Config.Arbin_4_23_PV090331: arbin_4_23_PV090331_reader.to_dataframe,
}

MAPPER_CONFIGS: dict[Config, tuple[dict[str, str], list[str]]] = {
    # zahner mappers
    Config.Zahner_1: (zahner_mapper.COLUMN_MAP_1, zahner_mapper.MISSING_REQUIRED_COLUMNS_1),
    Config.Zahner_2: (zahner_mapper.COLUMN_MAP_2, zahner_mapper.MISSING_REQUIRED_COLUMNS_2),
    # zahner New mappers
    Config.Zahner_new_1: (zahner_new_mapper.COLUMN_MAP_1, zahner_new_mapper.MISSING_REQUIRED_COLUMNS_1),
    Config.Zahner_new_2: (zahner_new_mapper.COLUMN_MAP_2, zahner_new_mapper.MISSING_REQUIRED_COLUMNS_2),
    Config.Zahner_new_3: (zahner_new_mapper.COLUMN_MAP_3, zahner_new_mapper.MISSING_REQUIRED_COLUMNS_3),
    # Other mappers
    Config.Safion_1_9: (safion_1_9_mapper.COLUMN_MAP, safion_1_9_mapper.MISSING_REQUIRED_COLUMNS),
    Config.Parstat_2_63_3: (parstat_2_63_3_mapper.COLUMN_MAP, parstat_2_63_3_mapper.MISSING_REQUIRED_COLUMNS),
    Config.Neware_8_0_0_516: (neware_8_0_0_516_mapper.COLUMN_MAP, neware_8_0_0_516_mapper.MISSING_REQUIRED_COLUMNS),
    Config.Digatron_4_20_6_236: (digatron_4_20_6_236_mapper.COLUMN_MAP, digatron_4_20_6_236_mapper.MISSING_REQUIRED_COLUMNS),
    Config.Digatron_EIS_4_20_6_236: (digatron_eis_4_20_6_236_mapper.COLUMN_MAP, digatron_eis_4_20_6_236_mapper.MISSING_REQUIRED_COLUMNS),
    Config.BaSyTec_6_3_1_0: (basytec_6_3_1_0_mapper.COLUMN_MAP, basytec_6_3_1_0_mapper.MISSING_REQUIRED_COLUMNS),
    Config.Arbin_8_00_PV221201: (arbin_8_00_PV221201_mapper.COLUMN_MAP, arbin_8_00_PV221201_mapper.MISSING_REQUIRED_COLUMNS),
    Config.Arbin_4_23_PV090331: (arbin_4_23_PV090331_mapper.COLUMN_MAP, arbin_4_23_PV090331_mapper.MISSING_REQUIRED_COLUMNS),
}

FORMATTER_CONFIGS: dict[Config, Callable[[DataFrame], DataFrame]] = {
    # zahner formatters
    Config.Zahner_1: zahner_formatter.get_data_into_format_zahner_1,
    Config.Zahner_2: zahner_formatter.get_data_into_format_zahner_2,
    # zahner New formatters
    Config.Zahner_new_1: zahner_new_formatter.get_data_into_format_zahner_1,
    Config.Zahner_new_2: zahner_new_formatter.get_data_into_format_zahner_2,
    Config.Zahner_new_3: zahner_new_formatter.get_data_into_format_zahner_3,
    # Other formatters
    Config.Safion_1_9: safion_1_9_formatter.get_data_into_format,
    Config.Parstat_2_63_3: parstat_2_63_3_formatter.get_data_into_format,
    Config.Neware_8_0_0_516: neware_8_0_0_516_formatter.get_data_into_format,
    Config.Digatron_4_20_6_236: digatron_4_20_6_236_formatter.get_data_into_format,
    Config.Digatron_EIS_4_20_6_236: digatron_eis_4_20_6_236_formatter.get_data_into_format,
    Config.BaSyTec_6_3_1_0: basytec_6_3_1_0_formatter.get_data_into_format,
    Config.Arbin_8_00_PV221201: arbin_8_00_PV221201_formatter.get_data_into_format,
    Config.Arbin_4_23_PV090331: arbin_4_23_PV090331_formatter.get_data_into_format,
}


class DataOutputFiletype(Enum):
    parquet = auto()
    csv = auto()
    xlsx = auto()
