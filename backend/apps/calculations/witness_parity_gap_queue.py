from __future__ import annotations

from typing import Any

from apps.calculations.witness_parity_roadmap import (
    PARITY_ROADMAP_DOMAINS,
    SCHEMA_VERSION as ROADMAP_SCHEMA_VERSION,
    build_witness_parity_roadmap,
)


SCHEMA_VERSION = "witness-parity-gap-queue.v1"

_STATE_ORDER = {"review": 0, "waiting": 1, "ready": 2}
_DOMAIN_ORDER = {key: index for index, (key, _label) in enumerate(PARITY_ROADMAP_DOMAINS)}


def build_witness_parity_gap_queue(summary_or_roadmap: dict[str, Any]) -> dict[str, Any]:
    generated_from_schema_version = _source_schema(summary_or_roadmap)
    roadmap = (
        summary_or_roadmap
        if summary_or_roadmap.get("schema_version") == ROADMAP_SCHEMA_VERSION
        else build_witness_parity_roadmap(summary_or_roadmap)
    )
    rows = [_queue_row(row) for row in roadmap.get("domains", []) if isinstance(row, dict)]
    rows.sort(key=_queue_sort_key)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from_schema_version": generated_from_schema_version,
        "queue": rows,
        "totals": {
            "queued_count": len(rows),
            "review_count": sum(1 for row in rows if row["state"] == "review"),
            "waiting_count": sum(1 for row in rows if row["state"] == "waiting"),
            "ready_count": sum(1 for row in rows if row["state"] == "ready"),
        },
    }


def _queue_row(roadmap_row: dict[str, Any]) -> dict[str, Any]:
    state = str(roadmap_row.get("state") or "waiting")
    if state not in _STATE_ORDER:
        state = "waiting"
    failed_count = _safe_int(roadmap_row.get("failed_count"))
    blocker_count = _safe_int(roadmap_row.get("blocker_count"))
    readiness_gap_count = _safe_int(roadmap_row.get("readiness_gap_count"))
    return {
        "key": str(roadmap_row.get("key") or ""),
        "label": str(roadmap_row.get("label") or ""),
        "state": state,
        "priority": _priority(state, failed_count, blocker_count, readiness_gap_count),
        "reason": _reason(state),
        "next_action": _next_action(state),
        "failed_count": failed_count,
        "blocker_count": blocker_count,
        "readiness_gap_count": readiness_gap_count,
        "target_reviewed_count": _safe_int(roadmap_row.get("target_reviewed_count")),
        "passed_count": _safe_int(roadmap_row.get("passed_count")),
    }


def _queue_sort_key(row: dict[str, Any]) -> tuple[int, int, int]:
    severity = row["failed_count"] + row["blocker_count"] + row["readiness_gap_count"]
    return (_STATE_ORDER.get(row["state"], 1), -severity, _DOMAIN_ORDER.get(row["key"], len(_DOMAIN_ORDER)))


def _priority(state: str, failed_count: int, blocker_count: int, readiness_gap_count: int) -> str:
    if state == "review" and failed_count + blocker_count + readiness_gap_count > 0:
        return "high"
    if state in {"review", "waiting"}:
        return "medium"
    return "low"


def _reason(state: str) -> str:
    if state == "ready":
        return "ready for demo"
    if state == "waiting":
        return "collect report"
    return "needs witness review"


def _next_action(state: str) -> str:
    if state == "ready":
        return "ready for demo"
    if state == "waiting":
        return "collect report"
    return "review witness rows"


def _source_schema(summary_or_roadmap: dict[str, Any]) -> str:
    schema_version = summary_or_roadmap.get("schema_version")
    if schema_version == ROADMAP_SCHEMA_VERSION:
        return ROADMAP_SCHEMA_VERSION
    return str(schema_version or "witness-summary")


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
