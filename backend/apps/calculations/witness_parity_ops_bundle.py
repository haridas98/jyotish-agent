from __future__ import annotations

from typing import Any

from apps.calculations.witness_parity_gap_queue import (
    SCHEMA_VERSION as GAP_QUEUE_SCHEMA_VERSION,
    build_witness_parity_gap_queue,
)
from apps.calculations.witness_parity_report_availability import build_witness_parity_report_availability
from apps.calculations.witness_parity_roadmap import (
    SCHEMA_VERSION as ROADMAP_SCHEMA_VERSION,
    build_witness_parity_roadmap,
)


SCHEMA_VERSION = "witness-parity-ops-bundle.v1"
_PRIORITIES = ("high", "medium", "low")
_STATES = ("ready", "review", "waiting")


def build_witness_parity_ops_bundle(
    summary_or_roadmap: dict[str, Any],
    *,
    limit: int = 0,
    states: set[str] | None = None,
    report_availability: dict[str, Any] | None = None,
) -> dict[str, Any]:
    generated_from_schema_version = _source_schema(summary_or_roadmap)
    roadmap = (
        summary_or_roadmap
        if summary_or_roadmap.get("schema_version") == ROADMAP_SCHEMA_VERSION
        else build_witness_parity_roadmap(summary_or_roadmap)
    )
    availability = report_availability if isinstance(report_availability, dict) else build_witness_parity_report_availability()
    availability_totals = _safe_totals(availability.get("totals"))
    availability_by_key = _availability_by_key(availability)
    gap_queue = build_witness_parity_gap_queue(roadmap)
    full_rows = gap_queue.get("queue", [])
    filtered_rows = [row for row in full_rows if not states or row.get("state") in states]
    safe_rows = [_safe_action_row(row, availability_by_key=availability_by_key) for row in filtered_rows]
    safe_rows.extend(_missing_availability_actions(availability, existing_keys={row.get("key") for row in filtered_rows}, states=states))
    if limit > 0:
        safe_rows = safe_rows[:limit]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from_schema_version": generated_from_schema_version,
        "roadmap_totals": _safe_totals(roadmap.get("totals")),
        "gap_queue_totals": _safe_totals(gap_queue.get("totals")),
        "report_availability_domain_count": _safe_int(availability_totals.get("domain_count")),
        "report_availability_present_count": _safe_int(availability_totals.get("present_count")),
        "report_availability_missing_count": _safe_int(availability_totals.get("missing_count")),
        "priority_totals": {priority: sum(1 for row in full_rows if row.get("priority") == priority) for priority in _PRIORITIES},
        "state_totals": {state: sum(1 for row in full_rows if row.get("state") == state) for state in _STATES},
        "next_actions": safe_rows,
    }


def _safe_action_row(row: dict[str, Any], *, availability_by_key: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    safe = {
        "key": str(row.get("key") or ""),
        "label": str(row.get("label") or ""),
        "state": str(row.get("state") or ""),
        "priority": str(row.get("priority") or ""),
        "reason": str(row.get("reason") or ""),
        "next_action": str(row.get("next_action") or ""),
        "failed_count": _safe_int(row.get("failed_count")),
        "blocker_count": _safe_int(row.get("blocker_count")),
        "readiness_gap_count": _safe_int(row.get("readiness_gap_count")),
        "target_reviewed_count": _safe_int(row.get("target_reviewed_count")),
        "passed_count": _safe_int(row.get("passed_count")),
    }
    availability_row = (availability_by_key or {}).get(safe["key"])
    if safe["state"] == "waiting" and availability_row and availability_row.get("state") == "missing":
        safe["collection_hint"] = _safe_collection_hint(availability_row.get("collection_hint"))
    return safe


def _missing_availability_actions(
    availability: dict[str, Any],
    *,
    existing_keys: set[Any],
    states: set[str] | None,
) -> list[dict[str, Any]]:
    if states and "waiting" not in states:
        return []
    rows = availability.get("domains")
    if not isinstance(rows, list):
        return []
    actions: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("state") != "missing" or row.get("key") in existing_keys:
            continue
        actions.append(
            {
                "key": str(row.get("key") or ""),
                "label": str(row.get("label") or ""),
                "state": "waiting",
                "priority": "medium",
                "reason": "collect report",
                "next_action": "collect report",
                "failed_count": 0,
                "blocker_count": 1,
                "readiness_gap_count": 0,
                "target_reviewed_count": 0,
                "passed_count": 0,
                "collection_hint": _safe_collection_hint(row.get("collection_hint")),
            }
        )
    return actions


def _availability_by_key(availability: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = availability.get("domains")
    if not isinstance(rows, list):
        return {}
    return {str(row.get("key") or ""): row for row in rows if isinstance(row, dict)}


def _safe_collection_hint(value: Any) -> str:
    hint = str(value or "")
    if "<report-json>" not in hint:
        return ""
    return hint


def _safe_totals(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _safe_int(item) for key, item in value.items()}


def _source_schema(summary_or_roadmap: dict[str, Any]) -> str:
    schema_version = summary_or_roadmap.get("schema_version")
    if schema_version == ROADMAP_SCHEMA_VERSION:
        return ROADMAP_SCHEMA_VERSION
    if schema_version == GAP_QUEUE_SCHEMA_VERSION:
        return GAP_QUEUE_SCHEMA_VERSION
    return str(schema_version or "witness-summary")


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
