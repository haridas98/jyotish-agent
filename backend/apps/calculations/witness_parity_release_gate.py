from __future__ import annotations

from typing import Any

from apps.calculations.witness_parity_ops_bundle import (
    SCHEMA_VERSION as OPS_BUNDLE_SCHEMA_VERSION,
    build_witness_parity_ops_bundle,
)
from apps.calculations.witness_parity_roadmap import SCHEMA_VERSION as ROADMAP_SCHEMA_VERSION


SCHEMA_VERSION = "witness-parity-release-gate.v1"


def build_witness_parity_release_gate(
    summary_or_roadmap_or_ops_bundle: dict[str, Any],
    *,
    limit: int = 0,
) -> dict[str, Any]:
    generated_from_schema_version = _source_schema(summary_or_roadmap_or_ops_bundle)
    ops_bundle = (
        summary_or_roadmap_or_ops_bundle
        if summary_or_roadmap_or_ops_bundle.get("schema_version") == OPS_BUNDLE_SCHEMA_VERSION
        else build_witness_parity_ops_bundle(summary_or_roadmap_or_ops_bundle, limit=0)
    )
    state_totals = ops_bundle.get("state_totals") if isinstance(ops_bundle.get("state_totals"), dict) else {}
    priority_totals = ops_bundle.get("priority_totals") if isinstance(ops_bundle.get("priority_totals"), dict) else {}
    review_count = _safe_int(state_totals.get("review"))
    waiting_count = _safe_int(state_totals.get("waiting"))
    high_priority_count = _safe_int(priority_totals.get("high"))
    full_actions = [_safe_required_action(row) for row in _required_action_rows(ops_bundle.get("next_actions"))]
    shown_actions = full_actions if limit <= 0 else full_actions[:limit]
    status = "ready" if review_count == 0 and waiting_count == 0 and high_priority_count == 0 else "blocked"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from_schema_version": generated_from_schema_version,
        "status": status,
        "criteria": {
            "review_domains": {"threshold": 0, "observed": review_count},
            "waiting_domains": {"threshold": 0, "observed": waiting_count},
            "high_priority_domains": {"threshold": 0, "observed": high_priority_count},
        },
        "blocker_totals": {
            "review_count": review_count,
            "waiting_count": waiting_count,
            "high_priority_count": high_priority_count,
            "action_count": len(full_actions),
        },
        "required_actions": shown_actions,
    }


def _required_action_rows(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    return [
        row
        for row in rows
        if isinstance(row, dict)
        and (row.get("state") != "ready" or str(row.get("priority") or "").lower() in {"high", "medium"})
    ]


def _safe_required_action(row: dict[str, Any]) -> dict[str, Any]:
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
    }


def _source_schema(summary_or_roadmap_or_ops_bundle: dict[str, Any]) -> str:
    schema_version = summary_or_roadmap_or_ops_bundle.get("schema_version")
    if schema_version in {OPS_BUNDLE_SCHEMA_VERSION, ROADMAP_SCHEMA_VERSION}:
        return str(schema_version)
    return str(schema_version or "witness-summary")


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
