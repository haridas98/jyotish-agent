from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from apps.calculations.witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript import (
    build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report,
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


SAFE_VALIDATION_FAMILIES = [
    "validate_manifest_shape",
    "validate_operator_handoff_readiness",
    "validate_no_external_action",
    "validate_release_gate_blocked",
]


EXACT_MARKER_LABELS = [
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


class ExternalReceiptManifestDecisionAuditOperatorHandoffSafeValidationTranscriptTests(SimpleTestCase):
    def test_transcript_preserves_p89_order_and_blocks_command_execution(self):
        smoke_matrix_path = self._write_payload("operator-handoff-smoke-matrix.json", _p89_payload())

        report = build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report(
            external_receipt_manifest_decision_audit_operator_handoff_smoke_matrix_report_path=smoke_matrix_path,
        )

        self.assertEqual(
            report["schema_version"],
            "jyotish-core-evidence-external-receipt-manifest-decision-audit-operator-handoff-safe-validation-transcript-v1",
        )
        self.assertEqual(report["domain"], "witness_core_parity")
        self.assertEqual(report["stage"], "P91-A")
        self.assertEqual(
            report["status"],
            "blocked_pending_external_evidence_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript",
        )
        self.assertEqual(report["upstream_operator_handoff_smoke_matrix_stage"], "P89-A")
        self.assertEqual(report["upstream_decision_audit_work_order_readiness_stage"], "P87-A")
        self.assertEqual(report["upstream_decision_audit_work_orders_stage"], "P85-A")
        self.assertEqual(report["upstream_decision_audit_stage"], "P83-A")
        self.assertEqual(report["upstream_decision_queue_stage"], "P81-A")
        self.assertEqual(report["upstream_acceptance_gate_stage"], "P79-A")
        self.assertEqual(report["upstream_preflight_stage"], "P77-A")
        self.assertEqual(report["upstream_template_stage"], "P75-A")
        self.assertEqual(report["summary"], _expected_summary())
        self.assertEqual([row["case_id"] for row in report["safe_validation_transcript_case_rows"]], CASE_IDS)
        self.assertEqual([row["case_id"] for row in report["safe_validation_transcript_attachment_rows"][::2]], CASE_IDS)
        self.assertEqual(
            [row["evidence_family"] for row in report["safe_validation_transcript_attachment_rows"][:4]],
            FAMILY_ORDER + FAMILY_ORDER,
        )
        self.assertEqual(len(report["safe_validation_transcript_command_rows"]), 40)
        self.assertEqual(
            [row["safe_validation_command_family"] for row in report["safe_validation_transcript_command_rows"][:4]],
            SAFE_VALIDATION_FAMILIES,
        )
        self.assertTrue(
            all(
                row["safe_validation_command_execution_status"] == "not_executed"
                for row in report["safe_validation_transcript_command_rows"]
            )
        )
        self.assertTrue(
            all(row["ready_to_attach"] is False for row in report["safe_validation_transcript_command_rows"])
        )
        self.assertTrue(all(row["ready_to_mark"] is False for row in report["safe_validation_transcript_command_rows"]))
        self.assertTrue(_contains_exact_marker_labels(report))
        self.assertTrue(_serialized_safe(report))

    def test_command_writes_json_without_mutating_p89_or_running_external_actions(self):
        smoke_matrix_path = self._write_payload("operator-handoff-smoke-matrix.json", _p89_payload())
        output_path = self.tmp_dir / "safe-validation-transcript.json"
        before = smoke_matrix_path.read_text(encoding="utf-8")

        with (
            mock.patch("subprocess.Popen", side_effect=AssertionError("P91 must not run external tools")),
            mock.patch("subprocess.run", side_effect=AssertionError("P91 must not run commands")),
            mock.patch("os.system", side_effect=AssertionError("P91 must not run shell commands")),
        ):
            call_command(
                "build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report",
                "--external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-report",
                str(smoke_matrix_path),
                "--output",
                str(output_path),
            )

        written = _read_json(output_path)
        self.assertEqual(written["stage"], "P91-A")
        self.assertEqual(written["summary"], _expected_summary())
        self.assertTrue(_contains_exact_marker_labels(written))
        self.assertTrue(_serialized_safe(written))
        self.assertEqual(smoke_matrix_path.read_text(encoding="utf-8"), before)

    def test_committed_p91_artifact_is_safe_and_current(self):
        repo_root = Path(__file__).resolve().parents[3]
        report = _read_json(
            repo_root
            / ".tmp"
            / "witness-review"
            / (
                "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
                "safe-validation-transcript-p91-report.json"
            )
        )
        smoke_matrix = _read_json(
            repo_root
            / ".tmp"
            / "witness-review"
            / "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-p89-report.json"
        )

        self.assertEqual(report["stage"], "P91-A")
        self.assertEqual(report["summary"], _expected_summary())
        self.assertEqual([row["case_id"] for row in report["safe_validation_transcript_case_rows"]], CASE_IDS)
        self.assertEqual([row["case_id"] for row in smoke_matrix["operator_handoff_smoke_case_rows"]], CASE_IDS)
        self.assertEqual([row["case_id"] for row in report["safe_validation_transcript_attachment_rows"][::2]], CASE_IDS)
        self.assertEqual(len(report["safe_validation_transcript_command_rows"]), 40)
        self.assertTrue(_contains_exact_marker_labels(report))
        self.assertTrue(_serialized_safe(report))

    def test_stage_does_not_change_forbidden_files(self):
        changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
        allowed = {
            (
                ".tmp/witness-review/core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
                "safe-validation-transcript-p91-report.json"
            ),
            (
                "backend/apps/calculations/"
                "witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript.py"
            ),
            (
                "backend/apps/calculations/management/commands/"
                "build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report.py"
            ),
            (
                "backend/apps/calculations/"
                "test_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript.py"
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

    def setUp(self):
        self.tmp_dir = Path(__file__).resolve().parents[3] / ".tmp" / "test-p91"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def _write_payload(self, name: str, payload: dict):
        path = self.tmp_dir / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path


def _expected_summary():
    return {
        "source_operator_handoff_smoke_case_rows": 5,
        "source_operator_handoff_smoke_attachment_rows": 10,
        "safe_validation_transcript_case_rows": 5,
        "safe_validation_transcript_attachment_rows": 10,
        "safe_validation_transcript_command_rows": 40,
        "safe_validation_command_family_count": 4,
        "safe_validation_command_execution_performed_count": 0,
        "safe_validation_command_ready_count": 0,
        "safe_validation_command_blocked_count": 40,
        "operator_handoff_case_packet_rows": 5,
        "operator_handoff_attachment_packet_rows": 10,
        "operator_handoff_smoke_case_rows": 5,
        "operator_handoff_smoke_attachment_rows": 10,
        "unsafe_external_action_command_count": 0,
        "command_execution_performed_count": 0,
        "command_smoke_matrix_ready_count": 0,
        "command_smoke_matrix_blocked_count": 10,
        "operator_handoff_ready_count": 0,
        "operator_handoff_blocked_count": 10,
        "work_order_delivery_ready_count": 0,
        "work_order_delivery_blocked_count": 10,
        "pending_external_evidence_decision_audit_work_order_count": 10,
        "pending_jhora_decision_audit_work_order_count": 5,
        "pending_parashara_light_decision_audit_work_order_count": 5,
        "decision_recorded_count": 0,
        "decision_audited_count": 0,
        "decision_audit_passed_count": 0,
        "decision_audit_failed_count": 0,
        "ready_to_attach_count": 0,
        "ready_to_mark_count": 0,
        "remaining_not_reviewed_count": 20,
        "release_gate_status": "blocked",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }


def _p89_payload():
    repo_root = Path(__file__).resolve().parents[3]
    return _read_json(
        repo_root
        / ".tmp"
        / "witness-review"
        / "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-p89-report.json"
    )


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)


def _contains_exact_marker_labels(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return all(marker in text for marker in EXACT_MARKER_LABELS)
