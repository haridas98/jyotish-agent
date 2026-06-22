from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from apps.calculations import (
    witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet as p99,
)


SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-v1"
)
DOMAIN_KEY = "witness_core_parity"
STAGE = "P101-A"
STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate"
)
DISPATCH_STATUS = "not_dispatched"
DISPATCH_DELIVERY_STATUS = "not_delivered"
DISPATCH_ACKNOWLEDGEMENT_STATUS = "not_acknowledged"
DISPATCH_CLOSURE_STATUS = "not_closed"
DISPATCH_EXECUTION_STATUS = "not_executed"

DISPATCH_GATE_FAMILY_LABELS = {
    "validate_manifest_shape": "gate_manifest_shape_operator_packet_dispatch_blocked_label_only",
    "validate_operator_handoff_readiness": "gate_operator_handoff_readiness_operator_packet_dispatch_blocked_label_only",
    "validate_no_external_action": "gate_no_external_action_operator_packet_dispatch_blocked_label_only",
    "validate_release_gate_blocked": "gate_release_gate_operator_packet_dispatch_blocked_label_only",
}
SAFE_NEXT_ACTION_LABELS = [
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_report",
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_report",
    *p99.SAFE_NEXT_ACTION_LABELS,
]
STATUS_LABELS = [
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_status=not_dispatched",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivery_status=not_delivered",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledgement_status=not_acknowledged",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closure_status=not_closed",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_execution_status=not_executed",
    *p99.STATUS_LABELS,
]
SAFETY_LABELS = [
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_only=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatched=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivered=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledged=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closed=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_executed=true",
    *p99.SAFETY_LABELS,
]
SOURCE_MARKER_LABELS = [
    SCHEMA_VERSION,
    "P101",
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
    "Dispatch gate rows are labels only; dispatch action, packet delivery, acknowledgement, closure, "
    "remediation, ticket action, notification, operator handoff, command execution, upload, attachment, "
    "mark, accept, reject, defer, result recording, or release action is blocked."
)


