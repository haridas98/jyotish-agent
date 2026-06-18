from __future__ import annotations

from datetime import date, time
from decimal import Decimal
from typing import Any

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import OuterRef, Subquery
from django.utils.dateparse import parse_datetime

from apps.calculations.chart import CALCULATION_VERSION, ChartInputError, build_birth_chart
from apps.calculations.ephemeris import CalculationSettings, EphemerisProvider, EphemerisUnavailable
from apps.places.catalog import PlaceCandidate, PlaceNotFound, resolve_place
from apps.places.geocoding import geocode_places

from .models import (
    BirthProfile,
    BirthProfileRelationship,
    ChartRelationship,
    ChartCalculation,
    DashaPeriod,
    Place,
    PlanetPosition,
    VargaPlacement,
)
from .relationship_contract import get_relationship_type_contract, is_known_role


class ChartProfileInputError(ValueError):
    pass


class ChartRelationshipConflict(ValueError):
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

_LATEST_CALCULATION_SENTINEL = object()


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
    is_self_profile = _optional_bool(data.get("is_self_profile"))
    profile = BirthProfile.objects.create(
        user=user,
        display_name=display_name,
        birth_date=birth_date,
        birth_time=birth_time,
        birth_time_accuracy=birth_time_accuracy,
        gender=_optional_gender(data.get("gender")),
        place=place,
        timezone_name=catalog_place.timezone,
        calculation_settings=_calculation_settings_snapshot(data),
        is_self_profile=is_self_profile,
        notes=str(data.get("notes", "")).strip(),
    )
    if is_self_profile:
        BirthProfile.objects.filter(user=user, is_self_profile=True).exclude(id=profile.id).update(is_self_profile=False)
    return profile


def update_birth_profile_flags(profile: BirthProfile, data: dict[str, Any]) -> BirthProfile:
    changed_fields: set[str] = set()

    if "display_name" in data:
        profile.display_name = _required_string(data, "display_name")
        changed_fields.add("display_name")
    if "birth_date" in data:
        profile.birth_date = _required_date(data, "birth_date")
        changed_fields.add("birth_date")
    if "birth_time" in data:
        profile.birth_time = _optional_time(data, "birth_time")
        changed_fields.add("birth_time")
    if "birth_time_accuracy" in data:
        birth_time_accuracy = str(data.get("birth_time_accuracy") or BirthProfile.TimeAccuracy.EXACT).strip()
        if birth_time_accuracy not in BirthProfile.TimeAccuracy.values:
            raise ChartProfileInputError("birth_time_accuracy is invalid")
        profile.birth_time_accuracy = birth_time_accuracy
        changed_fields.add("birth_time_accuracy")
    if "gender" in data:
        profile.gender = _optional_gender(data.get("gender"))
        changed_fields.add("gender")
    if "place_name" in data:
        place_name = _required_string(data, "place_name")
        catalog_place = _resolve_profile_place(data, place_name)
        profile.place = sync_catalog_place(catalog_place)
        profile.timezone_name = catalog_place.timezone
        changed_fields.update({"place", "timezone_name"})
    if "notes" in data:
        profile.notes = str(data.get("notes") or "").strip()
        changed_fields.add("notes")

    calculation_settings = _calculation_settings_snapshot(data)
    if any(key in data for key in CALCULATION_SETTING_KEYS):
        profile.calculation_settings = calculation_settings
        changed_fields.add("calculation_settings")

    if "is_self_profile" not in data and not changed_fields:
        return profile

    if "is_self_profile" in data:
        is_self_profile = _optional_bool(data.get("is_self_profile"))
        if is_self_profile:
            BirthProfile.objects.filter(user=profile.user, is_self_profile=True).exclude(id=profile.id).update(is_self_profile=False)
        profile.is_self_profile = is_self_profile
        changed_fields.add("is_self_profile")

    profile.save(update_fields=[*changed_fields, "updated_at"])
    return profile


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
    *,
    reuse_existing: bool = False,
) -> ChartCalculation:
    input_snapshot = _profile_input(profile)
    if reuse_existing:
        existing = (
            ChartCalculation.objects.filter(
                profile=profile,
                calculation_version=CALCULATION_VERSION,
                status=ChartCalculation.Status.COMPLETE,
                input_snapshot=input_snapshot,
            )
            .order_by("-created_at", "-id")
            .first()
        )
        if existing is not None:
            setattr(existing, "_jyotish_reused", True)
            return existing

    calculation = ChartCalculation.objects.create(
        profile=profile,
        calculation_version=CALCULATION_VERSION,
        input_snapshot=input_snapshot,
    )
    setattr(calculation, "_jyotish_reused", False)

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


