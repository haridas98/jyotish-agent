from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.utils.dateparse import parse_datetime

from apps.calculations.chart import CALCULATION_VERSION, ChartInputError, build_birth_chart
from apps.calculations.ephemeris import EphemerisProvider, EphemerisUnavailable
from apps.places.catalog import PlaceCandidate, PlaceNotFound, resolve_place

from .models import BirthProfile, ChartCalculation, DashaPeriod, Place, PlanetPosition, VargaPlacement


class ChartProfileInputError(ValueError):
    pass


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
    try:
        catalog_place = resolve_place(place_name)
    except PlaceNotFound as exc:
        raise ChartProfileInputError(str(exc)) from exc

    place = sync_catalog_place(catalog_place)
    return BirthProfile.objects.create(
        user=user,
        display_name=display_name,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_time_accuracy=birth_time_accuracy,
        place=place,
        timezone_name=catalog_place.timezone,
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
    calculation.status = ChartCalculation.Status.COMPLETE
    calculation.save(update_fields=["result", "status", "updated_at"])
    _persist_result_rows(calculation, result)
    return calculation


def profile_payload(profile: BirthProfile) -> dict[str, Any]:
    return {
        "id": profile.id,
        "display_name": profile.display_name,
        "birth_date": profile.birth_date.isoformat(),
        "birth_time": profile.birth_time.isoformat(timespec="minutes") if profile.birth_time else None,
        "birth_time_accuracy": profile.birth_time_accuracy,
        "timezone": profile.timezone_name,
        "place": place_payload(profile.place),
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


def _profile_input(profile: BirthProfile) -> dict[str, Any]:
    return {
        "birth_date": profile.birth_date.isoformat(),
        "birth_time": profile.birth_time.isoformat(timespec="minutes") if profile.birth_time else "",
        "place_name": profile.place.metadata.get("label") or profile.place.name,
        "timezone": profile.timezone_name,
        "latitude": float(profile.place.latitude),
        "longitude": float(profile.place.longitude),
    }


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
        VargaPlacement.objects.create(
            calculation=calculation,
            varga="D9",
            graha=graha["body"],
            rashi=graha["navamsa"],
            metadata={"navamsa_index": graha.get("navamsa_index")},
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
