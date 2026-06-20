from __future__ import annotations

import os
from datetime import datetime, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone as django_timezone
from django.utils.dateparse import parse_datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess
from apps.calculations.chart import ChartInputError, build_birth_chart
from apps.calculations.ephemeris import EphemerisUnavailable
from apps.calculations.graha_drishti import build_graha_drishti_aspects, graha_drishti_method_contract
from apps.calculations.transit_coordinates import transit_coordinate_golden_metadata
from apps.calculations.vargas import VARGA_METHOD_REGISTRY, varga_accuracy_contract, workbench_expert_varga_codes, workbench_varga_codes
from apps.calculations.vimshottari import VIMSHOTTARI_SEQUENCE, VIMSHOTTARI_YEAR_DAYS, VIMSHOTTARI_YEARS

from .models import BirthProfile, BirthProfileRelationship, ChartCalculation, ChartRelationship
from .services import (
    ChartRelationshipConflict,
    ChartProfileInputError,
    calculate_profile_chart,
    calculation_payload,
    chart_relationship_payload,
    create_birth_profile,
    create_chart_relationship,
    list_chart_relationships,
    list_incoming_profile_relationship_requests,
    list_profile_relationships,
    profile_payload,
    profiles_payload,
    profile_relationship_payload,
    _profile_input,
    update_chart_relationship,
    update_birth_profile_flags,
    update_incoming_profile_relationship_request,
    upsert_profile_relationship,
)


TRANSIT_WORKBENCH_METHOD_ID = "transit.d1.drik.v1"
TRANSIT_WORKBENCH_METHOD_VERSION = "1"
TRANSIT_WORKBENCH_BOUNDARY_POLICY = "instant_exact"
TRANSIT_WORKBENCH_VIEWS = ["transit_only", "overlay", "side_by_side"]


class TransitWorkbenchDevCheckView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        if not settings.ENABLE_DEV_LOGIN:
            return Response({"error": "not found"}, status=404)
        token = str(request.query_params.get("token") or "").strip()
        if not settings.DEV_LOGIN_TOKEN or token != settings.DEV_LOGIN_TOKEN:
            return Response({"error": "forbidden"}, status=403)
        try:
            chart_id = int(request.query_params.get("chart_id") or request.query_params.get("profile_id") or 0)
        except (TypeError, ValueError):
            return Response({"error": "chart_id is invalid"}, status=400)
        if chart_id <= 0:
            return Response({"error": "chart_id is required"}, status=400)
        profile = get_object_or_404(BirthProfile.objects.select_related("place"), id=chart_id)
        calculation = _latest_complete_calculation(profile)
        chart = calculation.result if calculation and isinstance(calculation.result, dict) else {}
        response = Response(_transit_workbench_check_payload(profile.id, chart, calculation is not None))
        response["Cache-Control"] = "no-store"
        return response


class BirthProfileTransitWorkbenchView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        try:
            control = _transit_control_from_query(profile, request.query_params)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        try:
            chart = _transit_chart_from_profile(profile, control)
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)
        calculation = _latest_complete_calculation(profile)
        natal_chart = calculation.result if calculation and isinstance(calculation.result, dict) else {}
        return Response(_transit_workbench_model(profile.id, chart, True, control, natal_chart))


def _latest_complete_calculation(profile: BirthProfile) -> ChartCalculation | None:
    return profile.calculations.filter(status=ChartCalculation.Status.COMPLETE).order_by("-created_at", "-id").first()


def _transit_control_from_query(profile: BirthProfile, query) -> dict[str, object]:
    scope = str(query.get("scope") or "d1").strip().lower()
    if scope != "d1":
        raise ValueError("only D1 transit scope is supported")
    timezone_name = str(query.get("timezone") or profile.timezone_name).strip()
    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("timezone is invalid") from exc
    raw_at = str(query.get("at") or "").strip()
    if raw_at:
        moment = parse_datetime(raw_at)
        if moment is None:
            raise ValueError("at is invalid")
    else:
        moment = django_timezone.now()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=tz)
    else:
        moment = moment.astimezone(tz)
    latitude = _transit_float(query.get("latitude"), float(profile.place.latitude), -90, 90, "latitude")
    longitude = _transit_float(query.get("longitude"), float(profile.place.longitude), -180, 180, "longitude")
    return {
        "isoDateTime": moment.isoformat(),
        "timezone": timezone_name,
        "location": {
            "label": str(query.get("location") or profile.place.metadata.get("label") or profile.place.name),
            "latitude": latitude,
            "longitude": longitude,
        },
    }


def _transit_float(value: object, default: float, minimum: float, maximum: float, label: str) -> float:
    if value in (None, ""):
        return default
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} is invalid") from exc
    if number < minimum or number > maximum:
        raise ValueError(f"{label} is invalid")
    return number