def profiles_payload(profiles: list[BirthProfile]) -> list[dict[str, Any]]:
    if not profiles:
        return []
    latest_id_subquery = (
        ChartCalculation.objects.filter(profile_id=OuterRef("pk"))
        .order_by("-created_at", "-id")
        .values("id")[:1]
    )
    latest_ids = [
        calculation_id
        for calculation_id in BirthProfile.objects.filter(id__in=[profile.id for profile in profiles])
        .annotate(latest_calculation_id=Subquery(latest_id_subquery))
        .values_list("latest_calculation_id", flat=True)
        if calculation_id is not None
    ]
    calculations = ChartCalculation.objects.filter(id__in=latest_ids).defer("input_snapshot", "result")
    by_profile_id = {calculation.profile_id: calculation for calculation in calculations}
    return [
        profile_payload(profile, latest_calculation=by_profile_id.get(profile.id))
        for profile in profiles
    ]


def profile_payload(profile: BirthProfile, *, latest_calculation: ChartCalculation | object = _LATEST_CALCULATION_SENTINEL) -> dict[str, Any]:
    if latest_calculation is _LATEST_CALCULATION_SENTINEL:
        latest_calculation = profile.calculations.order_by("-created_at", "-id").first()
    return {
        "id": profile.id,
        "display_name": profile.display_name,
        "birth_date": profile.birth_date.isoformat(),
        "birth_time": profile.birth_time.isoformat(timespec="minutes") if profile.birth_time else None,
        "birth_time_accuracy": profile.birth_time_accuracy,
        "gender": profile.gender,
        "timezone": profile.timezone_name,
        "is_self_profile": profile.is_self_profile,
        "notes": profile.notes,
        "calculation_settings": _profile_calculation_settings(profile),
        "place": place_payload(profile.place),
        "latest_calculation": latest_calculation_summary(latest_calculation)
        if isinstance(latest_calculation, ChartCalculation)
        else None,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }


def profile_relationship_payload(relationship: BirthProfileRelationship) -> dict[str, Any]:
    return {
        "id": relationship.id,
        "user": {
            "id": relationship.user_id,
            "username": relationship.user.username,
        }
        if getattr(relationship, "user", None)
        else None,
        "profile_id": relationship.profile_id,
        "related_profile_id": relationship.related_profile_id,
        "profile": _relationship_profile_summary(relationship.profile)
        if getattr(relationship, "profile", None)
        else None,
        "related_profile": _relationship_profile_summary(relationship.related_profile)
        if getattr(relationship, "related_profile", None)
        else None,
        "role": relationship.role,
        "link_status": relationship.link_status,
        "requested_user": {
            "id": relationship.requested_user_id,
            "username": relationship.requested_user.username,
        }
        if relationship.requested_user_id and relationship.requested_user
        else None,
        "notes": relationship.notes,
        "metadata": relationship.metadata,
        "created_at": relationship.created_at.isoformat(),
        "updated_at": relationship.updated_at.isoformat(),
    }


def _relationship_profile_summary(profile: BirthProfile) -> dict[str, Any]:
    return {
        "id": profile.id,
        "display_name": profile.display_name,
        "birth_date": profile.birth_date.isoformat(),
        "place_label": profile.place.metadata.get("label") or profile.place.name,
    }


def chart_relationship_payload(relationship: ChartRelationship) -> dict[str, Any]:
    return {
        "id": relationship.id,
        "chart_a_id": relationship.chart_a_id,
        "chart_b_id": relationship.chart_b_id,
        "chart_a": _relationship_profile_summary(relationship.chart_a)
        if getattr(relationship, "chart_a", None)
        else None,
        "chart_b": _relationship_profile_summary(relationship.chart_b)
        if getattr(relationship, "chart_b", None)
        else None,
        "relationship_type_id": relationship.relationship_type_id,
        "role_a_id": relationship.role_a_id,
        "role_b_id": relationship.role_b_id,
        "pair_key": relationship.pair_key,
        "notes": relationship.notes,
        "created_at": relationship.created_at.isoformat(),
        "updated_at": relationship.updated_at.isoformat(),
    }


def list_chart_relationships(
    user: AbstractBaseUser,
    *,
    chart_id: int | None = None,
    relationship_type_id: str | None = None,
) -> list[ChartRelationship]:
    queryset = ChartRelationship.objects.filter(owner_user=user).select_related(
        "chart_a",
        "chart_b",
        "chart_a__place",
        "chart_b__place",
    )
    if chart_id is not None:
        queryset = queryset.filter(models.Q(chart_a_id=chart_id) | models.Q(chart_b_id=chart_id))
    if relationship_type_id:
        queryset = queryset.filter(relationship_type_id=relationship_type_id)
    return list(queryset.order_by("-updated_at"))


def create_chart_relationship(user: AbstractBaseUser, data: dict[str, Any]) -> ChartRelationship:
    return _save_chart_relationship(user, data=data, existing=None)


