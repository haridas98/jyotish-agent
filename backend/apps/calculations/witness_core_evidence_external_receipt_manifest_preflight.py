from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-external-receipt-manifest-preflight-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P77-A"
STATUS = "blocked_pending_external_evidence_receipt_manifest_preflight"
UPSTREAM_SCHEMA_VERSION = "jyotish-core-evidence-external-receipt-manifest-templates-v1"
UPSTREAM_STAGE = "P75-A"
UPSTREAM_STATUS = "blocked_pending_external_evidence_receipt_manifests"
EXTERNAL_RECEIPT_GATE_STATUS = "blocked_pending_external_evidence_receipts"
EXTERNAL_INTAKE_STATUS = "blocked_pending_external_evidence_intake"
ATTACHMENT_READINESS_STATUS = "blocked_pending_external_evidence_attachment"
NOT_RECEIVED = "not_received"
NOT_STARTED = "not_started"
NOT_ATTACHED = "not_attached"
NOT_RECORDED = "not_recorded"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_NEXT_ACTION_LABELS = [
    "await_jhora_receipt_manifest_preflight",
    "await_parashara_light_receipt_manifest_preflight",
    "record_external_evidence_receipt_manifest_after_human_review",
    "rerun_external_receipt_manifest_preflight_report",
    "rerun_external_receipt_manifest_templates_report",
    "rerun_external_receipt_gate_report",
    "rerun_external_intake_contract_report",
    "rerun_operator_packet_attachment_readiness_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
]
SAFE_VALIDATION_COMMAND_FAMILIES = [
    "build_witness_core_evidence_external_receipt_manifest_preflight_report",
    "build_witness_core_evidence_external_receipt_manifest_templates_report",
    "build_witness_core_evidence_external_receipt_gate_report",
    "build_witness_core_evidence_external_intake_contract_report",
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
BLOCKED_NOTE = (
    "External receipt manifest preflight is blocked; rows are labels only; no evidence, raw values, "
    "private paths, uploads, attachments, or mark commands are used."
)
SLOT_BLOCKED_NOTE = (
    "Expected receipt manifest is absent; no evidence file or evidence hash is recorded; no upload, "
    "attachment, or mark command was executed."
)


def build_witness_core_evidence_external_receipt_manifest_preflight_report(
    *,
    external_receipt_manifest_templates_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(external_receipt_manifest_templates_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    case_template_rows = [
        row for row in source.get("case_receipt_manifest_template_rows", []) if isinstance(row, dict)
    ]
    slot_template_rows = [
        row for row in source.get("attachment_receipt_manifest_template_rows", []) if isinstance(row, dict)
    ]
    slots_by_case = _slots_by_case(slot_template_rows)

    case_rows = [
        _case_preflight_row(
            row,
            case_receipt_manifest_preflight_index=index,
            source_slots=slots_by_case.get(_safe_int(row.get("case_receipt_manifest_template_index")) or index, []),
        )
        for index, row in enumerate(case_template_rows, start=1)
    ]
    slot_rows = [
        _attachment_preflight_row(row, attachment_receipt_manifest_preflight_index=index)
        for index, row in enumerate(slot_template_rows, start=1)
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_rows else "empty",
        "upstream_template_schema_version": _safe_source_marker(
            source.get("schema_version"),
            UPSTREAM_SCHEMA_VERSION,
        ),
        "upstream_template_stage": _safe_source_marker(source.get("stage"), UPSTREAM_STAGE),
        "upstream_template_status": _safe_source_marker(source.get("status"), UPSTREAM_STATUS),
        "external_receipt_gate_status": EXTERNAL_RECEIPT_GATE_STATUS,
        "external_intake_status": EXTERNAL_INTAKE_STATUS,
        "attachment_readiness_status": ATTACHMENT_READINESS_STATUS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_case_receipt_manifest_template_rows": _safe_int(
                source_summary.get("case_receipt_manifest_template_rows", len(case_template_rows))
            ),
            "source_attachment_receipt_manifest_template_rows": _safe_int(
                source_summary.get("attachment_receipt_manifest_template_rows", len(slot_template_rows))
            ),
            "case_receipt_manifest_preflight_rows": len(case_rows),
            "attachment_receipt_manifest_preflight_rows": len(slot_rows),
            "pending_external_evidence_receipt_manifest_preflight_count": len(slot_rows),
            "pending_jhora_receipt_manifest_preflight_count": sum(
                1 for row in slot_rows if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_receipt_manifest_preflight_count": sum(
                1
                for row in slot_rows
                if row["evidence_family"] == "parashara_light_manual_values_or_packet"
            ),
            "receipt_manifest_received_count": 0,
            "evidence_received_count": 0,
            "evidence_validated_count": 0,
            "evidence_file_recorded_count": 0,
            "evidence_hash_recorded_count": 0,
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
        "case_receipt_manifest_preflight_rows": case_rows,
        "attachment_receipt_manifest_preflight_rows": slot_rows,
    }


def _case_preflight_row(
    row: dict[str, Any],
    *,
    case_receipt_manifest_preflight_index: int,
    source_slots: list[dict[str, Any]],
) -> dict[str, Any]:
    source_slot_indices = [
        _safe_int(slot.get("attachment_receipt_manifest_template_index")) for slot in source_slots
    ]
    families = {str(slot.get("evidence_family") or "") for slot in source_slots}
    return {
        "case_receipt_manifest_preflight_index": case_receipt_manifest_preflight_index,
        "case_id": str(row.get("case_id") or ""),
        "source_case_receipt_manifest_template_index": _safe_int(
            row.get("case_receipt_manifest_template_index")
        )
        or case_receipt_manifest_preflight_index,
        "source_attachment_receipt_manifest_template_indices": source_slot_indices,
        "preflight_status": STATUS,
        "receipt_manifest_template_status": _safe_template_status(row.get("receipt_manifest_template_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("receipt_gate_status")),
        "external_intake_status": _safe_intake_status(row.get("intake_status")),
        "attachment_readiness_status": _safe_readiness_status(row.get("readiness_status")),
        "required_external_evidence_receipt_manifests": len(REQUIRED_EVIDENCE_FAMILIES),
        "missing_external_evidence_receipt_manifests": len(REQUIRED_EVIDENCE_FAMILIES),
        "jhora_manifest_required": "jhora_screenshot_or_packet" in families,
        "parashara_light_manifest_required": "parashara_light_manual_values_or_packet" in families,
        "receipt_manifest_received": False,
        "evidence_received": False,
        "evidence_validated": False,
        "evidence_file_recorded": False,
        "evidence_hash_recorded": False,
        "evidence_uploaded": False,
        "evidence_attached": False,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "mark_commands_blocked": True,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_preflight_row(
    row: dict[str, Any],
    *,
    attachment_receipt_manifest_preflight_index: int,
) -> dict[str, Any]:
    family = _safe_evidence_family(row.get("evidence_family"))
    return {
        "attachment_receipt_manifest_preflight_index": attachment_receipt_manifest_preflight_index,
        "case_receipt_manifest_preflight_index": _safe_int(row.get("case_receipt_manifest_template_index")),
        "source_attachment_receipt_manifest_template_index": _safe_int(
            row.get("attachment_receipt_manifest_template_index")
        ),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": family,
        "external_tool_label": _external_tool_label(family),
        "expected_receipt_manifest_label": _expected_manifest_label(family),
        "redacted_receipt_manifest_id": "redacted_receipt_manifest_id_pending",
        "operator_preflight_note_label": "operator_preflight_note_label_pending",
        "required_human_receipt_timestamp_utc": "human_receipt_timestamp_utc_pending",
        "preflight_status": STATUS,
        "receipt_manifest_template_status": _safe_template_status(row.get("receipt_manifest_template_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("receipt_gate_status")),
        "external_intake_status": EXTERNAL_INTAKE_STATUS,
        "attachment_readiness_status": ATTACHMENT_READINESS_STATUS,
        "receipt_manifest_status": NOT_RECEIVED,
        "evidence_validation_status": NOT_STARTED,
        "evidence_file_status": NOT_ATTACHED,
        "evidence_hash_status": NOT_RECORDED,
        "evidence_upload_status": NOT_STARTED,
        "evidence_attachment_status": NOT_ATTACHED,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "no_raw_values_in_manifest": True,
        "no_private_paths_in_manifest": True,
        "no_secrets_in_manifest": True,
        "no_evidence_file_recorded": True,
        "no_evidence_hash_recorded": True,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "blocked_note": SLOT_BLOCKED_NOTE,
    }


def _slots_by_case(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index = _safe_int(row.get("case_receipt_manifest_template_index"))
        if index:
            grouped[index].append(row)
    for case_rows in grouped.values():
        case_rows.sort(key=lambda row: _safe_int(row.get("attachment_receipt_manifest_template_index")))
    return dict(grouped)


def _safe_evidence_family(value: Any) -> str:
    text = str(value or "")
    return text if text in REQUIRED_EVIDENCE_FAMILIES else "jhora_screenshot_or_packet"


def _external_tool_label(family: str) -> str:
    return "jhora" if family == "jhora_screenshot_or_packet" else "parashara_light"


def _expected_manifest_label(family: str) -> str:
    return (
        "await_jhora_receipt_manifest_preflight"
        if family == "jhora_screenshot_or_packet"
        else "await_parashara_light_receipt_manifest_preflight"
    )


def _safe_template_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_STATUS else UPSTREAM_STATUS


def _safe_receipt_gate_status(value: Any) -> str:
    text = str(value or "")
    return text if text == EXTERNAL_RECEIPT_GATE_STATUS else EXTERNAL_RECEIPT_GATE_STATUS


def _safe_intake_status(value: Any) -> str:
    text = str(value or "")
    return text if text == EXTERNAL_INTAKE_STATUS else EXTERNAL_INTAKE_STATUS


def _safe_readiness_status(value: Any) -> str:
    text = str(value or "")
    return text if text == ATTACHMENT_READINESS_STATUS else ATTACHMENT_READINESS_STATUS


def _safe_source_marker(value: Any, fallback: str) -> str:
    text = str(value or "")
    return text if text == fallback else fallback


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
