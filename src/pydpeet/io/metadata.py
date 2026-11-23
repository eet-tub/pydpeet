"""Storage and extraction of human-readable metadata in converted DataFrames.

PyDPEET stores the raw metadata string in the first row of the ``Meta_Data``
column and the name of the used :class:`ReadConfig` in the second row. All
other rows stay empty.

:func:`extract_metadata` reads those first two rows and turns the raw metadata
into a normalized :class:`Metadata` object. No caller needs to know which
cycler produced a file or which reader was selected.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Any

import pandas as pd

from pydpeet.io.configs.config import ReadConfig

__all__ = ["Metadata", "extract_metadata"]


@dataclass
class Metadata:
    """Normalized metadata of a single battery test."""

    name: str
    schedule: str | None = None
    channel: str | None = None
    cell_id: str | None = None
    cycler: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    raw_files: list[str] = field(default_factory=list)
    parquet_file: str = ""
    config: ReadConfig | None = None

    def dict_without_raw_files(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if key != "raw_files"}


def _match(pattern: str, string: str) -> str | None:
    match = re.search(pattern, string)
    if match is None:
        return None
    return match.group(1)


_TIMESTAMP_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%d.%m.%Y %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
)


def _parse_timestamp(time_str: str | None, fmt: str | None = None) -> datetime | None:
    if time_str is None:
        return None
    for candidate in (fmt,) if fmt is not None else _TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(time_str.strip(), candidate)
        except ValueError:
            continue
    return None


def _blank(name: str) -> Metadata:
    return Metadata(name=name)


def _extract_arbin(raw_file_name: str, metadata_str: str) -> Metadata:
    return Metadata(
        name=raw_file_name,
        schedule=_match(r"Process name: (\S+)\s", metadata_str),
        channel=_match(r"Sheet: (\S+)\s", metadata_str),
        start_time=_parse_timestamp(
            _match(r"Starting time.*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", metadata_str),
            "%Y-%m-%d %H:%M:%S",
        ),
        end_time=_parse_timestamp(
            _match(
                r"End Time.*\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.*(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
                metadata_str,
            ),
            "%Y-%m-%d %H:%M:%S",
        ),
    )


def _extract_basytec(raw_file_name: str, metadata_str: str) -> Metadata:
    channel1 = _match(r"Testchannel: (\S+)\s", metadata_str)
    # The CH number is the *second* group of this pattern; the first group is
    # the same value as channel1 (e.g. "1608 CH28" -> "1608" and "28").
    channel2 = _match(r"Testchannel: \S+ CH(\S+)\s", metadata_str)
    return Metadata(
        name=_match(r"Name of Test: (\S+)\s", metadata_str) or raw_file_name,
        schedule=_match(r"Testplan: (\S+)\s", metadata_str),
        channel=f"{channel1}.{channel2}" if channel1 and channel2 else channel1,
        cell_id=_match(r"Battery serial: (\S+)\s", metadata_str),
        start_time=_parse_timestamp(
            _match(r"Start of Test: (\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", metadata_str),
            "%d.%m.%Y %H:%M:%S",
        ),
        end_time=_parse_timestamp(
            _match(r"End of Test: (\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", metadata_str),
            "%d.%m.%Y %H:%M:%S",
        ),
    )


def _extract_digatron(raw_file_name: str, metadata_str: str) -> Metadata:
    return Metadata(
        name=raw_file_name,
        schedule=_match(r"Programm,([^\n]+)", metadata_str),
        channel=_match(r"Kreis,([^\n]+)", metadata_str),
        cell_id=_match(r"Batteriename,([^\n]+)", metadata_str),
        start_time=_parse_timestamp(
            _match(r"Startzeit,(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", metadata_str),
            "%d.%m.%Y %H:%M:%S",
        ),
        end_time=_parse_timestamp(
            _match(r"Stoppzeit,(\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2})", metadata_str),
            "%d.%m.%Y %H:%M:%S",
        ),
    )


def _extract_neware(raw_file_name: str, metadata_str: str) -> Metadata:
    return Metadata(
        name=raw_file_name,
        schedule=_match(r"^[^-]+-([^-]+)-", raw_file_name),
        channel=_match(r"^[^-]+-[^-]+-([^-]+-[^-]+)-", raw_file_name),
        cell_id=_match(r"^[^-]+-[^-]+-[^-]+-[^-]+-([^-._]+)", raw_file_name),
        start_time=_parse_timestamp(
            _match(r"Start time.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", metadata_str),
            "%Y-%m-%d %H:%M:%S",
        ),
        end_time=_parse_timestamp(
            _match(r"End time.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", metadata_str),
            "%Y-%m-%d %H:%M:%S",
        ),
    )


def _extract_ametek(raw_file_name: str, metadata_str: str) -> Metadata:
    return _blank(raw_file_name)


def _extract_safion(raw_file_name: str, metadata_str: str) -> Metadata:
    return Metadata(
        name=raw_file_name,
        cell_id=_match(r"battery name[^,]+,[^,]*,([^,\n]*)[,\n]", metadata_str),
        start_time=_parse_timestamp(
            _match(r"date,time.*\n(\d{4}/\d{2}/\d{2},\d{2}:\d{2}:\d{2})", metadata_str),
            "%Y/%m/%d,%H:%M:%S",
        ),
    )


def _extract_par(raw_file_name: str, metadata_str: str) -> Metadata:
    """Extract common ``Key=Value`` entries from VersaStudio PAR headers."""
    key_values: dict[str, str] = {}
    for line in metadata_str.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("<") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key_values[key.strip().lower()] = value.strip()

    def find(*keys: str) -> str | None:
        for key in keys:
            if key in key_values:
                return key_values[key]
        return None

    return Metadata(
        name=raw_file_name,
        schedule=find("testplan", "schedule", "process name", "program"),
        channel=find("channel", "testchannel"),
        cell_id=find("battery name", "cell name", "battery", "cell id"),
        start_time=_parse_timestamp(find("start time", "start")),
        end_time=_parse_timestamp(find("end time", "end")),
    )


_ExtractFn = Callable[[str, str], Metadata]

_EXTRACTORS: dict[ReadConfig, _ExtractFn] = {
    ReadConfig.Arbin_8_00_PV221201: _extract_arbin,
    ReadConfig.BaSyTec_6_3_1_0: _extract_basytec,
    ReadConfig.Digatron_4_20_6_236: _extract_digatron,
    ReadConfig.Digatron_EIS_4_20_6_236: _extract_digatron,
    ReadConfig.Neware_8_0_0_516: _extract_neware,
    ReadConfig.Parstat_2_63_3: _extract_ametek,
    ReadConfig.Safion_1_9: _extract_safion,
    ReadConfig.Par: _extract_par,
}


def _get_metadata_str(df: pd.DataFrame) -> tuple[str, str]:
    """Return ``(raw_metadata, config_name)`` from the first two ``Meta_Data`` rows."""
    if "Meta_Data" not in df.columns:
        logging.warning("no Meta_Data column, proceeding with empty metadata")
        return "", ""
    if df.empty:
        logging.warning("empty dataframe, proceeding with empty metadata")
        return "", ""
    metadata_str = df["Meta_Data"].iloc[0]  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportUnknownVariableType]
    config_name = df["Meta_Data"].iloc[1] if len(df) > 1 else None  # pyright: ignore[reportUnknownMemberType,reportUnknownArgumentType,reportUnknownVariableType]
    if pd.isna(metadata_str):
        metadata_str = ""
    if pd.isna(config_name):
        config_name = ""
    return str(metadata_str), str(config_name)


def extract_metadata(
    df: pd.DataFrame,
    file_name: str,
    *,
    raw_files: list[str] | None = None,
    parquet_file: str = "",
    cycler: str | None = None,
) -> Metadata:
    """Extract all metadata from an already converted PyDPEET DataFrame.

    The first two ``Meta_Data`` rows hold the raw metadata string and the name
    of the used ``ReadConfig``. The config name selects the device-specific
    extractor, so callers do not need to know the cycler or the configuration
    themselves.

    Parameters
    ----------
    df:
        DataFrame returned by :func:`pydpeet.io.read.read`.
    file_name:
        Name (usually the stem) of the raw main file, used as fallback name and
        by extractors that parse the file name (e.g. Neware).
    raw_files:
        Optional list of all raw files belonging to this test.
    parquet_file:
        Optional path of the converted parquet file.
    cycler:
        Optional cycler identifier supplied by the caller (e.g. from its
        directory). The extracted fields never depend on it.
    """
    metadata_str, config_name = _get_metadata_str(df)
    config = ReadConfig.__members__.get(config_name)

    if config is None:
        logging.warning("no known reader config in Meta_Data entry: %r", config_name)
        metadata = _blank(file_name)
    else:
        extractor = _EXTRACTORS.get(config)
        if extractor is None:
            logging.warning("no metadata extractor for config %s, fields left blank", config.name)
            metadata = _blank(file_name)
        else:
            metadata = extractor(file_name, metadata_str)

    metadata = replace(
        metadata,
        raw_files=list(raw_files) if raw_files is not None else [],
        parquet_file=parquet_file,
        cycler=cycler,
        config=config,
    )
    logging.info("extracted metadata: %s", metadata.dict_without_raw_files())
    return metadata
