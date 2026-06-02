from __future__ import annotations

from typing import Any

from .yoga_catalog import yoga_registry

YOGA_CATALOG_ALIASES = {
    "amala_chandra": "amala",
}


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
        "definition_scope": str(catalog_row.get("definition_scope") or ""),
        "detection_status": str(catalog_row.get("detection_status") or ""),
        "citation_policy": str(catalog_row.get("citation_policy") or ""),
        "review_status": _enum_value(catalog_row.get("review_status")),
        "vaishnava_guard": str(catalog_row.get("vaishnava_guard") or ""),
        "public_explanation_outline": str(catalog_row.get("public_explanation_outline") or ""),
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
        "bodies": list(detected.get("bodies") or []),
        "reference": str(detected.get("reference") or ""),
    }


def _enum_value(value: Any) -> str:
    return str(getattr(value, "value", value) or "")
