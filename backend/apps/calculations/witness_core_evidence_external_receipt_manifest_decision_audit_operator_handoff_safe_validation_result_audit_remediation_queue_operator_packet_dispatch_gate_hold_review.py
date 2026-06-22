from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from apps.calculations import (
    witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate as p101,
)


SCHEMA_VERSION = (
    "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
    "safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-hold-review-v1"
)
DOMAIN_KEY = "witness_core_parity"
STAGE = "P103-A"
STATUS = (
    "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review"
)
HOLD_REVIEW_RELEASE_STATUS = "not_released"
HOLD_REVIEW_DISPATCH_STATUS = "not_dispatched"
HOLD_REVIEW_ESCALATION_STATUS = "not_escalated"

HOLD_REVIEW_FAMILY_LABELS = {
    "validate_manifest_shape": "hold_review_manifest_shape_operator_packet_dispatch_blocked_label_only",
    "validate_operator_handoff_readiness": "hold_review_operator_handoff_readiness_operator_packet_dispatch_blocked_label_only",
    "validate_no_external_action": "hold_review_no_external_action_operator_packet_dispatch_blocked_label_only",
    "validate_release_gate_blocked": "hold_review_release_gate_operator_packet_dispatch_blocked_label_only",
}
SAFE_NEXT_ACTION_LABELS = [
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report",
    "rerun_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_report",
    *p101.SAFE_NEXT_ACTION_LABELS,
]
STATUS_LABELS = [
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_release_status=not_released",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatch_status=not_dispatched",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalation_status=not_escalated",
    *p101.STATUS_LABELS,
]
SAFETY_LABELS = [
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_only=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated=true",
    *p101.SAFETY_LABELS,
]
SOURCE_MARKER_LABELS = [
    SCHEMA_VERSION,
    "P103",
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
    "Hold-review rows are labels only; hold release, dispatch, escalation, packet delivery, acknowledgement, "
    "closure, remediation, ticket action, notification, operator handoff, command execution, upload, attachment, "
    "mark, accept, reject, defer, result recording, or release action is blocked."
)


def build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report(
    *,
    external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_report_path: str
    | Path,
) -> dict[str, Any]:
    source = _read_json(
        Path(
            external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_report_path
        )
    )
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    source_case_rows = [
        row
        for row in source.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_rows", [])
        if isinstance(row, dict)
    ]
    source_attachment_rows = [
        row
        for row in source.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_rows", [])
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
    source_dispatch_gate_rows = [
        row
        for row in source.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows", [])
        if isinstance(row, dict)
    ]
    hold_review_rows = [
        _hold_review_row(
            row,
            safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_index=index,
        )
        for index, row in enumerate(source_dispatch_gate_rows, start=1)
    ]
    hold_review_indices_by_attachment = _hold_review_indices_by_attachment(hold_review_rows)
    attachment_rows = [
        _attachment_row(
            row,
            safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_index=index,
            hold_review_indices=hold_review_indices_by_attachment.get(index, []),
        )
        for index, row in enumerate(source_attachment_rows, start=1)
    ]
    attachment_indices_by_case = _attachment_indices_by_case(attachment_rows)
    hold_review_indices_by_case = _hold_review_indices_by_case(hold_review_rows)
    case_rows = [
        _case_row(
            row,
            safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index=index,
            attachment_indices=attachment_indices_by_case.get(index, []),
            hold_review_indices=hold_review_indices_by_case.get(index, []),
        )
        for index, row in enumerate(source_case_rows, start=1)
    ]
    summary = _summary(
        source_summary,
        case_rows,
        attachment_rows,
        source_remediation_rows,
        source_operator_packet_rows,
        source_dispatch_gate_rows,
        hold_review_rows,
    )
    upstream = _upstream_fields(source)

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS if case_rows else "empty",
        "upstream_dispatch_gate_schema_version": _safe_source_marker(source.get("schema_version"), p101.SCHEMA_VERSION),
        "upstream_dispatch_gate_stage": _safe_source_marker(source.get("stage"), p101.STAGE),
        "upstream_dispatch_gate_status": _safe_source_marker(source.get("status"), p101.STATUS),
        **upstream,
        "external_receipt_gate_status": p101.p99.EXTERNAL_RECEIPT_GATE_STATUS,
        "external_intake_status": p101.p99.EXTERNAL_INTAKE_STATUS,
        "attachment_readiness_status": p101.p99.ATTACHMENT_READINESS_STATUS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "safe_validation_result_family_labels": list(p101.p99.RESULT_FAMILY_LABELS.values()),
        "safe_validation_result_audit_family_labels": list(p101.p99.AUDIT_FAMILY_LABELS.values()),
        "safe_validation_result_audit_remediation_family_labels": list(p101.p99.REMEDIATION_FAMILY_LABELS.values()),
        "safe_validation_result_audit_remediation_queue_operator_packet_family_labels": list(
            p101.p99.OPERATOR_PACKET_FAMILY_LABELS.values()
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_family_labels": list(
            p101.DISPATCH_GATE_FAMILY_LABELS.values()
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_family_labels": list(
            HOLD_REVIEW_FAMILY_LABELS.values()
        ),
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "source_marker_labels": SOURCE_MARKER_LABELS,
        "count_labels": _count_labels(summary),
        "operator_note": BLOCKED_NOTE,
        "summary": summary,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_rows": case_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_rows": attachment_rows,
        "safe_validation_result_audit_remediation_queue_rows": source_remediation_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_rows": source_operator_packet_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows": source_dispatch_gate_rows,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows": hold_review_rows,
    }