def _transit_chart_from_profile(profile: BirthProfile, control: dict[str, object]) -> dict[str, object]:
    moment = parse_datetime(str(control["isoDateTime"]))
    if moment is None:
        raise ChartInputError("transit moment is invalid")
    location = control["location"] if isinstance(control.get("location"), dict) else {}
    input_snapshot = {
        **_profile_input(profile),
        "birth_date": moment.date().isoformat(),
        "birth_time": moment.time().replace(microsecond=0).isoformat(),
        "birth_time_accuracy": "exact",
        "place_id": f"transit:{profile.place.external_id or profile.place.id}",
        "place_name": str(location.get("label") or profile.place.metadata.get("label") or profile.place.name),
        "timezone": str(control["timezone"]),
        "latitude": float(location.get("latitude")),
        "longitude": float(location.get("longitude")),
    }
    chart = build_birth_chart(input_snapshot)
    chart["transit_input"] = {
        "date": input_snapshot["birth_date"],
        "time": input_snapshot["birth_time"],
        "timezone": input_snapshot["timezone"],
        "latitude": input_snapshot["latitude"],
        "longitude": input_snapshot["longitude"],
    }
    return chart


def _transit_workbench_model(chart_id: int, chart: dict, has_calculation: bool, control: dict[str, object], natal_chart: dict | None = None) -> dict[str, object]:
    natal_chart = natal_chart if isinstance(natal_chart, dict) else {}
    houses = _transit_houses(chart)
    grahas = _transit_grahas(chart)
    special_points = _transit_special_points(chart)
    natal_houses = _transit_houses(natal_chart)
    natal_grahas = _contextual_grahas(natal_chart, "natal")
    natal_special_points = _contextual_special_points(natal_chart, "natal")
    settings_data = chart.get("settings") if isinstance(chart.get("settings"), dict) else {}
    return {
        "schemaVersion": "transit-workbench.v3",
        "chartId": chart_id,
        "hasCalculation": has_calculation,
        "transitMoment": {"isoDateTime": control["isoDateTime"], "timezone": control["timezone"]},
        "location": control["location"],
        "scopeId": "D1",
        "grahas": grahas,
        "specialPoints": special_points,
        "houses": houses,
        "rashis": _transit_rashis(houses),
        "natal": {
            "hasCalculation": bool(natal_chart),
            "grahas": natal_grahas,
            "specialPoints": natal_special_points,
            "houses": natal_houses,
            "rashis": _transit_rashis(natal_houses),
        },
        "overlay": _transit_overlay_contract(natal_chart, chart),
        "aspectLayer": _graha_drishti_layer(chart, natal_chart),
        "entityInspectorCount": 1,
        "method": {
            "methodId": TRANSIT_WORKBENCH_METHOD_ID,
            "methodVersion": TRANSIT_WORKBENCH_METHOD_VERSION,
            "ayanamshaId": str(settings_data.get("ayanamsa") or "lahiri"),
            "nodesMode": str(settings_data.get("node_type") or "true"),
            "calculationPreset": str(settings_data.get("calculation_model") or "drik_siddhanta"),
            "boundaryPolicy": TRANSIT_WORKBENCH_BOUNDARY_POLICY,
            "positionContext": "transit",
        },
        "calculationContract": _transit_calculation_contract(),
        "capabilities": _transit_capabilities(grahas, special_points),
        "warnings": [] if has_calculation else [{"code": "calculation_absent", "severity": "warning", "message": "Saved D1 calculation is absent for this chart."}],
    }


def _transit_workbench_check_payload(chart_id: int, chart: dict, has_calculation: bool) -> dict[str, object]:
    houses = _transit_houses(chart)
    grahas = _transit_grahas(chart)
    special_points = _transit_special_points(chart)
    overlay = _transit_overlay_contract(chart, chart)
    return {
        "status": "ok",
        "schemaVersion": "transit-workbench-check.v5",
        "deployCommit": _current_deploy_commit(),
        "scopeId": "D1",
        "methodId": TRANSIT_WORKBENCH_METHOD_ID,
        "methodVersion": TRANSIT_WORKBENCH_METHOD_VERSION,
        "boundaryPolicy": TRANSIT_WORKBENCH_BOUNDARY_POLICY,
        "positionContext": "transit",
        "objectRefPrefix": "transit:",
        "calculationContract": _transit_calculation_contract(),
        "coordinateGolden": transit_coordinate_golden_metadata(),
        "hasCalculation": has_calculation,
        "houseCount": len(houses),
        "rashiCount": len(_transit_rashis(houses)),
        "grahaCount": len(grahas),
        "specialPointCount": len(special_points),
        "chartObjectCount": len(grahas) + len(special_points),
        "natalObjectCount": overlay["natalObjectCount"],
        "transitObjectCount": overlay["transitObjectCount"],
        "supportedStyles": ["north", "south"],
        "supportedModes": ["novice", "astrologer"],
        "supportedViews": TRANSIT_WORKBENCH_VIEWS,
        "tabIds": ["overview", "grahas", "houses", "nakshatras"],
        "entityInspectorCount": 1,
        "supportsNatalOverlay": True,
        "supportsControlDate": True,
        "supportsControlTime": True,
        "supportsTimezone": True,
        "supportsLocation": True,
        "supportsNowAction": True,
        "overlayContract": overlay,
        "grahaDrishtiContract": _graha_drishti_dev_contract(chart, chart),
        "capabilities": {
            "natalOverlay": True,
            "aspects": True,
            "ashtakavarga": False,
            "sadeSati": False,
            "ai": False,
            "rawEvidence": False,
        },
    }


