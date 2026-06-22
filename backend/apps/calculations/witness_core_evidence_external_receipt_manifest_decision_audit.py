from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-external-receipt-manifest-decision-audit-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P83-A"
STATUS = "blocked_pending_external_evidence_receipt_manifest_decision_audit"
UPSTREAM_DECISION_QUEUE_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-queue-v1"
)
UPSTREAM_DECISION_QUEUE_STAGE = "P81-A"
UPSTREAM_DECISION_QUEUE_STATUS = "blocked_pending_external_evidence_receipt_manifest_decision"
UPSTREAM_ACCEPTANCE_GATE_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1"
)
UPSTREAM_ACCEPTANCE_GATE_STAGE = "P79-A"
UPSTREAM_ACCEPTANCE_GATE_STATUS = "blocked_pending_external_evidence_receipt_manifest_acceptance"
UPSTREAM_PREFLIGHT_SCHEMA_VERSION = "jyotish-core-evidence-external-receipt-manifest-preflight-v1"
UPSTREAM_PREFLIGHT_STAGE = "P77-A"
UPSTREAM_PREFLIGHT_STATUS = "blocked_pending_external_evidence_receipt_manifest_preflight"
UPSTREAM_TEMPLATE_SCHEMA_VERSION = "jyotish-core-evidence-external-receipt-manifest-templates-v1"
UPSTREAM_TEMPLATE_STAGE = "P75-A"
UPSTREAM_TEMPLATE_STATUS = "blocked_pending_external_evidence_receipt_manifests"
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
DECISION_AUDIT_CRITERIA_LABELS = [
    "require_human_decision_timestamp_utc",
    "require_human_decision_audit_timestamp_utc",
    "require_redacted_receipt_manifest_id",
    "require_operator_decision_label",
    "require_operator_decision_audit_label",
    "require_accept_or_reject_or_defer_label",
    "require_no_raw_values_in_manifest",
    "require_no_private_paths_in_manifest",
    "require_no_secrets_in_manifest",
    "require_no_evidence_file_recorded_before_decision_audit",
    "require_no_evidence_hash_recorded_before_decision_audit",
    "block_upload_until_manifest_decision_audited",
    "block_attachment_until_manifest_decision_audited",
    "block_mark_until_manifest_decision_audited",
]
SAFE_NEXT_ACTION_LABELS = [
    "await_jhora_receipt_manifest_decision_audit",
    "await_parashara_light_receipt_manifest_decision_audit",
    "audit_external_evidence_receipt_manifest_decision_after_human_review",
    "defer_external_evidence_receipt_manifest_decision_audit",
    "rerun_external_receipt_manifest_decision_audit_report",
    "rerun_external_receipt_manifest_decision_queue_report",
    "rerun_external_receipt_manifest_acceptance_gate_report",
    "rerun_external_receipt_manifest_preflight_report",
    "rerun_external_receipt_manifest_templates_report",
    "rerun_external_receipt_gate_report",
    "rerun_external_intake_contract_report",
    "rerun_operator_packet_attachment_readiness_report",
    "rerun_attachment_gate_report",
    "preflight_witness_review",
]
SAFE_VALIDATION_COMMAND_FAMILIES = [
    "build_witness_core_evidence_external_receipt_manifest_decision_audit_report",
    "build_witness_core_evidence_external_receipt_manifest_decision_queue_report",
    "build_witness_core_evidence_external_receipt_manifest_acceptance_gate_report",
    "build_witness_core_evidence_external_receipt_manifest_preflight_report",
    "build_witness_core_evidence_external_receipt_manifest_templates_report",
    "build_witness_core_evidence_external_receipt_gate_report",
    "build_witness_core_evidence_external_intake_contract_report",
    "build_witness_core_evidence_operator_packet_attachment_readiness_report",
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
]
STATUS_LABELS = [
    "external_receipt_gate_status=blocked_pending_external_evidence_receipts",
    "external_intake_status=blocked_pending_external_evidence_intake",
    "attachment_readiness_status=blocked_pending_external_evidence_attachment",
    "decision_queue_status=blocked_pending_external_evidence_receipt_manifest_decision",
    "decision_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit",
    "receipt_manifest_status=not_received",
    "decision_audit_record_status=not_started",
]
SAFETY_LABELS = [
    "no_raw_values_in_manifest=true",
    "no_private_paths_in_manifest=true",
    "no_secrets_in_manifest=true",
    "no_evidence_file_recorded=true",
    "no_evidence_hash_recorded=true",
    "no_upload_executed=true",
    "no_attachment_executed=true",
    "no_mark_command_executed=true",
]
BLOCKED_NOTE = (
    "Receipt manifest decision audit is blocked; no decision has been recorded or audited; "
    "rows are labels only and no upload, attachment, mark, accept, reject, or defer command is executed."
)
SLOT_BLOCKED_NOTE = (
    "Receipt manifest decision audit is blocked; receipt manifest is not received and decision audit is not "
    "started; no evidence file, evidence hash, upload, attachment, or mark command was executed."
)