def _summary(
    source_summary: dict[str, Any],
    case_rows: list[dict[str, Any]],
    attachment_rows: list[dict[str, Any]],
    remediation_rows: list[dict[str, Any]],
    operator_packet_rows: list[dict[str, Any]],
    dispatch_gate_rows: list[dict[str, Any]],
    hold_review_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_rows": len(case_rows),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_rows": len(
            attachment_rows
        ),
        "source_safe_validation_result_audit_remediation_queue_rows": len(remediation_rows),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_rows": len(operator_packet_rows),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows": len(dispatch_gate_rows),
        "safe_validation_transcript_case_rows": _safe_int(source_summary.get("safe_validation_transcript_case_rows")),
        "safe_validation_transcript_attachment_rows": _safe_int(
            source_summary.get("safe_validation_transcript_attachment_rows")
        ),
        "safe_validation_transcript_command_rows": _safe_int(source_summary.get("safe_validation_transcript_command_rows")),
        "safe_validation_result_ledger_rows": _safe_int(source_summary.get("safe_validation_result_ledger_rows")),
        "safe_validation_result_audit_rows": _safe_int(source_summary.get("safe_validation_result_audit_rows")),
        "safe_validation_result_audit_remediation_queue_rows": len(remediation_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_rows": len(operator_packet_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows": len(dispatch_gate_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_family_count": len(
            p101.DISPATCH_GATE_FAMILY_LABELS
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_ready_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_blocked_count": len(dispatch_gate_rows),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatched_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivered_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledged_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_executed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows": len(
            hold_review_rows
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_family_count": len(
            HOLD_REVIEW_FAMILY_LABELS
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_ready_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_blocked_count": len(
            hold_review_rows
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated_count": 0,
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
    safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index: int,
    attachment_indices: list[int],
    hold_review_indices: list[int],
) -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index": safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index,
        "case_id": str(row.get("case_id") or ""),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_indices": attachment_indices,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_indices": hold_review_indices,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_dispatch_gate_hold_review_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _attachment_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_index: int,
    hold_review_indices: list[int],
) -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_index": safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index")
        ),
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_index,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_indices": hold_review_indices,
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": str(row.get("evidence_family") or ""),
        "external_tool_label": str(row.get("external_tool_label") or ""),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_dispatch_gate_hold_review_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _hold_review_row(
    row: dict[str, Any],
    *,
    safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_index: int,
) -> dict[str, Any]:
    family = _safe_command_family(row.get("safe_validation_command_family"))
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_index": safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_index,
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_index")
        )
        or safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_index,
        "source_safe_validation_result_audit_remediation_queue_operator_packet_index": _safe_int(
            row.get("source_safe_validation_result_audit_remediation_queue_operator_packet_index")
        ),
        "source_safe_validation_result_audit_remediation_queue_index": _safe_int(
            row.get("source_safe_validation_result_audit_remediation_queue_index")
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_index")
        ),
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index": _safe_int(
            row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_index")
        ),
        "case_id": str(row.get("case_id") or ""),
        "evidence_family": str(row.get("evidence_family") or ""),
        "external_tool_label": str(row.get("external_tool_label") or ""),
        "safe_validation_command_family_index": _safe_int(row.get("safe_validation_command_family_index")),
        "safe_validation_command_family": family,
        "safe_validation_result_family_label": p101.p99.RESULT_FAMILY_LABELS[family],
        "safe_validation_result_audit_family_label": p101.p99.AUDIT_FAMILY_LABELS[family],
        "safe_validation_result_audit_remediation_family_label": p101.p99.REMEDIATION_FAMILY_LABELS[family],
        "safe_validation_result_audit_remediation_queue_operator_packet_family_label": p101.p99.OPERATOR_PACKET_FAMILY_LABELS[
            family
        ],
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_family_label": p101.DISPATCH_GATE_FAMILY_LABELS[
            family
        ],
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_family_label": HOLD_REVIEW_FAMILY_LABELS[
            family
        ],
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_status": STATUS,
        **_status_fields(),
        **_safety_flags(),
        "ready_to_attach": False,
        "ready_to_mark": False,
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "safe_next_action_labels": SAFE_NEXT_ACTION_LABELS,
        "blocked_reason_label": "blocked_no_external_evidence_operator_packet_dispatch_gate_hold_review_action",
        "blocked_note": BLOCKED_NOTE,
    }


