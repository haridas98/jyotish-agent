from __future__ import annotations

from typing import Any

from apps.calculations.shastra_audit import CALCULATION_SHASTRA_AUDIT
from apps.sources.coverage import source_coverage_matrix

from .shastra_catalog import explanation_schedule
from .yoga_catalog import yoga_registry


def shastra_condition_matrix() -> dict[str, Any]:
    calculation_inputs = list(CALCULATION_SHASTRA_AUDIT)
    section_inputs = explanation_schedule()
    yoga_inputs = yoga_registry()
    coverage_layers = iter(
        source_coverage_matrix(
            [
                *[_calculation_coverage_target(row) for row in calculation_inputs],
                *[_section_coverage_target(row) for row in section_inputs],
                *[_yoga_coverage_target(row) for row in yoga_inputs],
            ]
        )["layers"]
    )
    calculation_rows = [_calculation_row(row, next(coverage_layers)) for row in calculation_inputs]
    section_rows = [_section_row(row, next(coverage_layers)) for row in section_inputs]
    yoga_rows = [_yoga_row(row, next(coverage_layers)) for row in yoga_inputs]
    conditions = calculation_rows + section_rows + yoga_rows
    return {
        "schema_version": "jyotish-shastra-condition-matrix-v1",
        "summary": {
            "total_conditions": len(conditions),
            "calculation_layers": len(calculation_rows),
            "report_sections": len(section_rows),
            "yoga_conditions": len(yoga_rows),
            "conditions_needing_exact_mapping": sum(
                1 for row in conditions if row["needs_exact_mapping"]
            ),
            "public_release_policy": "approved_passage_required_for_final_interpretation",
        },
        "conditions": conditions,
    }


def _calculation_row(row: dict[str, Any], coverage: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "calculation_layer",
        "key": str(row["key"]),
        "title": str(row["label"]),
        "condition_summary": str(row.get("source_basis") or ""),
        "source_priority": _string_list(row.get("source_priority")),
        "implementation_status": str(row.get("implementation_status") or ""),
        "public_claim": str(row.get("public_claim") or ""),
        "public_release_policy": _release_policy(coverage),
        "coverage_status": coverage["coverage_status"],
        "needs_exact_mapping": bool(coverage["needs_exact_mapping"]),
        "search_queries": _queries(str(row["label"]), _string_list(row.get("source_priority"))),
    }


def _section_row(row: dict[str, Any], coverage: dict[str, Any]) -> dict[str, Any]:
    source_priority = _string_list(row.get("source_priority"))
    return {
        "kind": "report_section",
        "key": str(row["key"]),
        "title": str(row.get("title_ru") or row["key"]),
        "condition_summary": "Report section requiring shastra-grounded explanation.",
        "depends_on": _string_list(row.get("depends_on")),
        "source_priority": source_priority,
        "implementation_status": str(row.get("implementation_status") or ""),
        "public_release_policy": _release_policy(coverage),
        "coverage_status": coverage["coverage_status"],
        "needs_exact_mapping": bool(coverage["needs_exact_mapping"]),
        "search_queries": _queries(str(row.get("title_ru") or row["key"]), source_priority),
    }


def _yoga_row(row: dict[str, Any], coverage: dict[str, Any]) -> dict[str, Any]:
    title = str(row.get("name") or row["key"])
    source_priority = _string_list(row.get("source_priority"))
    return {
        "kind": "yoga_condition",
        "key": str(row["key"]),
        "title": title,
        "category": str(row.get("category") or ""),
        "rarity": str(row.get("rarity") or ""),
        "condition_summary": str(row.get("definition_scope") or ""),
        "detection_status": str(row.get("detection_status") or ""),
        "source_priority": source_priority,
        "citation_policy": str(row.get("citation_policy") or ""),
        "vaishnava_guard": str(row.get("vaishnava_guard") or ""),
        "public_release_policy": _release_policy(coverage),
        "coverage_status": coverage["coverage_status"],
        "needs_exact_mapping": bool(coverage["needs_exact_mapping"]),
        "search_queries": _queries(title, source_priority),
    }


def _calculation_coverage_target(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": str(row["key"]),
        "label": str(row["label"]),
        "source_priority": _string_list(row.get("source_priority")),
        "source_basis": str(row.get("source_basis") or ""),
    }


def _section_coverage_target(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": str(row["key"]),
        "label": str(row.get("title_ru") or row["key"]),
        "source_priority": _string_list(row.get("source_priority")),
    }


def _yoga_coverage_target(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": str(row["key"]),
        "label": str(row.get("name") or row["key"]),
        "source_priority": _string_list(row.get("source_priority")),
        "source_basis": str(row.get("definition_scope") or ""),
    }


def _release_policy(coverage: dict[str, Any]) -> str:
    if coverage["needs_exact_mapping"]:
        return "needs_approved_passage"
    return "approved_for_public_interpretation"


def _queries(title: str, source_priority: list[str]) -> list[str]:
    return [f"{title} {source}" for source in source_priority]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)]
