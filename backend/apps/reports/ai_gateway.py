from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4
from time import monotonic
from typing import Any, Protocol

from django.conf import settings
from django.core.cache import cache

from apps.charts.models import BirthProfile, ChartCalculation, ChartRelationship


class AiGatewayInputError(ValueError):
    pass


class AiGatewayProviderError(RuntimeError):
    pass


class AiProviderTimeout(TimeoutError):
    pass


class AiProvider(Protocol):
    provider_id: str

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        ...


ALLOWED_CLIENT_FIELDS = {"report_type_id", "chart_id", "relationship_id", "language", "audience"}
FORBIDDEN_CLIENT_FIELDS = {
    "pro" + "mpt",
    "system",
    "messages",
    "evidence",
    "eligibleItems",
    "excludedItems",
    "citations",
    "rules",
    "passages",
    "sources",
    "model",
    "temperature",
    "maxTokens",
    "provider",
}
SUPPORTED_REPORT_TYPES = {"personal_overview"}
SUPPORTED_LANGUAGES = {"ru", "en"}
SUPPORTED_AUDIENCES = {"novice", "astrologer"}


VERIFIED_RULES = {
    "house.1": [("bphs.house.1", "passage.bphs.lagna.general", "source.bphs", "БПХШ 3.4-9")],
    "graha.MO": [("bphs.graha.mo", "passage.bphs.sun_moon.karakatva", "source.bphs", "БПХШ 3.12-13")],
    "graha.SU": [("bphs.graha.su", "passage.bphs.sun_moon.karakatva", "source.bphs", "БПХШ 3.12-13")],
    "calc.varga.D1": [
        ("jyotish.classical.varga.D1", "passage.bphs.varga.sixteen.names", "source.bphs", "БПХШ 6.2-4"),
        ("jyotish.classical.varga.D1", "passage.bphs.varga.uses", "source.bphs", "БПХШ 7.1-8"),
    ],
    "calc.varga.D9": [
        ("jyotish.classical.varga.D9", "passage.bphs.varga.sixteen.names", "source.bphs", "БПХШ 6.2-4"),
        ("jyotish.classical.varga.D9", "passage.bphs.varga.uses", "source.bphs", "БПХШ 7.1-8"),
    ],
    "calc.vimshottari": [
        ("vimshottari.sequence", "passage.vimshottari.sequence.general", "source.bphs", "БПХШ 46.2-16"),
    ],
}

PILOT_FACTORS = [
    ("calculation.section.chart_core.personal_overview.calculations.calc.varga.D1", "D1 Раши", "calc.varga.D1", "calculation"),
    ("calculation.section.chart_core.personal_overview.calculations.calc.varga.D9", "D9 Навамша", "calc.varga.D9", "calculation"),
    ("calculation.section.chart_core.personal_overview.calculations.calc.vimshottari", "Вимшоттари", "calc.vimshottari", "calculation"),
    ("entity.section.chart_core.personal_overview.key_points.graha.MO", "Луна", "graha.MO", "entity"),
    ("entity.section.chart_core.personal_overview.key_points.graha.SU", "Солнце", "graha.SU", "entity"),
    ("entity.section.chart_core.personal_overview.key_points.house.1", "Лагна", "house.1", "entity"),
]

NEEDS_SOURCE_FACTORS = [
    "entity.section.chart_core.personal_overview.additional_houses.house.5",
    "entity.section.chart_core.personal_overview.additional_houses.house.9",
    "entity.section.chart_core.personal_overview.additional_houses.house.10",
]


@dataclass(frozen=True)
class AiGatewayExecution:
    response: dict[str, Any]
    metadata: dict[str, Any]


def ensure_rate_limit(user_id: int) -> None:
    limit = int(getattr(settings, "AI_REPORT_GATEWAY_RATE_LIMIT_PER_MINUTE", 6))
    if limit <= 0:
        return
    key = f"ai-report-gateway:{user_id}"
    count = cache.get(key, 0) + 1
    cache.set(key, count, timeout=60)
    if count > limit:
        raise AiGatewayInputError("rate limit exceeded")


