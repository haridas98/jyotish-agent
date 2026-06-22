from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from apps.calculations.witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review import (
    build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report,
)


FORBIDDEN_MARKERS = [
    "source_report",
    "field_results",
    "raw expected",
    "raw actual",
    "sources_present",
    "seal_witness_case",
    "--ack-diff-open",
    "C:\\",
    "C:/Users",
    "/Users/",
    "/home/",
    ".env",
    "sk-",
    "OPENAI_API_KEY",
    "evidence available",
    "external evidence attached",
    "ready for release",
    "release ready",
    "verified parity",
    "accepted parity",
    "parity success",
    "authoritative",
    "complete",
    "done",
    "packet dispatched",
    "packet delivered",
    "packet acknowledged",
    "ticket created",
    "notification sent",
    "hold review released",
    "release action performed",
]

CASE_IDS = [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
]

FAMILY_ORDER = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]

RESULT_FAMILY_LABELS = [
    "validate_manifest_shape_blocked_result_label_only",
    "validate_operator_handoff_readiness_blocked_result_label_only",
    "validate_no_external_action_blocked_result_label_only",
    "validate_release_gate_blocked_blocked_result_label_only",
]

AUDIT_FAMILY_LABELS = [
    "audit_manifest_shape_blocked_label_only",
    "audit_operator_handoff_readiness_blocked_label_only",
    "audit_no_external_action_blocked_label_only",
    "audit_release_gate_blocked_label_only",
]

REMEDIATION_FAMILY_LABELS = [
    "remediate_manifest_shape_blocked_label_only",
    "remediate_operator_handoff_readiness_blocked_label_only",
    "remediate_no_external_action_blocked_label_only",
    "remediate_release_gate_blocked_label_only",
]

OPERATOR_PACKET_FAMILY_LABELS = [
    "packetize_manifest_shape_remediation_blocked_label_only",
    "packetize_operator_handoff_readiness_remediation_blocked_label_only",
    "packetize_no_external_action_remediation_blocked_label_only",
    "packetize_release_gate_remediation_blocked_label_only",
]

DISPATCH_GATE_FAMILY_LABELS = [
    "gate_manifest_shape_operator_packet_dispatch_blocked_label_only",
    "gate_operator_handoff_readiness_operator_packet_dispatch_blocked_label_only",
    "gate_no_external_action_operator_packet_dispatch_blocked_label_only",
    "gate_release_gate_operator_packet_dispatch_blocked_label_only",
]

HOLD_REVIEW_FAMILY_LABELS = [
    "hold_review_manifest_shape_operator_packet_dispatch_blocked_label_only",
    "hold_review_operator_handoff_readiness_operator_packet_dispatch_blocked_label_only",
    "hold_review_no_external_action_operator_packet_dispatch_blocked_label_only",
    "hold_review_release_gate_operator_packet_dispatch_blocked_label_only",
]

EXACT_MARKER_LABELS = [
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_release_status=not_released",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatch_status=not_dispatched",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalation_status=not_escalated",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_status=not_dispatched",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivery_status=not_delivered",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledgement_status=not_acknowledged",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closure_status=not_closed",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_execution_status=not_executed",
    "safe_validation_result_audit_remediation_queue_operator_packet_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet",
    "safe_validation_result_audit_remediation_queue_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue",
    "safe_validation_result_audit_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_only=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated=true",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_only=true",
    "safe_validation_result_audit_remediation_queue_operator_packet_only=true",
    "safe_validation_result_audit_remediation_queue_only=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatched=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivered=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledged=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closed=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_executed=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_delivered=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_acknowledged=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_closed=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_executed=true",
    "no_safe_validation_result_audit_remediation_executed=true",
    "no_safe_validation_result_audit_remediation_ticket_created=true",
    "no_safe_validation_result_audit_remediation_notification_sent=true",
    "no_safe_validation_result_audit_remediation_operator_handoff_delivered=true",
    "no_safe_validation_result_audit_remediation_closed=true",
    "safe_validation_only=true",
    "no_command_execution_performed=true",
    "no_upload_executed=true",
    "no_attachment_executed=true",
    "no_mark_command_executed=true",
    "no_accept_executed=true",
    "no_reject_executed=true",
    "no_defer_executed=true",
    "no_external_notification_sent=true",
    "no_external_ticket_created=true",
    "parity_success_claimed=false",
    "release_ready_claimed=false",
    "release_gate_status=blocked",
] + RESULT_FAMILY_LABELS + AUDIT_FAMILY_LABELS + REMEDIATION_FAMILY_LABELS + OPERATOR_PACKET_FAMILY_LABELS + DISPATCH_GATE_FAMILY_LABELS + HOLD_REVIEW_FAMILY_LABELS


