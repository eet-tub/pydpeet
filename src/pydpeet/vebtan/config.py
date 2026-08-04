"""
Raw record types for the VEBTAN battery database, and their mapping onto BatteryConfig.

The ``Db`` prefix distinguishes these raw database records from the analysis-side
BatteryConfig they are translated into by :func:`db_config_into_battery_config`.
See :mod:`pydpeet.vebtan.read` for how these are populated.
"""

from dataclasses import dataclass
from typing import TypeAlias

from pydpeet.process.analyze.configs.battery_config import _BatteryConfigClass, battery_config_wrapper


@dataclass
class DbBatteryCell:
    id: int
    name: str


@dataclass
class DbBatteryBatch:
    id: int
    name: str


@dataclass
class DbBatteryType:
    id: int
    name: str
    manufacturer: int | None
    cathode: str | None
    anode: str | None
    v_nom: str | None
    c_nom: str | None
    e_nom: str | None
    v_max: str | None
    v_min: str | None
    mass: str | None
    dimensions: str | None
    t_chg_min: str | None
    t_chg_max: str | None
    t_dis_min: str | None
    t_dis_max: str | None
    t_sto_min: str | None
    t_sto_max: str | None


# One parsed battery config together with the raw db battery type it was built from.
# The raw type carries the fields (manufacturer, cathode, anode, mass, dimensions, ...)
# that have no equivalent in _BatteryConfigClass and would otherwise be lost.
DbBatteryConfigEntry: TypeAlias = tuple[_BatteryConfigClass, DbBatteryType]


def _parse_float(value: str, field_name: str, cell_name: str) -> float:
    """Parse a numeric string from the battery db, raising a clear error on invalid data."""
    try:
        return float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Battery cell '{cell_name}': could not parse '{field_name}' value {value!r} as float") from e


def _parse_optional_float(value: str | None, field_name: str, cell_name: str) -> float | None:
    if value is None:
        return None
    return _parse_float(value, field_name, cell_name)


def _parse_required_float(value: str | None, field_name: str, cell_name: str) -> float:
    if value is None:
        raise ValueError(f"Battery cell '{cell_name}': required field '{field_name}' must not be null")
    return _parse_float(value, field_name, cell_name)


def db_config_into_battery_config(battery_cell: DbBatteryCell, battery_type: DbBatteryType) -> _BatteryConfigClass:
    """
    Build an (existing-format) BatteryConfig from raw battery db cell/type data.

    Parameters
    ----------
    battery_cell : DbBatteryCell
        The linked battery cell, used for ``cell_name``.
    battery_type : DbBatteryType
        The linked battery type. Its numeric fields (``cNom``, ``vMax``, ``vMin``)
        are parsed to floats and mapped onto ``c_ref``, ``max_voltage`` and
        ``min_voltage``.

        ``vMax`` and ``vMin`` are required: they map onto non-optional
        BatteryConfig fields that the analyze functions use in arithmetic.
        ``cNom`` may be null, since a ``c_ref`` of ``None`` is handled downstream
        by falling back to the first valid measured capacity.

    Returns
    -------
    _BatteryConfigClass
        A BatteryConfig instance built via :func:`battery_config_wrapper`.

    Raises
    ------
    ValueError
        If ``vMax`` or ``vMin`` is null, if a numeric field cannot be parsed as
        a float, or if ``min_voltage`` is not lower than ``max_voltage``.
    """
    max_voltage = _parse_required_float(battery_type.v_max, "vMax", battery_cell.name)
    min_voltage = _parse_required_float(battery_type.v_min, "vMin", battery_cell.name)

    if min_voltage >= max_voltage:
        raise ValueError(
            f"Battery cell '{battery_cell.name}': min_voltage ({min_voltage}) "
            f"must be lower than max_voltage ({max_voltage})"
        )

    return battery_config_wrapper(
        cell_name=battery_cell.name,
        c_ref=_parse_optional_float(battery_type.c_nom, "cNom", battery_cell.name),
        max_voltage=max_voltage,
        min_voltage=min_voltage,
    )