def build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_report(
    *,
    external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_report_path: str
    | Path,
) -> dict[str, Any]:
    source = _read_json(
        Path(
            external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_report_path
        )
    )
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    source_case_rows = [
        row
        for row in source.get("safe_validation_result_audit_remediation_queue_operator_packet_case_rows", [])
        if isinstance(row, dict)
    ]
    source_attachment_rows = [
        row
        for row in source.get("safe_validation_result_audit_remediation_queue_operator_packet_attachment_rows", [])
        if isinstance(row, dict)
    ]
    source_remediation_rows = [
        row for row in source.get("safe_validation_result_audit_remediation_queue_rows", []) if isinstance(row, dict)
    ]
    source_operator_packet_rows = [
        row
        for row in source.get("safe_validation_result_audit_remediation_queue_operator_packet_rows", [])
        if isinstance(row, dict)
    ]
    dispatch_gate_rows = [
        _dispatch_gate_row(row, safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index=index)
        for index, row in enumerate(source_operator_packet_rows, start=1)
    ]
    dispatch_indices_by_attachment = _dispatch_indices_by_attachment(dispatch_gate_rows)
    attachment_rows = [
        _attachment_row(
            row,
            safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index=index,
            dispatch_indices=dispatch_indices_by_attachment.get(index, []),
        )
        for index, row in enumerate(source_attachment_rows, start=1)
    ]
    attachment_indices_by_case = _attachment_indices_by_case(attachment_rows)
    dispatch_indices_by_case = _dispatch_indices_by_case(dispatch_gate_rows)
    case_rows = [
        _case_row(
            row,
            safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index=index,
            attachment_indices=attachment_indices_by_case.get(index, []),
            dispatch_indices=dispatch_indices_by_case.get(index, []),
        )
        for index, row in enumerate(source_case_rows, start=1)
    ]
    summary = _summary(
        source_summary,
        case_rows,
        attachment_rows,
        source_remediation_rows,
        source_operator_packet_rows,
        dispatch_gate_rows,
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_rows else "empty",
        "upstream_operator_packet_schema_version": _safe_source_marker(
            source.get("schema_version"),
            p99.SCHEMA_VERSION,
        ),
        "upstream_operator_packet_stage": _safe_source_marker(source.get("stage"), p99.STAGE),
        "upstream_operator_packet_status": _safe_source_marker(source.get("status"), p99.STATUS),
        "upstream_remediation_queue_schema_version": _safe_source_marker(
            source.get("upstream_remediation_queue_schema_version"),
            p99.UPSTREAM_REMEDIATION_QUEUE_SCHEMA_VERSION,
        ),
        "upstream_remediation_queue_stage": _safe_source_marker(
            source.get("upstream_remediation_queue_stage"),
            p99.UPSTREAM_REMEDIATION_QUEUE_STAGE,
        ),
        "upstream_remediation_queue_status": _safe_source_marker(
            source.get("upstream_remediation_queue_status"),
            p99.UPSTREAM_REMEDIATION_QUEUE_STATUS,
        ),
        "upstream_safe_validation_result_audit_schema_version": _safe_source_marker(
            source.get("upstream_safe_validation_result_audit_schema_version"),
            p99.UPSTREAM_RESULT_AUDIT_SCHEMA_VERSION,
        ),
        "upstream_safe_validation_result_audit_stage": _safe_source_marker(
            source.get("upstream_safe_validation_result_audit_stage"),
            p99.UPSTREAM_RESULT_AUDIT_STAGE,
        ),
        "upstream_safe_validation_result_audit_status": _safe_source_marker(
            source.get("upstream_safe_validation_result_audit_status"),
            p99.UPSTREAM_RESULT_AUDIT_STATUS,
        ),
        "upstream_safe_validation_result_ledger_schema_version": _safe_source_marker(
            source.get("upstream_safe_validation_result_ledger_schema_version"),
            p99.UPSTREAM_RESULT_LEDGER_SCHEMA_VERSION,
        ),
        "upstream_safe_validation_result_ledger_stage": _safe_source_marker(
            source.get("upstream_safe_validation_result_ledger_stage"),
            p99.UPSTREAM_RESULT_LEDGER_STAGE,
        ),
        "upstream_safe_validation_result_ledger_status": _safe_source_marker(
            source.get("upstream_safe_validation_result_ledger_status"),
            p99.UPSTREAM_RESULT_LEDGER_STATUS,
        ),
        "upstream_safe_validation_transcript_schema_version": _safe_source_marker(
            source.get("upstream_safe_validation_transcript_schema_version"),
            p99.UPSTREAM_TRANSCRIPT_SCHEMA_VERSION,
        ),
        "upstream_safe_validation_transcript_stage": _safe_source_marker(
            source.get("upstream_safe_validation_transcript_stage"),
            p99.UPSTREAM_TRANSCRIPT_STAGE,
        ),
        "upstream_safe_validation_transcript_status": _safe_source_marker(
            source.get("upstream_safe_validation_transcript_status"),
            p99.UPSTREAM_TRANSCRIPT_STATUS,
        ),
        "upstream_operator_handoff_smoke_matrix_schema_version": _safe_source_marker(
            source.get("upstream_operator_handoff_smoke_matrix_schema_version"),
            p99.UPSTREAM_SMOKE_MATRIX_SCHEMA_VERSION,
        ),
        "upstream_operator_handoff_smoke_matrix_stage": _safe_source_marker(
            source.get("upstream_operator_handoff_smoke_matrix_stage"),
            p99.UPSTREAM_SMOKE_MATRIX_STAGE,
        ),
        "upstream_operator_handoff_smoke_matrix_status": _safe_source_marker(
            source.get("upstream_operator_handoff_smoke_matrix_status"),
            p99.UPSTREAM_SMOKE_MATRIX_STATUS,
        ),
        "upstream_decision_audit_work_order_readiness_schema_version": _safe_source_marker(
            source.get("upstream_decision_audit_work_order_readiness_schema_version"),
            p99.UPSTREAM_READINESS_SCHEMA_VERSION,
        ),
        "upstream_decision_audit_work_order_readiness_stage": _safe_source_marker(
            source.get("upstream_decision_audit_work_order_readiness_stage"),
            p99.UPSTREAM_READINESS_STAGE,
        ),
        "upstream_decision_audit_work_order_readiness_status": _safe_source_marker(
            source.get("upstream_decision_audit_work_order_readiness_status"),
            p99.UPSTREAM_READINESS_STATUS,
        ),
        "upstream_decision_audit_work_orders_schema_version": _safe_source_marker(
            source.get("upstream_decision_audit_work_orders_schema_version"),
            p99.UPSTREAM_WORK_ORDERS_SCHEMA_VERSION,
        ),
        "upstream_decision_audit_work_orders_stage": _safe_source_marker(
            source.get("upstream_decision_audit_work_orders_stage"),
            p99.UPSTREAM_WORK_ORDERS_STAGE,
        ),
        "upstream_decision_audit_work_orders_status": _safe_source_marker(
            source.get("upstream_decision_audit_work_orders_status"),
            p99.UPSTREAM_WORK_ORDERS_STATUS,
        ),
        "upstream_decision_audit_schema_version": _safe_source_marker(
            source.get("upstream_decision_audit_schema_version"),
            p99.UPSTREAM_DECISION_AUDIT_SCHEMA_VERSION,
        ),
        "upstream_decision_audit_stage": _safe_source_marker(
            source.get("upstream_decision_audit_stage"),
            p99.UPSTREAM_DECISION_AUDIT_STAGE,
        ),
        "upstream_decision_audit_status": _safe_source_marker(
            source.get("upstream_decision_audit_status"),
            p99.UPSTREAM_DECISION_AUDIT_STATUS,
        ),
        "upstream_decision_queue_schema_version": _safe_source_marker(
            source.get("upstream_decision_queue_schema_version"),
            p99.UPSTREAM_DECISION_QUEUE_SCHEMA_VERSION,
        ),
        "upstream_decision_queue_stage": _safe_source_marker(
            source.get("upstream_decision_queue_stage"),
            p99.UPSTREAM_DECISION_QUEUE_STAGE,
        ),
        "upstream_decision_queue_status": _safe_source_marker(
            source.get("upstream_decision_queue_status"),
            p99.UPSTREAM_DECISION_QUEUE_STATUS,
        ),
        "upstream_acceptance_gate_schema_version": _safe_source_marker(
            source.get("upstream_acceptance_gate_schema_version"),
            p99.UPSTREAM_ACCEPTANCE_GATE_SCHEMA_VERSION,
        ),
        "upstream_acceptance_gate_stage": _safe_source_marker(
            source.get("upstream_acceptance_gate_stage"),
            p99.UPSTREAM_ACCEPTANCE_GATE_STAGE,
        ),
        "upstream_acceptance_gate_status": _safe_source_marker(
            source.get("upstream_acceptance_gate_status"),
            p99.UPSTREAM_ACCEPTANCE_GATE_STATUS,
        ),
        "upstream_preflight_schema_version": _safe_source_marker(
            source.get("upstream_preflight_schema_version"),
            p99.UPSTREAM_PREFLIGHT_SCHEMA_VERSION,
        ),
        "upstream_preflight_stage": _safe_source_marker(source.get("upstream_preflight_stage"), p99.UPSTREAM_PREFLIGHT_STAGE),
        "upstream_preflight_status": _safe_source_marker(
            source.get("upstream_preflight_status"),
            p99.UPSTREAM_PREFLIGHT_STATUS,
        ),
        "upstream_template_schema_version": _safe_source_marker(
            source.get("upstream_template_schema_version"),
            p99.UPSTREAM_TEMPLATE_SCHEMA_VERSION,
        ),
        "upstream_template_stage": _safe_source_marker(source.get("upstream_template_stage"), p99.UPSTREAM_TEMPLATE_STAGE),
        "upstream_template_status": _safe_source_marker(source.get("upstream_template_status"), p99.UPSTREAM_TEMPLATE_STATUS),
        "external_receipt_gate_status": p99.EXTERNAL_RECEIPT_GATE_STATUS,
        "external_intake_status": p99.EXTERNAL_INTAKE_STATUS,
        "attachment_readiness_status": p99.ATTACHMENT_READINESS_STATUS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_result_family_labels": list(p99.RESULT_FAMILY_LABELS.values()),
        "safe_validation_result_audit_family_labels": list(p99.AUDIT_FAMILY_LABELS.values()),
        "safe_validation_result_audit_remediation_family_labels": list(p99.REMEDIATION_FAMILY_LABELS.values()),
        "safe_validation_result_audit_remediation_queue_operator_packet_family_labels": list(
            p99.OPERATOR_PACKET_FAMILY_LABELS.values()
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_family_labels": list(
            DISPATCH_GATE_FAMILY_LABELS.values()
        ),
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "source_marker_labels": SOURCE_MARKER_LABELS,
        "count_labels": _count_labels(summary),
        "operator_note": BLOCKED_NOTE,
        "summary": summary,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_rows": case_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_rows": attachment_rows,
        "safe_validation_result_audit_remediation_queue_rows": source_remediation_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_rows": source_operator_packet_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows": dispatch_gate_rows,
    }


