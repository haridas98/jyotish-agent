from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-operator-packet-attachment-readiness-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P69-A"
STATUS = "blocked_pending_external_evidence_attachment"
P67_QA_STATUS = "blocked_pending_operator_packet_qa"
P65_PACKET_STATUS = "blocked_pending_operator_packet_evidence"
EVIDENCE_FILE_STATUS = "not_attached"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_NEXT_OPERATOR_LABELS = [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_operator_packet_attachment_readiness_report",
    "rerun_operator_packet_qa_report",
    "rerun_operator_packets_report",
    "rerun_attachment_handoff_report",
    "rerun_attachment_work_orders_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
]
SAFE_VALIDATION_COMMAND_FAMILIES = [
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_operator_packet_qa_report",
    "build_witness_core_evidence_operator_packets_report",
    "build_witness_core_evidence_attachment_handoff_report",
    "build_witness_core_evidence_attachment_work_orders_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
BLOCKED_NOTE = (
    "External evidence has not been attached; readiness rows are labels only; "
    "collection/upload/mark commands are not executed."
)
SLOT_BLOCKED_NOTE = (
    "Slot is pending external evidence attachment; no upload/collection/mark command was executed."
)


def build_witness_core_evidence_operator_packet_attachment_readiness_report(
    *,
    operator_packet_qa_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(operator_packet_qa_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    packet_qa_rows = [row for row in source.get("operator_packet_qa_rows", []) if isinstance(row, dict)]
    slot_qa_rows = [row for row in source.get("attachment_slot_qa_rows", []) if isinstance(row, dict)]
    slots_by_packet = _slots_by_packet(slot_qa_rows)

    case_rows = [
        _case_attachment_readiness_row(
            row,
            case_attachment_readiness_index=index,
            source_slots=slots_by_packet.get(_safe_int(row.get("operator_packet_qa_index")) or index, []),
        )
        for index, row in enumerate(packet_qa_rows, start=1)
    ]
    slot_rows = [
        _attachment_readiness_slot_row(row, attachment_readiness_slot_index=index)
        for index, row in enumerate(slot_qa_rows, start=1)
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_rows else "empty",
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_operator_packet_qa_rows": _safe_int(
                source_summary.get("operator_packet_qa_rows", len(packet_qa_rows))
            ),
            "source_attachment_slot_qa_rows": _safe_int(
                source_summary.get("attachment_slot_qa_rows", len(slot_qa_rows))
            ),
            "case_attachment_readiness_rows": len(case_rows),
            "attachment_readiness_slot_rows": len(slot_rows),
            "blocked_case_attachment_count": len(case_rows),
            "pending_external_evidence_attachment_count": len(slot_rows),
            "pending_jhora_external_attachment_count": sum(
                1 for row in slot_rows if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_external_attachment_count": sum(
                1
                for row in slot_rows
                if row["evidence_family"] == "parashara_light_manual_values_or_packet"
            ),
            "ready_to_attach_count": 0,
            "ready_to_mark_count": 0,
            "external_evidence_attached_count": 0,
            "attached_evidence_files_count": _safe_int(source_summary.get("attached_evidence_files_count")),
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
        "case_attachment_readiness_rows": case_rows,
        "attachment_readiness_slot_rows": slot_rows,
    }


def _case_attachment_readiness_row(
    row: dict[str, Any],
    *,
    case_attachment_readiness_index: int,
    source_slots: list[dict[str, Any]],
) -> dict[str, Any]:
    source_slot_indices = [_safe_int(slot.get("attachment_slot_qa_index")) for slot in source_slots]
    families = {str(slot.get("evidence_family") or "") for slot in source_slots}
    return {
        "case_attachment_readiness_index": case_attachment_readiness_index,
        "case_id": str(row.get("case_id") or ""),
        "source_operator_packet_qa_index": _safe_int(row.get("operator_packet_qa_index"))
        or case_attachment_readiness_index,
        "source_attachment_slot_qa_indices": source_slot_indices,
        "readiness_status": STATUS,
        "qa_status": _safe_qa_status(row.get("qa_status")),
        "packet_status": _safe_packet_status(row.get("packet_status")),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "required_jhora_slot_qa_present": "jhora_screenshot_or_packet" in families,
        "required_parashara_light_slot_qa_present": "parashara_light_manual_values_or_packet" in families,
        "all_slots_not_attached": all(
            _safe_slot_status(slot.get("evidence_file_status")) == EVIDENCE_FILE_STATUS
            for slot in source_slots
        ),
        "external_evidence_attached": False,
        "evidence_collection_required": True,
        "attachment_required": True,
        "mark_commands_blocked": True,
        "safe_next_operator_labels": SAFE_NEXT_OPERATOR_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_readiness_slot_row(
    row: dict[str, Any],
    *,
    attachment_readiness_slot_index: int,
) -> dict[str, Any]:
    return {
        "attachment_readiness_slot_index": attachment_readiness_slot_index,
        "case_attachment_readiness_index": _safe_int(row.get("operator_packet_index")),
        "source_attachment_slot_qa_index": _safe_int(row.get("attachment_slot_qa_index")),
        "source_operator_packet_qa_index": _safe_int(row.get("operator_packet_index")),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": _safe_evidence_family(row.get("evidence_family")),
        "readiness_status": STATUS,
        "qa_status": _safe_qa_status(row.get("qa_status")),
        "packet_status": _safe_packet_status(row.get("p65_packet_status")),
        "evidence_file_status": EVIDENCE_FILE_STATUS,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "safe_attachment_label": _safe_action_label(row.get("safe_action_label"), row.get("evidence_family")),
        "blocked_note": SLOT_BLOCKED_NOTE,
    }


def _slots_by_packet(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index = _safe_int(row.get("operator_packet_index"))
        if index:
            grouped[index].append(row)
    for packet_rows in grouped.values():
        packet_rows.sort(key=lambda row: _safe_int(row.get("attachment_slot_qa_index")))
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


def _safe_qa_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P67_QA_STATUS else P67_QA_STATUS


def _safe_slot_status(value: Any) -> str:
    text = str(value or "")
    return text if text == EVIDENCE_FILE_STATUS else EVIDENCE_FILE_STATUS


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
