from __future__ import annotations

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess
from apps.calculations.vargas import VARGA_METHOD_REGISTRY, varga_accuracy_contract, workbench_expert_varga_codes, workbench_varga_codes

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
    update_chart_relationship,
    update_birth_profile_flags,
    update_incoming_profile_relationship_request,
    upsert_profile_relationship,
)



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

        return Response(
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