def _transit_houses(chart: dict) -> list[dict[str, object]]:
    houses = chart.get("houses") if isinstance(chart, dict) else []
    return [item for item in houses if isinstance(item, dict)] if isinstance(houses, list) else []


def _transit_grahas(chart: dict) -> list[dict[str, object]]:
    return _contextual_grahas(chart, "transit")


def _contextual_grahas(chart: dict, context: str) -> list[dict[str, object]]:
    grahas = chart.get("grahas") if isinstance(chart, dict) else []
    if not isinstance(grahas, list):
        return []
    return [_transit_object(item, "graha", context) for item in grahas if isinstance(item, dict)]


def _transit_special_points(chart: dict) -> list[dict[str, object]]:
    return _contextual_special_points(chart, "transit")


def _contextual_special_points(chart: dict, context: str) -> list[dict[str, object]]:
    ascendant = chart.get("ascendant") if isinstance(chart, dict) else None
    return [_transit_object(ascendant, "point", context)] if isinstance(ascendant, dict) else []


def _transit_object(item: dict[str, object], entity_type: str, context: str) -> dict[str, object]:
    body = str(item.get("body") or "")
    if entity_type == "point":
        entity_id = "point.LAGNA"
    else:
        entity_id = f"graha.{_graha_code(body)}"
    return {
        **item,
        "context": context,
        "entityId": entity_id,
        "objectRef": f"{context}:{entity_id}",
    }


def _transit_overlay_contract(natal_chart: dict, transit_chart: dict) -> dict[str, object]:
    natal_objects = [*_contextual_special_points(natal_chart, "natal"), *_contextual_grahas(natal_chart, "natal")]
    transit_objects = [*_contextual_special_points(transit_chart, "transit"), *_contextual_grahas(transit_chart, "transit")]
    return {
        "supportsNatalOverlay": True,
        "supportedViews": TRANSIT_WORKBENCH_VIEWS,
        "defaultView": "transit_only",
        "housesRelativeTo": "natal",
        "legendRequired": True,
        "legend": [
            {"context": "natal", "label": "Натал", "objectRefPrefix": "natal:"},
            {"context": "transit", "label": "Транзит", "objectRefPrefix": "transit:"},
        ],
        "natalObjectCount": len(natal_objects),
        "transitObjectCount": len(transit_objects),
        "natalObjectRefs": [item["objectRef"] for item in natal_objects],
        "transitObjectRefs": [item["objectRef"] for item in transit_objects],
        "aspects": False,
        "orbs": False,
        "ashtakavarga": False,
        "sadeSati": False,
        "ai": False,
        "rawEvidence": False,
    }


def _graha_drishti_layer(transit_chart: dict, natal_chart: dict) -> dict[str, object]:
    aspects = build_graha_drishti_aspects(transit_chart, natal_chart, source_context="transit", target_context="natal")
    sample_refs = [
        {
            "sourceEntityRef": item["sourceEntityRef"],
            "targetEntityRef": item["targetEntityRef"],
            "aspectKind": item["aspectKind"],
            "signDistance": item["signDistance"],
        }
        for item in aspects[:12]
    ]
    return {
        **graha_drishti_method_contract(),
        "sourceContext": "transit",
        "targetContext": "natal",
        "availableInModes": ["astrologer"],
        "enabledByDefault": False,
        "sourceStatus": "needs_source",
        "uiCapability": True,
        "aspectCount": len(aspects),
        "sampleRefs": sample_refs,
        "items": aspects,
    }


def _graha_drishti_dev_contract(transit_chart: dict, natal_chart: dict) -> dict[str, object]:
    layer = _graha_drishti_layer(transit_chart, natal_chart)
    return {key: value for key, value in layer.items() if key != "items"}


