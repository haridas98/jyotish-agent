from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta
from datetime import timezone as datetime_timezone
from datetime import tzinfo
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from apps.places.catalog import PlaceCandidate, PlaceNotFound, resolve_place
from apps.places.geocoding import geocode_places

from .classical import DEBILITATION_DEGREES, EXALTATION_SIGNS, OWN_SIGNS, classical_calculations
from .constants import GRAHAS, RASHIS
from .ephemeris import BodyPosition, CalculationSettings, EphemerisProvider, SwissEphemerisProvider
from .panchanga import panchanga_from_longitudes
from .dasha_systems import extra_dasha_payload
from .shastra_audit import shastra_audit_payload
from .solar import gulika_segment_for_moment, solar_day, solar_day_payload
from .vargas import divisional_chart, varga_accuracy_contract
from .vimshottari import vimshottari_payload

CALCULATION_VERSION = "mvp-0.1"
TIMEZONE_OFFSET_RE = re.compile(r"^(?:UTC|GMT)?\s*([+-])\s*(\d{1,2})(?::?(\d{2}))?$", re.IGNORECASE)


class ChartInputError(ValueError):
    pass


def build_birth_chart(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    birth_date = _required_date(data, "birth_date")
    birth_time = _required_time(data, "birth_time")
    birth_time_accuracy = str(data.get("birth_time_accuracy") or "exact").strip().lower()
    place_name = _required_string(data, "place_name")
    place = _resolve_place_or_custom(data, place_name)

    timezone_name = str(data.get("timezone") or place.timezone).strip()
    latitude = _optional_float(data, "latitude", default=place.latitude, minimum=-90, maximum=90)
    longitude = _optional_float(data, "longitude", default=place.longitude, minimum=-180, maximum=180)

    tz, timezone_name, timezone_source = _timezone_from_input(timezone_name)

    local_moment = datetime.combine(birth_date, birth_time, tzinfo=tz)
    settings_data = dict(data)
    if timezone_source != "iana" and not str(settings_data.get("timezone_source") or "").strip():
        settings_data["timezone_source"] = timezone_source
    settings = _calculation_settings(settings_data)
    ephemeris = provider or SwissEphemerisProvider()
    ayanamsa_degrees = _ayanamsa_degrees(ephemeris, local_moment, settings)
    positions = ephemeris.planet_positions(local_moment, GRAHAS, settings)
    ascendant = _calculate_ascendant(ephemeris, local_moment, latitude, longitude, settings)
    house_cusps = _calculate_house_cusps(ephemeris, local_moment, latitude, longitude, settings)
    solar = solar_day(birth_date, latitude, longitude, tz, source=settings.sunrise_source)
    upagraha_context = _upagraha_context(ephemeris, local_moment, latitude, longitude, settings)
    special_lagna_context = (
        _special_lagna_context(ephemeris, solar.sunrise, settings)
        if settings.sunrise_source == "swiss_center_no_refraction"
        else {}
    )

    payload = {
        "calculation_version": CALCULATION_VERSION,
        "settings": {
            "zodiac": settings.zodiac,
            "calculation_model": settings.calculation_model,
            "ayanamsa": settings.ayanamsa,
            **({"ayanamsa_degrees": ayanamsa_degrees} if ayanamsa_degrees is not None else {}),
            "node_type": settings.node_type,
            "ephemeris": settings.ephemeris,
            "house_system": settings.house_system,
            "bhava_system": settings.bhava_system,
            "varga_scheme": settings.varga_scheme,
            "sunrise_source": settings.sunrise_source,
            "timezone_source": settings.timezone_source,
            "shadbala_profile": settings.shadbala_profile,
        },
        "birth": {
            "date": birth_date.isoformat(),
            "time": _time_isoformat(birth_time),
            "timezone": timezone_name,
            "utc_offset": _utc_offset(local_moment),
            "local_datetime": local_moment.isoformat(),
            "utc_datetime": local_moment.astimezone(datetime_timezone.utc).isoformat(),
            "time_accuracy": birth_time_accuracy,
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
        "special_lagna_context": special_lagna_context,
        "grahas": [_position_payload(positions[body]) for body in GRAHAS if body in positions],
        "ascendant": _position_payload(ascendant) if ascendant else None,
        "houses": _whole_sign_houses(ascendant) if ascendant else [],
        "house_cusps": house_cusps,
        "vargas": _varga_payload(positions, ascendant, settings.varga_scheme, birth_time_accuracy),
        "varga_accuracy": _varga_accuracy_payload(birth_time_accuracy),
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
        payload["panchanga"]["nakshatra"] = _nakshatra_payload(positions["Chandra"])
        payload["dashas"]["vimshottari"] = vimshottari_payload(
            positions["Chandra"].longitude,
            local_moment,
        )
        payload["dashas"]["extra"] = extra_dasha_payload(
            positions["Chandra"].longitude,
            local_moment,
        )
    payload["classical"] = classical_calculations(payload)
    payload["shastra_audit"] = shastra_audit_payload()
    return payload


def _timezone_from_input(value: str) -> tuple[tzinfo, str, str]:
    try:
        return ZoneInfo(value), value, "iana"
    except ZoneInfoNotFoundError as exc:
        offset = _fixed_offset_timezone(value)
        if offset is None:
            raise ChartInputError(f"Unknown timezone: {value}") from exc
        tz, label = offset
        return tz, label, "fixed_offset"


def _fixed_offset_timezone(value: str) -> tuple[tzinfo, str] | None:
    match = TIMEZONE_OFFSET_RE.match(value.strip())
    if not match:
        return None
    sign, raw_hours, raw_minutes = match.groups()
    hours = int(raw_hours)
    minutes = int(raw_minutes or "0")
    if hours > 14 or minutes > 59:
        return None
    total_minutes = hours * 60 + minutes
    if sign == "-":
        total_minutes = -total_minutes
    label = _offset_label(total_minutes)
    return datetime_timezone(timedelta(minutes=total_minutes), name=f"UTC{label}"), label


def _offset_label(total_minutes: int) -> str:
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    hours, minutes = divmod(total_minutes, 60)
    return f"{sign}{hours:02d}:{minutes:02d}"


def _resolve_place_or_custom(data: dict[str, Any], place_name: str) -> PlaceCandidate:
    if str(data.get("place_id") or "").strip() and _has_custom_place_data(data):
        return _custom_place_from_input(data, place_name)

    try:
        return resolve_place(place_name)
    except PlaceNotFound as exc:
        if _has_custom_place_data(data):
            return _custom_place_from_input(data, place_name)

        geocoded = _safe_geocode_place(place_name)
        if geocoded:
            return geocoded
        raise ChartInputError(str(exc)) from exc


def _custom_place_from_input(data: dict[str, Any], place_name: str) -> PlaceCandidate:
    name, admin_name, country_code = _parse_place_label(place_name)
    return PlaceCandidate(
        id=str(data.get("place_id") or "custom").strip(),
        name=name,
        admin_name=str(data.get("admin_name") or admin_name).strip(),
        country_code=str(data.get("country_code") or country_code).strip().upper(),
        latitude=_optional_float(data, "latitude", default=0, minimum=-90, maximum=90),
        longitude=_optional_float(data, "longitude", default=0, minimum=-180, maximum=180),
        timezone=str(data["timezone"]).strip(),
    )


def _safe_geocode_place(place_name: str) -> PlaceCandidate | None:
    try:
        return next(iter(geocode_places(place_name, limit=1)), None)
    except Exception:
        return None


def _parse_place_label(label: str) -> tuple[str, str, str]:
    parts = [part.strip() for part in label.split(",") if part.strip()]
    name = parts[0] if parts else label
    country_code = parts[-1].upper() if len(parts) >= 2 and len(parts[-1]) == 2 else ""
    admin_name = parts[1] if len(parts) >= 3 else ""
    return name, admin_name, country_code


def _has_custom_place_data(data: dict[str, Any]) -> bool:
    return all(data.get(field) not in {None, ""} for field in ("timezone", "latitude", "longitude"))


def _calculation_settings(data: dict[str, Any]) -> CalculationSettings:
    try:
        return CalculationSettings(
            zodiac=str(data.get("zodiac") or "sidereal").strip().lower(),
            calculation_model=str(
                data.get("calculation_model") or data.get("siddhanta_model") or "drik_siddhanta"
            )
            .strip()
            .lower(),
            ayanamsa=str(data.get("ayanamsa") or "lahiri").strip().lower(),
            node_type=str(data.get("node_type") or "true").strip().lower(),
            ephemeris=str(data.get("ephemeris") or "swiss").strip().lower(),
            house_system=str(data.get("house_system") or "whole_sign").strip().lower(),
            bhava_system=str(data.get("bhava_system") or "whole_sign").strip().lower(),
            varga_scheme=str(data.get("varga_scheme") or "parashara").strip().lower(),
            sunrise_source=str(data.get("sunrise_source") or "noaa").strip().lower(),
            timezone_source=str(data.get("timezone_source") or "iana").strip().lower(),
            shadbala_profile=str(data.get("shadbala_profile") or "bphs_classical").strip().lower(),
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


def _calculate_house_cusps(
    provider: EphemerisProvider,
    local_moment: datetime,
    latitude: float,
    longitude: float,
    settings: CalculationSettings,
) -> list[dict[str, Any]]:
    calculator = getattr(provider, "house_cusps", None)
    if not callable(calculator):
        return []
    try:
        return list(calculator(local_moment, latitude, longitude, settings))
    except (EphemerisUnavailable, NotImplementedError):
        return []


def _ayanamsa_degrees(
    provider: EphemerisProvider,
    local_moment: datetime,
    settings: CalculationSettings,
) -> float | None:
    calculator = getattr(provider, "ayanamsa_degrees", None)
    if calculator is None:
        return None
    value = calculator(local_moment, settings)
    return round(float(value), 9) if value is not None else None


def _upagraha_context(
    provider: EphemerisProvider,
    local_moment: datetime,
    latitude: float,
    longitude: float,
    settings: CalculationSettings,
) -> dict[str, Any]:
    segment = gulika_segment_for_moment(local_moment, latitude, longitude, source=settings.sunrise_source)
    starts_at = datetime.fromisoformat(str(segment["starts_at"]))
    midpoint = datetime.fromisoformat(str(segment["midpoint"]))
    midpoint_ascendant = _calculate_ascendant(provider, midpoint, latitude, longitude, settings)
    start_ascendant = _calculate_ascendant(provider, starts_at, latitude, longitude, settings)
    return {
        "gulika": segment,
        "split_gulika_maandi": settings.sunrise_source == "swiss_center_no_refraction",
        "gulika_start_ascendant": _position_payload(start_ascendant) if start_ascendant else None,
        "gulika_midpoint_ascendant": _position_payload(midpoint_ascendant) if midpoint_ascendant else None,
        "gulika_ascendant": _position_payload(midpoint_ascendant) if midpoint_ascendant else None,
    }


def _special_lagna_context(
    provider: EphemerisProvider,
    sunrise: datetime,
    settings: CalculationSettings,
) -> dict[str, Any]:
    try:
        positions = provider.planet_positions(sunrise, ["Surya"], settings)
    except Exception:
        return {}
    surya = positions.get("Surya")
    return {
        "sunrise": sunrise.isoformat(),
        "surya_at_sunrise": _position_payload(surya) if surya else None,
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
    varga_scheme: str,
    birth_time_accuracy: str,
) -> dict[str, dict[str, object]]:
    return divisional_chart(
        {body: positions[body].longitude for body in GRAHAS if body in positions},
        ascendant_longitude=ascendant.longitude if ascendant else None,
        scheme=varga_scheme,
        birth_time_accuracy=birth_time_accuracy,
    )


def _varga_accuracy_payload(birth_time_accuracy: str) -> dict[str, dict[str, str]]:
    return {"D60": varga_accuracy_contract("D60", birth_time_accuracy)}


def _nakshatra_payload(position: BodyPosition) -> dict[str, Any]:
    return {
        "name": position.placement.nakshatra,
        "index": position.placement.nakshatra_index,
        "pada": position.placement.pada,
    }


def _basic_dignity(position: BodyPosition) -> str:
    body = position.body
    rashi = position.placement.rashi
    if rashi in OWN_SIGNS.get(body, set()):
        return "own"
    if rashi == EXALTATION_SIGNS.get(body):
        return "exaltation"
    debilitation = DEBILITATION_DEGREES.get(body)
    if debilitation is not None and rashi == RASHIS[int(debilitation // 30) % len(RASHIS)]:
        return "debilitation"
    return "unknown"


def _position_payload(position: BodyPosition) -> dict[str, Any]:
    return {
        "body": position.body,
        "longitude": position.longitude,
        "latitude": position.latitude,
        "declination": position.declination,
        "distance_au": position.distance_au,
        "speed_longitude": position.speed_longitude,
        "retrograde": bool(position.speed_longitude is not None and position.speed_longitude < 0),
        "dignity": _basic_dignity(position),
        **({"mean_longitude": position.mean_longitude} if position.mean_longitude is not None else {}),
        **(
            {"seeghrocha_longitude": position.seeghrocha_longitude}
            if position.seeghrocha_longitude is not None
            else {}
        ),
        "ephemeris_engine": position.ephemeris_engine,
        "ephemeris_flags": position.ephemeris_flags,
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