def _summary(
    source_summary: dict[str, Any],
    case_rows: list[dict[str, Any]],
    attachment_rows: list[dict[str, Any]],
    remediation_rows: list[dict[str, Any]],
    operator_packet_rows: list[dict[str, Any]],
    dispatch_gate_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "source_safe_validation_result_audit_remediation_queue_operator_packet_case_rows": len(case_rows),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_attachment_rows": len(attachment_rows),
        "source_safe_validation_result_audit_remediation_queue_rows": len(remediation_rows),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_rows": len(operator_packet_rows),
        "safe_validation_transcript_case_rows": _safe_int(source_summary.get("safe_validation_transcript_case_rows")),
        "safe_validation_transcript_attachment_rows": _safe_int(
            source_summary.get("safe_validation_transcript_attachment_rows")
        ),
        "safe_validation_transcript_command_rows": _safe_int(source_summary.get("safe_validation_transcript_command_rows")),
        "safe_validation_result_ledger_rows": _safe_int(source_summary.get("safe_validation_result_ledger_rows")),
        "safe_validation_result_audit_rows": _safe_int(source_summary.get("safe_validation_result_audit_rows")),
        "safe_validation_result_audit_remediation_queue_rows": len(remediation_rows),
        "safe_validation_result_audit_remediation_family_count": _safe_int(
            source_summary.get("safe_validation_result_audit_remediation_family_count")
        )
        or len(p99.REMEDIATION_FAMILY_LABELS),
        "safe_validation_result_audit_remediation_ready_count": 0,
        "safe_validation_result_audit_remediation_blocked_count": len(remediation_rows),
        "safe_validation_result_audit_remediation_executed_count": 0,
        "safe_validation_result_audit_remediation_ticket_created_count": 0,
        "safe_validation_result_audit_remediation_notification_sent_count": 0,
        "safe_validation_result_audit_remediation_operator_handoff_delivered_count": 0,
        "safe_validation_result_audit_remediation_closed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_rows": len(operator_packet_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_family_count": len(p99.OPERATOR_PACKET_FAMILY_LABELS),
        "safe_validation_result_audit_remediation_queue_operator_packet_ready_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_blocked_count": len(operator_packet_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_delivered_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_acknowledged_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_closed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_executed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows": len(dispatch_gate_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_family_count": len(
            DISPATCH_GATE_FAMILY_LABELS
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_ready_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_blocked_count": len(dispatch_gate_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatched_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivered_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledged_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_executed_count": 0,
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
    safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index: int,
    attachment_indices: list[int],
    dispatch_indices: list[int],
) -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index": safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index,
        "case_id": str(row.get("case_id") or ""),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_case_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_indices": attachment_indices,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_indices": dispatch_indices,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_dispatch_gate_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index: int,
    dispatch_indices: list[int],
) -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index": safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_case_index")
        ),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_attachment_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_attachment_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_indices": dispatch_indices,
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": str(row.get("evidence_family") or ""),
        "external_tool_label": str(row.get("external_tool_label") or ""),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_dispatch_gate_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _dispatch_gate_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index: int,
) -> dict[str, Any]:
    family = _safe_command_family(row.get("safe_validation_command_family"))
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index": safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index,
        "source_safe_validation_result_audit_remediation_queue_operator_packet_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index,
        "source_safe_validation_result_audit_remediation_queue_index": _safe_int(
            row.get("source_safe_validation_result_audit_remediation_queue_index")
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_attachment_index")
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_case_index")
        ),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": str(row.get("evidence_family") or ""),
        "external_tool_label": str(row.get("external_tool_label") or ""),
        "safe_validation_command_family_index": _safe_int(row.get("safe_validation_command_family_index")),
        "safe_validation_command_family": family,
        "safe_validation_result_family_label": p99.RESULT_FAMILY_LABELS[family],
        "safe_validation_result_audit_family_label": p99.AUDIT_FAMILY_LABELS[family],
        "safe_validation_result_audit_remediation_family_label": p99.REMEDIATION_FAMILY_LABELS[family],
        "safe_validation_result_audit_remediation_queue_operator_packet_family_label": p99.OPERATOR_PACKET_FAMILY_LABELS[
            family
        ],
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_family_label": DISPATCH_GATE_FAMILY_LABELS[
            family
        ],
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_dispatch_gate_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _status_fields() -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_status": DISPATCH_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivery_status": DISPATCH_DELIVERY_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledgement_status": DISPATCH_ACKNOWLEDGEMENT_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closure_status": DISPATCH_CLOSURE_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_execution_status": DISPATCH_EXECUTION_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_status": p99.STATUS,
        **p99._status_fields(),
    }


def _safety_flags() -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_only": True,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatched": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivered": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledged": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closed": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_executed": False,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatched": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivered": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledged": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closed": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_executed": True,
        **p99._safety_flags(),
    }


def _dispatch_indices_by_attachment(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[
            _safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index"))
        ].append(_safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index")))
    return {key: values for key, values in grouped.items() if key}


def _dispatch_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[_safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index"))].append(
            _safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index"))
        )
    return {key: values for key, values in grouped.items() if key}


def _attachment_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[_safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index"))].append(
            _safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index"))
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
    return value if value in DISPATCH_GATE_FAMILY_LABELS else "validate_manifest_shape"


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _safe_status(value: Any, *, fallback: str) -> str:
    return str(value) if isinstance(value, str) and value else fallback


def _safe_source_marker(value: Any, fallback: str) -> str:
    return str(value) if isinstance(value, str) and value else fallback


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))