def _transit_calculation_contract() -> dict[str, object]:
    return {
        "scopeId": "D1",
        "methodId": TRANSIT_WORKBENCH_METHOD_ID,
        "methodVersion": TRANSIT_WORKBENCH_METHOD_VERSION,
        "boundaryPolicy": TRANSIT_WORKBENCH_BOUNDARY_POLICY,
        "positionContext": "transit",
        "usesNatalOverlay": True,
        "usesAspects": True,
        "usesAshtakavarga": False,
        "usesSadeSati": False,
        "usesAi": False,
        "rawEvidence": False,
    }


def _transit_rashis(houses: list[dict[str, object]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[object] = set()
    for house in houses:
        key = house.get("rashi_index") if house.get("rashi_index") is not None else house.get("rashi")
        if key in seen:
            continue
        seen.add(key)
        rows.append({"rashiIndex": house.get("rashi_index"), "rashiName": house.get("rashi"), "house": house.get("house")})
    return rows


def _transit_capabilities(grahas: list[dict[str, object]], special_points: list[dict[str, object]]) -> dict[str, bool]:
    placements = [*grahas, *special_points]
    return {
        "northChart": True,
        "southChart": True,
        "nakshatras": any(item.get("nakshatra") for item in placements),
        "padas": any(item.get("pada") for item in placements),
        "natalOverlay": True,
        "aspects": True,
        "ashtakavarga": False,
        "sadeSati": False,
        "ai": False,
    }
class D1WorkbenchDevCheckView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        if not settings.ENABLE_DEV_LOGIN:
            return Response({"error": "not found"}, status=404)
        token = str(request.query_params.get("token") or "").strip()
        if not settings.DEV_LOGIN_TOKEN or token != settings.DEV_LOGIN_TOKEN:
            return Response({"error": "forbidden"}, status=403)
        scope = str(request.query_params.get("scope") or "d1").strip().lower()
        try:
            chart_id = int(request.query_params.get("chart_id") or request.query_params.get("profile_id") or 0)
        except (TypeError, ValueError):
            return Response({"error": "chart_id is invalid"}, status=400)
        if chart_id <= 0:
            return Response({"error": "chart_id is required"}, status=400)

        profile = get_object_or_404(BirthProfile.objects.select_related("place"), id=chart_id)
        if scope not in _workbench_supported_scope_keys(profile):
            return Response({"error": "scope is not supported"}, status=400)
        calculation = (
            profile.calculations.filter(status=ChartCalculation.Status.COMPLETE)
            .order_by("-created_at", "-id")
            .first()
        )
        chart = calculation.result if calculation else {}
        scope_summary = _workbench_scope_summary(chart if isinstance(chart, dict) else {}, scope)

        response = Response(
            {
                "status": "ok",
                "schemaVersion": "d1-workbench-check.v2" if scope == "d1" else "varga-workbench-check.v1",
                "scopeId": _workbench_scope_id(scope),
                "chartId": profile.id,
                "hasCalculation": calculation is not None,
                **scope_summary,
                **_workbench_scope_method_summary(chart if isinstance(chart, dict) else {}, scope),
                "supportedStyles": ["north", "south"],
                "supportedModes": ["novice", "astrologer"],
                "entityInspectorCount": 1,
                "supportedScopes": list(_workbench_supported_scopes(profile)),
                "expertOnlyScopes": list(_workbench_expert_scopes(profile)),
                "vargaScopes": _workbench_varga_scopes(profile),
                "warnings": _workbench_warnings(profile, scope),
                "accuracyGates": _workbench_accuracy_gates(profile),
                "forbiddenScopesPresent": {
                    "D60": False,
                    "AI": False,
                    "rawEvidence": False,
                },
            }
        )
        response["Cache-Control"] = "no-store"
        return response



class DashaWorkbenchDevCheckView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        if not settings.ENABLE_DEV_LOGIN:
            return Response({"error": "not found"}, status=404)
        token = str(request.query_params.get("token") or "").strip()
        if not settings.DEV_LOGIN_TOKEN or token != settings.DEV_LOGIN_TOKEN:
            return Response({"error": "forbidden"}, status=403)
        try:
            chart_id = int(request.query_params.get("chart_id") or request.query_params.get("profile_id") or 0)
        except (TypeError, ValueError):
            return Response({"error": "chart_id is invalid"}, status=400)
        if chart_id <= 0:
            return Response({"error": "chart_id is required"}, status=400)

        profile = get_object_or_404(BirthProfile.objects.select_related("place"), id=chart_id)
        calculation = (
            profile.calculations.filter(status=ChartCalculation.Status.COMPLETE)
            .order_by("-created_at", "-id")
            .first()
        )
        chart = calculation.result if calculation and isinstance(calculation.result, dict) else {}
        response = Response(_dasha_workbench_check_payload(profile.id, chart, calculation is not None))
        response["Cache-Control"] = "no-store"
        return response


def _dasha_workbench_check_payload(chart_id: int, chart: dict, has_calculation: bool) -> dict[str, object]:
    vimshottari = ((chart.get("dashas") or {}).get("vimshottari") or {}) if isinstance(chart, dict) else {}
    mahadashas = vimshottari.get("mahadashas") if isinstance(vimshottari.get("mahadashas"), list) else []
    current_mahadasha = mahadashas[0] if mahadashas and isinstance(mahadashas[0], dict) else {}
    antardashas = current_mahadasha.get("antardashas") if isinstance(current_mahadasha.get("antardashas"), list) else []
    if not antardashas:
        antardashas = vimshottari.get("antardashas") if isinstance(vimshottari.get("antardashas"), list) else []
    if not antardashas:
        antardashas = _legacy_dasha_antardashas(current_mahadasha)
    current_antardasha = antardashas[0] if antardashas and isinstance(antardashas[0], dict) else {}
    pratyantardashas = current_antardasha.get("pratyantardashas") if isinstance(current_antardasha.get("pratyantardashas"), list) else []
    if not pratyantardashas:
        pratyantardashas = _legacy_dasha_subperiods(
            current_antardasha,
            level=3,
            parent_lord=str(current_antardasha.get("lord") or ""),
            mahadasha_lord=str(current_mahadasha.get("lord") or ""),
        )
    current_pratyantardasha = pratyantardashas[0] if pratyantardashas and isinstance(pratyantardashas[0], dict) else {}
    return {
        "status": "ok",
        "schemaVersion": "dasha-workbench-check.v3",
        "deployCommit": _current_deploy_commit(),
        "chartId": chart_id,
        "hasCalculation": has_calculation,
        "supportedSystems": ["vimshottari"],
        "activeSystem": "vimshottari",
        "methodId": str(vimshottari.get("methodId") or "dasha.vimshottari.parashara.v1"),
        "methodVersion": str(vimshottari.get("methodVersion") or "1"),
        "sourceAnchor": str(vimshottari.get("sourceAnchor") or "BPHS 46.2-16"),
        "boundaryPolicy": str(vimshottari.get("boundary_policy") or "start_inclusive_end_exclusive"),
        "boundaryDisplayPolicy": str(vimshottari.get("boundary_policy") or "start_inclusive_end_exclusive"),
        "supportedViews": ["tree", "table", "timeline"],
        "defaultView": "tree",
        "supportsControlDate": True,
        "supportsGoToCurrentPeriod": True,
        "collapsibleLevels": ["mahadasha", "antardasha", "pratyantardasha"],
        "mahadashaCount": len(mahadashas),
        "antardashaCount": len(antardashas),
        "pratyantardashaCount": len(pratyantardashas),
        "yearLengthDays": vimshottari.get("year_length_days") or 365.25,
        "currentMahadashaLord": str(current_mahadasha.get("lord") or ""),
        "currentAntardashaLord": str(current_antardasha.get("lord") or ""),
        "currentAntardashaParentLord": str(current_antardasha.get("parent_lord") or current_mahadasha.get("lord") or ""),
        "currentPratyantardashaLord": str(current_pratyantardasha.get("lord") or ""),
        "currentPratyantardashaParentLord": str(current_pratyantardasha.get("parent_lord") or current_antardasha.get("lord") or ""),
        "entityInspectorCount": 1,
        "supportedModes": ["novice", "astrologer"],
        "forbiddenScopesPresent": {"AI": False, "rawEvidence": False},
    }

def _current_deploy_commit() -> str:
    value = os.getenv("JYOTISH_DEPLOY_COMMIT", "").strip()
    if value:
        return value
    try:
        return (settings.ROOT_DIR / ".deploy-commit").read_text(encoding="utf-8").strip()
    except OSError:
        return ""

def _legacy_dasha_antardashas(mahadasha: dict) -> list[dict[str, object]]:
    return _legacy_dasha_subperiods(
        mahadasha,
        level=2,
        parent_lord=str(mahadasha.get("lord") or ""),
    )


def _legacy_dasha_subperiods(
    parent: dict,
    level: int,
    parent_lord: str,
    mahadasha_lord: str = "",
) -> list[dict[str, object]]:
    starts_at = parse_datetime(str(parent.get("starts_at") or ""))
    ends_at = parse_datetime(str(parent.get("ends_at") or ""))
    if parent_lord not in VIMSHOTTARI_SEQUENCE or starts_at is None or ends_at is None or starts_at >= ends_at:
        return []

    total_seconds = (ends_at - starts_at).total_seconds()
    parent_index = VIMSHOTTARI_SEQUENCE.index(parent_lord)
    periods: list[dict[str, object]] = []
    current_start = starts_at
    for offset in range(len(VIMSHOTTARI_SEQUENCE)):
        sequence_index = (parent_index + offset) % len(VIMSHOTTARI_SEQUENCE)
        period_lord = VIMSHOTTARI_SEQUENCE[sequence_index]
        duration_seconds = total_seconds * (VIMSHOTTARI_YEARS[period_lord] / 120.0)
        current_end = current_start + (ends_at - starts_at) * (duration_seconds / total_seconds)
        period = {
            "lord": period_lord,
            "parent_lord": parent_lord,
            "level": level,
            "starts_at": current_start.isoformat(),
            "ends_at": current_end.isoformat(),
            "duration_years": round((current_end - current_start).total_seconds() / 86_400 / VIMSHOTTARI_YEAR_DAYS, 10),
            "sequence_index": sequence_index,
        }
        if mahadasha_lord:
            period["mahadasha_lord"] = mahadasha_lord
        periods.append(period)
        current_start = current_end
    return periods

def _workbench_supported_scopes(profile: BirthProfile | None = None) -> tuple[str, ...]:
    codes = tuple(workbench_varga_codes())
    if profile is not None and getattr(profile, "birth_time_accuracy", "") != BirthProfile.TimeAccuracy.EXACT:
        return tuple(code for code in codes if code != "D60")
    return codes


def _workbench_expert_scopes(profile: BirthProfile | None = None) -> tuple[str, ...]:
    supported = set(_workbench_supported_scopes(profile))
    return tuple(code for code in workbench_expert_varga_codes() if code in supported)


def _workbench_supported_scope_keys(profile: BirthProfile | None = None) -> set[str]:
    return {code.lower() for code in _workbench_supported_scopes(profile)}


def _workbench_varga_scopes(profile: BirthProfile) -> list[dict[str, object]]:
    supported = set(_workbench_supported_scopes(profile))
    return [
        {
            "code": code,
            "name": method.name,
            "category": method.category,
            "methodId": method.method_id,
            "methodVersion": method.method_version,
            "calculationPreset": "parashara",
            "expertOnly": method.expert_only,
            "timeAccuracyRequired": method.time_accuracy_required,
        }
        for code, method in VARGA_METHOD_REGISTRY.items()
        if code in supported
    ]


def _workbench_accuracy_gates(profile: BirthProfile) -> dict[str, dict[str, str]]:
    return {"D60": varga_accuracy_contract("D60", profile.birth_time_accuracy)}


def _workbench_warnings(profile: BirthProfile, scope: str) -> list[dict[str, str]]:
    if _workbench_scope_id(scope) != "D60":
        return []
    return [
        {
            "code": "d60_birth_time_accuracy",
            "severity": "warning",
            "message": "D60 is expert-only and requires exact birth time.",
        }
    ]


def _workbench_scope_id(scope: str) -> str:
    return scope.upper() if scope in _workbench_supported_scope_keys() else "D1"


def _workbench_scope_method_summary(chart: dict, scope: str) -> dict:
    settings = chart.get("settings") if isinstance(chart.get("settings"), dict) else {}
    default_preset = str(settings.get("varga_scheme") or "parashara")
    if scope == "d1":
        return {"methodId": "varga.parashara_shodasha.v1", "methodVersion": "1", "calculationPreset": default_preset}
    code = _workbench_scope_id(scope)
    varga = chart.get("vargas", {}).get(code, {}) if isinstance(chart.get("vargas"), dict) else {}
    registry_method = VARGA_METHOD_REGISTRY.get(code)
    preset = str(varga.get("calculationPreset") or default_preset)
    method_id = str(varga.get("methodId") or (registry_method.method_id if registry_method else "varga.parashara_shodasha.v1"))
    if code == "D2" and preset == "jhora_uma_shambhu" and not varga.get("methodId"):
        method_id = "varga.jhora_uma_shambhu_hora.v1"
    return {
        "methodId": method_id,
        "methodVersion": str(varga.get("methodVersion") or (registry_method.method_version if registry_method else "1")),
        "calculationPreset": preset,
    }


def _workbench_scope_summary(chart: dict, scope: str) -> dict:
    if scope != "d1":
        code = _workbench_scope_id(scope)
        varga = chart.get("vargas", {}).get(code, {}) if isinstance(chart.get("vargas"), dict) else {}
        placements = [item for item in varga.get("placements", []) if isinstance(item, dict)] if isinstance(varga, dict) else []
        grahas = [item for item in placements if str(item.get("body") or "") not in {"Lagna", "Ascendant"}]
        special_points = [item for item in placements if str(item.get("body") or "") in {"Lagna", "Ascendant"}]
        house_count = 12 if special_points else 0
        rashi_count = 12 if special_points else len({item.get("rashi_index") for item in placements if item.get("rashi_index") is not None})
        return {
            "houseCount": house_count,
            "rashiCount": rashi_count,
            "grahaCount": len(grahas),
            "specialPointCount": len(special_points),
            "chartObjectCount": len(grahas) + len(special_points),
            "tabIds": ["overview", "grahas", "houses"],
            "nakshatrasAvailable": False,
            "clickTargets": {
                "houses": house_count,
                "rashis": rashi_count,
                "grahas": len(grahas),
                "specialPoints": len(special_points),
            },
        }

    houses = chart.get("houses") if isinstance(chart, dict) else []
    if not isinstance(houses, list):
        houses = []
    grahas = chart.get("grahas") if isinstance(chart, dict) else []
    if not isinstance(grahas, list):
        grahas = []
    ascendant = chart.get("ascendant") if isinstance(chart, dict) else None
    d1_grahas = [item for item in grahas if isinstance(item, dict)]
    special_points = [ascendant] if isinstance(ascendant, dict) else []
    sorted_houses = sorted(
        int(item.get("house")) for item in houses if isinstance(item, dict) and str(item.get("house", "")).isdigit()
    )
    rashi_values = set()
    for item in houses if isinstance(houses, list) else []:
        if not isinstance(item, dict):
            continue
        rashi_index = item.get("rashi_index")
        if isinstance(rashi_index, int):
            rashi_values.add(rashi_index + 1 if 0 <= rashi_index <= 11 else rashi_index)
        elif item.get("rashi"):
            rashi_values.add(str(item.get("rashi")))
    nakshatras_available = any(isinstance(item, dict) and item.get("nakshatra") for item in [*special_points, *d1_grahas])
    tab_ids = ["overview", "grahas", "houses"] + (["nakshatras"] if nakshatras_available else [])
    return {
        "houseCount": len(sorted_houses),
        "rashiCount": len(rashi_values),
        "grahaCount": len(d1_grahas),
        "specialPointCount": len(special_points),
        "chartObjectCount": len(d1_grahas) + len(special_points),
        "tabIds": tab_ids,
        "nakshatrasAvailable": nakshatras_available,
        "clickTargets": {
            "houses": len(sorted_houses),
            "rashis": len(rashi_values),
            "grahas": len(d1_grahas),
            "specialPoints": len(special_points),
        },
    }


def _graha_code(body: str) -> str:
    return {
        "Ascendant": "AS",
        "Lagna": "AS",
        "Surya": "SU",
        "Sun": "SU",
        "Chandra": "MO",
        "Moon": "MO",
        "Mangala": "MA",
        "Mars": "MA",
        "Budha": "ME",
        "Mercury": "ME",
        "Guru": "JU",
        "Jupiter": "JU",
        "Shukra": "VE",
        "Venus": "VE",
        "Shani": "SA",
        "Saturn": "SA",
        "Rahu": "RA",
        "Ketu": "KE",
    }.get(body, body[:2].upper())


def _graha_order(code: str) -> int:
    order = ["AS", "SU", "MO", "MA", "ME", "JU", "VE", "SA", "RA", "KE"]
    return order.index(code) if code in order else 99

class BirthProfileListView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        profiles = (
            BirthProfile.objects.filter(user=request.user).select_related("place").order_by("-created_at")
        )
        return Response({"profiles": profiles_payload(list(profiles))})

    def post(self, request):
        try:
            profile = create_birth_profile(request.user, request.data)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"profile": profile_payload(profile)}, status=201)