def _status_fields() -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_release_status": HOLD_REVIEW_RELEASE_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatch_status": HOLD_REVIEW_DISPATCH_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalation_status": HOLD_REVIEW_ESCALATION_STATUS,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_status": p101.STATUS,
        **p101._status_fields(),
    }


def _safety_flags() -> dict[str, Any]:
    return {
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_only": True,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched": False,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated": False,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched": True,
        "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated": True,
        **p101._safety_flags(),
    }


def _hold_review_indices_by_attachment(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[
            _safe_int(
                row.get(
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_index"
                )
            )
        ].append(
            _safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_index"))
        )
    return {key: values for key, values in grouped.items() if key}


def _hold_review_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[
            _safe_int(
                row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index")
            )
        ].append(
            _safe_int(row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_index"))
        )
    return {key: values for key, values in grouped.items() if key}


def _attachment_indices_by_case(rows: list[dict[str, Any]]) -> dict[int, list[int]]:
    grouped: dict[int, list[int]] = defaultdict(list)
    for row in rows:
        grouped[
            _safe_int(
                row.get("safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_index")
            )
        ].append(
            _safe_int(
                row.get(
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_index"
                )
            )
        )
    return {key: values for key, values in grouped.items() if key}


def _upstream_fields(source: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in source.items() if key.startswith("upstream_") and isinstance(value, str)}


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
    return value if value in HOLD_REVIEW_FAMILY_LABELS else "validate_manifest_shape"


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _safe_status(value: Any, *, fallback: str) -> str:
    return str(value) if isinstance(value, str) and value else fallback


def _safe_source_marker(value: Any, fallback: str) -> str:
    return str(value) if isinstance(value, str) and value else fallback


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))