def update_chart_relationship(
    user: AbstractBaseUser,
    relationship: ChartRelationship,
    data: dict[str, Any],
) -> ChartRelationship:
    return _save_chart_relationship(user, data=data, existing=relationship)


def _save_chart_relationship(
    user: AbstractBaseUser,
    *,
    data: dict[str, Any],
    existing: ChartRelationship | None,
) -> ChartRelationship:
    chart_a_id = _required_int(data, "chart_a_id")
    chart_b_id = _required_int(data, "chart_b_id")
    if chart_a_id == chart_b_id:
        raise ChartProfileInputError("chart_b_id must differ from chart_a_id")

    chart_a = BirthProfile.objects.get(id=chart_a_id, user=user)
    chart_b = BirthProfile.objects.get(id=chart_b_id, user=user)
    relationship_type_id = str(data.get("relationship_type_id") or "").strip()
    role_a_id = str(data.get("role_a_id") or "").strip()
    role_b_id = str(data.get("role_b_id") or "").strip()
    notes = str(data.get("notes") or "").strip()
    if len(notes) > 5000:
        raise ChartProfileInputError("notes is too long")

    _validate_relationship_contract(relationship_type_id, role_a_id, role_b_id)
    pair_key = relationship_pair_key(chart_a_id, chart_b_id)
    duplicate = ChartRelationship.objects.filter(
        owner_user=user,
        relationship_type_id=relationship_type_id,
        pair_key=pair_key,
    )
    if existing is not None:
        duplicate = duplicate.exclude(id=existing.id)
    if duplicate.exists():
        raise ChartRelationshipConflict("relationship already exists")

    relationship = existing or ChartRelationship(owner_user=user)
    relationship.chart_a = chart_a
    relationship.chart_b = chart_b
    relationship.relationship_type_id = relationship_type_id
    relationship.role_a_id = role_a_id
    relationship.role_b_id = role_b_id
    relationship.pair_key = pair_key
    relationship.notes = notes
    relationship.save()
    return relationship


def relationship_pair_key(chart_a_id: int, chart_b_id: int) -> str:
    low, high = sorted((int(chart_a_id), int(chart_b_id)))
    return f"{low}:{high}"


def _validate_relationship_contract(relationship_type_id: str, role_a_id: str, role_b_id: str) -> None:
    relationship_type = get_relationship_type_contract(relationship_type_id)
    if relationship_type is None:
        raise ChartProfileInputError("relationship_type_id is invalid")
    if relationship_type.get("status") != "active":
        raise ChartProfileInputError("relationship_type_id is not available")
    if not is_known_role(role_a_id) or not is_known_role(role_b_id):
        raise ChartProfileInputError("role is invalid")
    if role_a_id != relationship_type["roleA"] or role_b_id != relationship_type["roleB"]:
        raise ChartProfileInputError("roles do not match relationship_type_id")


def list_profile_relationships(user: AbstractBaseUser) -> list[BirthProfileRelationship]:
    return list(
        BirthProfileRelationship.objects.filter(user=user)
        .select_related("user", "profile", "related_profile", "requested_user", "profile__place", "related_profile__place")
        .order_by("-updated_at")
    )


def list_incoming_profile_relationship_requests(user: AbstractBaseUser) -> list[BirthProfileRelationship]:
    return list(
        BirthProfileRelationship.objects.filter(
            requested_user=user,
            link_status=BirthProfileRelationship.LinkStatus.REQUESTED,
        )
        .select_related("user", "profile", "related_profile", "requested_user", "profile__place", "related_profile__place")
        .order_by("-updated_at")
    )


def upsert_profile_relationship(user: AbstractBaseUser, data: dict[str, Any]) -> BirthProfileRelationship:
    profile_id = _required_int(data, "profile_id")
    related_profile_id = _required_int(data, "related_profile_id")
    if profile_id == related_profile_id:
        raise ChartProfileInputError("related_profile_id must differ from profile_id")

    profile = BirthProfile.objects.get(id=profile_id, user=user)
    related_profile = BirthProfile.objects.get(id=related_profile_id, user=user)
    role = str(data.get("role") or BirthProfileRelationship.Role.PARTNER).strip()
    if role not in BirthProfileRelationship.Role.values:
        raise ChartProfileInputError("role is invalid")

    requested_user = _requested_user_from_data(data)
    link_status = (
        BirthProfileRelationship.LinkStatus.REQUESTED
        if requested_user
        else str(data.get("link_status") or BirthProfileRelationship.LinkStatus.PRIVATE).strip()
    )
    if link_status not in BirthProfileRelationship.LinkStatus.values:
        raise ChartProfileInputError("link_status is invalid")
    if link_status != BirthProfileRelationship.LinkStatus.PRIVATE and requested_user is None:
        raise ChartProfileInputError("requested_user is required for non-private links")
    if requested_user is not None and requested_user.id == user.id:
        raise ChartProfileInputError("requested_user must be another registered user")
    if requested_user is not None and BirthProfileRelationship.objects.filter(
        user=user,
        requested_user=requested_user,
        link_status=BirthProfileRelationship.LinkStatus.BLOCKED,
    ).exists():
        raise ChartProfileInputError("relationship request was blocked by this user")

    relationship, _ = BirthProfileRelationship.objects.update_or_create(
        user=user,
        profile=profile,
        related_profile=related_profile,
        defaults={
            "role": role,
            "link_status": link_status,
            "requested_user": requested_user,
            "notes": str(data.get("notes") or "").strip(),
            "metadata": data.get("metadata") if isinstance(data.get("metadata"), dict) else {},
        },
    )
    return relationship


