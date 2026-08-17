"""
Readers for the VEBTAN battery database, which is internal to the PyDPEET maintainers.

These helpers are only useful together with JSON exports from that database and are
deliberately kept out of the public ``pydpeet`` API, so import them from this module
directly::

    from pydpeet.vebtan.read import read_db_config
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd

from pydpeet.io.utils.ext_path import _ExtPath
from pydpeet.vebtan.config import (
    DbBatteryCell,
    DbBatteryConfigEntry,
    DbBatteryType,
    db_config_into_battery_config,
)


def read_db_config(file_path: str) -> list[DbBatteryConfigEntry]:
    """
    Read a battery config JSON file (as exported from the battery db) into BatteryConfig objects.

    Parameters
    ----------
    file_path : str
        Path to the battery config JSON file.

    Returns
    -------
    list[DbBatteryConfigEntry]
        One ``(BatteryConfig, DbBatteryType)`` pair per entry in the JSON's
        "batteryCells" list. The BatteryConfig (see
        :func:`battery_config_wrapper`) is built from the linked cell/type data,
        the DbBatteryType is the raw db entry it was built from.
        Empty if "batteryCells" is empty.

    Raises
    ------
    ValueError
        If ``file_path`` does not point to an existing file, the JSON is
        missing required keys, a cell has no linked "batteryType", or a battery
        type's numeric fields cannot be parsed/verified
        (see :func:`db_config_into_battery_config`).
    """
    if _ExtPath._is_not_valid(file_path):
        raise ValueError("file_path must point to an existing file!")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    if "batteryCells" not in data:
        raise ValueError("Battery config JSON is missing required key 'batteryCells'!")

    entries: list[DbBatteryConfigEntry] = []
    for entry in data["batteryCells"]:
        if "batteryCell" not in entry:
            raise ValueError("Battery cell entry is missing required key 'batteryCell'!")

        cell_data = entry["batteryCell"]
        battery_cell = DbBatteryCell(id=cell_data["id"], name=cell_data["name"])

        type_data = entry.get("batteryType")
        if type_data is None:
            raise ValueError(f"Battery cell '{battery_cell.name}' has no linked 'batteryType'!")

        battery_type = DbBatteryType(
            id=type_data["id"],
            name=type_data["name"],
            manufacturer=type_data.get("manufacturer"),
            cathode=type_data.get("cathode"),
            anode=type_data.get("anode"),
            v_nom=type_data.get("vNom"),
            c_nom=type_data.get("cNom"),
            e_nom=type_data.get("eNom"),
            v_max=type_data.get("vMax"),
            v_min=type_data.get("vMin"),
            mass=type_data.get("mass"),
            dimensions=type_data.get("dimensions"),
            t_chg_min=type_data.get("tChgMin"),
            t_chg_max=type_data.get("tChgMax"),
            t_dis_min=type_data.get("tDisMin"),
            t_dis_max=type_data.get("tDisMax"),
            t_sto_min=type_data.get("tStoMin"),
            t_sto_max=type_data.get("tStoMax"),
        )

        entries.append((db_config_into_battery_config(battery_cell, battery_type), battery_type))

    return entries


def read_db_parquet_battery_config_pair(file_path: str) -> tuple[pd.DataFrame, list[DbBatteryConfigEntry]]:
    """
    Read a <x>.parquet / <x>.json pair, where the JSON file is the battery config for the parquet data.

    Only the basename (without extension) of ``file_path`` is used to locate the pair,
    so ``file_path`` may point to either the ``.parquet`` file, the ``.json`` file, or
    any other path sharing the same basename.

    Parameters
    ----------
    file_path : str
        Path used to derive the shared basename ``<x>``. The directory of
        ``file_path`` is searched for ``<x>.parquet`` and ``<x>.json``.

    Returns
    -------
    tuple[pandas.DataFrame, list[DbBatteryConfigEntry]]
        The parquet data and the corresponding
        ``(BatteryConfig, DbBatteryType)`` pairs.
    """
    directory = os.path.dirname(file_path)
    stem = Path(file_path).stem

    parquet_path = os.path.join(directory, f"{stem}.parquet")
    json_path = os.path.join(directory, f"{stem}.json")

    if _ExtPath._is_not_valid(parquet_path):
        raise ValueError(f"Parquet file not found: {parquet_path}")
    if _ExtPath._is_not_valid(json_path):
        raise ValueError(f"Battery config JSON file not found: {json_path}")

    df = pd.read_parquet(parquet_path)
    entries = read_db_config(json_path)

    return df, entries