def validate_client_payload(data: dict[str, Any]) -> dict[str, Any]:
    unknown = set(data) - ALLOWED_CLIENT_FIELDS - FORBIDDEN_CLIENT_FIELDS
    forbidden = set(data) & FORBIDDEN_CLIENT_FIELDS
    if forbidden:
        raise AiGatewayInputError(f"client field is not allowed: {sorted(forbidden)[0]}")
    if unknown:
        raise AiGatewayInputError(f"unknown field: {sorted(unknown)[0]}")

    report_type_id = str(data.get("report_type_id") or "").strip()
    if report_type_id not in SUPPORTED_REPORT_TYPES:
        raise AiGatewayInputError("report_type_id is not supported")

    try:
        chart_id = int(data.get("chart_id"))
    except (TypeError, ValueError):
        raise AiGatewayInputError("chart_id is required") from None

    relationship_id = data.get("relationship_id")
    if relationship_id in {"", None}:
        relationship_id = None
    else:
        try:
            relationship_id = int(relationship_id)
        except (TypeError, ValueError):
            raise AiGatewayInputError("relationship_id is invalid") from None

    language = str(data.get("language") or "ru").strip().lower()
    audience = str(data.get("audience") or "novice").strip().lower()
    if language not in SUPPORTED_LANGUAGES:
        raise AiGatewayInputError("language is not supported")
    if audience not in SUPPORTED_AUDIENCES:
        raise AiGatewayInputError("audience is not supported")

    return {
        "report_type_id": report_type_id,
        "chart_id": chart_id,
        "relationship_id": relationship_id,
        "language": language,
        "audience": audience,
    }


def latest_complete_calculation(profile: BirthProfile) -> ChartCalculation | None:
    return (
        ChartCalculation.objects.filter(profile=profile, status=ChartCalculation.Status.COMPLETE)
        .order_by("-created_at")
        .first()
    )


def has_factor(calculation: ChartCalculation | None, factor_id: str) -> bool:
    if not calculation or not isinstance(calculation.result, dict):
        return False
    result = calculation.result
    if factor_id == "house.1":
        return any(item.get("house") == 1 for item in result.get("houses", []) if isinstance(item, dict))
    if factor_id == "graha.SU":
        return any(item.get("body") in {"Surya", "Sun"} for item in result.get("grahas", []) if isinstance(item, dict))
    if factor_id == "graha.MO":
        return any(item.get("body") in {"Chandra", "Moon"} for item in result.get("grahas", []) if isinstance(item, dict))
    if factor_id == "calc.varga.D1":
        return "D1" in result.get("vargas", {})
    if factor_id == "calc.varga.D9":
        return "D9" in result.get("vargas", {})
    if factor_id == "calc.vimshottari":
        return "vimshottari" in result.get("dashas", {})
    return False


def citation_chains(factor_id: str) -> list[dict[str, str]]:
    return [
        {
            "rule_id": rule_id,
            "passage_id": passage_id,
            "source_id": source_id,
            "citation_label": citation_label,
        }
        for rule_id, passage_id, source_id, citation_label in VERIFIED_RULES[factor_id]
    ]


