from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from apps.calculations.witness_core_evidence_ui_handoff import build_witness_core_evidence_ui_handoff_report


EXPECTED_CHAIN = [
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

EXACT_MARKER_LABELS = [
    "parity_micro_chain_capped=true",
    "next_stage_should_be_ui_product_implementation=true",
    "next_stage_recommended_id=E106-A",
    "next_stage_recommended_focus=south_indian_chart_ui_and_accuracy_dashboard_cleanup",
    "release_gate_status=blocked",
    "parity_success_claimed=false",
    "release_ready_claimed=false",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows=40",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_family_count=4",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_ready_count=0",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_blocked_count=40",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released_count=0",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched_count=0",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated_count=0",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_status=blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_release_status=not_released",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatch_status=not_dispatched",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalation_status=not_escalated",
    "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_only=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched=true",
    "no_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated=true",
    "micro_chain_no_further_parity_scaffolding_planned=true",
    "handoff_report_only=true",
    "no_external_service_called=true",
    "no_dispatch_executed=true",
    "no_release_executed=true",
    "no_escalation_executed=true",
    "no_upload_executed=true",
    "no_attachment_executed=true",
    "no_accept_executed=true",
    "no_reject_executed=true",
    "no_defer_executed=true",
    "no_external_notification_sent=true",
    "no_external_ticket_created=true",
]

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
    "ticket created",
    "notification sent",
    "hold review released",
    "release action performed",
]


class WitnessCoreEvidenceUiHandoffTests(SimpleTestCase):
    def setUp(self):
        self.tmp_dir = _repo_root() / ".tmp" / "test-p105"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def test_ui_handoff_caps_parity_micro_chain_and_recommends_product_stage(self):
        report = build_witness_core_evidence_ui_handoff_report(
            external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report_path=_p103_artifact_path(),
        )

        self.assertEqual(report["schema_version"], "jyotish-core-evidence-ui-handoff-v1")
        self.assertEqual(report["domain"], "witness_core_parity")
        self.assertEqual(report["stage"], "P105-A")
        self.assertEqual(report["status"], "blocked_parity_micro_chain_capped_pending_ui_product_implementation")
        self.assertEqual(report["upstream_hold_review_stage"], "P103-A")
        self.assertEqual(report["upstream_frontend_reflection_stage"], "E104-A")
        self.assertEqual(report["upstream_chain"], EXPECTED_CHAIN)
        self.assertEqual(report["summary"], _expected_summary())
        self.assertTrue(report["parity_micro_chain_capped"])
        self.assertTrue(report["next_stage_should_be_ui_product_implementation"])
        self.assertEqual(report["next_stage_recommended_id"], "E106-A")
        self.assertEqual(
            report["next_stage_recommended_focus"],
            "south_indian_chart_ui_and_accuracy_dashboard_cleanup",
        )
        self.assertTrue(_contains_exact_marker_labels(report))
        self.assertTrue(_serialized_safe(report))

    def test_command_writes_json_without_mutating_p103_or_running_external_actions(self):
        source_path = _p103_artifact_path()
        output_path = self.tmp_dir / "core-evidence-ui-handoff-p105-report.json"
        before = source_path.read_text(encoding="utf-8")

        with (
            mock.patch("subprocess.Popen", side_effect=AssertionError("P105 must not run external tools")),
            mock.patch("subprocess.run", side_effect=AssertionError("P105 must not run commands")),
            mock.patch("os.system", side_effect=AssertionError("P105 must not run shell commands")),
        ):
            call_command(
                "build_witness_core_evidence_ui_handoff_report",
                "--external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-hold-review-report",
                str(source_path),
                "--output",
                str(output_path),
            )

        written = _read_json(output_path)
        self.assertEqual(written["stage"], "P105-A")
        self.assertEqual(written["summary"], _expected_summary())
        self.assertTrue(_contains_exact_marker_labels(written))
        self.assertTrue(_serialized_safe(written))
        self.assertEqual(source_path.read_text(encoding="utf-8"), before)

    def test_committed_p105_artifact_is_safe_current_and_deterministic(self):
        report = _read_json(_p105_artifact_path())
        rebuilt = build_witness_core_evidence_ui_handoff_report(
            external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_report_path=_p103_artifact_path(),
        )

        self.assertEqual(report, rebuilt)
        self.assertEqual(report["summary"], _expected_summary())
        self.assertTrue(_contains_exact_marker_labels(report))
        self.assertTrue(_serialized_safe(report))

    def test_stage_does_not_change_forbidden_files(self):
        changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
        allowed = {
            ".tmp/witness-review/core-evidence-ui-handoff-p105-report.json",
            "backend/apps/calculations/witness_core_evidence_ui_handoff.py",
            "backend/apps/calculations/management/commands/build_witness_core_evidence_ui_handoff_report.py",
            "backend/apps/calculations/test_witness_core_evidence_ui_handoff.py",
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
        "safe_validation_transcript_case_rows": 5,
        "safe_validation_transcript_attachment_rows": 10,
        "safe_validation_transcript_command_rows": 40,
        "safe_validation_result_ledger_rows": 40,
        "safe_validation_result_audit_rows": 40,
        "safe_validation_result_audit_remediation_queue_rows": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_rows": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_rows": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_rows": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_family_count": 4,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_ready_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_blocked_count": 40,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_released_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_dispatched_count": 0,
        "safe_validation_result_audit_remediation_queue_operator_packet_dispatch_gate_hold_review_escalated_count": 0,
        "parity_micro_chain_capped": True,
        "next_stage_should_be_ui_product_implementation": True,
        "release_gate_status": "blocked",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _p103_artifact_path() -> Path:
    return _repo_root() / ".tmp" / "witness-review" / (
        "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
        "safe-validation-result-audit-remediation-queue-operator-packet-dispatch-gate-hold-review-p103-report.json"
    )


def _p105_artifact_path() -> Path:
    return _repo_root() / ".tmp" / "witness-review" / "core-evidence-ui-handoff-p105-report.json"


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)


def _contains_exact_marker_labels(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return all(marker in text for marker in EXACT_MARKER_LABELS)