class BirthProfileDetailView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        return Response({"profile": profile_payload(profile)})

    def patch(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        try:
            profile = update_birth_profile_flags(profile, request.data)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"profile": profile_payload(profile)})

    def delete(self, request, profile_id: int):
        profile = get_object_or_404(BirthProfile, id=profile_id, user=request.user)
        profile.delete()
        return Response(status=204)



class BirthProfileWorkbenchView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, profile_id: int):
        scope = str(request.query_params.get("scope") or "d1").strip().lower()
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        if scope not in _workbench_supported_scope_keys(profile):
            return Response({"error": "scope is not supported"}, status=400)
        calculation = (
            profile.calculations.filter(status=ChartCalculation.Status.COMPLETE)
            .order_by("-created_at", "-id")
            .first()
        )
        return Response(
            {
                "scope": scope,
                "profile": profile_payload(profile, latest_calculation=calculation),
                "calculation": calculation_payload(calculation) if calculation else None,
                "method": _workbench_scope_method_summary(calculation.result if calculation else {}, scope),
                "warnings": _workbench_warnings(profile, scope),
                "accuracyGates": _workbench_accuracy_gates(profile),
                "supportedScopes": list(_workbench_supported_scopes(profile)),
                "expertOnlyScopes": list(_workbench_expert_scopes(profile)),
                "vargaScopes": _workbench_varga_scopes(profile),
                "result": calculation.result if calculation else None,
            }
        )

