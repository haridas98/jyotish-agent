from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-external-receipt-manifest-templates-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P75-A"
STATUS = "blocked_pending_external_evidence_receipt_manifests"
SOURCE_SCHEMA_VERSION = "jyotish-core-evidence-external-receipt-gate-v1"
SOURCE_STAGE = "P73-A"
SOURCE_STATUS = "blocked_pending_external_evidence_receipts"
P71_INTAKE_STATUS = "blocked_pending_external_evidence_intake"
P69_READINESS_STATUS = "blocked_pending_external_evidence_attachment"
NOT_RECEIVED = "not_received"
NOT_STARTED = "not_started"
NOT_ATTACHED = "not_attached"
NOT_RECORDED = "not_recorded"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_MANIFEST_TEMPLATE_LABELS = [
    "await_jhora_receipt_manifest",
    "await_parashara_light_receipt_manifest",
    "record_external_evidence_receipt_manifest",
    "rerun_external_receipt_manifest_templates_report",
    "rerun_external_receipt_gate_report",
    "rerun_external_intake_contract_report",
    "rerun_operator_packet_attachment_readiness_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
]
SAFE_VALIDATION_COMMAND_FAMILIES = [
    "build_witness_core_evidence_external_receipt_manifest_templates_report",
    "build_witness_core_evidence_external_receipt_gate_report",
    "build_witness_core_evidence_external_intake_contract_report",
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
SAFE_REQUIRED_MANIFEST_FIELDS = [
    "case_id",
    "evidence_family",
    "external_tool_label",
    "human_receipt_timestamp_utc",
    "redacted_receipt_manifest_id",
    "operator_receipt_note_label",
    "no_raw_values_in_manifest",
    "no_private_paths_in_manifest",
    "no_secrets_in_manifest",
]
BLOCKED_NOTE = (
    "Receipt manifests have not arrived; template rows are labels only; no evidence file, hash, upload, "
    "attachment, or mark command is executed."
)
SLOT_BLOCKED_NOTE = (
    "Receipt manifest is pending human-provided external evidence; no file/hash/validation/upload/"
    "attachment/mark command was executed."
)


def build_witness_core_evidence_external_receipt_manifest_templates_report(
    *,
    external_receipt_gate_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(external_receipt_gate_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    case_receipt_rows = [
        row for row in source.get("case_receipt_gate_rows", []) if isinstance(row, dict)
    ]
    slot_receipt_rows = [
        row for row in source.get("attachment_receipt_slot_rows", []) if isinstance(row, dict)
    ]
    slots_by_case = _slots_by_case(slot_receipt_rows)

    case_rows = [
        _case_manifest_template_row(
            row,
            case_receipt_manifest_template_index=index,
            source_slots=slots_by_case.get(_safe_int(row.get("case_receipt_gate_index")) or index, []),
        )
        for index, row in enumerate(case_receipt_rows, start=1)
    ]
    slot_rows = [
        _attachment_manifest_template_row(row, attachment_receipt_manifest_template_index=index)
        for index, row in enumerate(slot_receipt_rows, start=1)
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_rows else "empty",
        "source_schema_version": _safe_source_marker(source.get("schema_version"), SOURCE_SCHEMA_VERSION),
        "source_stage": _safe_source_marker(source.get("stage"), SOURCE_STAGE),
        "source_status": _safe_source_marker(source.get("status"), SOURCE_STATUS),
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_case_receipt_gate_rows": _safe_int(
                source_summary.get("case_receipt_gate_rows", len(case_receipt_rows))
            ),
            "source_attachment_receipt_slot_rows": _safe_int(
                source_summary.get("attachment_receipt_slot_rows", len(slot_receipt_rows))
            ),
            "case_receipt_manifest_template_rows": len(case_rows),
            "attachment_receipt_manifest_template_rows": len(slot_rows),
            "pending_external_evidence_receipt_manifest_count": len(slot_rows),
            "pending_jhora_receipt_manifest_count": sum(
                1 for row in slot_rows if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_receipt_manifest_count": sum(
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
        "case_receipt_manifest_template_rows": case_rows,
        "attachment_receipt_manifest_template_rows": slot_rows,
    }


def _case_manifest_template_row(
    row: dict[str, Any],
    *,
    case_receipt_manifest_template_index: int,
    source_slots: list[dict[str, Any]],
) -> dict[str, Any]:
    source_slot_indices = [_safe_int(slot.get("attachment_receipt_slot_index")) for slot in source_slots]
    families = {str(slot.get("evidence_family") or "") for slot in source_slots}
    return {
        "case_receipt_manifest_template_index": case_receipt_manifest_template_index,
        "case_id": str(row.get("case_id") or ""),
        "source_case_receipt_gate_index": _safe_int(row.get("case_receipt_gate_index"))
        or case_receipt_manifest_template_index,
        "source_attachment_receipt_slot_indices": source_slot_indices,
        "receipt_manifest_template_status": STATUS,
        "receipt_gate_status": _safe_receipt_gate_status(row.get("receipt_gate_status")),
        "intake_status": _safe_intake_status(row.get("intake_status")),
        "readiness_status": _safe_readiness_status(row.get("readiness_status")),
        "required_external_evidence_receipt_manifests": len(REQUIRED_EVIDENCE_FAMILIES),
        "missing_external_evidence_receipt_manifests": len(REQUIRED_EVIDENCE_FAMILIES),
        "jhora_manifest_required": "jhora_screenshot_or_packet" in families,
        "parashara_light_manifest_required": "parashara_light_manual_values_or_packet" in families,
        "receipt_manifest_received": False,
        "evidence_received": False,
        "evidence_validated": False,
        "evidence_collected": False,
        "evidence_uploaded": False,
        "evidence_attached": False,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "mark_commands_blocked": True,
        "safe_manifest_template_labels": SAFE_MANIFEST_TEMPLATE_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_manifest_template_row(
    row: dict[str, Any],
    *,
    attachment_receipt_manifest_template_index: int,
) -> dict[str, Any]:
    family = _safe_evidence_family(row.get("evidence_family"))
    return {
        "attachment_receipt_manifest_template_index": attachment_receipt_manifest_template_index,
        "case_receipt_manifest_template_index": _safe_int(row.get("case_receipt_gate_index")),
        "source_attachment_receipt_slot_index": _safe_int(row.get("attachment_receipt_slot_index")),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": family,
        "receipt_manifest_template_status": STATUS,
        "receipt_gate_status": _safe_receipt_gate_status(row.get("receipt_gate_status")),
        "evidence_receipt_status": NOT_RECEIVED,
        "receipt_manifest_status": NOT_RECEIVED,
        "evidence_validation_status": NOT_STARTED,
        "evidence_file_status": NOT_ATTACHED,
        "evidence_hash_status": NOT_RECORDED,
        "evidence_upload_status": NOT_STARTED,
        "evidence_attachment_status": NOT_ATTACHED,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "safe_receipt_manifest_label": _safe_manifest_label(family),
        "safe_required_manifest_fields": SAFE_REQUIRED_MANIFEST_FIELDS,
        "blocked_note": SLOT_BLOCKED_NOTE,
    }


def _slots_by_case(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index = _safe_int(row.get("case_receipt_gate_index"))
        if index:
            grouped[index].append(row)
    for case_rows in grouped.values():
        case_rows.sort(key=lambda row: _safe_int(row.get("attachment_receipt_slot_index")))
    return dict(grouped)


def _safe_evidence_family(value: Any) -> str:
    text = str(value or "")
    return text if text in REQUIRED_EVIDENCE_FAMILIES else "jhora_screenshot_or_packet"


def _safe_manifest_label(family: str) -> str:
    return (
        "await_jhora_receipt_manifest"
        if family == "jhora_screenshot_or_packet"
        else "await_parashara_light_receipt_manifest"
    )


def _safe_receipt_gate_status(value: Any) -> str:
    text = str(value or "")
    return text if text == SOURCE_STATUS else SOURCE_STATUS


def _safe_intake_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P71_INTAKE_STATUS else P71_INTAKE_STATUS


def _safe_readiness_status(value: Any) -> str:
    text = str(value or "")
    return text if text == P69_READINESS_STATUS else P69_READINESS_STATUS


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
