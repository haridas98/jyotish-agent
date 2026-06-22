from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-operator-packet-qa-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P67-A"
STATUS = "blocked_pending_operator_packet_qa"
P65_PACKET_STATUS = "blocked_pending_operator_packet_evidence"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_VALIDATION_COMMANDS = [
    "build_witness_core_evidence_operator_packet_qa_report",
    "build_witness_core_evidence_operator_packets_report",
    "build_witness_core_evidence_attachment_handoff_report",
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
BLOCKED_NOTE = (
    "External evidence has not been attached; operator packets are labels only; "
    "mark commands remain blocked."
)
SLOT_BLOCKED_NOTE = (
    "Attachment slot is pending and not attached; evidence must be attached before mark commands."
)


def build_witness_core_evidence_operator_packet_qa_report(
    *,
    operator_packets_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(operator_packets_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    packet_rows = [row for row in source.get("operator_packet_rows", []) if isinstance(row, dict)]
    slot_rows = [row for row in source.get("operator_attachment_slot_rows", []) if isinstance(row, dict)]
    slots_by_packet = _slots_by_packet(slot_rows)

    packet_qa_rows = [
        _operator_packet_qa_row(
            row,
            operator_packet_qa_index=index,
            source_slots=slots_by_packet.get(_safe_int(row.get("operator_packet_index")) or index, []),
        )
        for index, row in enumerate(packet_rows, start=1)
    ]
    attachment_qa_rows = [
        _attachment_slot_qa_row(row, attachment_slot_qa_index=index)
        for index, row in enumerate(slot_rows, start=1)
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if packet_qa_rows else "empty",
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_operator_packet_rows": _safe_int(
                source_summary.get("operator_packet_rows", len(packet_rows))
            ),
            "source_operator_attachment_slot_rows": _safe_int(
                source_summary.get("operator_attachment_slot_rows", len(slot_rows))
            ),
            "operator_packet_qa_rows": len(packet_qa_rows),
            "attachment_slot_qa_rows": len(attachment_qa_rows),
            "blocked_packet_qa_count": len(packet_qa_rows),
            "pending_attachment_slot_qa_count": len(attachment_qa_rows),
            "pending_jhora_attachment_slot_qa_count": sum(
                1 for row in attachment_qa_rows if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_attachment_slot_qa_count": sum(
                1
                for row in attachment_qa_rows
                if row["evidence_family"] == "parashara_light_manual_values_or_packet"
            ),
            "ready_to_mark_count": 0,
            "attached_evidence_files_count": _safe_int(source_summary.get("attached_evidence_files_count")),
            "missing_attachment_slot_count": _safe_int(
                source_summary.get("missing_attachment_slot_count", len(attachment_qa_rows))
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
        "operator_packet_qa_rows": packet_qa_rows,
        "attachment_slot_qa_rows": attachment_qa_rows,
    }


def _operator_packet_qa_row(
    row: dict[str, Any],
    *,
    operator_packet_qa_index: int,
    source_slots: list[dict[str, Any]],
) -> dict[str, Any]:
    source_slot_indices = [_safe_int(slot.get("operator_attachment_slot_index")) for slot in source_slots]
    families = {str(slot.get("evidence_family") or "") for slot in source_slots}
    return {
        "operator_packet_qa_index": operator_packet_qa_index,
        "case_id": str(row.get("case_id") or ""),
        "source_operator_packet_index": _safe_int(row.get("operator_packet_index")) or operator_packet_qa_index,
        "source_attachment_slot_indices": source_slot_indices,
        "qa_status": STATUS,
        "packet_status": _safe_packet_status(row.get("packet_status")),
        "ready_to_mark": False,
        "required_jhora_slot_present": "jhora_screenshot_or_packet" in families,
        "required_parashara_light_slot_present": "parashara_light_manual_values_or_packet" in families,
        "all_attachment_slots_not_attached": all(
            _safe_slot_status(slot.get("evidence_file_status")) == "not_attached"
            and _safe_slot_status(slot.get("p59_attachment_slot_status")) == "not_attached"
            for slot in source_slots
        ),
        "no_external_evidence_attached": all(
            _safe_slot_status(slot.get("evidence_file_status")) == "not_attached"
            for slot in source_slots
        ),
        "release_gate_blocked": True,
        "safe_validation_commands": SAFE_VALIDATION_COMMANDS,
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_slot_qa_row(row: dict[str, Any], *, attachment_slot_qa_index: int) -> dict[str, Any]:
    return {
        "attachment_slot_qa_index": attachment_slot_qa_index,
        "source_operator_attachment_slot_index": _safe_int(row.get("operator_attachment_slot_index")),
        "operator_packet_index": _safe_int(row.get("operator_packet_index")),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": _safe_evidence_family(row.get("evidence_family")),
        "p57_evidence_slot_status": "missing",
        "p59_attachment_slot_status": "not_attached",
        "p61_work_order_status": "pending_not_attached",
        "p63_handoff_status": "blocked_pending_operator_evidence",
        "p65_packet_status": _safe_packet_status(row.get("p65_packet_status")),
        "evidence_file_status": "not_attached",
        "qa_status": STATUS,
        "ready_to_mark": False,
        "safe_action_label": _safe_action_label(row.get("safe_action_label"), row.get("evidence_family")),
        "blocked_note": SLOT_BLOCKED_NOTE,
    }


def _slots_by_packet(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index = _safe_int(row.get("operator_packet_index"))
        if index:
            grouped[index].append(row)
    for packet_rows in grouped.values():
        packet_rows.sort(key=lambda row: _safe_int(row.get("operator_attachment_slot_index")))
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


def _safe_evidence_family(value: Any) -> str:
    text = str(value or "")
    return text if text in REQUIRED_EVIDENCE_FAMILIES else "jhora_screenshot_or_packet"


def _safe_packet_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P65_PACKET_STATUS else P65_PACKET_STATUS


def _safe_slot_status(value: Any) -> str:
    text = str(value or "")
    return text if text == "not_attached" else "not_attached"


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
