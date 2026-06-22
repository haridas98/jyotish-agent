from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-operator-packets-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P65-A"
STATUS = "blocked_pending_operator_packet_evidence"
P63_HANDOFF_STATUS = "blocked_pending_operator_evidence"
CASE_WORK_ORDER_STATUS = "blocked_pending_attachments"
EVIDENCE_FILE_STATUS = "not_attached"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_PACKET_SEQUENCE_LABELS = [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_operator_packets_report",
    "rerun_attachment_handoff_report",
    "rerun_attachment_work_orders_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
]
SAFE_VALIDATION_COMMAND_FAMILIES = [
    "build_witness_core_evidence_operator_packets_report",
    "build_witness_core_evidence_attachment_handoff_report",
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
BLOCKED_NOTE = (
    "External evidence has not been attached; operator packets are labels only "
    "and do not collect or attach evidence."
)


def build_witness_core_evidence_operator_packets_report(
    *,
    handoff_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(handoff_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    case_handoffs = [row for row in source.get("case_handoff_rows", []) if isinstance(row, dict)]
    handoff_orders = [row for row in source.get("handoff_work_order_rows", []) if isinstance(row, dict)]
    orders_by_case = _orders_by_case(handoff_orders)

    packet_rows: list[dict[str, Any]] = []
    slot_rows: list[dict[str, Any]] = []
    for packet_index, row in enumerate(case_handoffs, start=1):
        case_id = str(row.get("case_id") or "")
        case_orders = orders_by_case.get(case_id, [])
        slot_indices: list[int] = []
        for source_order in case_orders:
            slot_index = len(slot_rows) + 1
            slot_indices.append(slot_index)
            slot_rows.append(
                _operator_attachment_slot_row(
                    source_order,
                    operator_packet_index=packet_index,
                    operator_attachment_slot_index=slot_index,
                )
            )
        packet_rows.append(
            _operator_packet_row(
                row,
                operator_packet_index=packet_index,
                attachment_slot_indices=slot_indices,
                source_orders=case_orders,
            )
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if packet_rows else "empty",
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_case_handoff_rows": _safe_int(
                source_summary.get("case_handoff_rows", len(case_handoffs))
            ),
            "source_handoff_work_order_rows": _safe_int(
                source_summary.get("handoff_work_order_rows", len(handoff_orders))
            ),
            "operator_packet_rows": len(packet_rows),
            "operator_attachment_slot_rows": len(slot_rows),
            "pending_operator_packet_count": len(packet_rows),
            "pending_operator_attachment_slot_count": len(slot_rows),
            "pending_jhora_attachment_slot_count": sum(
                1 for row in slot_rows if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_attachment_slot_count": sum(
                1
                for row in slot_rows
                if row["evidence_family"] == "parashara_light_manual_values_or_packet"
            ),
            "blocked_packet_count": len(packet_rows),
            "ready_to_mark_count": 0,
            "attached_evidence_files_count": _safe_int(source_summary.get("attached_evidence_files_count")),
            "attached_evidence_family_count": _safe_int(source_summary.get("attached_evidence_family_count")),
            "missing_attachment_slot_count": _safe_int(
                source_summary.get("missing_attachment_slot_count", len(slot_rows))
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
        "operator_packet_rows": packet_rows,
        "operator_attachment_slot_rows": slot_rows,
    }


def _operator_packet_row(
    row: dict[str, Any],
    *,
    operator_packet_index: int,
    attachment_slot_indices: list[int],
    source_orders: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "operator_packet_index": operator_packet_index,
        "case_id": str(row.get("case_id") or ""),
        "source_case_handoff_index": _safe_int(row.get("case_handoff_index")) or operator_packet_index,
        "source_handoff_work_order_indices": [
            _safe_int(order.get("handoff_work_order_index")) for order in source_orders
        ],
        "required_evidence_families": REQUIRED_EVIDENCE_FAMILIES,
        "attachment_slot_indices": attachment_slot_indices,
        "packet_status": STATUS,
        "case_handoff_status": _safe_handoff_status(row.get("case_handoff_status")),
        "case_work_order_status": _safe_case_work_order_status(row.get("case_work_order_status")),
        "ready_to_mark": False,
        "safe_packet_sequence_labels": SAFE_PACKET_SEQUENCE_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "blocked_note": BLOCKED_NOTE,
    }


def _operator_attachment_slot_row(
    row: dict[str, Any],
    *,
    operator_packet_index: int,
    operator_attachment_slot_index: int,
) -> dict[str, Any]:
    return {
        "operator_attachment_slot_index": operator_attachment_slot_index,
        "operator_packet_index": operator_packet_index,
        "source_handoff_work_order_index": _safe_int(row.get("handoff_work_order_index")),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": _safe_evidence_family(row.get("evidence_family")),
        "p57_evidence_slot_status": "missing",
        "p59_attachment_slot_status": "not_attached",
        "p61_work_order_status": "pending_not_attached",
        "p63_handoff_status": _safe_handoff_status(row.get("p63_handoff_status")),
        "p65_packet_status": STATUS,
        "evidence_file_status": EVIDENCE_FILE_STATUS,
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
        case_rows.sort(key=lambda row: _safe_int(row.get("handoff_work_order_index")))
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


def _safe_handoff_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P63_HANDOFF_STATUS else P63_HANDOFF_STATUS


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
