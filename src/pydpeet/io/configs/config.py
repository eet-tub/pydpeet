from collections.abc import Callable, Iterable
from enum import Enum, auto, nonmember
from typing import Any

from pandas import DataFrame

# Arbin MITS Pro
# v4.23 (090331), schedule version 3.03
import pydpeet.io.device.arbin_4_23_PV090331.formatter as arbin_4_23_PV090331_formatter
import pydpeet.io.device.arbin_4_23_PV090331.mapper as arbin_4_23_PV090331_mapper
import pydpeet.io.device.arbin_4_23_PV090331.reader as arbin_4_23_PV090331_reader

# Arbin MITS Pro
# v8.00 (PV221201), schedule version 8.00.13
import pydpeet.io.device.arbin_8_00_PV221201.formatter as arbin_8_00_PV221201_formatter
import pydpeet.io.device.arbin_8_00_PV221201.mapper as arbin_8_00_PV221201_mapper
import pydpeet.io.device.arbin_8_00_PV221201.reader as arbin_8_00_PV221201_reader

# BaSyTec Battery Test Software
# File version 6.3.1.0, product version 6.2
import pydpeet.io.device.basytec_6_3_1_0.formatter as basytec_6_3_1_0_formatter
import pydpeet.io.device.basytec_6_3_1_0.mapper as basytec_6_3_1_0_mapper
import pydpeet.io.device.basytec_6_3_1_0.reader as basytec_6_3_1_0_reader

# Battery Data Format
import pydpeet.io.device.bdf.formatter as bdf_formatter
import pydpeet.io.device.bdf.mapper as bdf_mapper
import pydpeet.io.device.bdf.reader as bdf_reader

# Digatron Battery Manager and Battery Manager Workstation
# v4.20.6.236 (2018-09-28)
import pydpeet.io.device.digatron_4_20_6_236.formatter as digatron_4_20_6_236_formatter
import pydpeet.io.device.digatron_4_20_6_236.mapper as digatron_4_20_6_236_mapper
import pydpeet.io.device.digatron_4_20_6_236.reader as digatron_4_20_6_236_reader

# Digatron (EIS) Battery Manager and Battery Manager Workstation
# v4.20.6.236 (2018-09-28)
import pydpeet.io.device.digatron_eis_4_20_6_236.formatter as digatron_eis_4_20_6_236_formatter
import pydpeet.io.device.digatron_eis_4_20_6_236.mapper as digatron_eis_4_20_6_236_mapper
import pydpeet.io.device.digatron_eis_4_20_6_236.reader as digatron_eis_4_20_6_236_reader

# Neware BTS
# Client version 8.0.0.516 (2023-05-13 R3), server version 8.0.0.323 (2023-05-13 R3)
import pydpeet.io.device.neware_8_0_0_516.formatter as neware_8_0_0_516_formatter
import pydpeet.io.device.neware_8_0_0_516.mapper as neware_8_0_0_516_mapper
import pydpeet.io.device.neware_8_0_0_516.reader as neware_8_0_0_516_reader

# Parstat VersaStudio
# v2.63.3, firmware version 2.63.1
import pydpeet.io.device.parstat_2_63_3.formatter as parstat_2_63_3_formatter
import pydpeet.io.device.parstat_2_63_3.mapper as parstat_2_63_3_mapper
import pydpeet.io.device.parstat_2_63_3.reader as parstat_2_63_3_reader

# Safion Inspectrum Suite
# v1.9 (2023-10-18)
import pydpeet.io.device.safion_1_9.formatter as safion_1_9_formatter
import pydpeet.io.device.safion_1_9.mapper as safion_1_9_mapper
import pydpeet.io.device.safion_1_9.reader as safion_1_9_reader

# Zahner
# TODO: Add specs
import pydpeet.io.device.zahner.formatter as zahner_formatter
import pydpeet.io.device.zahner.mapper as zahner_mapper
import pydpeet.io.device.zahner.reader as zahner_reader