class ExternalReceiptManifestDecisionAuditOperatorHandoffSafeValidationResultAuditRemediationQueueOperatorPacketDispatchGateHoldReviewTests(
    SimpleTestCase
):
    def setUp(self):
        self.tmp_dir = Path(__file__).resolve().parents[3] / ".tmp" / "test-p103"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def test_hold_review_preserves_p101_order_and_blocks_release_dispatch_escalation(self):
        dispatch_gate_path = _p101_artifact_path()

        report = build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report(
            external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_report_path=dispatch_gate_path,
        )

        self.assertEqual(
            report["schema_version"],
            (
                "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
                "safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-hold-review-v1"
            ),
        )
        self.assertEqual(report["domain"], "witness_core_parity")
        self.assertEqual(report["stage"], "P103-A")
        self.assertEqual(
            report["status"],
            (
                "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_"
                "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review"
            ),
        )
        self.assertEqual(report["upstream_dispatch_gate_stage"], "P101-A")
        self.assertEqual(report["upstream_operator_packet_stage"], "P99-A")
        self.assertEqual(report["upstream_remediation_queue_stage"], "P97-A")
        self.assertEqual(report["upstream_safe_validation_result_audit_stage"], "P95-A")
        self.assertEqual(report["upstream_safe_validation_result_ledger_stage"], "P93-A")
        self.assertEqual(report["upstream_safe_validation_transcript_stage"], "P91-A")
        self.assertEqual(report["upstream_operator_handoff_smoke_matrix_stage"], "P89-A")
        self.assertEqual(report["upstream_decision_audit_work_order_readiness_stage"], "P87-A")
        self.assertEqual(report["upstream_decision_audit_work_orders_stage"], "P85-A")
        self.assertEqual(report["upstream_decision_audit_stage"], "P83-A")
        self.assertEqual(report["upstream_decision_queue_stage"], "P81-A")
        self.assertEqual(report["upstream_acceptance_gate_stage"], "P79-A")
        self.assertEqual(report["upstream_preflight_stage"], "P77-A")
        self.assertEqual(report["upstream_template_stage"], "P75-A")
        self.assertEqual(report["summary"], _expected_summary())
        self.assertEqual(
            [
                row["case_id"]
                for row in report[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_rows"
                ]
            ],
            CASE_IDS,
        )
        self.assertEqual(
            [
                row["case_id"]
                for row in report[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_rows"
                ][::2]
            ],
            CASE_IDS,
        )
        self.assertEqual(
            [
                row["evidence_family"]
                for row in report[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_attachment_rows"
                ][:4]
            ],
            FAMILY_ORDER + FAMILY_ORDER,
        )
        self.assertEqual(len(report["safe_validation_result_audit_remediation_queue_rows"]), 40)
        self.assertEqual(len(report["safe_validation_result_audit_remediation_queue_operator_packet_rows"]), 40)
        self.assertEqual(
            len(report["safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows"]),
            40,
        )
        self.assertEqual(
            len(report["safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows"]),
            40,
        )
        self.assertEqual(
            [
                row[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_family_label"
                ]
                for row in report[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows"
                ][:4]
            ],
            HOLD_REVIEW_FAMILY_LABELS,
        )
        hold_rows = report["safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows"]
        self.assertTrue(
            all(
                row[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_release_status"
                ]
                == "not_released"
                for row in hold_rows
            )
        )
        self.assertTrue(
            all(
                row[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatch_status"
                ]
                == "not_dispatched"
                for row in hold_rows
            )
        )
        self.assertTrue(
            all(
                row[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalation_status"
                ]
                == "not_escalated"
                for row in hold_rows
            )
        )
        self.assertTrue(all(row["ready_to_attach"] is False for row in hold_rows))
        self.assertTrue(all(row["ready_to_mark"] is False for row in hold_rows))
        self.assertTrue(_contains_exact_marker_labels(report))
        self.assertTrue(_serialized_safe(report))

    def test_command_writes_json_without_mutating_p101_or_running_external_actions(self):
        dispatch_gate_path = _p101_artifact_path()
        output_path = self.tmp_dir / "safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-hold-review.json"
        before = dispatch_gate_path.read_text(encoding="utf-8")

        with (
            mock.patch("subprocess.Popen", side_effect=AssertionError("P103 must not run external tools")),
            mock.patch("subprocess.run", side_effect=AssertionError("P103 must not run commands")),
            mock.patch("os.system", side_effect=AssertionError("P103 must not run shell commands")),
        ):
            call_command(
                "build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report",
                "--external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-report",
                str(dispatch_gate_path),
                "--output",
                str(output_path),
            )

        written = _read_json(output_path)
        self.assertEqual(written["stage"], "P103-A")
        self.assertEqual(written["summary"], _expected_summary())
        self.assertTrue(_contains_exact_marker_labels(written))
        self.assertTrue(_serialized_safe(written))
        self.assertEqual(dispatch_gate_path.read_text(encoding="utf-8"), before)

    def test_committed_p103_artifact_is_safe_and_current(self):
        report = _read_json(_p103_artifact_path())
        dispatch_gate = _read_json(_p101_artifact_path())

        self.assertEqual(report["stage"], "P103-A")
        self.assertEqual(report["summary"], _expected_summary())
        self.assertEqual(
            [
                row["case_id"]
                for row in report[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_case_rows"
                ]
            ],
            CASE_IDS,
        )
        self.assertEqual(
            [
                row["case_id"]
                for row in dispatch_gate[
                    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_rows"
                ]
            ],
            CASE_IDS,
        )
        self.assertEqual(
            len(report["safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows"]),
            40,
        )
        self.assertTrue(_contains_exact_marker_labels(report))
        self.assertTrue(_serialized_safe(report))

    def test_stage_does_not_change_forbidden_files(self):
        changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
        allowed = {
            (
                ".tmp/witness-review/core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
                "safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-hold-review-p103-report.json"
            ),
            (
                "backend/apps/calculations/"
                "witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review.py"
            ),
            (
                "backend/apps/calculations/management/commands/"
                "build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report.py"
            ),
            (
                "backend/apps/calculations/"
                "test_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review.py"
            ),
        }
        for path in changed:
            normalized = path.replace("\\", "/")
            self.assertIn(normalized, allowed)
            self.assertFalse(normalized.startswith("frontend/"))
            self.assertFalse(normalized.startswith("deploy/"))
            self.assertFalse(normalized.startswith(".github/"))
            self.assertNotIn("/migrations/", normalized)
            self.assertNotIn("/fixtures/", normalized)