class BirthProfileCalculateView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request, profile_id: int):
        profile = get_object_or_404(
            BirthProfile.objects.select_related("place"),
            id=profile_id,
            user=request.user,
        )
        calculation = calculate_profile_chart(profile, reuse_existing=True)
        if getattr(calculation, "_jyotish_reused", False):
            status_code = 200
        else:
            status_code = 201 if calculation.status == ChartCalculation.Status.COMPLETE else 503
        return Response({"calculation": calculation_payload(calculation)}, status=status_code)


class BirthProfileRelationshipListView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        relationships = list_profile_relationships(request.user)
        return Response({"relationships": [profile_relationship_payload(item) for item in relationships]})

    def post(self, request):
        try:
            relationship = upsert_profile_relationship(request.user, request.data)
        except BirthProfile.DoesNotExist:
            return Response({"error": "profile not found"}, status=404)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"relationship": profile_relationship_payload(relationship)}, status=201)


class BirthProfileRelationshipInboxView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        requests = list_incoming_profile_relationship_requests(request.user)
        return Response({"relationships": [profile_relationship_payload(item) for item in requests]})


class BirthProfileRelationshipDetailView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, relationship_id: int):
        relationship = get_object_or_404(
            BirthProfileRelationship.objects.select_related(
                "user",
                "profile",
                "related_profile",
                "requested_user",
                "profile__place",
                "related_profile__place",
            ),
            id=relationship_id,
            user=request.user,
        )
        return Response({"relationship": profile_relationship_payload(relationship)})

    def delete(self, request, relationship_id: int):
        relationship = get_object_or_404(BirthProfileRelationship, id=relationship_id, user=request.user)
        relationship.delete()
        return Response(status=204)