def build_witness_core_evidence_external_receipt_manifest_decision_audit_report(
    *,
    external_receipt_manifest_decision_queue_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(external_receipt_manifest_decision_queue_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    case_decision_rows = [
        row for row in source.get("case_receipt_manifest_decision_queue_rows", []) if isinstance(row, dict)
    ]
    slot_decision_rows = [
        row
        for row in source.get("attachment_receipt_manifest_decision_queue_rows", [])
        if isinstance(row, dict)
    ]
    slots_by_case = _slots_by_case(slot_decision_rows)

    case_rows = [
        _case_decision_audit_row(
            row,
            case_receipt_manifest_decision_audit_index=index,
            source_slots=slots_by_case.get(
                _safe_int(row.get("case_receipt_manifest_decision_queue_index")) or index,
                [],
            ),
        )
        for index, row in enumerate(case_decision_rows, start=1)
    ]
    slot_rows = [
        _attachment_decision_audit_row(row, attachment_receipt_manifest_decision_audit_index=index)
        for index, row in enumerate(slot_decision_rows, start=1)
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_rows else "empty",
        "upstream_decision_queue_schema_version": _safe_source_marker(
            source.get("schema_version"),
            UPSTREAM_DECISION_QUEUE_SCHEMA_VERSION,
        ),
        "upstream_decision_queue_stage": _safe_source_marker(source.get("stage"), UPSTREAM_DECISION_QUEUE_STAGE),
        "upstream_decision_queue_status": _safe_source_marker(
            source.get("status"),
            UPSTREAM_DECISION_QUEUE_STATUS,
        ),
        "upstream_acceptance_gate_schema_version": _safe_source_marker(
            source.get("upstream_acceptance_gate_schema_version"),
            UPSTREAM_ACCEPTANCE_GATE_SCHEMA_VERSION,
        ),
        "upstream_acceptance_gate_stage": _safe_source_marker(
            source.get("upstream_acceptance_gate_stage"),
            UPSTREAM_ACCEPTANCE_GATE_STAGE,
        ),
        "upstream_acceptance_gate_status": _safe_source_marker(
            source.get("upstream_acceptance_gate_status"),
            UPSTREAM_ACCEPTANCE_GATE_STATUS,
        ),
        "upstream_preflight_schema_version": _safe_source_marker(
            source.get("upstream_preflight_schema_version"),
            UPSTREAM_PREFLIGHT_SCHEMA_VERSION,
        ),
        "upstream_preflight_stage": _safe_source_marker(
            source.get("upstream_preflight_stage"),
            UPSTREAM_PREFLIGHT_STAGE,
        ),
        "upstream_preflight_status": _safe_source_marker(
            source.get("upstream_preflight_status"),
            UPSTREAM_PREFLIGHT_STATUS,
        ),
        "upstream_template_schema_version": _safe_source_marker(
            source.get("upstream_template_schema_version"),
            UPSTREAM_TEMPLATE_SCHEMA_VERSION,
        ),
        "upstream_template_stage": _safe_source_marker(
            source.get("upstream_template_stage"),
            UPSTREAM_TEMPLATE_STAGE,
        ),
        "upstream_template_status": _safe_source_marker(
            source.get("upstream_template_status"),
            UPSTREAM_TEMPLATE_STATUS,
        ),
        "external_receipt_gate_status": EXTERNAL_RECEIPT_GATE_STATUS,
        "external_intake_status": EXTERNAL_INTAKE_STATUS,
        "attachment_readiness_status": ATTACHMENT_READINESS_STATUS,
        "decision_audit_criteria_labels": DECISION_AUDIT_CRITERIA_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_case_receipt_manifest_decision_queue_rows": _safe_int(
                source_summary.get("case_receipt_manifest_decision_queue_rows", len(case_decision_rows))
            ),
            "source_attachment_receipt_manifest_decision_queue_rows": _safe_int(
                source_summary.get(
                    "attachment_receipt_manifest_decision_queue_rows",
                    len(slot_decision_rows),
                )
            ),
            "case_receipt_manifest_decision_audit_rows": len(case_rows),
            "attachment_receipt_manifest_decision_audit_rows": len(slot_rows),
            "pending_external_evidence_receipt_manifest_decision_audit_count": len(slot_rows),
            "pending_jhora_receipt_manifest_decision_audit_count": sum(
                1 for row in slot_rows if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_receipt_manifest_decision_audit_count": sum(
                1
                for row in slot_rows
                if row["evidence_family"] == "parashara_light_manual_values_or_packet"
            ),
            "decision_queue_rows": len(slot_rows),
            "decision_audit_ready_count": 0,
            "decision_audit_blocked_count": len(slot_rows),
            "receipt_manifest_received_count": 0,
            "receipt_manifest_accepted_count": 0,
            "receipt_manifest_rejected_count": 0,
            "receipt_manifest_deferred_count": 0,
            "decision_recorded_count": 0,
            "decision_audited_count": 0,
            "decision_audit_passed_count": 0,
            "decision_audit_failed_count": 0,
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
        "case_receipt_manifest_decision_audit_rows": case_rows,
        "attachment_receipt_manifest_decision_audit_rows": slot_rows,
    }


def _case_decision_audit_row(
    row: dict[str, Any],
    *,
    case_receipt_manifest_decision_audit_index: int,
    source_slots: list[dict[str, Any]],
) -> dict[str, Any]:
    source_slot_indices = [
        _safe_int(slot.get("attachment_receipt_manifest_decision_queue_index")) for slot in source_slots
    ]
    families = {str(slot.get("evidence_family") or "") for slot in source_slots}
    return {
        "case_receipt_manifest_decision_audit_index": case_receipt_manifest_decision_audit_index,
        "case_id": str(row.get("case_id") or ""),
        "source_case_receipt_manifest_decision_queue_index": _safe_int(
            row.get("case_receipt_manifest_decision_queue_index")
        )
        or case_receipt_manifest_decision_audit_index,
        "source_attachment_receipt_manifest_decision_queue_indices": source_slot_indices,
        "decision_audit_status": STATUS,
        "decision_queue_status": _safe_decision_queue_status(row.get("decision_queue_status")),
        "acceptance_gate_status": _safe_acceptance_gate_status(row.get("acceptance_gate_status")),
        "preflight_status": _safe_preflight_status(row.get("preflight_status")),
        "receipt_manifest_template_status": _safe_template_status(row.get("receipt_manifest_template_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("external_receipt_gate_status")),
        "external_intake_status": _safe_intake_status(row.get("external_intake_status")),
        "attachment_readiness_status": _safe_readiness_status(row.get("attachment_readiness_status")),
        "required_external_evidence_receipt_manifest_decision_audits": len(REQUIRED_EVIDENCE_FAMILIES),
        "pending_external_evidence_receipt_manifest_decision_audits": len(REQUIRED_EVIDENCE_FAMILIES),
        "jhora_decision_audit_required": "jhora_screenshot_or_packet" in families,
        "parashara_light_decision_audit_required": "parashara_light_manual_values_or_packet" in families,
        "receipt_manifest_received": False,
        "receipt_manifest_accepted": False,
        "receipt_manifest_rejected": False,
        "receipt_manifest_deferred": False,
        "decision_recorded": False,
        "decision_audited": False,
        "decision_audit_passed": False,
        "decision_audit_failed": False,
        "evidence_received": False,
        "evidence_validated": False,
        "evidence_file_recorded": False,
        "evidence_hash_recorded": False,
        "evidence_uploaded": False,
        "evidence_attached": False,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "mark_commands_blocked": True,
        "decision_audit_criteria_labels": DECISION_AUDIT_CRITERIA_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_decision_audit_row(
    row: dict[str, Any],
    *,
    attachment_receipt_manifest_decision_audit_index: int,
) -> dict[str, Any]:
    family = _safe_evidence_family(row.get("evidence_family"))
    return {
        "attachment_receipt_manifest_decision_audit_index": attachment_receipt_manifest_decision_audit_index,
        "case_receipt_manifest_decision_audit_index": _safe_int(
            row.get("case_receipt_manifest_decision_queue_index")
        ),
        "source_attachment_receipt_manifest_decision_queue_index": _safe_int(
            row.get("attachment_receipt_manifest_decision_queue_index")
        ),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": family,
        "external_tool_label": _external_tool_label(family),
        "expected_receipt_manifest_label": str(
            row.get("expected_receipt_manifest_label") or _expected_manifest_label(family)
        ),
        "redacted_receipt_manifest_id": "redacted_receipt_manifest_id_pending",
        "operator_decision_label": _operator_decision_label(family),
        "operator_decision_audit_label": _operator_decision_audit_label(family),
        "required_human_decision_timestamp_utc": "human_decision_timestamp_utc_pending",
        "required_human_decision_audit_timestamp_utc": "human_decision_audit_timestamp_utc_pending",
        "decision_queue_status": _safe_decision_queue_status(row.get("decision_queue_status")),
        "decision_audit_status": STATUS,
        "acceptance_gate_status": _safe_acceptance_gate_status(row.get("acceptance_gate_status")),
        "preflight_status": _safe_preflight_status(row.get("preflight_status")),
        "receipt_manifest_template_status": _safe_template_status(row.get("receipt_manifest_template_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("external_receipt_gate_status")),
        "external_intake_status": _safe_intake_status(row.get("external_intake_status")),
        "attachment_readiness_status": _safe_readiness_status(row.get("attachment_readiness_status")),
        "receipt_manifest_status": NOT_RECEIVED,
        "receipt_manifest_acceptance_status": NOT_STARTED,
        "receipt_manifest_rejection_status": NOT_STARTED,
        "receipt_manifest_defer_status": NOT_STARTED,
        "decision_record_status": NOT_STARTED,
        "decision_audit_record_status": NOT_STARTED,
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
        "no_upload_executed": True,
        "no_attachment_executed": True,
        "no_mark_command_executed": True,
        "decision_audit_criteria_labels": DECISION_AUDIT_CRITERIA_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "blocked_note": SLOT_BLOCKED_NOTE,
    }


def _slots_by_case(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index = _safe_int(row.get("case_receipt_manifest_decision_queue_index"))
        if index:
            grouped[index].append(row)
    for case_rows in grouped.values():
        case_rows.sort(key=lambda row: _safe_int(row.get("attachment_receipt_manifest_decision_queue_index")))
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


def _operator_decision_label(family: str) -> str:
    return (
        "await_jhora_receipt_manifest_decision"
        if family == "jhora_screenshot_or_packet"
        else "await_parashara_light_receipt_manifest_decision"
    )


def _operator_decision_audit_label(family: str) -> str:
    return (
        "await_jhora_receipt_manifest_decision_audit"
        if family == "jhora_screenshot_or_packet"
        else "await_parashara_light_receipt_manifest_decision_audit"
    )


def _safe_decision_queue_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_DECISION_QUEUE_STATUS else UPSTREAM_DECISION_QUEUE_STATUS


def _safe_acceptance_gate_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_ACCEPTANCE_GATE_STATUS else UPSTREAM_ACCEPTANCE_GATE_STATUS


def _safe_preflight_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_PREFLIGHT_STATUS else UPSTREAM_PREFLIGHT_STATUS


def _safe_template_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_TEMPLATE_STATUS else UPSTREAM_TEMPLATE_STATUS


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
