from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps.calculations import (
    witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review as p103,
)


SCHEMA_VERSION = "jyotish-core-evidence-ui-handoff-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P105-A"
STATUS = "blocked_parity_micro_chain_capped_pending_ui_product_implementation"
UPSTREAM_FRONTEND_REFLECTION_STAGE = "E104-A"
NEXT_STAGE_RECOMMENDED_ID = "E106-A"
NEXT_STAGE_RECOMMENDED_FOCUS = "south_indian_chart_ui_and_accuracy_dashboard_cleanup"
UPSTREAM_CHAIN = [
    "P105",
    "E104",
    "P103",
    "E102",
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
STATUS_LABELS = [
    "parity_micro_chain_capped=true",
    "next_stage_should_be_ui_product_implementation=true",
    "next_stage_recommended_id=E106-A",
    "next_stage_recommended_focus=south_indian_chart_ui_and_accuracy_dashboard_cleanup",
    "release_gate_status=blocked",
    "parity_success_claimed=false",
    "release_ready_claimed=false",
    *p103.STATUS_LABELS,
]
SAFETY_LABELS = [
    "micro_chain_no_further_parity_scaffolding_planned=true",
    "handoff_report_only=true",
    "no_external_service_called=true",
    "no_dispatch_executed=true",
    "no_release_executed=true",
    "no_escalation_executed=true",
    *p103.SAFETY_LABELS,
]
COUNT_KEYS = [
    "safe_validation_transcript_case_rows",
    "safe_validation_transcript_attachment_rows",
    "safe_validation_transcript_command_rows",
    "safe_validation_result_ledger_rows",
    "safe_validation_result_audit_rows",
    "safe_validation_result_audit_remediation_queue_rows",
    "safe_validation_result_audit_remediation_queue_operator_packet_rows",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_family_count",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_ready_count",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_blocked_count",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released_count",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched_count",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated_count",
]
BLOCKED_NOTE = (
    "Parity micro-chain is capped at P105 for now; release remains blocked, while product/UI implementation "
    "planning can proceed from labels-only state without external actions."
)


def build_witness_core_evidence_ui_handoff_report(
    *,
    external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report_path: str
    | Path,
) -> dict[str, Any]:
    source = _read_json(
        Path(
            external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report_path
        )
    )
    source_summary = source.get("summary") if isinstance(source.get("summary"), dict) else {}
    summary = _summary(source_summary)
    count_labels = _count_labels(summary)

    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": STATUS,
        "upstream_hold_review_schema_version": _safe_source_marker(source.get("schema_version"), p103.SCHEMA_VERSION),
        "upstream_hold_review_stage": _safe_source_marker(source.get("stage"), p103.STAGE),
        "upstream_hold_review_status": _safe_source_marker(source.get("status"), p103.STATUS),
        "upstream_frontend_reflection_stage": UPSTREAM_FRONTEND_REFLECTION_STAGE,
        "upstream_chain": UPSTREAM_CHAIN,
        "parity_micro_chain_capped": True,
        "next_stage_should_be_ui_product_implementation": True,
        "next_stage_recommended_id": NEXT_STAGE_RECOMMENDED_ID,
        "next_stage_recommended_focus": NEXT_STAGE_RECOMMENDED_FOCUS,
        "release_gate_status": "blocked",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
        "safe_product_ui_work_labels": [
            "south_indian_chart_ui",
            "accuracy_dashboard_cleanup",
            "blocked_state_copy_review",
            "no_release_readiness_claim",
        ],
        "blocked_status_summary": {
            "release_gate_status": "blocked",
            "hold_review_rows": summary[
                "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows"
            ],
            "hold_review_blocked_count": summary[
                "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_blocked_count"
            ],
            "hold_review_ready_count": summary[
                "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_ready_count"
            ],
            "hold_review_released_count": summary[
                "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released_count"
            ],
            "hold_review_dispatched_count": summary[
                "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched_count"
            ],
            "hold_review_escalated_count": summary[
                "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated_count"
            ],
        },
        "status_labels": STATUS_LABELS,
        "safety_labels": SAFETY_LABELS,
        "count_labels": count_labels,
        "operator_note": BLOCKED_NOTE,
        "summary": summary,
    }


def _summary(source_summary: dict[str, Any]) -> dict[str, Any]:
    summary = {key: _safe_int(source_summary.get(key)) for key in COUNT_KEYS}
    summary.update(
        {
            "parity_micro_chain_capped": True,
            "next_stage_should_be_ui_product_implementation": True,
            "release_gate_status": "blocked",
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        }
    )
    return summary


def _count_labels(summary: dict[str, Any]) -> list[str]:
    labels = [
        f"{key}={str(value).lower() if isinstance(value, bool) else value}"
        for key, value in summary.items()
        if isinstance(value, (bool, int))
    ]
    labels.extend(
        [
            f"release_gate_status={summary['release_gate_status']}",
            "next_stage_recommended_id=E106-A",
            "next_stage_recommended_focus=south_indian_chart_ui_and_accuracy_dashboard_cleanup",
        ]
    )
    return labels


def _safe_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _safe_source_marker(value: Any, fallback: str) -> str:
    return str(value) if isinstance(value, str) and value else fallback


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))
