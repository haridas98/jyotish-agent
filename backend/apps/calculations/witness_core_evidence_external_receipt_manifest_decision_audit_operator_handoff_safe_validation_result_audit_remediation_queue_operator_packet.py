from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-result-audit-remediation-queue-operator-packet-v1"
)
DOMAIN_KEY = "witness_core_parity"
STAGE = "P99-A"
STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
    "safe_validation_result_audit_remediation_queue_operator_packet"
)
UPSTREAM_REMEDIATION_QUEUE_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-result-audit-remediation-queue-v1"
)
UPSTREAM_REMEDIATION_QUEUE_STAGE = "P97-A"
UPSTREAM_REMEDIATION_QUEUE_STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
    "safe_validation_result_audit_remediation_queue"
)
UPSTREAM_RESULT_AUDIT_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-result-audit-v1"
)
UPSTREAM_RESULT_AUDIT_STAGE = "P95-A"
UPSTREAM_RESULT_AUDIT_STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
    "safe_validation_result_audit"
)
UPSTREAM_RESULT_LEDGER_SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-result-ledger-v1"
)
UPSTREAM_RESULT_LEDGER_STAGE = "P93-A"
UPSTREAM_RESULT_LEDGER_STATUS = (
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
UPSTREAM_DECISION_AUDIT_STATUS = "blocked_pending_external_evidence_receipt_manifest_decision_audit"
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
RESULT_EXECUTION_STATUS = "not_executed"
RESULT_RECORD_STATUS = "not_recorded"
RESULT_ACCEPTANCE_STATUS = "not_accepted"
RESULT_FAILURE_STATUS = "not_failed"
AUDIT_EXECUTION_STATUS = "not_executed"
AUDIT_RECORD_STATUS = "not_recorded"
AUDIT_PASS_STATUS = "not_passed"
AUDIT_FAILURE_STATUS = "not_failed"
REMEDIATION_EXECUTION_STATUS = "not_executed"
REMEDIATION_TICKET_STATUS = "not_created"
REMEDIATION_NOTIFICATION_STATUS = "not_sent"
REMEDIATION_OPERATOR_HANDOFF_STATUS = "not_delivered"
REMEDIATION_CLOSURE_STATUS = "not_closed"
PACKET_DELIVERY_STATUS = "not_delivered"
PACKET_ACKNOWLEDGEMENT_STATUS = "not_acknowledged"
PACKET_CLOSURE_STATUS = "not_closed"
PACKET_EXECUTION_STATUS = "not_executed"
COMMAND_SMOKE_MATRIX_STATUS = "blocked_pending_external_evidence_and_operator_handoff"
NOT_RECEIVED = "not_received"
NOT_STARTED = "not_started"
NOT_DELIVERED = "not_delivered"

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
REMEDIATION_FAMILY_LABELS = {
    "validate_manifest_shape": "remediate_manifest_shape_blocked_label_only",
    "validate_operator_handoff_readiness": "remediate_operator_handoff_readiness_blocked_label_only",
    "validate_no_external_action": "remediate_no_external_action_blocked_label_only",
    "validate_release_gate_blocked": "remediate_release_gate_blocked_label_only",
}
OPERATOR_PACKET_FAMILY_LABELS = {
    "validate_manifest_shape": "packetize_manifest_shape_remediation_blocked_label_only",
    "validate_operator_handoff_readiness": "packetize_operator_handoff_readiness_remediation_blocked_label_only",
    "validate_no_external_action": "packetize_no_external_action_remediation_blocked_label_only",
    "validate_release_gate_blocked": "packetize_release_gate_remediation_blocked_label_only",
}
SAFE_NEXT_ACTION_LABELS = [
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_report",
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_report",
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
STATUS_LABELS = [
    "safe_validation_result_audit_remediation_queue_operator_packet_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet",
    "safe_validation_result_audit_remediation_queue_operator_packet_delivery_status=not_delivered",
    "safe_validation_result_audit_remediation_queue_operator_packet_acknowledgement_status=not_acknowledged",
    "safe_validation_result_audit_remediation_queue_operator_packet_closure_status=not_closed",
    "safe_validation_result_audit_remediation_queue_operator_packet_execution_status=not_executed",
    "safe_validation_result_audit_remediation_queue_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue",
    "safe_validation_result_audit_remediation_execution_status=not_executed",
    "safe_validation_result_audit_remediation_ticket_status=not_created",
    "safe_validation_result_audit_remediation_notification_status=not_sent",
    "safe_validation_result_audit_remediation_operator_handoff_status=not_delivered",
    "safe_validation_result_audit_remediation_closure_status=not_closed",
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
    "safe_validation_result_audit_remediation_queue_only=true",
    "safe_validation_result_audit_remediation_queue_operator_packet_only=true",
    "no_command_execution_performed=true",
    "no_safe_validation_result_recorded=true",
    "no_safe_validation_result_accepted=true",
    "no_safe_validation_result_failed=true",
    "no_safe_validation_result_audit_performed=true",
    "no_safe_validation_result_audit_passed=true",
    "no_safe_validation_result_audit_failed=true",
    "no_safe_validation_result_audit_remediation_executed=true",
    "no_safe_validation_result_audit_remediation_ticket_created=true",
    "no_safe_validation_result_audit_remediation_notification_sent=true",
    "no_safe_validation_result_audit_remediation_operator_handoff_delivered=true",
    "no_safe_validation_result_audit_remediation_closed=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_delivered=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_acknowledged=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_closed=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_executed=true",
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
    SCHEMA_VERSION,
    "P99",
    "P97",
    "P95",
    "P93",
    "P91",
    "P89",
    "P87",
    "P85",
    "P83",
    "P81",
    "P79",
    "P77",
    "P75",
]
BLOCKED_NOTE = (
    "Operator packet rows are labels only; no packet delivery, acknowledgement, closure, remediation, "
    "ticket action, notification, operator handoff, command execution, upload, attachment, mark, accept, "
    "reject, defer, result recording, or release action is executed."
)


def build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_report(
    *,
    external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_report_path: str
    | Path,
) -> dict[str, Any]:
    source = _read_json(
        Path(external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_report_path)
    )
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    source_case_rows = [row for row in source.get("safe_validation_result_audit_remediation_case_rows", []) if isinstance(row, dict)]
    source_attachment_rows = [
        row for row in source.get("safe_validation_result_audit_remediation_attachment_rows", []) if isinstance(row, dict)
    ]
    source_remediation_rows = [
        row for row in source.get("safe_validation_result_audit_remediation_queue_rows", []) if isinstance(row, dict)
    ]
    operator_packet_rows = [
        _operator_packet_row(row, safe_validation_result_audit_remediation_queue_operator_packet_index=index)
        for index, row in enumerate(source_remediation_rows, start=1)
    ]
    packet_indices_by_attachment = _packet_indices_by_attachment(operator_packet_rows)
    attachment_packet_rows = [
        _attachment_packet_row(
            row,
            safe_validation_result_audit_remediation_queue_operator_packet_attachment_index=index,
            packet_indices=packet_indices_by_attachment.get(index, []),
        )
        for index, row in enumerate(source_attachment_rows, start=1)
    ]
    attachment_indices_by_case = _attachment_indices_by_case(attachment_packet_rows)
    packet_indices_by_case = _packet_indices_by_case(operator_packet_rows)
    case_packet_rows = [
        _case_packet_row(
            row,
            safe_validation_result_audit_remediation_queue_operator_packet_case_index=index,
            attachment_indices=attachment_indices_by_case.get(index, []),
            packet_indices=packet_indices_by_case.get(index, []),
        )
        for index, row in enumerate(source_case_rows, start=1)
    ]
    summary = _summary(source_summary, case_packet_rows, attachment_packet_rows, source_remediation_rows, operator_packet_rows)

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_packet_rows else "empty",
        "upstream_remediation_queue_schema_version": _safe_source_marker(
            source.get("schema_version"),
            UPSTREAM_REMEDIATION_QUEUE_SCHEMA_VERSION,
        ),
        "upstream_remediation_queue_stage": _safe_source_marker(source.get("stage"), UPSTREAM_REMEDIATION_QUEUE_STAGE),
        "upstream_remediation_queue_status": _safe_source_marker(source.get("status"), UPSTREAM_REMEDIATION_QUEUE_STATUS),
        "upstream_safe_validation_result_audit_schema_version": _safe_source_marker(
            source.get("upstream_safe_validation_result_audit_schema_version"),
            UPSTREAM_RESULT_AUDIT_SCHEMA_VERSION,
        ),
        "upstream_safe_validation_result_audit_stage": _safe_source_marker(
            source.get("upstream_safe_validation_result_audit_stage"),
            UPSTREAM_RESULT_AUDIT_STAGE,
        ),
        "upstream_safe_validation_result_audit_status": _safe_source_marker(
            source.get("upstream_safe_validation_result_audit_status"),
            UPSTREAM_RESULT_AUDIT_STATUS,
        ),
        "upstream_safe_validation_result_ledger_schema_version": _safe_source_marker(
            source.get("upstream_safe_validation_result_ledger_schema_version"),
            UPSTREAM_RESULT_LEDGER_SCHEMA_VERSION,
        ),
        "upstream_safe_validation_result_ledger_stage": _safe_source_marker(
            source.get("upstream_safe_validation_result_ledger_stage"),
            UPSTREAM_RESULT_LEDGER_STAGE,
        ),
        "upstream_safe_validation_result_ledger_status": _safe_source_marker(
            source.get("upstream_safe_validation_result_ledger_status"),
            UPSTREAM_RESULT_LEDGER_STATUS,
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
        "upstream_decision_audit_stage": _safe_source_marker(source.get("upstream_decision_audit_stage"), UPSTREAM_DECISION_AUDIT_STAGE),
        "upstream_decision_audit_status": _safe_source_marker(source.get("upstream_decision_audit_status"), UPSTREAM_DECISION_AUDIT_STATUS),
        "upstream_decision_queue_schema_version": _safe_source_marker(
            source.get("upstream_decision_queue_schema_version"),
            UPSTREAM_DECISION_QUEUE_SCHEMA_VERSION,
        ),
        "upstream_decision_queue_stage": _safe_source_marker(source.get("upstream_decision_queue_stage"), UPSTREAM_DECISION_QUEUE_STAGE),
        "upstream_decision_queue_status": _safe_source_marker(source.get("upstream_decision_queue_status"), UPSTREAM_DECISION_QUEUE_STATUS),
        "upstream_acceptance_gate_schema_version": _safe_source_marker(
            source.get("upstream_acceptance_gate_schema_version"),
            UPSTREAM_ACCEPTANCE_GATE_SCHEMA_VERSION,
        ),
        "upstream_acceptance_gate_stage": _safe_source_marker(source.get("upstream_acceptance_gate_stage"), UPSTREAM_ACCEPTANCE_GATE_STAGE),
        "upstream_acceptance_gate_status": _safe_source_marker(source.get("upstream_acceptance_gate_status"), UPSTREAM_ACCEPTANCE_GATE_STATUS),
        "upstream_preflight_schema_version": _safe_source_marker(source.get("upstream_preflight_schema_version"), UPSTREAM_PREFLIGHT_SCHEMA_VERSION),
        "upstream_preflight_stage": _safe_source_marker(source.get("upstream_preflight_stage"), UPSTREAM_PREFLIGHT_STAGE),
        "upstream_preflight_status": _safe_source_marker(source.get("upstream_preflight_status"), UPSTREAM_PREFLIGHT_STATUS),
        "upstream_template_schema_version": _safe_source_marker(source.get("upstream_template_schema_version"), UPSTREAM_TEMPLATE_SCHEMA_VERSION),
        "upstream_template_stage": _safe_source_marker(source.get("upstream_template_stage"), UPSTREAM_TEMPLATE_STAGE),
        "upstream_template_status": _safe_source_marker(source.get("upstream_template_status"), UPSTREAM_TEMPLATE_STATUS),
        "external_receipt_gate_status": EXTERNAL_RECEIPT_GATE_STATUS,
        "external_intake_status": EXTERNAL_INTAKE_STATUS,
        "attachment_readiness_status": ATTACHMENT_READINESS_STATUS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_result_family_labels": list(RESULT_FAMILY_LABELS.values()),
        "safe_validation_result_audit_family_labels": list(AUDIT_FAMILY_LABELS.values()),
        "safe_validation_result_audit_remediation_family_labels": list(REMEDIATION_FAMILY_LABELS.values()),
        "safe_validation_result_audit_remediation_queue_operator_packet_family_labels": list(
            OPERATOR_PACKET_FAMILY_LABELS.values()
        ),
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "source_marker_labels": SOURCE_MARKER_LABELS,
        "count_labels": _count_labels(summary),
        "operator_note": BLOCKED_NOTE,
        "summary": summary,
        "safe_validation_result_audit_remediation_queue_operator_packet_case_rows": case_packet_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_attachment_rows": attachment_packet_rows,
        "safe_validation_result_audit_remediation_queue_rows": source_remediation_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_rows": operator_packet_rows,
    }


def _summary(
    source_summary: dict[str, Any],
    case_rows: list[dict[str, Any]],
    attachment_rows: list[dict[str, Any]],
    remediation_rows: list[dict[str, Any]],
    operator_packet_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "source_safe_validation_result_audit_remediation_case_rows": len(case_rows),
        "source_safe_validation_result_audit_remediation_attachment_rows": len(attachment_rows),
        "source_safe_validation_result_audit_remediation_queue_rows": len(remediation_rows),
        "safe_validation_transcript_case_rows": _safe_int(source_summary.get("safe_validation_transcript_case_rows")),
        "safe_validation_transcript_attachment_rows": _safe_int(source_summary.get("safe_validation_transcript_attachment_rows")),
        "safe_validation_transcript_command_rows": _safe_int(source_summary.get("safe_validation_transcript_command_rows")),
        "safe_validation_result_ledger_rows": _safe_int(source_summary.get("safe_validation_result_ledger_rows")),
        "safe_validation_result_audit_rows": _safe_int(source_summary.get("safe_validation_result_audit_rows")),
        "safe_validation_result_audit_remediation_queue_rows": len(remediation_rows),
        "safe_validation_result_audit_remediation_family_count": _safe_int(
            source_summary.get("safe_validation_result_audit_remediation_family_count")
        )
        or len(REMEDIATION_FAMILY_LABELS),
        "safe_validation_result_audit_remediation_ready_count": 0,
        "safe_validation_result_audit_remediation_blocked_count": len(remediation_rows),
        "safe_validation_result_audit_remediation_executed_count": 0,
        "safe_validation_result_audit_remediation_ticket_created_count": 0,
        "safe_validation_result_audit_remediation_notification_sent_count": 0,
        "safe_validation_result_audit_remediation_operator_handoff_delivered_count": 0,
        "safe_validation_result_audit_remediation_closed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_rows": len(operator_packet_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_family_count": len(OPERATOR_PACKET_FAMILY_LABELS),
        "safe_validation_result_audit_remediation_queue_operator_packet_ready_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_blocked_count": len(operator_packet_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_delivered_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_acknowledged_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_closed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_executed_count": 0,
        "ready_to_attach_count": 0,
        "ready_to_mark_count": 0,
        "remaining_not_reviewed_count": _safe_int(source_summary.get("remaining_not_reviewed_count")),
        "release_gate_status": _safe_status(source_summary.get("release_gate_status"), fallback="blocked"),
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }


def _case_packet_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_remediation_queue_operator_packet_case_index: int,
    attachment_indices: list[int],
    packet_indices: list[int],
) -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_case_index": safe_validation_result_audit_remediation_queue_operator_packet_case_index,
        "case_id": str(row.get("case_id") or ""),
        "source_safe_validation_result_audit_remediation_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_case_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_case_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_attachment_indices": attachment_indices,
        "safe_validation_result_audit_remediation_queue_operator_packet_indices": packet_indices,
        "safe_validation_result_audit_remediation_queue_operator_packet_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_or_remediation_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_packet_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_remediation_queue_operator_packet_attachment_index: int,
    packet_indices: list[int],
) -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_attachment_index": safe_validation_result_audit_remediation_queue_operator_packet_attachment_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_case_index")
        ),
        "source_safe_validation_result_audit_remediation_attachment_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_attachment_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_attachment_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_indices": packet_indices,
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": str(row.get("evidence_family") or ""),
        "external_tool_label": str(row.get("external_tool_label") or ""),
        "safe_validation_result_audit_remediation_queue_operator_packet_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_or_remediation_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _operator_packet_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_remediation_queue_operator_packet_index: int,
) -> dict[str, Any]:
    family = _safe_command_family(row.get("safe_validation_command_family"))
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_index": safe_validation_result_audit_remediation_queue_operator_packet_index,
        "source_safe_validation_result_audit_remediation_queue_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_attachment_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_attachment_index")
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_case_index")
        ),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": str(row.get("evidence_family") or ""),
        "external_tool_label": str(row.get("external_tool_label") or ""),
        "safe_validation_command_family_index": _safe_int(row.get("safe_validation_command_family_index")),
        "safe_validation_command_family": family,
        "safe_validation_result_family_label": RESULT_FAMILY_LABELS[family],
        "safe_validation_result_audit_family_label": AUDIT_FAMILY_LABELS[family],
        "safe_validation_result_audit_remediation_family_label": REMEDIATION_FAMILY_LABELS[family],
        "safe_validation_result_audit_remediation_queue_operator_packet_family_label": OPERATOR_PACKET_FAMILY_LABELS[
            family
        ],
        "safe_validation_result_audit_remediation_queue_operator_packet_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_or_remediation_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _status_fields() -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_delivery_status": PACKET_DELIVERY_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_acknowledgement_status": PACKET_ACKNOWLEDGEMENT_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_closure_status": PACKET_CLOSURE_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_execution_status": PACKET_EXECUTION_STATUS,
        "safe_validation_result_audit_remediation_queue_status": UPSTREAM_REMEDIATION_QUEUE_STATUS,
        "safe_validation_result_audit_remediation_execution_status": REMEDIATION_EXECUTION_STATUS,
        "safe_validation_result_audit_remediation_ticket_status": REMEDIATION_TICKET_STATUS,
        "safe_validation_result_audit_remediation_notification_status": REMEDIATION_NOTIFICATION_STATUS,
        "safe_validation_result_audit_remediation_operator_handoff_status": REMEDIATION_OPERATOR_HANDOFF_STATUS,
        "safe_validation_result_audit_remediation_closure_status": REMEDIATION_CLOSURE_STATUS,
        "safe_validation_result_audit_status": UPSTREAM_RESULT_AUDIT_STATUS,
        "safe_validation_result_audit_execution_status": AUDIT_EXECUTION_STATUS,
        "safe_validation_result_audit_record_status": AUDIT_RECORD_STATUS,
        "safe_validation_result_audit_pass_status": AUDIT_PASS_STATUS,
        "safe_validation_result_audit_failure_status": AUDIT_FAILURE_STATUS,
        "safe_validation_result_ledger_status": UPSTREAM_RESULT_LEDGER_STATUS,
        "safe_validation_result_execution_status": RESULT_EXECUTION_STATUS,
        "safe_validation_result_record_status": RESULT_RECORD_STATUS,
        "safe_validation_result_acceptance_status": RESULT_ACCEPTANCE_STATUS,
        "safe_validation_result_failure_status": RESULT_FAILURE_STATUS,
        "safe_validation_transcript_status": UPSTREAM_TRANSCRIPT_STATUS,
        "safe_validation_command_status": SAFE_VALIDATION_COMMAND_STATUS,
        "safe_validation_command_execution_status": SAFE_VALIDATION_COMMAND_EXECUTION_STATUS,
        "operator_handoff_smoke_matrix_status": UPSTREAM_SMOKE_MATRIX_STATUS,
        "decision_audit_work_order_readiness_status": UPSTREAM_READINESS_STATUS,
        "decision_audit_work_order_status": UPSTREAM_WORK_ORDERS_STATUS,
        "decision_audit_status": UPSTREAM_DECISION_AUDIT_STATUS,
        "decision_queue_status": UPSTREAM_DECISION_QUEUE_STATUS,
        "external_receipt_gate_status": EXTERNAL_RECEIPT_GATE_STATUS,
        "external_intake_status": EXTERNAL_INTAKE_STATUS,
        "attachment_readiness_status": ATTACHMENT_READINESS_STATUS,
        "receipt_manifest_status": NOT_RECEIVED,
        "decision_audit_record_status": NOT_STARTED,
        "work_order_delivery_status": NOT_DELIVERED,
        "operator_handoff_status": NOT_DELIVERED,
        "human_decision_audit_status": NOT_STARTED,
        "command_smoke_matrix_status": COMMAND_SMOKE_MATRIX_STATUS,
    }