def _expected_summary():
    return {
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_case_rows": 5,
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_attachment_rows": 10,
        "source_safe_validation_result_audit_remediation_queue_rows": 40,
        "source_safe_validation_result_audit_remediation_queue_operator_packet_rows": 40,
        "source_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows": 40,
        "safe_validation_transcript_case_rows": 5,
        "safe_validation_transcript_attachment_rows": 10,
        "safe_validation_transcript_command_rows": 40,
        "safe_validation_result_ledger_rows": 40,
        "safe_validation_result_audit_rows": 40,
        "safe_validation_result_audit_remediation_queue_rows": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_rows": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_family_count": 4,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_ready_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_blocked_count": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatched_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_delivered_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_acknowledged_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_closed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_executed_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_family_count": 4,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_ready_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_blocked_count": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated_count": 0,
        "ready_to_attach_count": 0,
        "ready_to_mark_count": 0,
        "remaining_not_reviewed_count": 20,
        "release_gate_status": "blocked",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _p101_artifact_path() -> Path:
    return _repo_root() / ".tmp" / "witness-review" / (
        "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
        "safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-p101-report.json"
    )


def _p103_artifact_path() -> Path:
    return _repo_root() / ".tmp" / "witness-review" / (
        "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
        "safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-hold-review-p103-report.json"
    )


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)


def _contains_exact_marker_labels(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return all(marker in text for marker in EXACT_MARKER_LABELS)