def update_incoming_profile_relationship_request(
    user: AbstractBaseUser,
    relationship_id: int,
    action: str,
    data: dict[str, Any] | None = None,
) -> BirthProfileRelationship:
    data = data or {}
    relationship = BirthProfileRelationship.objects.select_related(
        "user",
        "profile",
        "profile__place",
        "related_profile",
        "related_profile__place",
        "requested_user",
    ).get(
        id=relationship_id,
        requested_user=user,
        link_status=BirthProfileRelationship.LinkStatus.REQUESTED,
    )
    action_statuses = {
        "accept": BirthProfileRelationship.LinkStatus.ACCEPTED,
        "decline": BirthProfileRelationship.LinkStatus.DECLINED,
        "block": BirthProfileRelationship.LinkStatus.BLOCKED,
    }
    status = action_statuses.get(action)
    if not status:
        raise ChartProfileInputError("action must be accept, decline, or block")
    if status == BirthProfileRelationship.LinkStatus.ACCEPTED:
        accepted_profile_id = _required_int(data, "accepted_profile_id")
        try:
            accepted_profile = BirthProfile.objects.get(id=accepted_profile_id, user=user)
        except BirthProfile.DoesNotExist as exc:
            raise ChartProfileInputError("accepted_profile_id must belong to the recipient user") from exc
        relationship.related_profile = accepted_profile
        relationship.metadata = {
            **(relationship.metadata or {}),
            "accepted_profile_id": accepted_profile.id,
            "accepted_profile_display_name": accepted_profile.display_name,
        }
        BirthProfileRelationship.objects.update_or_create(
            user=user,
            profile=accepted_profile,
            related_profile=relationship.profile,
            defaults={
                "role": relationship.role,
                "link_status": BirthProfileRelationship.LinkStatus.ACCEPTED,
                "requested_user": relationship.user,
                "notes": relationship.notes,
                "metadata": {
                    "accepted_from_relationship_id": relationship.id,
                    "requested_by_user_id": relationship.user_id,
                },
            },
        )
    relationship.link_status = status
    relationship.save(update_fields=["related_profile", "link_status", "metadata", "updated_at"])
    return relationship


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
        "reused": bool(getattr(calculation, "_jyotish_reused", False)),
        "error": calculation.error,
        "result": calculation.result,
        "created_at": calculation.created_at.isoformat(),
        "updated_at": calculation.updated_at.isoformat(),
    }


def latest_calculation_summary(calculation: ChartCalculation) -> dict[str, Any]:
    return {
        "id": calculation.id,
        "status": calculation.status,
        "calculation_version": calculation.calculation_version,
        "graha_count": calculation.graha_count,
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
        "place_id": profile.place.external_id or str(profile.place.id),
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


def _required_int(data: dict[str, Any], field: str) -> int:
    try:
        value = int(data.get(field))
    except (TypeError, ValueError) as exc:
        raise ChartProfileInputError(f"{field} is required") from exc
    if value <= 0:
        raise ChartProfileInputError(f"{field} is required")
    return value


def _requested_user_from_data(data: dict[str, Any]) -> AbstractBaseUser | None:
    requested_user_id = data.get("requested_user_id")
    requested_username = str(data.get("requested_username") or "").strip()
    if requested_user_id in {None, ""} and not requested_username:
        return None
    user_model = get_user_model()
    try:
        if requested_user_id not in {None, ""}:
            return user_model.objects.get(id=int(requested_user_id))
        return user_model.objects.get(username__iexact=requested_username)
    except (ValueError, user_model.DoesNotExist) as exc:
        raise ChartProfileInputError("requested user not found") from exc


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


def _optional_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _optional_gender(value: Any) -> str:
    gender = str(value or BirthProfile.Gender.UNKNOWN).strip()
    if gender not in BirthProfile.Gender.values:
        raise ChartProfileInputError("gender is invalid")
    return gender


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