def _safety_flags() -> dict[str, Any]:
    return {
        "safe_validation_only": True,
        "safe_validation_result_ledger_only": True,
        "safe_validation_result_audit_only": True,
        "safe_validation_result_audit_remediation_queue_only": True,
        "safe_validation_result_audit_remediation_queue_operator_packet_only": True,
        "safe_validation_result_audit_remediation_queue_operator_packet_delivered": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_acknowledged": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_closed": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_executed": False,
        "no_command_execution_performed": True,
        "no_safe_validation_result_recorded": True,
        "no_safe_validation_result_accepted": True,
        "no_safe_validation_result_failed": True,
        "no_safe_validation_result_audit_performed": True,
        "no_safe_validation_result_audit_passed": True,
        "no_safe_validation_result_audit_failed": True,
        "no_safe_validation_result_audit_remediation_executed": True,
        "no_safe_validation_result_audit_remediation_ticket_created": True,
        "no_safe_validation_result_audit_remediation_notification_sent": True,
        "no_safe_validation_result_audit_remediation_operator_handoff_delivered": True,
        "no_safe_validation_result_audit_remediation_closed": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_delivered": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_acknowledged": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_closed": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_executed": True,
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


def _packet_indices_by_attachment(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[_safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_attachment_index"))].append(
            _safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_index"))
        )
    return {key: values for key, values in grouped.items() if key}


def _packet_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[_safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_case_index"))].append(
            _safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_index"))
        )
    return {key: values for key, values in grouped.items() if key}


def _attachment_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[_safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_case_index"))].append(
            _safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_attachment_index"))
        )
    return {key: values for key, values in grouped.items() if key}


def _count_labels(summary: dict[str, Any]) -> list[str]:
    labels = [f"{key}={value}" for key, value in summary.items() if isinstance(value, int)]
    labels.extend(
        [
            f"release_gate_status={summary['release_gate_status']}",
            f"parity_success_claimed={str(summary['parity_success_claimed']).lower()}",
            f"release_ready_claimed={str(summary['release_ready_claimed']).lower()}",
        ]
    )
    return labels


def _safe_command_family(value: Any) -> str:
    value = str(value or "")
    return value if value in OPERATOR_PACKET_FAMILY_LABELS else "validate_manifest_shape"


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _safe_status(value: Any, *, fallback: str) -> str:
    return str(value) if isinstance(value, str) and value else fallback


def _safe_source_marker(value: Any, fallback: str) -> str:
    return str(value) if isinstance(value, str) and value else fallback


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))
