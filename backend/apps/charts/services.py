from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.utils.dateparse import parse_datetime

from apps.calculations.chart import CALCULATION_VERSION, ChartInputError, build_birth_chart
from apps.calculations.ephemeris import CalculationSettings, EphemerisProvider, EphemerisUnavailable
from apps.places.catalog import PlaceCandidate, PlaceNotFound, resolve_place
from apps.places.geocoding import geocode_places

from .models import BirthProfile, ChartCalculation, DashaPeriod, Place, PlanetPosition, VargaPlacement


class ChartProfileInputError(ValueError):
    pass


CALCULATION_SETTING_KEYS = (
    "zodiac",
    "calculation_model",
    "ayanamsa",
    "node_type",
    "ephemeris",
    "house_system",
    "bhava_system",
    "varga_scheme",
    "sunrise_source",
    "timezone_source",
    "shadbala_profile",
)


def create_birth_profile(user: AbstractBaseUser, data: dict[str, Any]) -> BirthProfile:
    display_name = _required_string(data, "display_name")
    birth_date = _required_date(data, "birth_date")
    birth_time = _optional_time(data, "birth_time")
    birth_time_accuracy = str(
        data.get("birth_time_accuracy") or BirthProfile.TimeAccuracy.EXACT,
    ).strip()
    if birth_time_accuracy not in BirthProfile.TimeAccuracy.values:
        raise ChartProfileInputError("birth_time_accuracy is invalid")

    place_name = _required_string(data, "place_name")
    catalog_place = _resolve_profile_place(data, place_name)

    place = sync_catalog_place(catalog_place)
    return BirthProfile.objects.create(
        user=user,
        display_name=display_name,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_time_accuracy=birth_time_accuracy,
        place=place,
        timezone_name=catalog_place.timezone,
        calculation_settings=_calculation_settings_snapshot(data),
        notes=str(data.get("notes", "")).strip(),
    )


def sync_catalog_place(candidate: PlaceCandidate) -> Place:
    defaults = {
        "name": candidate.name,
        "country_code": candidate.country_code,
        "latitude": _decimal(candidate.latitude),
        "longitude": _decimal(candidate.longitude),
        "timezone_name": candidate.timezone,
        "metadata": {
            "admin_name": candidate.admin_name,
            "label": candidate.label,
            "source": "curated_catalog",
        },
    }
    place, created = Place.objects.get_or_create(external_id=candidate.id, defaults=defaults)
    if created:
        return place

    changed_fields: list[str] = []
    for field, value in defaults.items():
        if getattr(place, field) != value:
            setattr(place, field, value)
            changed_fields.append(field)
    if changed_fields:
        place.save(update_fields=changed_fields)
    return place


def calculate_profile_chart(
    profile: BirthProfile,
    provider: EphemerisProvider | None = None,
) -> ChartCalculation:
    calculation = ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=_profile_input(profile),
    )

    try:
        result = build_birth_chart(calculation.input_snapshot, provider=provider)
    except (ChartInputError, EphemerisUnavailable, ValueError) as exc:
        calculation.status = ChartCalculation.Status.FAILED
        calculation.error = str(exc)
        calculation.save(update_fields=["status", "error", "updated_at"])
        return calculation

    calculation.result = result
    calculation.ayanamsa = str(result.get("settings", {}).get("ayanamsa") or calculation.ayanamsa)
    calculation.house_system = str(result.get("settings", {}).get("house_system") or calculation.house_system)
    calculation.status = ChartCalculation.Status.COMPLETE
    calculation.save(update_fields=["ayanamsa", "house_system", "result", "status", "updated_at"])
    _persist_result_rows(calculation, result)
    return calculation


def profile_payload(profile: BirthProfile) -> dict[str, Any]:
    latest_calculation = profile.calculations.order_by("-created_at").first()
    return {
        "id": profile.id,
        "display_name": profile.display_name,
        "birth_date": profile.birth_date.isoformat(),
        "birth_time": profile.birth_time.isoformat(timespec="minutes") if profile.birth_time else None,
        "birth_time_accuracy": profile.birth_time_accuracy,
        "timezone": profile.timezone_name,
        "calculation_settings": _profile_calculation_settings(profile),
        "place": place_payload(profile.place),
        "latest_calculation": latest_calculation_summary(latest_calculation)
        if latest_calculation
        else None,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }


def place_payload(place: Place) -> dict[str, Any]:
    return {
        "id": place.id,
        "external_id": place.external_id,
        "name": place.name,
        "label": place.metadata.get("label") or place.name,
        "country_code": place.country_code,
        "latitude": float(place.latitude),
        "longitude": float(place.longitude),
        "timezone": place.timezone_name,
    }


def calculation_payload(calculation: ChartCalculation) -> dict[str, Any]:
    return {
        "id": calculation.id,
        "profile_id": calculation.profile_id,
        "calculation_version": calculation.calculation_version,
        "ayanamsa": calculation.ayanamsa,
        "house_system": calculation.house_system,
        "status": calculation.status,
        "error": calculation.error,
        "result": calculation.result,
        "created_at": calculation.created_at.isoformat(),
        "updated_at": calculation.updated_at.isoformat(),
    }


