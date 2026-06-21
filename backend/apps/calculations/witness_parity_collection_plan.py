from __future__ import annotations

from typing import Any

from apps.calculations.witness_parity_command_smoke_matrix import build_witness_parity_command_smoke_matrix
from apps.calculations.witness_parity_ops_bundle import build_witness_parity_ops_bundle
from apps.calculations.witness_parity_release_gate import build_witness_parity_release_gate
from apps.calculations.witness_parity_report_availability import build_witness_parity_report_availability


SCHEMA_VERSION = "witness-parity-collection-plan.v1"


def build_witness_parity_collection_plan(
    summary_or_roadmap_or_ops_bundle: dict[str, Any],
    *,
    report_availability: dict[str, Any] | None = None,
    command_smoke_matrix: dict[str, Any] | None = None,
) -> dict[str, Any]:
    availability = report_availability if isinstance(report_availability, dict) else build_witness_parity_report_availability()
    smoke_matrix = command_smoke_matrix if isinstance(command_smoke_matrix, dict) else build_witness_parity_command_smoke_matrix()
    ops_bundle = build_witness_parity_ops_bundle(
        summary_or_roadmap_or_ops_bundle,
        limit=0,
        report_availability=availability,
    )
    release_gate = build_witness_parity_release_gate(
        ops_bundle,
        command_smoke_matrix=smoke_matrix,
        limit=0,
    )
    actions_by_key = _actions_by_key(ops_bundle.get("next_actions"))

    collect_report: list[dict[str, Any]] = []
    review_witness_rows: list[dict[str, Any]] = []
    ready_for_demo: list[dict[str, Any]] = []
    for row in _availability_rows(availability):
        key = str(row.get("key") or "")
        label = str(row.get("label") or "")
        if row.get("state") == "missing":
            collect_report.append(
                {
                    "key": key,
                    "label": label,
                    "status": "missing_report",
                    "action": "collect report",
                    "release_blocker": True,
                    "command_hint": _safe_collection_hint(row.get("collection_hint")),
                }
            )
            continue

        action = actions_by_key.get(key, {})
        if action.get("state") == "review":
            review_witness_rows.append(
                {
                    "key": key,
                    "label": label,
                    "status": "review",
                    "action": "review witness rows",
                    "release_blocker": True,
                }
            )
        elif action.get("state") == "ready":
            ready_for_demo.append(
                {
                    "key": key,
                    "label": label,
                    "status": "ready",
                    "action": "ready for demo",
                    "release_blocker": False,
                }
            )

    availability_totals = availability.get("totals") if isinstance(availability.get("totals"), dict) else {}
    return {
        "schema_version": SCHEMA_VERSION,
        "report_availability": {
            "domain_count": _safe_int(availability_totals.get("domain_count")),
            "present_count": _safe_int(availability_totals.get("present_count")),
            "missing_count": _safe_int(availability_totals.get("missing_count")),
        },
        "release_gate_status": str(release_gate.get("status") or ""),
        "command_smoke_matrix_status": str(smoke_matrix.get("status") or ""),
        "groups": {
            "collect_report": collect_report,
            "review_witness_rows": review_witness_rows,
            "ready_for_demo": ready_for_demo,
        },
    }


def _availability_rows(availability: dict[str, Any]) -> list[dict[str, Any]]:
    rows = availability.get("domains")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _actions_by_key(rows: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        return {}
    return {str(row.get("key") or ""): row for row in rows if isinstance(row, dict)}


def _safe_collection_hint(value: Any) -> str:
    hint = str(value or "")
    if "<report-json>" not in hint:
        return ""
    return hint


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
