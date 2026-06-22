from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-attachment-handoff-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P63-A"
STATUS = "blocked_pending_operator_evidence"
P61_WORK_ORDER_STATUS = "pending_not_attached"
CASE_WORK_ORDER_STATUS = "blocked_pending_attachments"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_OPERATOR_SEQUENCE_LABELS = [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_attachment_work_orders_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
]
SAFE_VALIDATION_COMMAND_FAMILIES = [
    "build_witness_core_evidence_attachment_handoff_report",
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
BLOCKED_NOTE = "External evidence has not been attached; handoff rows are labels only and do not collect evidence."


def build_witness_core_evidence_attachment_handoff_report(
    *,
    work_orders_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(work_orders_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    source_work_orders = [row for row in source.get("work_orders", []) if isinstance(row, dict)]
    source_cases = [
        row for row in source.get("case_attachment_work_order_manifest", []) if isinstance(row, dict)
    ]
    orders_by_case = _orders_by_case(source_work_orders)
    handoff_cases = [
        _case_handoff_row(row, case_handoff_index=index, source_orders=orders_by_case.get(str(row.get("case_id") or ""), []))
        for index, row in enumerate(source_cases, start=1)
    ]
    handoff_orders: list[dict[str, Any]] = []
    for case in handoff_cases:
        case_id = case["case_id"]
        source_orders = orders_by_case.get(case_id, [])
        for source_order in source_orders:
            handoff_orders.append(
                _handoff_work_order_row(
                    source_order,
                    case_handoff_index=case["case_handoff_index"],
                    handoff_work_order_index=len(handoff_orders) + 1,
                )
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if handoff_orders else "empty",
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_work_order_rows": _safe_int(source_summary.get("work_order_rows", len(source_work_orders))),
            "source_case_work_order_rows": _safe_int(
                source_summary.get("case_work_order_rows", len(source_cases))
            ),
            "case_handoff_rows": len(handoff_cases),
            "handoff_work_order_rows": len(handoff_orders),
            "pending_handoff_count": len(handoff_orders),
            "pending_jhora_handoff_count": sum(
                1 for row in handoff_orders if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_handoff_count": sum(
                1 for row in handoff_orders if row["evidence_family"] == "parashara_light_manual_values_or_packet"
            ),
            "blocked_case_count": len(handoff_cases),
            "ready_to_mark_count": 0,
            "attached_evidence_files_count": _safe_int(source_summary.get("attached_evidence_files_count")),
            "attached_evidence_family_count": _safe_int(source_summary.get("attached_evidence_family_count")),
            "missing_attachment_slot_count": _safe_int(
                source_summary.get("missing_attachment_slot_count", len(handoff_orders))
            ),
            "remaining_not_reviewed_count": _safe_int(source_summary.get("remaining_not_reviewed_count")),
            "release_gate_status": _safe_status(source_summary.get("release_gate_status"), fallback="blocked"),
            "command_smoke_matrix_status": _safe_status(
                source_summary.get("command_smoke_matrix_status"),
                fallback="ready",
            ),
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "case_handoff_rows": handoff_cases,
        "handoff_work_order_rows": handoff_orders,
    }


def _case_handoff_row(
    row: dict[str, Any],
    *,
    case_handoff_index: int,
    source_orders: list[dict[str, Any]],
) -> dict[str, Any]:
    work_order_statuses = {
        order["evidence_family"]: _safe_work_order_status(order.get("work_order_status"))
        for order in source_orders
        if str(order.get("evidence_family") or "") in REQUIRED_EVIDENCE_FAMILIES
    }
    return {
        "case_handoff_index": case_handoff_index,
        "case_id": str(row.get("case_id") or ""),
        "source_work_order_indices": [_safe_int(order.get("work_order_index")) for order in source_orders],
        "required_evidence_families": REQUIRED_EVIDENCE_FAMILIES,
        "work_order_statuses": work_order_statuses,
        "case_handoff_status": STATUS,
        "case_work_order_status": _safe_case_work_order_status(row.get("case_work_order_status")),
        "ready_to_mark": False,
        "safe_operator_sequence_labels": SAFE_OPERATOR_SEQUENCE_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "blocked_note": BLOCKED_NOTE,
    }


def _handoff_work_order_row(
    row: dict[str, Any],
    *,
    case_handoff_index: int,
    handoff_work_order_index: int,
) -> dict[str, Any]:
    return {
        "handoff_work_order_index": handoff_work_order_index,
        "source_work_order_index": _safe_int(row.get("work_order_index")),
        "case_handoff_index": case_handoff_index,
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": _safe_evidence_family(row.get("evidence_family")),
        "p57_evidence_slot_status": "missing",
        "p59_attachment_slot_status": "not_attached",
        "p61_work_order_status": _safe_work_order_status(row.get("work_order_status")),
        "p63_handoff_status": STATUS,
        "ready_to_mark": False,
        "safe_action_label": _safe_action_label(row.get("safe_action_label"), row.get("evidence_family")),
        "blocked_note": BLOCKED_NOTE,
    }


def _orders_by_case(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        case_id = str(row.get("case_id") or "")
        if case_id:
            grouped[case_id].append(row)
    for case_rows in grouped.values():
        case_rows.sort(key=lambda row: _safe_int(row.get("work_order_index")))
    return dict(grouped)


def _safe_action_label(value: Any, family: Any) -> str:
    text = str(value or "")
    if text in {"collect_jhora_screenshot", "attach_parashara_light_manual_values"}:
        return text
    return (
        "collect_jhora_screenshot"
        if str(family or "") == "jhora_screenshot_or_packet"
        else "attach_parashara_light_manual_values"
    )


def _safe_case_work_order_status(value: Any) -> str:
    text = str(value or "")
    return text if text == CASE_WORK_ORDER_STATUS else CASE_WORK_ORDER_STATUS


def _safe_evidence_family(value: Any) -> str:
    text = str(value or "")
    return text if text in REQUIRED_EVIDENCE_FAMILIES else "jhora_screenshot_or_packet"


def _safe_work_order_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P61_WORK_ORDER_STATUS else P61_WORK_ORDER_STATUS


def _safe_status(value: Any, *, fallback: str) -> str:
    text = str(value or "")
    return text if text in {"blocked", "ready"} else fallback


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
