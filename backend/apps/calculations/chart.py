from __future__ import annotations

from datetime import date, datetime, time
from datetime import timezone as datetime_timezone
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from apps.places.catalog import PlaceCandidate, PlaceNotFound, resolve_place

from .classical import classical_calculations
from .constants import GRAHAS
from .ephemeris import BodyPosition, CalculationSettings, EphemerisProvider, SwissEphemerisProvider
from .panchanga import panchanga_from_longitudes
from .shastra_audit import shastra_audit_payload
from .solar import gulika_segment_for_moment, solar_day, solar_day_payload
from .vargas import divisional_chart
from .vimshottari import vimshottari_payload

CALCULATION_VERSION = "mvp-0.1"


class ChartInputError(ValueError):
    pass


def build_birth_chart(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    birth_date = _required_date(data, "birth_date")
    birth_time = _required_time(data, "birth_time")
    place_name = _required_string(data, "place_name")
    place = _resolve_place_or_custom(data, place_name)

    timezone_name = str(data.get("timezone") or place.timezone).strip()
    latitude = _optional_float(data, "latitude", default=place.latitude, minimum=-90, maximum=90)
    longitude = _optional_float(data, "longitude", default=place.longitude, minimum=-180, maximum=180)

    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ChartInputError(f"Unknown timezone: {timezone_name}") from exc

    local_moment = datetime.combine(birth_date, birth_time, tzinfo=tz)
    settings = _calculation_settings(data)
    ephemeris = provider or SwissEphemerisProvider()
    positions = ephemeris.planet_positions(local_moment, GRAHAS, settings)
    ascendant = _calculate_ascendant(ephemeris, local_moment, latitude, longitude, settings)
    solar = solar_day(birth_date, latitude, longitude, tz)
    upagraha_context = _upagraha_context(ephemeris, local_moment, latitude, longitude, settings)

    payload = {
        "calculation_version": CALCULATION_VERSION,
        "settings": {
            "zodiac": settings.zodiac,
            "ayanamsa": settings.ayanamsa,
            "node_type": settings.node_type,
            "ephemeris": settings.ephemeris,
        },
        "birth": {
            "date": birth_date.isoformat(),
            "time": _time_isoformat(birth_time),
            "timezone": timezone_name,
            "utc_offset": _utc_offset(local_moment),
            "local_datetime": local_moment.isoformat(),
            "utc_datetime": local_moment.astimezone(datetime_timezone.utc).isoformat(),
        },
        "place": {
            "id": place.id,
            "name": place.name,
            "label": place.label,
            "country_code": place.country_code,
            "latitude": latitude,
            "longitude": longitude,
        },
        "solar_day": solar_day_payload(solar),
        "upagraha_context": upagraha_context,
        "grahas": [_position_payload(positions[body]) for body in GRAHAS if body in positions],
        "ascendant": _position_payload(ascendant) if ascendant else None,
        "houses": _whole_sign_houses(ascendant) if ascendant else [],
        "vargas": _varga_payload(positions, ascendant),
        "panchanga": {},
        "dashas": {},
    }
    if "Surya" in positions and "Chandra" in positions:
        payload["panchanga"] = panchanga_from_longitudes(
            positions["Surya"].longitude,
            positions["Chandra"].longitude,
            local_moment,
        )
    if "Chandra" in positions:
        payload["dashas"]["vimshottari"] = vimshottari_payload(
            positions["Chandra"].longitude,
            local_moment,
        )
    payload["classical"] = classical_calculations(payload)
    payload["shastra_audit"] = shastra_audit_payload()
    return payload


def _resolve_place_or_custom(data: dict[str, Any], place_name: str) -> PlaceCandidate:
    try:
        return resolve_place(place_name)
    except PlaceNotFound as exc:
        if not _has_custom_place_data(data):
            raise ChartInputError(str(exc)) from exc

    return PlaceCandidate(
        id="custom",
        name=place_name,
        admin_name="",
        country_code="",
        latitude=_optional_float(data, "latitude", default=0, minimum=-90, maximum=90),
        longitude=_optional_float(data, "longitude", default=0, minimum=-180, maximum=180),
        timezone=str(data["timezone"]).strip(),
    )


def _has_custom_place_data(data: dict[str, Any]) -> bool:
    return all(data.get(field) not in {None, ""} for field in ("timezone", "latitude", "longitude"))


def _calculation_settings(data: dict[str, Any]) -> CalculationSettings:
    try:
        return CalculationSettings(
            ayanamsa=str(data.get("ayanamsa") or "lahiri").strip().lower(),
            node_type=str(data.get("node_type") or "true").strip().lower(),
            ephemeris=str(data.get("ephemeris") or "swiss").strip().lower(),
        )
    except ValueError as exc:
        raise ChartInputError(str(exc)) from exc


def _utc_offset(moment: datetime) -> str:
    offset = moment.utcoffset()
    if offset is None:
        return ""
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    hours, minutes = divmod(total_minutes, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def _calculate_ascendant(
    provider: EphemerisProvider,
    local_moment: datetime,
    latitude: float,
    longitude: float,
    settings: CalculationSettings,
) -> BodyPosition | None:
    calculator = getattr(provider, "ascendant_position", None)
    if calculator is None:
        return None
    return calculator(local_moment, latitude, longitude, settings)


def _upagraha_context(
    provider: EphemerisProvider,
    local_moment: datetime,
    latitude: float,
    longitude: float,
    settings: CalculationSettings,
) -> dict[str, Any]:
    segment = gulika_segment_for_moment(local_moment, latitude, longitude)
    midpoint = datetime.fromisoformat(str(segment["midpoint"]))
    ascendant = _calculate_ascendant(provider, midpoint, latitude, longitude, settings)
    return {
        "gulika": segment,
        "gulika_ascendant": _position_payload(ascendant) if ascendant else None,
    }


def _whole_sign_houses(ascendant: BodyPosition) -> list[dict[str, Any]]:
    from .constants import RASHIS

    start = ascendant.placement.rashi_index
    return [
        {
            "house": house,
            "rashi_index": (start + house - 1) % len(RASHIS),
            "rashi": RASHIS[(start + house - 1) % len(RASHIS)],
        }
        for house in range(1, 13)
    ]


def _varga_payload(
    positions: dict[str, BodyPosition],
    ascendant: BodyPosition | None,
) -> dict[str, dict[str, object]]:
    return divisional_chart(
        {body: positions[body].longitude for body in GRAHAS if body in positions},
        ascendant_longitude=ascendant.longitude if ascendant else None,
    )


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
    return parsed.replace(microsecond=0)


def _time_isoformat(value: time) -> str:
    timespec = "seconds" if value.second else "minutes"
    return value.isoformat(timespec=timespec)


def _optional_float(
    data: dict[str, Any],
    field: str,
    default: float,
    minimum: float,
    maximum: float,
) -> float:
    if data.get(field) in {None, ""}:
        return default
    try:
        value = float(data[field])
    except (TypeError, ValueError) as exc:
        raise ChartInputError(f"{field} must be a number") from exc
    if value < minimum or value > maximum:
        raise ChartInputError(f"{field} must be between {minimum} and {maximum}")
    return value