class BirthProfileRelationshipActionView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request, relationship_id: int):
        try:
            relationship = update_incoming_profile_relationship_request(
                request.user,
                relationship_id,
                str(request.data.get("action") or "").strip(),
                request.data,
            )
        except BirthProfileRelationship.DoesNotExist:
            return Response({"error": "relationship request not found"}, status=404)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"relationship": profile_relationship_payload(relationship)})


class ChartRelationshipListView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        chart_id = request.query_params.get("chart_id")
        relationship_type_id = request.query_params.get("relationship_type_id")
        try:
            parsed_chart_id = int(chart_id) if chart_id else None
        except ValueError:
            return Response({"error": "chart_id is invalid"}, status=400)
        relationships = list_chart_relationships(
            request.user,
            chart_id=parsed_chart_id,
            relationship_type_id=relationship_type_id,
        )
        return Response({"relationships": [chart_relationship_payload(item) for item in relationships]})

    def post(self, request):
        try:
            relationship = create_chart_relationship(request.user, request.data)
        except BirthProfile.DoesNotExist:
            return Response({"error": "chart not found"}, status=404)
        except ChartRelationshipConflict as exc:
            return Response({"error": str(exc)}, status=409)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"relationship": chart_relationship_payload(relationship)}, status=201)


class ChartRelationshipDetailView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, relationship_id: int):
        relationship = get_object_or_404(
            ChartRelationship.objects.select_related("chart_a", "chart_b", "chart_a__place", "chart_b__place"),
            id=relationship_id,
            owner_user=request.user,
        )
        return Response({"relationship": chart_relationship_payload(relationship)})

    def patch(self, request, relationship_id: int):
        relationship = get_object_or_404(ChartRelationship, id=relationship_id, owner_user=request.user)
        try:
            relationship = update_chart_relationship(request.user, relationship, request.data)
        except BirthProfile.DoesNotExist:
            return Response({"error": "chart not found"}, status=404)
        except ChartRelationshipConflict as exc:
            return Response({"error": str(exc)}, status=409)
        except ChartProfileInputError as exc:
            return Response({"error": str(exc)}, status=400)
        return Response({"relationship": chart_relationship_payload(relationship)})

    def delete(self, request, relationship_id: int):
        relationship = get_object_or_404(ChartRelationship, id=relationship_id, owner_user=request.user)
        relationship.delete()
        return Response(status=204)
