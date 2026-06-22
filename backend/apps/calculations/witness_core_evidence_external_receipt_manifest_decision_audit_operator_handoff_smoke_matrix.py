from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-v1"
)
DOMAIN_KEY = "witness_core_parity"
STAGE = "P89-A"
STATUS = "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_smoke_matrix"
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
SAFE_NEXT_ACTION_LABELS = [
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
    "no_command_execution_performed=true",
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
]
BLOCKED_NOTE = (
    "Operator handoff smoke matrix rows are labels only; no command execution, work-order delivery, "
    "operator handoff, notification, ticket, upload, attachment, mark, accept, reject, or defer action is executed."
)
SLOT_BLOCKED_NOTE = (
    "Attachment smoke row is blocked pending external evidence and operator handoff; validation command "
    "families are labels only and no external action was executed."
)


def build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_smoke_matrix_report(
    *,
    external_receipt_manifest_decision_audit_work_order_readiness_report_path: str | Path,
) -> dict[str, Any]:
    source = _read_json(Path(external_receipt_manifest_decision_audit_work_order_readiness_report_path))
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    case_packets = [
        row for row in source.get("operator_handoff_case_packet_rows", []) if isinstance(row, dict)
    ]
    attachment_packets = [
        row for row in source.get("operator_handoff_attachment_packet_rows", []) if isinstance(row, dict)
    ]
    attachments_by_case = _attachments_by_case(attachment_packets)

    attachment_smoke_rows = [
        _attachment_smoke_row(row, operator_handoff_smoke_attachment_index=index)
        for index, row in enumerate(attachment_packets, start=1)
    ]
    smoke_indices_by_case = _smoke_indices_by_case(attachment_smoke_rows)
    case_smoke_rows = [
        _case_smoke_row(
            row,
            operator_handoff_smoke_case_index=index,
            source_attachments=attachments_by_case.get(
                _safe_int(row.get("operator_handoff_case_packet_index")) or index,
                [],
            ),
            smoke_attachment_indices=smoke_indices_by_case.get(index, []),
        )
        for index, row in enumerate(case_packets, start=1)
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_smoke_rows else "empty",
        "upstream_decision_audit_work_order_readiness_schema_version": _safe_source_marker(
            source.get("schema_version"),
            UPSTREAM_READINESS_SCHEMA_VERSION,
        ),
        "upstream_decision_audit_work_order_readiness_stage": _safe_source_marker(
            source.get("stage"),
            UPSTREAM_READINESS_STAGE,
        ),
        "upstream_decision_audit_work_order_readiness_status": _safe_source_marker(
            source.get("status"),
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
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "operator_note": BLOCKED_NOTE,
        "summary": {
            "source_operator_handoff_case_packet_rows": _safe_int(
                source_summary.get("operator_handoff_case_packet_rows", len(case_packets))
            ),
            "source_operator_handoff_attachment_packet_rows": _safe_int(
                source_summary.get("operator_handoff_attachment_packet_rows", len(attachment_packets))
            ),
            "operator_handoff_case_packet_rows": len(case_packets),
            "operator_handoff_attachment_packet_rows": len(attachment_packets),
            "operator_handoff_smoke_case_rows": len(case_smoke_rows),
            "operator_handoff_smoke_attachment_rows": len(attachment_smoke_rows),
            "safe_validation_command_family_count": len(SAFE_VALIDATION_COMMAND_FAMILIES),
            "unsafe_external_action_command_count": 0,
            "command_execution_performed_count": 0,
            "command_smoke_matrix_ready_count": 0,
            "command_smoke_matrix_blocked_count": len(attachment_smoke_rows),
            "operator_handoff_ready_count": 0,
            "operator_handoff_blocked_count": len(attachment_smoke_rows),
            "work_order_delivery_ready_count": 0,
            "work_order_delivery_blocked_count": len(attachment_smoke_rows),
            "pending_external_evidence_decision_audit_work_order_count": len(attachment_smoke_rows),
            "pending_jhora_decision_audit_work_order_count": sum(
                1 for row in attachment_smoke_rows if row["evidence_family"] == "jhora_screenshot_or_packet"
            ),
            "pending_parashara_light_decision_audit_work_order_count": sum(
                1
                for row in attachment_smoke_rows
                if row["evidence_family"] == "parashara_light_manual_values_or_packet"
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
        },
        "operator_handoff_smoke_case_rows": case_smoke_rows,
        "operator_handoff_smoke_attachment_rows": attachment_smoke_rows,
    }


def _case_smoke_row(
    row: dict[str, Any],
    *,
    operator_handoff_smoke_case_index: int,
    source_attachments: list[dict[str, Any]],
    smoke_attachment_indices: list[int],
) -> dict[str, Any]:
    source_attachment_indices = [
        _safe_int(slot.get("operator_handoff_attachment_packet_index")) for slot in source_attachments
    ]
    families = {str(slot.get("evidence_family") or "") for slot in source_attachments}
    return {
        "operator_handoff_smoke_case_index": operator_handoff_smoke_case_index,
        "case_id": str(row.get("case_id") or ""),
        "source_operator_handoff_case_packet_index": _safe_int(row.get("operator_handoff_case_packet_index"))
        or operator_handoff_smoke_case_index,
        "source_operator_handoff_attachment_packet_indices": source_attachment_indices,
        "operator_handoff_smoke_attachment_indices": smoke_attachment_indices,
        "operator_handoff_smoke_matrix_status": STATUS,
        "decision_audit_work_order_readiness_status": _safe_readiness_gate_status(
            row.get("decision_audit_work_order_readiness_status")
        ),
        "decision_audit_work_order_status": _safe_work_order_status(row.get("decision_audit_work_order_status")),
        "decision_audit_status": _safe_decision_audit_status(row.get("decision_audit_status")),
        "decision_queue_status": _safe_decision_queue_status(row.get("decision_queue_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("external_receipt_gate_status")),
        "external_intake_status": _safe_intake_status(row.get("external_intake_status")),
        "attachment_readiness_status": _safe_attachment_readiness_status(row.get("attachment_readiness_status")),
        "required_operator_handoff_smoke_rows": len(REQUIRED_EVIDENCE_FAMILIES),
        "blocked_operator_handoff_smoke_rows": len(REQUIRED_EVIDENCE_FAMILIES),
        "jhora_smoke_matrix_required": "jhora_screenshot_or_packet" in families,
        "parashara_light_smoke_matrix_required": (
            "parashara_light_manual_values_or_packet" in families
        ),
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "safe_validation_only": True,
        "command_execution_performed": False,
        "command_smoke_matrix_ready": False,
        "operator_handoff_ready": False,
        "work_order_delivery_ready": False,
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_or_operator_handoff",
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_smoke_row(
    row: dict[str, Any],
    *,
    operator_handoff_smoke_attachment_index: int,
) -> dict[str, Any]:
    family = _safe_evidence_family(row.get("evidence_family"))
    return {
        "operator_handoff_smoke_attachment_index": operator_handoff_smoke_attachment_index,
        "operator_handoff_smoke_case_index": _safe_int(row.get("operator_handoff_case_packet_index")),
        "source_operator_handoff_attachment_packet_index": _safe_int(
            row.get("operator_handoff_attachment_packet_index")
        ),
        "source_operator_handoff_case_packet_index": _safe_int(row.get("operator_handoff_case_packet_index")),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": family,
        "external_tool_label": _external_tool_label(family),
        "operator_label": _operator_label(family),
        "readiness_label": _readiness_label(family),
        "safe_validation_command_families": SAFE_VALIDATION_COMMAND_FAMILIES,
        "safe_validation_command_family_labels": SAFE_VALIDATION_COMMAND_FAMILIES,
        "command_smoke_timestamp_utc_label": "command_smoke_timestamp_utc_pending",
        "blocked_reason_label": "blocked_no_external_evidence_or_operator_handoff",
        "operator_handoff_smoke_matrix_status": STATUS,
        "decision_audit_work_order_readiness_status": _safe_readiness_gate_status(
            row.get("decision_audit_work_order_readiness_status")
        ),
        "decision_audit_work_order_status": _safe_work_order_status(row.get("decision_audit_work_order_status")),
        "decision_audit_status": _safe_decision_audit_status(row.get("decision_audit_status")),
        "decision_queue_status": _safe_decision_queue_status(row.get("decision_queue_status")),
        "external_receipt_gate_status": _safe_receipt_gate_status(row.get("external_receipt_gate_status")),
        "external_intake_status": _safe_intake_status(row.get("external_intake_status")),
        "attachment_readiness_status": _safe_attachment_readiness_status(row.get("attachment_readiness_status")),
        "receipt_manifest_status": NOT_RECEIVED,
        "decision_audit_record_status": NOT_STARTED,
        "work_order_delivery_status": NOT_DELIVERED,
        "operator_handoff_status": NOT_DELIVERED,
        "human_decision_audit_status": NOT_STARTED,
        "command_smoke_matrix_status": COMMAND_SMOKE_MATRIX_STATUS,
        "safe_validation_only": True,
        "no_command_execution_performed": True,
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
        "no_accept_executed": True,
        "no_reject_executed": True,
        "no_defer_executed": True,
        "no_work_order_delivery_executed": True,
        "no_operator_handoff_delivered": True,
        "no_external_notification_sent": True,
        "no_external_ticket_created": True,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_note": SLOT_BLOCKED_NOTE,
    }


def _attachments_by_case(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        index = _safe_int(row.get("operator_handoff_case_packet_index"))
        if index:
            grouped[index].append(row)
    for case_rows in grouped.values():
        case_rows.sort(key=lambda row: _safe_int(row.get("operator_handoff_attachment_packet_index")))
    return dict(grouped)


def _smoke_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        case_index = _safe_int(row.get("operator_handoff_smoke_case_index"))
        smoke_index = _safe_int(row.get("operator_handoff_smoke_attachment_index"))
        if case_index and smoke_index:
            grouped[case_index].append(smoke_index)
    return dict(grouped)


def _safe_evidence_family(value: Any) -> str:
    text = str(value or "")
    return text if text in REQUIRED_EVIDENCE_FAMILIES else "jhora_screenshot_or_packet"


def _external_tool_label(family: str) -> str:
    return "jhora" if family == "jhora_screenshot_or_packet" else "parashara_light"


def _operator_label(family: str) -> str:
    return (
        "await_jhora_operator_handoff_smoke_matrix"
        if family == "jhora_screenshot_or_packet"
        else "await_parashara_light_operator_handoff_smoke_matrix"
    )


def _readiness_label(family: str) -> str:
    return (
        "validate_jhora_operator_handoff_readiness"
        if family == "jhora_screenshot_or_packet"
        else "validate_parashara_light_operator_handoff_readiness"
    )


def _safe_readiness_gate_status(value: Any) -> str:
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