# Zahner (new)
# TODO: Add specs
import pydpeet.io.device.zahner_new.formatter as zahner_new_formatter
import pydpeet.io.device.zahner_new.mapper as zahner_new_mapper
import pydpeet.io.device.zahner_new.reader as zahner_new_reader


class _FiletypeIterable(type):
    """Metaclass that makes a filetype group iterable over its _ALL set."""

    # type annotation to _FiletypeIterable metaclass (forward reference via string) so mypy knows the attribute exists
    _ALL: "tuple[ReadConfig, ...]"

    def __iter__(cls):
        return iter(cls._ALL)

    def __len__(cls):
        return len(cls._ALL)


class ReadConfig(Enum):
    """
    Links device specific reader, formatter and mapper via enums.
    """

    Zahner_1 = auto()  # .txt / .csv
    Zahner_2 = auto()  # .txt / .csv
    Zahner_new_1 = auto()  # .txt / .csv
    Zahner_new_2 = auto()  # .txt / .csv
    Zahner_new_3 = auto()  # .txt / .csv
    Safion_1_9 = auto()  # .txt
    Parstat_2_63_3 = auto()  # .txt / .csv
    Neware_8_0_0_516 = auto()  # .xls / .xlsx
    Digatron_4_20_6_236 = auto()  # .csv
    Digatron_EIS_4_20_6_236 = auto()  # .csv
    BaSyTec_6_3_1_0 = auto()  # .txt
    BDF = auto()  # .bdf / .bdf.csv / .bdf.parquet / .bdf.gz
    Arbin_8_00_PV221201 = auto()  # .xls / .xlsx
    Arbin_4_23_PV090331 = auto()  # .xls / .xlsx
    Custom = auto()

    @nonmember
    class Excel(metaclass=_FiletypeIterable):
        """ReadConfigs for Excel files (.xls/.xlsx)."""

    @nonmember
    class Csv(metaclass=_FiletypeIterable):
        """ReadConfigs for CSV files."""

    @nonmember
    class Text(metaclass=_FiletypeIterable):
        """ReadConfigs for text files."""

    @classmethod
    def _from_string(cls, value: str) -> "ReadConfig":
        if not isinstance(value, str):
            raise TypeError("ReadConfig must be str or ReadConfig enum")

        key = value.strip().lower()

        aliases = {
            "arbin_4_23_pv090331": cls.Arbin_4_23_PV090331,
            "arbin_8_00_pv221201": cls.Arbin_8_00_PV221201,
            "basytec_6_3_1_0": cls.BaSyTec_6_3_1_0,
            "bdf": cls.BDF,
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
        except KeyError as k:
            known = ", ".join(aliases.keys())
            raise ValueError(f"Unknown config '{value}'. Known: {known}") from k

    @staticmethod
    def _exists(maybe_config: Any) -> bool:
        """
        Checks if a given configuration is a member of the ReadConfig enum.

        Args:
            maybe_config (any): The configuration to check, which can be an enum member or its value.

        Returns:
            bool: True if maybe_config is a member of the ReadConfig enum or its value; False otherwise.
        """
        try:
            return maybe_config in ReadConfig.__members__ or maybe_config.value in {
                read_config.value for read_config in ReadConfig
            }
        except Exception:
            return False

    @staticmethod
    def _not_exists(value: Any) -> bool:
        """
        Checks if a given configuration does not exist.

        Args:
            value (any): The configuration to check, which can be an enum member or its value.

        Returns:
            bool: True if maybe_config is not a member of the ReadConfig enum or its value; False otherwise.
        """
        return not ReadConfig._exists(value)


# filetype groupings for automatic selection
_EXTENSION_GROUPS: dict[str, Iterable[ReadConfig]] = {
    ".bdf": (ReadConfig.BDF,),
    ".gz": (ReadConfig.BDF,),
    ".parquet": (ReadConfig.BDF,),
    ".xls": ReadConfig.Excel,
    ".xlsx": ReadConfig.Excel,
    ".csv": ReadConfig.Csv,
    ".txt": ReadConfig.Text,
}

# order changes Priority, we choose Alphabetical order
ReadConfig.Excel._ALL = (
    ReadConfig.Arbin_4_23_PV090331,
    ReadConfig.Arbin_8_00_PV221201,
    ReadConfig.Neware_8_0_0_516,
)
ReadConfig.Csv._ALL = (
    ReadConfig.BDF,
    ReadConfig.Digatron_4_20_6_236,
    ReadConfig.Digatron_EIS_4_20_6_236,
)
ReadConfig.Text._ALL = (
    ReadConfig.BaSyTec_6_3_1_0,
    ReadConfig.Parstat_2_63_3,
    ReadConfig.Safion_1_9,
    ReadConfig.Zahner_1,
    ReadConfig.Zahner_2,
    ReadConfig.Zahner_new_1,
    ReadConfig.Zahner_new_2,
    ReadConfig.Zahner_new_3,
)


_STANDARD_COLUMNS = [
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
    "EIS_DC[A]",
]

_READER_CONFIGS: dict[ReadConfig, Callable[[str], DataFrame]] = {
    # zahner readers
    ReadConfig.Zahner_1: zahner_reader._to_dataframe,
    ReadConfig.Zahner_2: zahner_reader._to_dataframe,
    # zahner New readers
    ReadConfig.Zahner_new_1: zahner_new_reader._to_dataframe,
    ReadConfig.Zahner_new_2: zahner_new_reader._to_dataframe,
    ReadConfig.Zahner_new_3: zahner_new_reader._to_dataframe,
    # Other readers
    ReadConfig.Safion_1_9: safion_1_9_reader._to_dataframe,
    ReadConfig.Parstat_2_63_3: parstat_2_63_3_reader._to_dataframe,
    ReadConfig.Neware_8_0_0_516: neware_8_0_0_516_reader._to_dataframe,
    ReadConfig.Digatron_4_20_6_236: digatron_4_20_6_236_reader._to_dataframe,
    ReadConfig.Digatron_EIS_4_20_6_236: digatron_eis_4_20_6_236_reader._to_dataframe,
    ReadConfig.BaSyTec_6_3_1_0: basytec_6_3_1_0_reader._to_dataframe,
    ReadConfig.BDF: bdf_reader._to_dataframe,
    ReadConfig.Arbin_8_00_PV221201: arbin_8_00_PV221201_reader._to_dataframe,
    ReadConfig.Arbin_4_23_PV090331: arbin_4_23_PV090331_reader._to_dataframe,
}

_MAPPER_CONFIGS: dict[ReadConfig, tuple[dict[str, str], list[str]]] = {
    # zahner mappers
    ReadConfig.Zahner_1: (zahner_mapper._COLUMN_MAP_1, zahner_mapper._MISSING_REQUIRED_COLUMNS_1),
    ReadConfig.Zahner_2: (zahner_mapper._COLUMN_MAP_2, zahner_mapper._MISSING_REQUIRED_COLUMNS_2),
    # zahner New mappers
    ReadConfig.Zahner_new_1: (zahner_new_mapper._COLUMN_MAP_1, zahner_new_mapper._MISSING_REQUIRED_COLUMNS_1),
    ReadConfig.Zahner_new_2: (zahner_new_mapper._COLUMN_MAP_2, zahner_new_mapper._MISSING_REQUIRED_COLUMNS_2),
    ReadConfig.Zahner_new_3: (zahner_new_mapper._COLUMN_MAP_3, zahner_new_mapper._MISSING_REQUIRED_COLUMNS_3),
    # Other mappers
    ReadConfig.Safion_1_9: (safion_1_9_mapper._COLUMN_MAP, safion_1_9_mapper._MISSING_REQUIRED_COLUMNS),
    ReadConfig.Parstat_2_63_3: (parstat_2_63_3_mapper._COLUMN_MAP, parstat_2_63_3_mapper._MISSING_REQUIRED_COLUMNS),
    ReadConfig.Neware_8_0_0_516: (
        neware_8_0_0_516_mapper._COLUMN_MAP,
        neware_8_0_0_516_mapper._MISSING_REQUIRED_COLUMNS,
    ),
    ReadConfig.Digatron_4_20_6_236: (
        digatron_4_20_6_236_mapper._COLUMN_MAP,
        digatron_4_20_6_236_mapper._MISSING_REQUIRED_COLUMNS,
    ),
    ReadConfig.Digatron_EIS_4_20_6_236: (
        digatron_eis_4_20_6_236_mapper._COLUMN_MAP,
        digatron_eis_4_20_6_236_mapper._MISSING_REQUIRED_COLUMNS,
    ),
    ReadConfig.BaSyTec_6_3_1_0: (basytec_6_3_1_0_mapper._COLUMN_MAP, basytec_6_3_1_0_mapper._MISSING_REQUIRED_COLUMNS),
    ReadConfig.BDF: (bdf_mapper._COLUMN_MAP, bdf_mapper._MISSING_REQUIRED_COLUMNS),
    ReadConfig.Arbin_8_00_PV221201: (
        arbin_8_00_PV221201_mapper._COLUMN_MAP,
        arbin_8_00_PV221201_mapper._MISSING_REQUIRED_COLUMNS,
    ),
    ReadConfig.Arbin_4_23_PV090331: (
        arbin_4_23_PV090331_mapper._COLUMN_MAP,
        arbin_4_23_PV090331_mapper._MISSING_REQUIRED_COLUMNS,
    ),
}

_FORMATTER_CONFIGS: dict[ReadConfig, Callable[[DataFrame], DataFrame]] = {
    # zahner formatters
    ReadConfig.Zahner_1: zahner_formatter._get_data_into_format_zahner_1,
    ReadConfig.Zahner_2: zahner_formatter._get_data_into_format_zahner_2,
    # zahner New formatters
    ReadConfig.Zahner_new_1: zahner_new_formatter._get_data_into_format_zahner_1,
    ReadConfig.Zahner_new_2: zahner_new_formatter._get_data_into_format_zahner_2,
    ReadConfig.Zahner_new_3: zahner_new_formatter._get_data_into_format_zahner_3,
    # Other formatters
    ReadConfig.Safion_1_9: safion_1_9_formatter._get_data_into_format,
    ReadConfig.Parstat_2_63_3: parstat_2_63_3_formatter._get_data_into_format,
    ReadConfig.Neware_8_0_0_516: neware_8_0_0_516_formatter._get_data_into_format,
    ReadConfig.Digatron_4_20_6_236: digatron_4_20_6_236_formatter._get_data_into_format,
    ReadConfig.Digatron_EIS_4_20_6_236: digatron_eis_4_20_6_236_formatter._get_data_into_format,
    ReadConfig.BaSyTec_6_3_1_0: basytec_6_3_1_0_formatter._get_data_into_format,
    ReadConfig.BDF: bdf_formatter._get_data_into_format,
    ReadConfig.Arbin_8_00_PV221201: arbin_8_00_PV221201_formatter._get_data_into_format,
    ReadConfig.Arbin_4_23_PV090331: arbin_4_23_PV090331_formatter._get_data_into_format,
}


class DataOutputFiletype(Enum):
    """
    Enum representing the file types that can be used for output data.

    Attributes:
        parquet (DataOutputFiletype): Parquet file format.
        csv (DataOutputFiletype): CSV (Comma Separated Values) file format.
        xlsx (DataOutputFiletype): Excel (XLSX) file format.
    """

    parquet = auto()
    csv = auto()
    xlsx = auto()