def latest_calculation_summary(calculation: ChartCalculation) -> dict[str, Any]:
    result = calculation.result or {}
    return {
        "id": calculation.id,
        "status": calculation.status,
        "calculation_version": calculation.calculation_version,
        "graha_count": len(result.get("grahas", [])) if isinstance(result, dict) else 0,
        "created_at": calculation.created_at.isoformat(),
        "updated_at": calculation.updated_at.isoformat(),
    }


def _resolve_profile_place(data: dict[str, Any], place_name: str) -> PlaceCandidate:
    try:
        return resolve_place(place_name)
    except PlaceNotFound as exc:
        if all(data.get(field) not in {None, ""} for field in ("timezone", "latitude", "longitude")):
            return _custom_profile_place(data, place_name)

        geocoded = _safe_geocode_place(place_name)
        if geocoded:
            return geocoded
        raise ChartProfileInputError(str(exc)) from exc


def _custom_profile_place(data: dict[str, Any], place_name: str) -> PlaceCandidate:
    name, admin_name, country_code = _parse_place_label(place_name)
    return PlaceCandidate(
        id=str(data.get("place_id") or f"custom:{place_name}").strip(),
        name=name,
        admin_name=str(data.get("admin_name") or admin_name).strip(),
        country_code=str(data.get("country_code") or country_code).strip().upper(),
        latitude=_float_in_range(data, "latitude", -90, 90),
        longitude=_float_in_range(data, "longitude", -180, 180),
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


def _profile_input(profile: BirthProfile) -> dict[str, Any]:
    return {
        "birth_date": profile.birth_date.isoformat(),
        "birth_time": profile.birth_time.isoformat(timespec="minutes") if profile.birth_time else "",
        "place_name": profile.place.metadata.get("label") or profile.place.name,
        "timezone": profile.timezone_name,
        "latitude": float(profile.place.latitude),
        "longitude": float(profile.place.longitude),
        **_profile_calculation_settings(profile),
    }


def _profile_calculation_settings(profile: BirthProfile) -> dict[str, Any]:
    defaults = _calculation_settings_snapshot({})
    return {
        **defaults,
        **{key: value for key, value in (profile.calculation_settings or {}).items() if key in defaults},
    }


def _calculation_settings_snapshot(data: dict[str, Any]) -> dict[str, str]:
    try:
        settings = CalculationSettings(
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
        raise ChartProfileInputError(str(exc)) from exc

    return {key: getattr(settings, key) for key in CALCULATION_SETTING_KEYS}


def _persist_result_rows(calculation: ChartCalculation, result: dict[str, Any]) -> None:
    for graha in result.get("grahas", []):
        PlanetPosition.objects.create(
            calculation=calculation,
            graha=graha["body"],
            longitude=_decimal(graha["longitude"]),
            latitude=_optional_decimal(graha.get("latitude")),
            speed=_optional_decimal(graha.get("speed_longitude")),
            rashi=graha["rashi"],
            nakshatra=graha["nakshatra"],
            pada=int(graha["pada"]),
            metadata={
                "distance_au": graha.get("distance_au"),
                "rashi_index": graha.get("rashi_index"),
                "nakshatra_index": graha.get("nakshatra_index"),
            },
        )
    for varga_code, varga in result.get("vargas", {}).items():
        if not isinstance(varga, dict):
            continue
        for placement in varga.get("placements", []):
            if placement.get("body") == "Lagna":
                continue
            VargaPlacement.objects.create(
                calculation=calculation,
                varga=varga_code,
                graha=placement["body"],
                rashi=placement["rashi"],
                metadata={
                    "rashi_index": placement.get("rashi_index"),
                    "method": varga.get("method"),
                },
            )

    for period in result.get("dashas", {}).get("vimshottari", {}).get("mahadashas", []):
        starts_at = parse_datetime(period["starts_at"])
        ends_at = parse_datetime(period["ends_at"])
        if starts_at is None or ends_at is None:
            continue
        DashaPeriod.objects.create(
            calculation=calculation,
            system="vimshottari",
            level=int(period["level"]),
            lord=period["lord"],
            starts_at=starts_at,
            ends_at=ends_at,
            metadata={
                "duration_years": period["duration_years"],
                "sequence_index": period["sequence_index"],
                "year_length_days": result["dashas"]["vimshottari"]["year_length_days"],
            },
        )


def _required_string(data: dict[str, Any], field: str) -> str:
    value = str(data.get(field, "")).strip()
    if not value:
        raise ChartProfileInputError(f"{field} is required")
    return value


def _required_date(data: dict[str, Any], field: str) -> date:
    value = _required_string(data, field)
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ChartProfileInputError(f"{field} must be YYYY-MM-DD") from exc


def _optional_time(data: dict[str, Any], field: str) -> time | None:
    value = str(data.get(field, "")).strip()
    if not value:
        return None
    try:
        return time.fromisoformat(value).replace(second=0, microsecond=0)
    except ValueError as exc:
        raise ChartProfileInputError(f"{field} must be HH:MM") from exc


def _decimal(value: object) -> Decimal:
    return Decimal(str(value))


def _optional_decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    return _decimal(value)


def _float_in_range(data: dict[str, Any], field: str, minimum: float, maximum: float) -> float:
    try:
        value = float(data[field])
    except (TypeError, ValueError) as exc:
        raise ChartProfileInputError(f"{field} must be a number") from exc
    if value < minimum or value > maximum:
        raise ChartProfileInputError(f"{field} must be between {minimum} and {maximum}")
    return value
