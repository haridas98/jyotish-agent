from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-external-intake-contract-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P71-A"
STATUS = "blocked_pending_external_evidence_intake"
P69_READINESS_STATUS = "blocked_pending_external_evidence_attachment"
P67_QA_STATUS = "blocked_pending_operator_packet_qa"
P65_PACKET_STATUS = "blocked_pending_operator_packet_evidence"
EVIDENCE_FILE_STATUS = "not_attached"
NOT_STARTED = "not_started"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_INTAKE_LABELS = [
    "request_jhora_screenshot_or_packet",
    "request_parashara_light_manual_values_or_packet",
    "receive_external_evidence_from_human",
    "rerun_external_intake_contract_report",
    "rerun_operator_packet_attachment_readiness_report",
    "rerun_operator_packet_qa_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
]
SAFE_VALIDATION_COMMAND_FAMILIES = [
    "build_witness_core_evidence_external_intake_contract_report",
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_operator_packet_qa_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
BLOCKED_NOTE = (
    "External evidence has not been collected, uploaded, or attached; intake rows are labels only; "
    "mark commands are not executed."
)
SLOT_BLOCKED_NOTE = (
    "Evidence is pending human-provided external intake; no collection/upload/attachment/mark "
    "command was executed."
)


def build_witness_core_evidence_external_intake_contract_report(
    *,
    attachment_readiness_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(attachment_readiness_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    case_readiness_rows = [
        row for row in source.get("case_attachment_readiness_rows", []) if isinstance(row, dict)
    ]
    slot_readiness_rows = [
        row for row in source.get("attachment_readiness_slot_rows", []) if isinstance(row, dict)
    ]
    slots_by_case = _slots_by_case(slot_readiness_rows)

    case_rows = [
        _case_intake_contract_row(
            row,
            case_intake_contract_index=index,
            source_slots=slots_by_case.get(_safe_int(row.get("case_attachment_readiness_index")) or index, []),
        )
        for index, row in enumerate(case_readiness_rows, start=1)
    ]
    slot_rows = [
        _attachment_intake_slot_row(row, attachment_intake_slot_index=index)
        for index, row in enumerate(slot_readiness_rows, start=1)
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_rows else "empty",
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_case_attachment_readiness_rows": _safe_int(
                source_summary.get("case_attachment_readiness_rows", len(case_readiness_rows))
            ),
            "source_attachment_readiness_slot_rows": _safe_int(
                source_summary.get("attachment_readiness_slot_rows", len(slot_readiness_rows))
            ),
            "case_intake_contract_rows": len(case_rows),
            "attachment_intake_slot_rows": len(slot_rows),
            "pending_external_evidence_intake_count": len(slot_rows),
            "pending_jhora_external_intake_count": sum(
                1 for row in slot_rows if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_external_intake_count": sum(
                1
                for row in slot_rows
                if row["evidence_family"] == "parashara_light_manual_values_or_packet"
            ),
            "evidence_collected_count": 0,
            "evidence_uploaded_count": 0,
            "evidence_attached_count": 0,
            "ready_to_attach_count": 0,
            "ready_to_mark_count": 0,
            "remaining_not_reviewed_count": _safe_int(source_summary.get("remaining_not_reviewed_count")),
            "release_gate_status": _safe_status(source_summary.get("release_gate_status"), fallback="blocked"),
            "command_smoke_matrix_status": _safe_status(
                source_summary.get("command_smoke_matrix_status"),
                fallback="ready",
            ),
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "case_intake_contract_rows": case_rows,
        "attachment_intake_slot_rows": slot_rows,
    }


def _case_intake_contract_row(
    row: dict[str, Any],
    *,
    case_intake_contract_index: int,
    source_slots: list[dict[str, Any]],
) -> dict[str, Any]:
    source_slot_indices = [_safe_int(slot.get("attachment_readiness_slot_index")) for slot in source_slots]
    families = {str(slot.get("evidence_family") or "") for slot in source_slots}
    return {
        "case_intake_contract_index": case_intake_contract_index,
        "case_id": str(row.get("case_id") or ""),
        "source_case_attachment_readiness_index": _safe_int(row.get("case_attachment_readiness_index"))
        or case_intake_contract_index,
        "source_attachment_readiness_slot_indices": source_slot_indices,
        "intake_status": STATUS,
        "readiness_status": _safe_readiness_status(row.get("readiness_status")),
        "qa_status": _safe_qa_status(row.get("qa_status")),
        "packet_status": _safe_packet_status(row.get("packet_status")),
        "required_external_evidence_slots": len(REQUIRED_EVIDENCE_FAMILIES),
        "pending_external_evidence_slots": len(REQUIRED_EVIDENCE_FAMILIES),
        "jhora_external_evidence_required": "jhora_screenshot_or_packet" in families,
        "parashara_light_external_evidence_required": "parashara_light_manual_values_or_packet" in families,
        "evidence_collected": False,
        "evidence_uploaded": False,
        "evidence_attached": False,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "mark_commands_blocked": True,
        "safe_intake_labels": SAFE_INTAKE_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_intake_slot_row(
    row: dict[str, Any],
    *,
    attachment_intake_slot_index: int,
) -> dict[str, Any]:
    family = _safe_evidence_family(row.get("evidence_family"))
    return {
        "attachment_intake_slot_index": attachment_intake_slot_index,
        "case_intake_contract_index": _safe_int(row.get("case_attachment_readiness_index")),
        "source_attachment_readiness_slot_index": _safe_int(row.get("attachment_readiness_slot_index")),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": family,
        "intake_status": STATUS,
        "readiness_status": _safe_readiness_status(row.get("readiness_status")),
        "evidence_file_status": EVIDENCE_FILE_STATUS,
        "evidence_collection_status": NOT_STARTED,
        "evidence_upload_status": NOT_STARTED,
        "evidence_attachment_status": EVIDENCE_FILE_STATUS,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "safe_request_label": _safe_request_label(family),
        "safe_validation_label": _safe_validation_label(family),
        "blocked_note": SLOT_BLOCKED_NOTE,
    }


def _slots_by_case(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index = _safe_int(row.get("case_attachment_readiness_index"))
        if index:
            grouped[index].append(row)
    for case_rows in grouped.values():
        case_rows.sort(key=lambda row: _safe_int(row.get("attachment_readiness_slot_index")))
    return dict(grouped)


def _safe_evidence_family(value: Any) -> str:
    text = str(value or "")
    return text if text in REQUIRED_EVIDENCE_FAMILIES else "jhora_screenshot_or_packet"


def _safe_request_label(family: str) -> str:
    return (
        "request_jhora_screenshot_or_packet"
        if family == "jhora_screenshot_or_packet"
        else "request_parashara_light_manual_values_or_packet"
    )


def _safe_validation_label(family: str) -> str:
    return (
        "validate_jhora_screenshot_or_packet"
        if family == "jhora_screenshot_or_packet"
        else "validate_parashara_light_manual_values_or_packet"
    )


def _safe_packet_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P65_PACKET_STATUS else P65_PACKET_STATUS


def _safe_qa_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P67_QA_STATUS else P67_QA_STATUS


def _safe_readiness_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P69_READINESS_STATUS else P69_READINESS_STATUS


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
