from __future__ import annotations

from datetime import date, datetime, time
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .constants import GRAHAS
from .ephemeris import BodyPosition, CalculationSettings, EphemerisProvider, SwissEphemerisProvider

CALCULATION_VERSION = "mvp-0.1"


class ChartInputError(ValueError):
    pass


def build_birth_chart(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    birth_date = _required_date(data, "birth_date")
    birth_time = _required_time(data, "birth_time")
    timezone_name = _required_string(data, "timezone")
    place_name = _required_string(data, "place_name")
    latitude = _required_float(data, "latitude", minimum=-90, maximum=90)
    longitude = _required_float(data, "longitude", minimum=-180, maximum=180)

    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ChartInputError(f"Unknown timezone: {timezone_name}") from exc

    local_moment = datetime.combine(birth_date, birth_time, tzinfo=tz)
    settings = CalculationSettings()
    ephemeris = provider or SwissEphemerisProvider()
    positions = ephemeris.planet_positions(local_moment, GRAHAS, settings)

    return {
        "calculation_version": CALCULATION_VERSION,
        "settings": {
            "zodiac": settings.zodiac,
            "ayanamsa": settings.ayanamsa,
            "node_type": settings.node_type,
            "ephemeris": settings.ephemeris,
        },
        "birth": {
            "date": birth_date.isoformat(),
            "time": birth_time.isoformat(timespec="minutes"),
            "timezone": timezone_name,
            "local_datetime": local_moment.isoformat(),
            "utc_datetime": local_moment.astimezone(ZoneInfo("UTC")).isoformat(),
        },
        "place": {
            "name": place_name,
            "latitude": latitude,
            "longitude": longitude,
        },
        "grahas": [_position_payload(positions[body]) for body in GRAHAS if body in positions],
    }


def _position_payload(position: BodyPosition) -> dict[str, Any]:
    return {
        "body": position.body,
        "longitude": position.longitude,
        "latitude": position.latitude,
        "distance_au": position.distance_au,
        "speed_longitude": position.speed_longitude,
        "rashi": position.placement.rashi,
        "rashi_index": position.placement.rashi_index,
        "nakshatra": position.placement.nakshatra,
        "nakshatra_index": position.placement.nakshatra_index,
        "pada": position.placement.pada,
        "navamsa": position.placement.navamsa,
        "navamsa_index": position.placement.navamsa_index,
    }


def _required_string(data: dict[str, Any], field: str) -> str:
    value = str(data.get(field, "")).strip()
    if not value:
        raise ChartInputError(f"{field} is required")
    return value


def _required_date(data: dict[str, Any], field: str) -> date:
    value = _required_string(data, field)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ChartInputError(f"{field} must be YYYY-MM-DD") from exc


def _required_time(data: dict[str, Any], field: str) -> time:
    value = _required_string(data, field)
    try:
        parsed = time.fromisoformat(value)
    except ValueError as exc:
        raise ChartInputError(f"{field} must be HH:MM") from exc
    return parsed.replace(second=0, microsecond=0)


def _required_float(
    data: dict[str, Any],
    field: str,
    minimum: float,
    maximum: float,
) -> float:
    if data.get(field) in {None, ""}:
        raise ChartInputError(f"{field} is required")
    try:
        value = float(data[field])
    except (TypeError, ValueError) as exc:
        raise ChartInputError(f"{field} must be a number") from exc
    if value < minimum or value > maximum:
        raise ChartInputError(f"{field} must be between {minimum} and {maximum}")
    return value
