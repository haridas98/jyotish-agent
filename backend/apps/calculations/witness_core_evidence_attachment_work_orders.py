from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-attachment-work-orders-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P61-A"
STATUS = "blocked_pending_attachments"
WORK_ORDER_STATUS = "pending_not_attached"
CASE_WORK_ORDER_STATUS = "blocked_pending_attachments"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_VALIDATION_COMMANDS = [
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
OPERATOR_NOTE = (
    "Evidence must be attached before mark commands are attempted; "
    "work orders are labels only and do not collect evidence."
)


def build_witness_core_evidence_attachment_work_orders_report(
    *,
    attachment_gate_report_path: str | Path,
) -> dict[str, Any]:
    gate = _read_json(Path(attachment_gate_report_path))
    gate_summary = gate.get("summary") if isinstance(gate.get("summary"), dict) else {}
    attachment_rows = [row for row in gate.get("rows", []) if isinstance(row, dict)]
    work_orders: list[dict[str, Any]] = []
    case_manifest: list[dict[str, Any]] = []
    for case_index, row in enumerate(attachment_rows, start=1):
        case_work_orders = [
            _work_order(row, case_attachment_index=case_index, evidence_family=family)
            for family in REQUIRED_EVIDENCE_FAMILIES
        ]
        for order in case_work_orders:
            order["work_order_index"] = len(work_orders) + 1
            work_orders.append(order)
        case_manifest.append(_case_manifest_row(row, case_work_orders=case_work_orders))
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if work_orders else "empty",
        "operator_note": OPERATOR_NOTE,
        "summary": {
            "source_attachment_rows": _safe_int(gate_summary.get("attachment_rows", len(attachment_rows))),
            "source_operator_attachment_manifest_rows": _safe_int(
                gate_summary.get("operator_attachment_manifest_rows")
            ),
            "case_work_order_rows": len(case_manifest),
            "work_order_rows": len(work_orders),
            "pending_work_order_count": len(work_orders),
            "pending_jhora_work_order_count": sum(
                1 for row in work_orders if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_work_order_count": sum(
                1 for row in work_orders if row["evidence_family"] == "parashara_light_manual_values_or_packet"
            ),
            "ready_to_mark_count": 0,
            "blocked_case_count": len(case_manifest),
            "attached_evidence_files_count": _safe_int(gate_summary.get("attached_evidence_files_count")),
            "attached_evidence_family_count": _safe_int(gate_summary.get("attached_evidence_family_count")),
            "missing_attachment_slot_count": _safe_int(
                gate_summary.get("missing_attachment_slot_count", len(work_orders))
            ),
            "remaining_not_reviewed_count": _safe_int(gate_summary.get("remaining_not_reviewed_count")),
            "release_gate_status": _safe_status(gate_summary.get("release_gate_status"), fallback="blocked"),
            "command_smoke_matrix_status": _safe_status(
                gate_summary.get("command_smoke_matrix_status"),
                fallback="ready",
            ),
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "work_orders": work_orders,
        "case_attachment_work_order_manifest": case_manifest,
    }


def _work_order(
    row: dict[str, Any],
    *,
    case_attachment_index: int,
    evidence_family: str,
) -> dict[str, Any]:
    return {
        "work_order_index": 0,
        "case_attachment_index": case_attachment_index,
        "attachment_index": _safe_int(row.get("attachment_index")) or case_attachment_index,
        "readiness_index": _safe_int(row.get("readiness_index")) or case_attachment_index,
        "intake_index": _safe_int(row.get("intake_index")) or case_attachment_index,
        "candidate_index": _safe_int(row.get("candidate_index")),
        "case_id": str(row.get("case_id") or ""),
        "source_family": _safe_source_family(row.get("source_family")),
        "evidence_family": evidence_family,
        "p57_evidence_slot_status": "missing",
        "p59_attachment_slot_status": "not_attached",
        "work_order_status": WORK_ORDER_STATUS,
        "ready_to_mark": False,
        "safe_action_label": _safe_action_for_family(evidence_family),
        "safe_validation_command_families": SAFE_VALIDATION_COMMANDS,
        "blocked_note": OPERATOR_NOTE,
    }


def _case_manifest_row(row: dict[str, Any], *, case_work_orders: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "case_attachment_index": case_work_orders[0]["case_attachment_index"] if case_work_orders else 0,
        "attachment_index": _safe_int(row.get("attachment_index")),
        "case_id": str(row.get("case_id") or ""),
        "source_family": _safe_source_family(row.get("source_family")),
        "work_order_indices": [order["work_order_index"] for order in case_work_orders],
        "family_statuses": {
            order["evidence_family"]: order["work_order_status"]
            for order in case_work_orders
            if order["evidence_family"] in REQUIRED_EVIDENCE_FAMILIES
        },
        "case_work_order_status": CASE_WORK_ORDER_STATUS,
        "ready_to_mark": False,
        "safe_action_labels": [_safe_action_for_family(family) for family in REQUIRED_EVIDENCE_FAMILIES],
        "validation_command_families": SAFE_VALIDATION_COMMANDS,
        "blocked_note": OPERATOR_NOTE,
    }


def _safe_action_for_family(family: str) -> str:
    if family == "jhora_screenshot_or_packet":
        return "collect_jhora_screenshot"
    return "attach_parashara_light_manual_values"


def _safe_status(value: Any, *, fallback: str) -> str:
    text = str(value or "")
    return text if text in {"blocked", "ready"} else fallback


def _safe_source_family(value: Any) -> str:
    text = str(value or "")
    return text if text in {"jhora", "parashara_light", "both", "none"} else "none"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
