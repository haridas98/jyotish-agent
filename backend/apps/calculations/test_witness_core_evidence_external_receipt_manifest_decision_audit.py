from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest import mock

from django.core.management import call_command
from django.test import SimpleTestCase

from apps.calculations.witness_core_evidence_external_receipt_manifest_decision_audit import (
    build_witness_core_evidence_external_receipt_manifest_decision_audit_report,
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


class ExternalReceiptManifestDecisionAuditTests(SimpleTestCase):
    def test_decision_audit_preserves_p81_order_and_blocks_missing_audits(self):
        decision_queue_path = self._write_payload("decision-queue.json", _p81_payload())

        report = build_witness_core_evidence_external_receipt_manifest_decision_audit_report(
            external_receipt_manifest_decision_queue_report_path=decision_queue_path,
        )

        self.assertEqual(
            report["schema_version"],
            "jyotish-core-evidence-external-receipt-manifest-decision-audit-v1",
        )
        self.assertEqual(report["domain"], "witness_core_parity")
        self.assertEqual(report["stage"], "P83-A")
        self.assertEqual(report["status"], "blocked_pending_external_evidence_receipt_manifest_decision_audit")
        self.assertEqual(
            report["upstream_decision_queue_schema_version"],
            "jyotish-core-evidence-external-receipt-manifest-decision-queue-v1",
        )
        self.assertEqual(report["upstream_decision_queue_stage"], "P81-A")
        self.assertEqual(
            report["upstream_decision_queue_status"],
            "blocked_pending_external_evidence_receipt_manifest_decision",
        )
        self.assertEqual(
            report["upstream_acceptance_gate_schema_version"],
            "jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1",
        )
        self.assertEqual(report["upstream_acceptance_gate_stage"], "P79-A")
        self.assertEqual(
            report["upstream_acceptance_gate_status"],
            "blocked_pending_external_evidence_receipt_manifest_acceptance",
        )
        self.assertEqual(report["upstream_preflight_stage"], "P77-A")
        self.assertEqual(report["upstream_template_stage"], "P75-A")
        self.assertEqual(report["external_receipt_gate_status"], "blocked_pending_external_evidence_receipts")
        self.assertEqual(report["external_intake_status"], "blocked_pending_external_evidence_intake")
        self.assertEqual(report["attachment_readiness_status"], "blocked_pending_external_evidence_attachment")
        self.assertEqual(report["summary"], _expected_summary())
        self.assertEqual([row["case_id"] for row in report["case_receipt_manifest_decision_audit_rows"]], CASE_IDS)
        self.assertEqual([row["case_id"] for row in report["attachment_receipt_manifest_decision_audit_rows"][::2]], CASE_IDS)
        self.assertEqual(
            [row["evidence_family"] for row in report["attachment_receipt_manifest_decision_audit_rows"][:4]],
            FAMILY_ORDER + FAMILY_ORDER,
        )
        self.assertEqual(
            report["case_receipt_manifest_decision_audit_rows"][0][
                "source_attachment_receipt_manifest_decision_queue_indices"
            ],
            [1, 2],
        )
        self.assertEqual(
            report["case_receipt_manifest_decision_audit_rows"][-1][
                "source_attachment_receipt_manifest_decision_queue_indices"
            ],
            [9, 10],
        )
        self.assertTrue(
            all(
                row["decision_audit_status"]
                == "blocked_pending_external_evidence_receipt_manifest_decision_audit"
                for row in report["case_receipt_manifest_decision_audit_rows"]
            )
        )
        self.assertTrue(all(row["decision_recorded"] is False for row in report["case_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["decision_audited"] is False for row in report["case_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["ready_to_attach"] is False for row in report["case_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["ready_to_mark"] is False for row in report["case_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["receipt_manifest_status"] == "not_received" for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["decision_record_status"] == "not_started" for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["decision_audit_record_status"] == "not_started" for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["no_upload_executed"] is True for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["no_attachment_executed"] is True for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["no_mark_command_executed"] is True for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertEqual(
            report["attachment_receipt_manifest_decision_audit_rows"][0]["operator_decision_audit_label"],
            "await_jhora_receipt_manifest_decision_audit",
        )
        self.assertEqual(
            report["attachment_receipt_manifest_decision_audit_rows"][1]["operator_decision_audit_label"],
            "await_parashara_light_receipt_manifest_decision_audit",
        )
        self.assertIn("require_operator_decision_audit_label", report["decision_audit_criteria_labels"])
        self.assertIn("block_mark_until_manifest_decision_audited", report["decision_audit_criteria_labels"])
        self.assertIn(
            "audit_external_evidence_receipt_manifest_decision_after_human_review",
            report["safe_next_action_labels"],
        )
        self.assertTrue(_serialized_safe(report))

    def test_command_writes_json_without_mutating_p81_or_running_external_actions(self):
        decision_queue_path = self._write_payload("decision-queue.json", _p81_payload())
        output_path = self.tmp_dir / "decision-audit.json"
        before = decision_queue_path.read_text(encoding="utf-8")

        with mock.patch("subprocess.Popen", side_effect=AssertionError("P83 must not run external tools")):
            call_command(
                "build_witness_core_evidence_external_receipt_manifest_decision_audit_report",
                "--external-receipt-manifest-decision-queue-report",
                str(decision_queue_path),
                "--output",
                str(output_path),
            )

        written = _read_json(output_path)
        self.assertEqual(
            written["schema_version"],
            "jyotish-core-evidence-external-receipt-manifest-decision-audit-v1",
        )
        self.assertEqual(written["summary"], _expected_summary())
        self.assertTrue(_serialized_safe(written))
        self.assertEqual(decision_queue_path.read_text(encoding="utf-8"), before)

    def test_committed_p83_artifact_is_safe_and_current(self):
        repo_root = Path(__file__).resolve().parents[3]
        report = _read_json(
            repo_root
            / ".tmp"
            / "witness-review"
            / "core-evidence-external-receipt-manifest-decision-audit-p83-report.json"
        )
        decision_queue = _read_json(
            repo_root
            / ".tmp"
            / "witness-review"
            / "core-evidence-external-receipt-manifest-decision-queue-p81-report.json"
        )

        self.assertEqual(
            report["schema_version"],
            "jyotish-core-evidence-external-receipt-manifest-decision-audit-v1",
        )
        self.assertEqual(report["stage"], "P83-A")
        self.assertEqual(report["status"], "blocked_pending_external_evidence_receipt_manifest_decision_audit")
        self.assertEqual(report["summary"], _expected_summary())
        self.assertEqual([row["case_id"] for row in report["case_receipt_manifest_decision_audit_rows"]], CASE_IDS)
        self.assertEqual([row["case_id"] for row in decision_queue["case_receipt_manifest_decision_queue_rows"]], CASE_IDS)
        self.assertEqual([row["case_id"] for row in report["attachment_receipt_manifest_decision_audit_rows"][::2]], CASE_IDS)
        self.assertTrue(all(row["decision_record_status"] == "not_started" for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["decision_audit_record_status"] == "not_started" for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["ready_to_attach"] is False for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(all(row["ready_to_mark"] is False for row in report["attachment_receipt_manifest_decision_audit_rows"]))
        self.assertTrue(_serialized_safe(report))

    def test_stage_does_not_change_forbidden_files(self):
        changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
        allowed = {
            ".tmp/witness-review/core-evidence-external-receipt-manifest-decision-audit-p83-report.json",
            "backend/apps/calculations/witness_core_evidence_external_receipt_manifest_decision_audit.py",
            (
                "backend/apps/calculations/management/commands/"
                "build_witness_core_evidence_external_receipt_manifest_decision_audit_report.py"
            ),
            "backend/apps/calculations/test_witness_core_evidence_external_receipt_manifest_decision_audit.py",
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
        self.tmp_dir = Path(__file__).resolve().parents[3] / ".tmp" / "test-p83"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def _write_payload(self, name: str, payload: dict):
        path = self.tmp_dir / name
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path


def _expected_summary():
    return {
        "source_case_receipt_manifest_decision_queue_rows": 5,
        "source_attachment_receipt_manifest_decision_queue_rows": 10,
        "case_receipt_manifest_decision_audit_rows": 5,
        "attachment_receipt_manifest_decision_audit_rows": 10,
        "pending_external_evidence_receipt_manifest_decision_audit_count": 10,
        "pending_jhora_receipt_manifest_decision_audit_count": 5,
        "pending_parashara_light_receipt_manifest_decision_audit_count": 5,
        "decision_queue_rows": 10,
        "decision_audit_ready_count": 0,
        "decision_audit_blocked_count": 10,
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
        "remaining_not_reviewed_count": 20,
        "release_gate_status": "blocked",
        "command_smoke_matrix_status": "ready",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }


def _p81_payload():
    case_rows = []
    slot_rows = []
    for case_index, case_id in enumerate(CASE_IDS, start=1):
        slot_indices = []
        for family in FAMILY_ORDER:
            slot_index = len(slot_rows) + 1
            slot_indices.append(slot_index)
            slot_rows.append(
                {
                    "attachment_receipt_manifest_decision_queue_index": slot_index,
                    "case_receipt_manifest_decision_queue_index": case_index,
                    "source_attachment_receipt_manifest_acceptance_gate_index": slot_index,
                    "case_id": case_id,
                    "evidence_family": family,
                    "external_tool_label": "jhora" if family == "jhora_screenshot_or_packet" else "parashara_light",
                    "expected_receipt_manifest_label": (
                        "await_jhora_receipt_manifest_preflight"
                        if family == "jhora_screenshot_or_packet"
                        else "await_parashara_light_receipt_manifest_preflight"
                    ),
                    "redacted_receipt_manifest_id": "redacted_receipt_manifest_id_pending",
                    "operator_decision_label": (
                        "await_jhora_receipt_manifest_decision"
                        if family == "jhora_screenshot_or_packet"
                        else "await_parashara_light_receipt_manifest_decision"
                    ),
                    "required_human_decision_timestamp_utc": "human_decision_timestamp_utc_pending",
                    "decision_queue_status": "blocked_pending_external_evidence_receipt_manifest_decision",
                    "acceptance_gate_status": "blocked_pending_external_evidence_receipt_manifest_acceptance",
                    "preflight_status": "blocked_pending_external_evidence_receipt_manifest_preflight",
                    "receipt_manifest_template_status": "blocked_pending_external_evidence_receipt_manifests",
                    "external_receipt_gate_status": "blocked_pending_external_evidence_receipts",
                    "external_intake_status": "blocked_pending_external_evidence_intake",
                    "attachment_readiness_status": "blocked_pending_external_evidence_attachment",
                    "receipt_manifest_status": "not_received",
                    "receipt_manifest_acceptance_status": "not_started",
                    "receipt_manifest_rejection_status": "not_started",
                    "receipt_manifest_defer_status": "not_started",
                    "decision_record_status": "not_started",
                    "evidence_validation_status": "not_started",
                    "evidence_file_status": "not_attached",
                    "evidence_hash_status": "not_recorded",
                    "evidence_upload_status": "not_started",
                    "evidence_attachment_status": "not_attached",
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
                }
            )
        case_rows.append(
            {
                "case_receipt_manifest_decision_queue_index": case_index,
                "case_id": case_id,
                "source_case_receipt_manifest_acceptance_gate_index": case_index,
                "source_attachment_receipt_manifest_acceptance_gate_indices": slot_indices,
                "decision_queue_status": "blocked_pending_external_evidence_receipt_manifest_decision",
                "acceptance_gate_status": "blocked_pending_external_evidence_receipt_manifest_acceptance",
                "preflight_status": "blocked_pending_external_evidence_receipt_manifest_preflight",
                "receipt_manifest_template_status": "blocked_pending_external_evidence_receipt_manifests",
                "external_receipt_gate_status": "blocked_pending_external_evidence_receipts",
                "external_intake_status": "blocked_pending_external_evidence_intake",
                "attachment_readiness_status": "blocked_pending_external_evidence_attachment",
                "receipt_manifest_received": False,
                "receipt_manifest_accepted": False,
                "receipt_manifest_rejected": False,
                "receipt_manifest_deferred": False,
                "decision_recorded": False,
                "evidence_received": False,
                "evidence_validated": False,
                "evidence_file_recorded": False,
                "evidence_hash_recorded": False,
                "evidence_uploaded": False,
                "evidence_attached": False,
                "ready_to_attach": False,
                "ready_to_mark": False,
                "mark_commands_blocked": True,
            }
        )
    return {
        "schema_version": "jyotish-core-evidence-external-receipt-manifest-decision-queue-v1",
        "domain": "witness_core_parity",
        "stage": "P81-A",
        "status": "blocked_pending_external_evidence_receipt_manifest_decision",
        "upstream_acceptance_gate_schema_version": "jyotish-core-evidence-external-receipt-manifest-acceptance-gate-v1",
        "upstream_acceptance_gate_stage": "P79-A",
        "upstream_acceptance_gate_status": "blocked_pending_external_evidence_receipt_manifest_acceptance",
        "upstream_preflight_schema_version": "jyotish-core-evidence-external-receipt-manifest-preflight-v1",
        "upstream_preflight_stage": "P77-A",
        "upstream_preflight_status": "blocked_pending_external_evidence_receipt_manifest_preflight",
        "upstream_template_schema_version": "jyotish-core-evidence-external-receipt-manifest-templates-v1",
        "upstream_template_stage": "P75-A",
        "upstream_template_status": "blocked_pending_external_evidence_receipt_manifests",
        "external_receipt_gate_status": "blocked_pending_external_evidence_receipts",
        "external_intake_status": "blocked_pending_external_evidence_intake",
        "attachment_readiness_status": "blocked_pending_external_evidence_attachment",
        "summary": {
            "source_case_receipt_manifest_acceptance_gate_rows": 5,
            "source_attachment_receipt_manifest_acceptance_gate_rows": 10,
            "case_receipt_manifest_decision_queue_rows": 5,
            "attachment_receipt_manifest_decision_queue_rows": 10,
            "pending_external_evidence_receipt_manifest_decision_count": 10,
            "pending_jhora_receipt_manifest_decision_count": 5,
            "pending_parashara_light_receipt_manifest_decision_count": 5,
            "receipt_manifest_received_count": 0,
            "receipt_manifest_accepted_count": 0,
            "receipt_manifest_rejected_count": 0,
            "receipt_manifest_deferred_count": 0,
            "decision_recorded_count": 0,
            "evidence_received_count": 0,
            "evidence_validated_count": 0,
            "evidence_file_recorded_count": 0,
            "evidence_hash_recorded_count": 0,
            "evidence_uploaded_count": 0,
            "evidence_attached_count": 0,
            "ready_to_attach_count": 0,
            "ready_to_mark_count": 0,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "case_receipt_manifest_decision_queue_rows": case_rows,
        "attachment_receipt_manifest_decision_queue_rows": slot_rows,
    }


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