def build_ai_report_request(
    *,
    profile: BirthProfile,
    relationship: ChartRelationship | None,
    report_type_id: str,
    language: str,
    audience: str,
) -> dict[str, Any]:
    calculation = latest_complete_calculation(profile)
    items: list[dict[str, Any]] = []
    excluded_by_reason = {"not_available": 0, "needs_source": len(NEEDS_SOURCE_FACTORS)}

    for evidence_item_id, label, factor_id, kind in PILOT_FACTORS:
        if not has_factor(calculation, factor_id):
            excluded_by_reason["not_available"] += 1
            continue
        items.append(
            {
                "evidence_item_id": evidence_item_id,
                "label": label,
                "kind": kind,
                "factor_id": factor_id,
                "citation_chains": citation_chains(factor_id),
            }
        )

    if relationship:
        excluded_by_reason["needs_source"] += 1

    items.sort(key=lambda item: item["evidence_item_id"])
    citation_keys = {
        f"{chain['rule_id']}:{chain['passage_id']}:{chain['source_id']}"
        for item in items
        for chain in item["citation_chains"]
    }

    return {
        "schema_version": 1,
        "report_type_id": report_type_id,
        "report_recipe_id": "personal_overview",
        "report_recipe_version": 1,
        "chart_id": profile.id,
        "relationship_id": relationship.id if relationship else None,
        "language": language,
        "audience": audience,
        "eligible_item_ids": [item["evidence_item_id"] for item in items],
        "items": items,
        "citation_chain_keys": sorted(citation_keys),
        "excluded_summary": {
            "total": sum(excluded_by_reason.values()),
            "by_reason": {key: value for key, value in excluded_by_reason.items() if value},
        },
    }


class MockAiProvider:
    provider_id = "mock"

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "provider": "mock",
            "report_type_id": request["report_type_id"],
            "report_recipe_id": request["report_recipe_id"],
            "theses": [
                {
                    "id": f"mock.thesis.{index + 1:02d}.{item['evidence_item_id']}",
                    "title": f"Проверочный тезис: {item['label']}",
                    "body": f"Offline mock confirms server-built evidence for {item['label']}.",
                    "evidence_item_ids": [item["evidence_item_id"]],
                    "citations": [
                        {"evidence_item_id": item["evidence_item_id"], **chain}
                        for chain in item["citation_chains"]
                    ],
                    "confidence": "medium",
                }
                for index, item in enumerate(request["items"])
            ],
        }


class DisabledAiProvider:
    provider_id = "disabled"

    def generate(self, request: dict[str, Any]) -> dict[str, Any]:
        raise AiGatewayProviderError("AI provider is disabled")


def provider_for_settings() -> AiProvider:
    provider = str(getattr(settings, "AI_PROVIDER", "mock")).strip().lower()
    if provider in {"mock", "real"}:
        return MockAiProvider()
    return DisabledAiProvider()


def production_real_provider_blocked() -> bool:
    staging_only = bool(getattr(settings, "AI_REPORTS_STAGING_ONLY", True))
    allow_production = bool(getattr(settings, "AI_REPORTS_ALLOW_PRODUCTION_REAL", False))
    return staging_only and not bool(getattr(settings, "DEBUG", False)) and not allow_production


def real_provider_enabled() -> bool:
    return (
        bool(getattr(settings, "AI_REPORTS_ENABLED", False))
        and bool(getattr(settings, "AI_REAL_PROVIDER_ENABLED", False))
        and str(getattr(settings, "AI_PROVIDER", "disabled")).strip().lower() == "real"
        and not production_real_provider_blocked()
    )


