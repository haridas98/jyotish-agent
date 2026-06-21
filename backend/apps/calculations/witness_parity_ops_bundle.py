from __future__ import annotations

from typing import Any

from apps.calculations.witness_parity_gap_queue import (
    SCHEMA_VERSION as GAP_QUEUE_SCHEMA_VERSION,
    build_witness_parity_gap_queue,
)
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
) -> dict[str, Any]:
    generated_from_schema_version = _source_schema(summary_or_roadmap)
    roadmap = (
        summary_or_roadmap
        if summary_or_roadmap.get("schema_version") == ROADMAP_SCHEMA_VERSION
        else build_witness_parity_roadmap(summary_or_roadmap)
    )
    gap_queue = build_witness_parity_gap_queue(roadmap)
    full_rows = gap_queue.get("queue", [])
    filtered_rows = [row for row in full_rows if not states or row.get("state") in states]
    if limit > 0:
        filtered_rows = filtered_rows[:limit]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from_schema_version": generated_from_schema_version,
        "roadmap_totals": _safe_totals(roadmap.get("totals")),
        "gap_queue_totals": _safe_totals(gap_queue.get("totals")),
        "priority_totals": {priority: sum(1 for row in full_rows if row.get("priority") == priority) for priority in _PRIORITIES},
        "state_totals": {state: sum(1 for row in full_rows if row.get("state") == state) for state in _STATES},
        "next_actions": [_safe_action_row(row) for row in filtered_rows],
    }


def _safe_action_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
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
