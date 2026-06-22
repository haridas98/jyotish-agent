from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-result-audit-v1"
)
DOMAIN_KEY = "witness_core_parity"
STAGE = "P95-A"
STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
    "safe_validation_result_audit"
)
UPSTREAM_LEDGER_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-result-ledger-v1"
)
UPSTREAM_LEDGER_STAGE = "P93-A"
UPSTREAM_LEDGER_STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
    "safe_validation_result_ledger"
)
UPSTREAM_TRANSCRIPT_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-transcript-v1"
)
UPSTREAM_TRANSCRIPT_STAGE = "P91-A"
UPSTREAM_TRANSCRIPT_STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
    "safe_validation_transcript"
)
UPSTREAM_SMOKE_MATRIX_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "smoke-matrix-v1"
)
UPSTREAM_SMOKE_MATRIX_STAGE = "P89-A"
UPSTREAM_SMOKE_MATRIX_STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_smoke_matrix"
)
UPSTREAM_READINESS_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-work-order-readiness-v1"
)
UPSTREAM_READINESS_STAGE = "P87-A"
UPSTREAM_READINESS_STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_work_order_readiness"
)
UPSTREAM_WORK_ORDERS_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-work-orders-v1"
)
UPSTREAM_WORK_ORDERS_STAGE = "P85-A"
UPSTREAM_WORK_ORDERS_STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_work_orders"
)
UPSTREAM_DECISION_AUDIT_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-v1"
)
UPSTREAM_DECISION_AUDIT_STAGE = "P83-A"
UPSTREAM_DECISION_AUDIT_STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit"
)
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
SAFE_VALIDATION_COMMAND_STATUS = "blocked_pending_external_evidence_and_operator_handoff"
SAFE_VALIDATION_COMMAND_EXECUTION_STATUS = "not_executed"
SAFE_VALIDATION_RESULT_EXECUTION_STATUS = "not_executed"
SAFE_VALIDATION_RESULT_RECORD_STATUS = "not_recorded"
SAFE_VALIDATION_RESULT_ACCEPTANCE_STATUS = "not_accepted"
SAFE_VALIDATION_RESULT_FAILURE_STATUS = "not_failed"
SAFE_VALIDATION_RESULT_AUDIT_EXECUTION_STATUS = "not_executed"
SAFE_VALIDATION_RESULT_AUDIT_RECORD_STATUS = "not_recorded"
SAFE_VALIDATION_RESULT_AUDIT_PASS_STATUS = "not_passed"
SAFE_VALIDATION_RESULT_AUDIT_FAILURE_STATUS = "not_failed"
COMMAND_SMOKE_MATRIX_STATUS = "blocked_pending_external_evidence_and_operator_handoff"
NOT_RECEIVED = "not_received"
NOT_STARTED = "not_started"
NOT_DELIVERED = "not_delivered"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_VALIDATION_COMMAND_FAMILIES = [
    "validate_manifest_shape",
    "validate_operator_handoff_readiness",
    "validate_no_external_action",
    "validate_release_gate_blocked",
]
RESULT_FAMILY_LABELS = {
    "validate_manifest_shape": "validate_manifest_shape_blocked_result_label_only",
    "validate_operator_handoff_readiness": "validate_operator_handoff_readiness_blocked_result_label_only",
    "validate_no_external_action": "validate_no_external_action_blocked_result_label_only",
    "validate_release_gate_blocked": "validate_release_gate_blocked_blocked_result_label_only",
}
AUDIT_FAMILY_LABELS = {
    "validate_manifest_shape": "audit_manifest_shape_blocked_label_only",
    "validate_operator_handoff_readiness": "audit_operator_handoff_readiness_blocked_label_only",
    "validate_no_external_action": "audit_no_external_action_blocked_label_only",
    "validate_release_gate_blocked": "audit_release_gate_blocked_label_only",
}
SAFE_NEXT_ACTION_LABELS = [
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_report",
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger_report",
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report",
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_smoke_matrix_report",
    "rerun_external_receipt_manifest_decision_audit_work_order_readiness_report",
    "rerun_external_receipt_manifest_decision_audit_work_orders_report",
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
RESULT_AUDIT_STATUS_LABELS = [
    "safe_validation_result_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit",
    "safe_validation_result_audit_execution_status=not_executed",
    "safe_validation_result_audit_record_status=not_recorded",
    "safe_validation_result_audit_pass_status=not_passed",
    "safe_validation_result_audit_failure_status=not_failed",
    "safe_validation_result_ledger_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger",
    "safe_validation_result_execution_status=not_executed",
    "safe_validation_result_record_status=not_recorded",
    "safe_validation_result_acceptance_status=not_accepted",
    "safe_validation_result_failure_status=not_failed",
    "safe_validation_transcript_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript",
    "safe_validation_command_status=blocked_pending_external_evidence_and_operator_handoff",
    "safe_validation_command_execution_status=not_executed",
    "operator_handoff_smoke_matrix_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_smoke_matrix",
    "decision_audit_work_order_readiness_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_work_order_readiness",
    "decision_audit_work_order_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_work_orders",
    "decision_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit",
    "decision_queue_status=blocked_pending_external_evidence_receipt_manifest_decision",
    "external_receipt_gate_status=blocked_pending_external_evidence_receipts",
    "external_intake_status=blocked_pending_external_evidence_intake",
    "attachment_readiness_status=blocked_pending_external_evidence_attachment",
    "receipt_manifest_status=not_received",
    "decision_audit_record_status=not_started",
    "work_order_delivery_status=not_delivered",
    "operator_handoff_status=not_delivered",
    "human_decision_audit_status=not_started",
    "command_smoke_matrix_status=blocked_pending_external_evidence_and_operator_handoff",
]
SAFETY_LABELS = [
    "safe_validation_only=true",
    "safe_validation_result_ledger_only=true",
    "safe_validation_result_audit_only=true",
    "no_command_execution_performed=true",
    "no_safe_validation_result_recorded=true",
    "no_safe_validation_result_accepted=true",
    "no_safe_validation_result_failed=true",
    "no_safe_validation_result_audit_performed=true",
    "no_safe_validation_result_audit_passed=true",
    "no_safe_validation_result_audit_failed=true",
    "no_raw_values_in_manifest=true",
    "no_private_paths_in_manifest=true",
    "no_secrets_in_manifest=true",
    "no_evidence_file_recorded=true",
    "no_evidence_hash_recorded=true",
    "no_upload_executed=true",
    "no_attachment_executed=true",
    "no_mark_command_executed=true",
    "no_accept_executed=true",
    "no_reject_executed=true",
    "no_defer_executed=true",
    "no_work_order_delivery_executed=true",
    "no_operator_handoff_delivered=true",
    "no_external_notification_sent=true",
    "no_external_ticket_created=true",
    "parity_success_claimed=false",
    "release_ready_claimed=false",
    "release_gate_status=blocked",
]
SOURCE_MARKER_LABELS = [
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-audit-v1",
    "safe_validation_transcript_case_rows=5",
    "safe_validation_transcript_attachment_rows=10",
    "safe_validation_transcript_command_rows=40",
    "safe_validation_result_ledger_rows=40",
    "safe_validation_result_audit_rows=40",
    "safe_validation_command_family_count=4",
    "safe_validation_command_execution_performed_count=0",
    "safe_validation_command_ready_count=0",
    "safe_validation_command_blocked_count=40",
    "safe_validation_result_recorded_count=0",
    "safe_validation_result_accepted_count=0",
    "safe_validation_result_failed_count=0",
    "safe_validation_result_blocked_count=40",
    "safe_validation_result_audit_performed_count=0",
    "safe_validation_result_audit_passed_count=0",
    "safe_validation_result_audit_failed_count=0",
    "safe_validation_result_audit_blocked_count=40",
]
BLOCKED_NOTE = (
    "Safe validation result audit rows are labels only; no command execution, result recording, audit, "
    "operator handoff, work-order delivery, notification, ticket, upload, attachment, mark, accept, "
    "reject, or defer action is executed."
)
AUDIT_BLOCKED_NOTE = (
    "Safe validation result audit row is blocked pending external evidence and operator handoff; "
    "the audit family is a label only and no result audit is recorded."
)


def build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_report(
    *,
    external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_ledger_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    case_rows = [
        row for row in source.get("safe_validation_result_ledger_case_rows", []) if isinstance(row, dict)
    ]
    attachment_rows = [
        row for row in source.get("safe_validation_result_ledger_attachment_rows", []) if isinstance(row, dict)
    ]
    ledger_rows = [
        row for row in source.get("safe_validation_result_ledger_rows", []) if isinstance(row, dict)
    ]

    audit_rows = [
        _audit_row(row, safe_validation_result_audit_index=index)
        for index, row in enumerate(ledger_rows, start=1)
    ]
    audit_indices_by_attachment = _audit_indices_by_attachment(audit_rows)
    audit_attachment_rows = [
        _attachment_row(
            row,
            safe_validation_result_audit_attachment_index=index,
            audit_indices=audit_indices_by_attachment.get(index, []),
        )
        for index, row in enumerate(attachment_rows, start=1)
    ]
    attachment_indices_by_case = _attachment_indices_by_case(audit_attachment_rows)
    audit_indices_by_case = _audit_indices_by_case(audit_rows)
    audit_case_rows = [
        _case_row(
            row,
            safe_validation_result_audit_case_index=index,
            attachment_indices=attachment_indices_by_case.get(index, []),
            audit_indices=audit_indices_by_case.get(index, []),
        )
        for index, row in enumerate(case_rows, start=1)
    ]
    summary = _summary(source_summary, audit_case_rows, audit_attachment_rows, audit_rows)

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if audit_case_rows else "empty",
        "upstream_safe_validation_result_ledger_schema_version": _safe_source_marker(
            source.get("schema_version"),
            UPSTREAM_LEDGER_SCHEMA_VERSION,
        ),
        "upstream_safe_validation_result_ledger_stage": _safe_source_marker(source.get("stage"), UPSTREAM_LEDGER_STAGE),
        "upstream_safe_validation_result_ledger_status": _safe_source_marker(
            source.get("status"),
            UPSTREAM_LEDGER_STATUS,
        ),
        "upstream_safe_validation_transcript_schema_version": _safe_source_marker(
            source.get("upstream_safe_validation_transcript_schema_version"),
            UPSTREAM_TRANSCRIPT_SCHEMA_VERSION,
        ),
        "upstream_safe_validation_transcript_stage": _safe_source_marker(
            source.get("upstream_safe_validation_transcript_stage"),
            UPSTREAM_TRANSCRIPT_STAGE,
        ),
        "upstream_safe_validation_transcript_status": _safe_source_marker(
            source.get("upstream_safe_validation_transcript_status"),
            UPSTREAM_TRANSCRIPT_STATUS,
        ),
        "upstream_operator_handoff_smoke_matrix_schema_version": _safe_source_marker(
            source.get("upstream_operator_handoff_smoke_matrix_schema_version"),
            UPSTREAM_SMOKE_MATRIX_SCHEMA_VERSION,
        ),
        "upstream_operator_handoff_smoke_matrix_stage": _safe_source_marker(
            source.get("upstream_operator_handoff_smoke_matrix_stage"),
            UPSTREAM_SMOKE_MATRIX_STAGE,
        ),
        "upstream_operator_handoff_smoke_matrix_status": _safe_source_marker(
            source.get("upstream_operator_handoff_smoke_matrix_status"),
            UPSTREAM_SMOKE_MATRIX_STATUS,
        ),
        "upstream_decision_audit_work_order_readiness_schema_version": _safe_source_marker(
            source.get("upstream_decision_audit_work_order_readiness_schema_version"),
            UPSTREAM_READINESS_SCHEMA_VERSION,
        ),
        "upstream_decision_audit_work_order_readiness_stage": _safe_source_marker(
            source.get("upstream_decision_audit_work_order_readiness_stage"),
            UPSTREAM_READINESS_STAGE,
        ),
        "upstream_decision_audit_work_order_readiness_status": _safe_source_marker(
            source.get("upstream_decision_audit_work_order_readiness_status"),
            UPSTREAM_READINESS_STATUS,
        ),
        "upstream_decision_audit_work_orders_schema_version": _safe_source_marker(
            source.get("upstream_decision_audit_work_orders_schema_version"),
            UPSTREAM_WORK_ORDERS_SCHEMA_VERSION,
        ),
        "upstream_decision_audit_work_orders_stage": _safe_source_marker(
            source.get("upstream_decision_audit_work_orders_stage"),
            UPSTREAM_WORK_ORDERS_STAGE,
        ),
        "upstream_decision_audit_work_orders_status": _safe_source_marker(
            source.get("upstream_decision_audit_work_orders_status"),
            UPSTREAM_WORK_ORDERS_STATUS,
        ),
        "upstream_decision_audit_schema_version": _safe_source_marker(
            source.get("upstream_decision_audit_schema_version"),
            UPSTREAM_DECISION_AUDIT_SCHEMA_VERSION,
        ),
        "upstream_decision_audit_stage": _safe_source_marker(
            source.get("upstream_decision_audit_stage"),
            UPSTREAM_DECISION_AUDIT_STAGE,
        ),
        "upstream_decision_audit_status": _safe_source_marker(
            source.get("upstream_decision_audit_status"),
            UPSTREAM_DECISION_AUDIT_STATUS,
        ),
        "upstream_decision_queue_schema_version": _safe_source_marker(
            source.get("upstream_decision_queue_schema_version"),
            UPSTREAM_DECISION_QUEUE_SCHEMA_VERSION,
        ),
        "upstream_decision_queue_stage": _safe_source_marker(
            source.get("upstream_decision_queue_stage"),
            UPSTREAM_DECISION_QUEUE_STAGE,
        ),
        "upstream_decision_queue_status": _safe_source_marker(
            source.get("upstream_decision_queue_status"),
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
        "upstream_template_stage": _safe_source_marker(source.get("upstream_template_stage"), UPSTREAM_TEMPLATE_STAGE),
        "upstream_template_status": _safe_source_marker(
            source.get("upstream_template_status"),
            UPSTREAM_TEMPLATE_STATUS,
        ),
        "external_receipt_gate_status": EXTERNAL_RECEIPT_GATE_STATUS,
        "external_intake_status": EXTERNAL_INTAKE_STATUS,
        "attachment_readiness_status": ATTACHMENT_READINESS_STATUS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "safe_validation_result_family_labels": list(RESULT_FAMILY_LABELS.values()),
        "safe_validation_result_audit_family_labels": list(AUDIT_FAMILY_LABELS.values()),
        "status_labels": RESULT_AUDIT_STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "source_marker_labels": SOURCE_MARKER_LABELS,
        "count_labels": _count_labels(summary),
        "operator_note": BLOCKED_NOTE,
        "summary": summary,
        "safe_validation_result_audit_case_rows": audit_case_rows,
        "safe_validation_result_audit_attachment_rows": audit_attachment_rows,
        "safe_validation_result_audit_rows": audit_rows,
    }


def _summary(
    source_summary: dict[str, Any],
    case_rows: list[dict[str, Any]],
    attachment_rows: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "source_safe_validation_result_ledger_case_rows": len(case_rows),
        "source_safe_validation_result_ledger_attachment_rows": len(attachment_rows),
        "source_safe_validation_result_ledger_rows": len(audit_rows),
        "safe_validation_transcript_case_rows": _safe_int(source_summary.get("safe_validation_transcript_case_rows")),
        "safe_validation_transcript_attachment_rows": _safe_int(
            source_summary.get("safe_validation_transcript_attachment_rows")
        ),
        "safe_validation_transcript_command_rows": _safe_int(
            source_summary.get("safe_validation_transcript_command_rows")
        ),
        "safe_validation_result_ledger_rows": _safe_int(source_summary.get("safe_validation_result_ledger_rows")),
        "safe_validation_result_audit_rows": len(audit_rows),
        "safe_validation_command_family_count": _safe_int(source_summary.get("safe_validation_command_family_count")),
        "safe_validation_command_execution_performed_count": 0,
        "safe_validation_command_ready_count": 0,
        "safe_validation_command_blocked_count": len(audit_rows),
        "safe_validation_result_recorded_count": 0,
        "safe_validation_result_accepted_count": 0,
        "safe_validation_result_failed_count": 0,
        "safe_validation_result_blocked_count": len(audit_rows),
        "safe_validation_result_audit_performed_count": 0,
        "safe_validation_result_audit_passed_count": 0,
        "safe_validation_result_audit_failed_count": 0,
        "safe_validation_result_audit_blocked_count": len(audit_rows),
        "operator_handoff_case_packet_rows": _safe_int(source_summary.get("operator_handoff_case_packet_rows")),
        "operator_handoff_attachment_packet_rows": _safe_int(
            source_summary.get("operator_handoff_attachment_packet_rows")
        ),
        "operator_handoff_smoke_case_rows": _safe_int(source_summary.get("operator_handoff_smoke_case_rows")),
        "operator_handoff_smoke_attachment_rows": _safe_int(
            source_summary.get("operator_handoff_smoke_attachment_rows")
        ),
        "unsafe_external_action_command_count": 0,
        "command_execution_performed_count": 0,
        "command_smoke_matrix_ready_count": 0,
        "command_smoke_matrix_blocked_count": _safe_int(source_summary.get("command_smoke_matrix_blocked_count")),
        "operator_handoff_ready_count": 0,
        "operator_handoff_blocked_count": _safe_int(source_summary.get("operator_handoff_blocked_count")),
        "work_order_delivery_ready_count": 0,
        "work_order_delivery_blocked_count": _safe_int(source_summary.get("work_order_delivery_blocked_count")),
        "pending_external_evidence_decision_audit_work_order_count": _safe_int(
            source_summary.get("pending_external_evidence_decision_audit_work_order_count")
        ),
        "pending_jhora_decision_audit_work_order_count": _safe_int(
            source_summary.get("pending_jhora_decision_audit_work_order_count")
        ),
        "pending_parashara_light_decision_audit_work_order_count": _safe_int(
            source_summary.get("pending_parashara_light_decision_audit_work_order_count")
        ),
        "decision_recorded_count": 0,
        "decision_audited_count": 0,
        "decision_audit_passed_count": 0,
        "decision_audit_failed_count": 0,
        "ready_to_attach_count": 0,
        "ready_to_mark_count": 0,
        "remaining_not_reviewed_count": _safe_int(source_summary.get("remaining_not_reviewed_count")),
        "release_gate_status": _safe_status(source_summary.get("release_gate_status"), fallback="blocked"),
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }


def _case_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_case_index: int,
    attachment_indices: list[int],
    audit_indices: list[int],
) -> dict[str, Any]:
    return {
        "safe_validation_result_audit_case_index": safe_validation_result_audit_case_index,
        "case_id": str(row.get("case_id") or ""),
        "source_safe_validation_result_ledger_case_index": _safe_int(
            row.get("safe_validation_result_ledger_case_index")
        )
        or safe_validation_result_audit_case_index,
        "source_safe_validation_result_ledger_attachment_indices": [
            _safe_int(value) for value in row.get("safe_validation_result_ledger_attachment_indices", [])
        ],
        "safe_validation_result_audit_attachment_indices": attachment_indices,
        "safe_validation_result_audit_indices": audit_indices,
        "safe_validation_result_audit_status": STATUS,
        "safe_validation_result_ledger_status": _safe_ledger_status(row.get("safe_validation_result_ledger_status")),
        "safe_validation_transcript_status": _safe_transcript_status(row.get("safe_validation_transcript_status")),
        "safe_validation_command_status": SAFE_VALIDATION_COMMAND_STATUS,
        "safe_validation_command_execution_status": SAFE_VALIDATION_COMMAND_EXECUTION_STATUS,
        "operator_handoff_smoke_matrix_status": _safe_smoke_matrix_status(
            row.get("operator_handoff_smoke_matrix_status")
        ),
        "decision_audit_work_order_readiness_status": _safe_readiness_status(
            row.get("decision_audit_work_order_readiness_status")
        ),
        "decision_audit_work_order_status": _safe_work_order_status(row.get("decision_audit_work_order_status")),
        "decision_audit_status": _safe_decision_audit_status(row.get("decision_audit_status")),
        "decision_queue_status": _safe_decision_queue_status(row.get("decision_queue_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("external_receipt_gate_status")),
        "external_intake_status": _safe_intake_status(row.get("external_intake_status")),
        "attachment_readiness_status": _safe_attachment_readiness_status(row.get("attachment_readiness_status")),
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "safe_validation_result_audit_performed": False,
        "safe_validation_result_audit_passed": False,
        "safe_validation_result_audit_failed": False,
        "safe_validation_result_audit_blocked": True,
        "safe_validation_only": True,
        "safe_validation_result_ledger_only": True,
        "safe_validation_result_audit_only": True,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": RESULT_AUDIT_STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_handoff_or_safe_validation_result_audit",
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_attachment_index: int,
    audit_indices: list[int],
) -> dict[str, Any]:
    family = _safe_evidence_family(row.get("evidence_family"))
    return {
        "safe_validation_result_audit_attachment_index": safe_validation_result_audit_attachment_index,
        "safe_validation_result_audit_case_index": _safe_int(row.get("safe_validation_result_ledger_case_index")),
        "source_safe_validation_result_ledger_attachment_index": _safe_int(
            row.get("safe_validation_result_ledger_attachment_index")
        ),
        "source_safe_validation_result_ledger_case_index": _safe_int(row.get("safe_validation_result_ledger_case_index")),
        "safe_validation_result_audit_indices": audit_indices,
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": family,
        "external_tool_label": _external_tool_label(family),
        "operator_label": str(row.get("operator_label") or _operator_label(family)),
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "safe_validation_result_audit_status": STATUS,
        "safe_validation_result_ledger_status": _safe_ledger_status(row.get("safe_validation_result_ledger_status")),
        "safe_validation_transcript_status": _safe_transcript_status(row.get("safe_validation_transcript_status")),
        "safe_validation_command_status": SAFE_VALIDATION_COMMAND_STATUS,
        "safe_validation_command_execution_status": SAFE_VALIDATION_COMMAND_EXECUTION_STATUS,
        "operator_handoff_smoke_matrix_status": _safe_smoke_matrix_status(
            row.get("operator_handoff_smoke_matrix_status")
        ),
        "decision_audit_work_order_readiness_status": _safe_readiness_status(
            row.get("decision_audit_work_order_readiness_status")
        ),
        "decision_audit_work_order_status": _safe_work_order_status(row.get("decision_audit_work_order_status")),
        "decision_audit_status": _safe_decision_audit_status(row.get("decision_audit_status")),
        "decision_queue_status": _safe_decision_queue_status(row.get("decision_queue_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("external_receipt_gate_status")),
        "external_intake_status": _safe_intake_status(row.get("external_intake_status")),
        "attachment_readiness_status": _safe_attachment_readiness_status(row.get("attachment_readiness_status")),
        **_audit_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": RESULT_AUDIT_STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_handoff_or_safe_validation_result_audit",
        "blocked_note": BLOCKED_NOTE,
    }


def _audit_row(row: dict[str, Any], *, safe_validation_result_audit_index: int) -> dict[str, Any]:
    family = _safe_evidence_family(row.get("evidence_family"))
    attachment_index = _safe_int(row.get("safe_validation_result_ledger_attachment_index"))
    case_index = _safe_int(row.get("safe_validation_result_ledger_case_index"))
    command_family = _safe_validation_family(row.get("safe_validation_command_family"))
    return {
        "safe_validation_result_audit_index": safe_validation_result_audit_index,
        "source_safe_validation_result_ledger_index": _safe_int(row.get("safe_validation_result_ledger_index"))
        or safe_validation_result_audit_index,
        "safe_validation_result_audit_attachment_index": attachment_index,
        "safe_validation_result_audit_case_index": case_index,
        "source_safe_validation_result_ledger_attachment_index": attachment_index,
        "source_safe_validation_result_ledger_case_index": case_index,
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": family,
        "external_tool_label": _external_tool_label(family),
        "operator_label": str(row.get("operator_label") or _operator_label(family)),
        "safe_validation_command_family_index": _safe_int(row.get("safe_validation_command_family_index")),
        "safe_validation_command_family": command_family,
        "safe_validation_result_family_label": _result_family_label(command_family),
        "safe_validation_result_audit_family_label": _audit_family_label(command_family),
        "safe_validation_result_audit_status": STATUS,
        "safe_validation_result_ledger_status": _safe_ledger_status(row.get("safe_validation_result_ledger_status")),
        "safe_validation_transcript_status": _safe_transcript_status(row.get("safe_validation_transcript_status")),
        "safe_validation_command_status": SAFE_VALIDATION_COMMAND_STATUS,
        "safe_validation_command_execution_status": SAFE_VALIDATION_COMMAND_EXECUTION_STATUS,
        "operator_handoff_smoke_matrix_status": _safe_smoke_matrix_status(
            row.get("operator_handoff_smoke_matrix_status")
        ),
        "decision_audit_work_order_readiness_status": _safe_readiness_status(
            row.get("decision_audit_work_order_readiness_status")
        ),
        "decision_audit_work_order_status": _safe_work_order_status(row.get("decision_audit_work_order_status")),
        "decision_audit_status": _safe_decision_audit_status(row.get("decision_audit_status")),
        "decision_queue_status": _safe_decision_queue_status(row.get("decision_queue_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("external_receipt_gate_status")),
        "external_intake_status": _safe_intake_status(row.get("external_intake_status")),
        "attachment_readiness_status": _safe_attachment_readiness_status(row.get("attachment_readiness_status")),
        **_audit_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": RESULT_AUDIT_STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_handoff_or_safe_validation_result_audit",
        "blocked_note": AUDIT_BLOCKED_NOTE,
    }


def _audit_status_fields() -> dict[str, Any]:
    return {
        "safe_validation_result_audit_execution_status": SAFE_VALIDATION_RESULT_AUDIT_EXECUTION_STATUS,
        "safe_validation_result_audit_record_status": SAFE_VALIDATION_RESULT_AUDIT_RECORD_STATUS,
        "safe_validation_result_audit_pass_status": SAFE_VALIDATION_RESULT_AUDIT_PASS_STATUS,
        "safe_validation_result_audit_failure_status": SAFE_VALIDATION_RESULT_AUDIT_FAILURE_STATUS,
        "safe_validation_result_execution_status": SAFE_VALIDATION_RESULT_EXECUTION_STATUS,
        "safe_validation_result_record_status": SAFE_VALIDATION_RESULT_RECORD_STATUS,
        "safe_validation_result_acceptance_status": SAFE_VALIDATION_RESULT_ACCEPTANCE_STATUS,
        "safe_validation_result_failure_status": SAFE_VALIDATION_RESULT_FAILURE_STATUS,
        "receipt_manifest_status": NOT_RECEIVED,
        "decision_audit_record_status": NOT_STARTED,
        "work_order_delivery_status": NOT_DELIVERED,
        "operator_handoff_status": NOT_DELIVERED,
        "human_decision_audit_status": NOT_STARTED,
        "command_smoke_matrix_status": COMMAND_SMOKE_MATRIX_STATUS,
        "safe_validation_only": True,
        "safe_validation_result_ledger_only": True,
        "safe_validation_result_audit_only": True,
        "safe_validation_command_execution_performed": False,
        "safe_validation_result_recorded": False,
        "safe_validation_result_accepted": False,
        "safe_validation_result_failed": False,
        "safe_validation_result_blocked": True,
        "safe_validation_result_audit_performed": False,
        "safe_validation_result_audit_passed": False,
        "safe_validation_result_audit_failed": False,
        "safe_validation_result_audit_blocked": True,
        "no_command_execution_performed": True,
        "no_safe_validation_result_recorded": True,
        "no_safe_validation_result_accepted": True,
        "no_safe_validation_result_failed": True,
        "no_safe_validation_result_audit_performed": True,
        "no_safe_validation_result_audit_passed": True,
        "no_safe_validation_result_audit_failed": True,
    }


def _safety_flags() -> dict[str, bool]:
    return {
        "no_raw_values_in_manifest": True,
        "no_private_paths_in_manifest": True,
        "no_secrets_in_manifest": True,
        "no_evidence_file_recorded": True,
        "no_evidence_hash_recorded": True,
        "no_upload_executed": True,
        "no_attachment_executed": True,
        "no_mark_command_executed": True,
        "no_accept_executed": True,
        "no_reject_executed": True,
        "no_defer_executed": True,
        "no_work_order_delivery_executed": True,
        "no_operator_handoff_delivered": True,
        "no_external_notification_sent": True,
        "no_external_ticket_created": True,
    }


def _count_labels(summary: dict[str, Any]) -> list[str]:
    return [f"{key}={str(value).lower()}" for key, value in summary.items()]


def _audit_indices_by_attachment(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        attachment_index = _safe_int(row.get("safe_validation_result_audit_attachment_index"))
        audit_index = _safe_int(row.get("safe_validation_result_audit_index"))
        if attachment_index and audit_index:
            grouped[attachment_index].append(audit_index)
    return dict(grouped)


def _attachment_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        case_index = _safe_int(row.get("safe_validation_result_audit_case_index"))
        attachment_index = _safe_int(row.get("safe_validation_result_audit_attachment_index"))
        if case_index and attachment_index:
            grouped[case_index].append(attachment_index)
    return dict(grouped)


def _audit_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        case_index = _safe_int(row.get("safe_validation_result_audit_case_index"))
        audit_index = _safe_int(row.get("safe_validation_result_audit_index"))
        if case_index and audit_index:
            grouped[case_index].append(audit_index)
    return dict(grouped)


def _safe_evidence_family(value: Any) -> str:
    text = str(value or "")
    return text if text in REQUIRED_EVIDENCE_FAMILIES else "jhora_screenshot_or_packet"


def _safe_validation_family(value: Any) -> str:
    text = str(value or "")
    return text if text in SAFE_VALIDATION_COMMAND_FAMILIES else SAFE_VALIDATION_COMMAND_FAMILIES[0]


def _result_family_label(family: str) -> str:
    return RESULT_FAMILY_LABELS.get(family, RESULT_FAMILY_LABELS[SAFE_VALIDATION_COMMAND_FAMILIES[0]])


def _audit_family_label(family: str) -> str:
    return AUDIT_FAMILY_LABELS.get(family, AUDIT_FAMILY_LABELS[SAFE_VALIDATION_COMMAND_FAMILIES[0]])


def _external_tool_label(family: str) -> str:
    return "jhora" if family == "jhora_screenshot_or_packet" else "parashara_light"


def _operator_label(family: str) -> str:
    return (
        "await_jhora_safe_validation_result_audit"
        if family == "jhora_screenshot_or_packet"
        else "await_parashara_light_safe_validation_result_audit"
    )


def _safe_ledger_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_LEDGER_STATUS else UPSTREAM_LEDGER_STATUS


def _safe_transcript_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_TRANSCRIPT_STATUS else UPSTREAM_TRANSCRIPT_STATUS


def _safe_smoke_matrix_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_SMOKE_MATRIX_STATUS else UPSTREAM_SMOKE_MATRIX_STATUS


def _safe_readiness_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_READINESS_STATUS else UPSTREAM_READINESS_STATUS


def _safe_work_order_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_WORK_ORDERS_STATUS else UPSTREAM_WORK_ORDERS_STATUS


def _safe_decision_audit_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_DECISION_AUDIT_STATUS else UPSTREAM_DECISION_AUDIT_STATUS


def _safe_decision_queue_status(value: Any) -> str:
    text = str(value or "")
    return text if text == UPSTREAM_DECISION_QUEUE_STATUS else UPSTREAM_DECISION_QUEUE_STATUS


def _safe_receipt_gate_status(value: Any) -> str:
    text = str(value or "")
    return text if text == EXTERNAL_RECEIPT_GATE_STATUS else EXTERNAL_RECEIPT_GATE_STATUS


def _safe_intake_status(value: Any) -> str:
    text = str(value or "")
    return text if text == EXTERNAL_INTAKE_STATUS else EXTERNAL_INTAKE_STATUS


def _safe_attachment_readiness_status(value: Any) -> str:
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