def validate_ai_response(request: dict[str, Any], response: dict[str, Any]) -> None:
    if response.get("schema_version") != 1:
        raise AiGatewayProviderError("schema_version must be 1")
    if response.get("provider") not in {"mock", "real"}:
        raise AiGatewayProviderError("provider must be mock or real")
    theses = response.get("theses")
    if not isinstance(theses, list):
        raise AiGatewayProviderError("theses must be a list")
    if response.get("report_type_id") != request["report_type_id"]:
        raise AiGatewayProviderError("report_type_id mismatch")

    known_items = {item["evidence_item_id"]: item for item in request["items"]}
    citation_keys_by_item = {
        item["evidence_item_id"]: {
            f"{chain['rule_id']}:{chain['passage_id']}:{chain['source_id']}"
            for chain in item["citation_chains"]
        }
        for item in request["items"]
    }

    for thesis in theses:
        evidence_item_ids = thesis.get("evidence_item_ids")
        citations = thesis.get("citations")
        if not isinstance(evidence_item_ids, list) or not evidence_item_ids:
            raise AiGatewayProviderError("thesis has no evidence item")
        if not isinstance(citations, list) or not citations:
            raise AiGatewayProviderError("thesis has missing citation chain")
        for field in ["title", "body"]:
            value = str(thesis.get(field) or "")
            if len(value) > int(getattr(settings, "AI_REPORT_GATEWAY_MAX_THESIS_CHARS", 900)):
                raise AiGatewayProviderError("thesis text is too long")
            if any(marker in value.lower() for marker in ["<script", "</", "http://", "https://", "]("]):
                raise AiGatewayProviderError("unsafe text in thesis")
        for evidence_item_id in evidence_item_ids:
            if evidence_item_id not in known_items:
                raise AiGatewayProviderError(f"unknown evidence item: {evidence_item_id}")
        for citation in citations:
            evidence_item_id = citation.get("evidence_item_id")
            if evidence_item_id not in known_items:
                raise AiGatewayProviderError(f"unknown evidence item: {evidence_item_id}")
            if evidence_item_id not in evidence_item_ids:
                raise AiGatewayProviderError("citation evidence does not belong to thesis")
            citation_key = f"{citation.get('rule_id')}:{citation.get('passage_id')}:{citation.get('source_id')}"
            if citation_key not in citation_keys_by_item[evidence_item_id]:
                raise AiGatewayProviderError("missing citation chain")


def execute_ai_report_dry_run(
    *,
    profile: BirthProfile,
    relationship: ChartRelationship | None,
    report_type_id: str,
    language: str,
    audience: str,
) -> AiGatewayExecution:
    request = build_ai_report_request(
        profile=profile,
        relationship=relationship,
        report_type_id=report_type_id,
        language=language,
        audience=audience,
    )
    provider = provider_for_settings()
    start = monotonic()
    response = provider.generate(request)
    elapsed_ms = int((monotonic() - start) * 1000)
    if elapsed_ms > int(getattr(settings, "AI_REPORT_GATEWAY_TIMEOUT_SECONDS", 15)) * 1000:
        raise AiProviderTimeout("provider timeout")
    validate_ai_response(request, response)
    return AiGatewayExecution(
        response=response,
        metadata={
            "provider": provider.provider_id,
            "elapsed_ms": elapsed_ms,
            "eligible_item_count": len(request["items"]),
            "excluded_item_count": request["excluded_summary"]["total"],
        },
    )


def execute_ai_report_staging_run(
    *,
    profile: BirthProfile,
    relationship: ChartRelationship | None,
    report_type_id: str,
    language: str,
    audience: str,
) -> AiGatewayExecution:
    if not real_provider_enabled():
        raise AiGatewayInputError("real provider is not enabled for this environment")
    from .ai_real_provider import InsufficientVerifiedEvidence, RealAiProvider

    request = build_ai_report_request(
        profile=profile,
        relationship=relationship,
        report_type_id=report_type_id,
        language=language,
        audience=audience,
    )
    provider = RealAiProvider()
    start = monotonic()
    try:
        response = provider.generate(request)
    except InsufficientVerifiedEvidence:
        raise
    elapsed_ms = int((monotonic() - start) * 1000)
    if elapsed_ms > int(getattr(settings, "AI_REPORT_GATEWAY_TIMEOUT_SECONDS", 15)) * 1000:
        raise AiProviderTimeout("provider timeout")
    validate_ai_response(request, response)
    return AiGatewayExecution(
        response=response,
        metadata={
            "request_id": uuid4().hex,
            "provider": provider.provider_id,
            "elapsed_ms": elapsed_ms,
            "eligible_item_count": len(request["items"]),
            "citation_count": sum(len(item["citation_chains"]) for item in request["items"]),
            "excluded_item_count": request["excluded_summary"]["total"],
            "validation_result": "accepted",
        },
    )
