from __future__ import annotations

from typing import Any

from apps.sources.models import ReviewStatus

from .models import ShastraConditionEvidence
from .yoga_catalog import yoga_registry

YOGA_CATALOG_ALIASES = {}


def detected_yoga_source_map(chart: dict[str, Any]) -> list[dict[str, Any]]:
    catalog = {str(yoga.get("key")): yoga for yoga in yoga_registry()}
    rows = []
    for detected in _detected_yogas(chart):
        key = str(detected.get("key") or "")
        if not key:
            continue
        catalog_key = YOGA_CATALOG_ALIASES.get(key, key)
        catalog_row = catalog.get(catalog_key)
        if catalog_row is None:
            rows.append(_unmapped_row(detected, key))
            continue
        rows.append(_mapped_row(detected, catalog_row, key, catalog_key))
    return rows


def _detected_yogas(chart: dict[str, Any]) -> list[dict[str, Any]]:
    yogas = (((chart.get("classical") or {}).get("yogas") or {}).get("items") or [])
    return [yoga for yoga in yogas if isinstance(yoga, dict)]


def _mapped_row(
    detected: dict[str, Any],
    catalog_row: dict[str, Any],
    key: str,
    catalog_key: str,
) -> dict[str, Any]:
    formula = dict(catalog_row.get("formula") or {})
    source_anchors = list(catalog_row.get("source_anchors") or [])
    anchor_status = str(catalog_row.get("source_anchor_status") or "")
    evidence = _evidence_counts(catalog_key)
    return {
        "key": key,
        "catalog_key": catalog_key,
        "name": str(detected.get("name") or catalog_row.get("name") or key),
        "detected_status": str(detected.get("status") or ""),
        "source_mapping_status": "mapped_research_only",
        "public_release_policy": "needs_approved_passage",
        "category": str(catalog_row.get("category") or ""),
        "rarity": str(catalog_row.get("rarity") or ""),
        "source_priority": list(catalog_row.get("source_priority") or []),
        "formula": formula,
        "source_anchors": source_anchors,
        "source_anchor_status": anchor_status,
        "definition_scope": str(catalog_row.get("definition_scope") or ""),
        "detection_status": str(catalog_row.get("detection_status") or ""),
        "citation_policy": str(catalog_row.get("citation_policy") or ""),
        "review_status": _enum_value(catalog_row.get("review_status")),
        "vaishnava_guard": str(catalog_row.get("vaishnava_guard") or ""),
        "public_explanation_outline": str(catalog_row.get("public_explanation_outline") or ""),
        **evidence,
        "explanation_plan": _explanation_plan(
            formula=formula,
            source_anchors=source_anchors,
            anchor_status=anchor_status,
            vaishnava_guard=str(catalog_row.get("vaishnava_guard") or ""),
            approved_citation_count=int(evidence["approved_citation_count"]),
        ),
        "bodies": list(detected.get("bodies") or []),
        "reference": str(detected.get("reference") or ""),
    }


def _unmapped_row(detected: dict[str, Any], key: str) -> dict[str, Any]:
    return {
        "key": key,
        "name": str(detected.get("name") or key),
        "detected_status": str(detected.get("status") or ""),
        "source_mapping_status": "missing_catalog_entry",
        "public_release_policy": "block_public_interpretation",
        "citation_policy": "required_for_public_interpretation",
        "review_status": "needs_catalog_entry",
        "source_link_count": 0,
        "evidence_status": "missing",
        "approved_citation_count": 0,
        "formula": {},
        "source_anchors": [],
        "source_anchor_status": "missing_catalog_entry",
        "explanation_plan": {
            "condition": "",
            "primary_reference": {},
            "source_summary": "",
            "interpretation_hint": "",
            "gaudiya_guard": "",
            "client_text_sequence": [
                "condition",
                "shastra_reference",
                "chart_evidence",
                "qualified_interpretation",
                "gaudiya_guard",
            ],
            "citation_status": "missing_catalog_entry",
        },
        "bodies": list(detected.get("bodies") or []),
        "reference": str(detected.get("reference") or ""),
    }


def _explanation_plan(
    *,
    formula: dict[str, Any],
    source_anchors: list[dict[str, Any]],
    anchor_status: str,
    vaishnava_guard: str,
    approved_citation_count: int,
) -> dict[str, Any]:
    primary = source_anchors[0] if source_anchors else {}
    citation_status = "approved_public_quote_ready" if approved_citation_count else anchor_status
    return {
        "condition": str(formula.get("description") or primary.get("condition_formula") or ""),
        "primary_reference": {
            "work_title": str(primary.get("work_title") or ""),
            "reference": str(primary.get("reference") or ""),
            "reference_status": str(primary.get("reference_status") or ""),
            "source_url": str(primary.get("source_url") or ""),
        }
        if primary
        else {},
        "source_summary": str(primary.get("source_summary") or ""),
        "interpretation_hint": str(primary.get("interpretation_hint") or ""),
        "gaudiya_guard": vaishnava_guard,
        "client_text_sequence": [
            "condition",
            "shastra_reference",
            "chart_evidence",
            "qualified_interpretation",
            "gaudiya_guard",
        ],
        "citation_status": citation_status,
    }


def _evidence_counts(condition_key: str) -> dict[str, Any]:
    queryset = ShastraConditionEvidence.objects.filter(condition_key=condition_key)
    source_link_count = queryset.count()
    approved_count = queryset.filter(
        review_status=ReviewStatus.APPROVED,
        reference_status="approved",
        public_quote_policy="approved_public_quote",
        passage__review_status=ReviewStatus.APPROVED,
    ).count()
    return {
        "source_link_count": source_link_count,
        "evidence_status": "matched" if source_link_count else "missing",
        "approved_citation_count": approved_count,
    }


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value) or "")
