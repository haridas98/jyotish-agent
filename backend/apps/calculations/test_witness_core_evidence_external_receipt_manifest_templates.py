from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_external_receipt_manifest_templates import (
    build_witness_core_evidence_external_receipt_manifest_templates_report,
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
    "file_hash",
    "sha256",
    "checksum",
    "evidence available",
    "external evidence attached",
    "evidence received",
    "evidence validated",
    "manifest received",
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


REQUIRED_MANIFEST_FIELDS = [
    "case_id",
    "evidence_family",
    "external_tool_label",
    "human_receipt_timestamp_utc",
    "redacted_receipt_manifest_id",
    "operator_receipt_note_label",
    "no_raw_values_in_manifest",
    "no_private_paths_in_manifest",
    "no_secrets_in_manifest",
]


def test_external_receipt_manifest_templates_preserve_p73_order_and_block_manifests(tmp_path):
    receipt_gate_path = tmp_path / "external-receipt-gate.json"
    receipt_gate_path.write_text(json.dumps(_p73_payload()), encoding="utf-8")

    report = build_witness_core_evidence_external_receipt_manifest_templates_report(
        external_receipt_gate_report_path=receipt_gate_path,
    )

    assert report["schema_version"] == "jyotish-core-evidence-external-receipt-manifest-templates-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P75-A"
    assert report["status"] == "blocked_pending_external_evidence_receipt_manifests"
    assert report["source_schema_version"] == "jyotish-core-evidence-external-receipt-gate-v1"
    assert report["source_stage"] == "P73-A"
    assert report["source_status"] == "blocked_pending_external_evidence_receipts"
    assert report["summary"] == {
        "source_case_receipt_gate_rows": 5,
        "source_attachment_receipt_slot_rows": 10,
        "case_receipt_manifest_template_rows": 5,
        "attachment_receipt_manifest_template_rows": 10,
        "pending_external_evidence_receipt_manifest_count": 10,
        "pending_jhora_receipt_manifest_count": 5,
        "pending_parashara_light_receipt_manifest_count": 5,
        "receipt_manifest_received_count": 0,
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
    assert [row["case_id"] for row in report["case_receipt_manifest_template_rows"]] == CASE_IDS
    assert [row["case_id"] for row in report["attachment_receipt_manifest_template_rows"][::2]] == CASE_IDS
    assert [row["evidence_family"] for row in report["attachment_receipt_manifest_template_rows"][:4]] == (
        FAMILY_ORDER + FAMILY_ORDER
    )
    assert report["case_receipt_manifest_template_rows"][0]["source_attachment_receipt_slot_indices"] == [1, 2]
    assert report["case_receipt_manifest_template_rows"][-1]["source_attachment_receipt_slot_indices"] == [9, 10]
    assert all(
        row["receipt_manifest_template_status"] == "blocked_pending_external_evidence_receipt_manifests"
        for row in report["case_receipt_manifest_template_rows"]
    )
    assert all(
        row["receipt_gate_status"] == "blocked_pending_external_evidence_receipts"
        for row in report["case_receipt_manifest_template_rows"]
    )
    assert all(
        row["intake_status"] == "blocked_pending_external_evidence_intake"
        for row in report["case_receipt_manifest_template_rows"]
    )
    assert all(
        row["readiness_status"] == "blocked_pending_external_evidence_attachment"
        for row in report["case_receipt_manifest_template_rows"]
    )
    assert all(row["required_external_evidence_receipt_manifests"] == 2 for row in report["case_receipt_manifest_template_rows"])
    assert all(row["missing_external_evidence_receipt_manifests"] == 2 for row in report["case_receipt_manifest_template_rows"])
    assert all(row["jhora_manifest_required"] is True for row in report["case_receipt_manifest_template_rows"])
    assert all(row["parashara_light_manifest_required"] is True for row in report["case_receipt_manifest_template_rows"])
    assert all(row["receipt_manifest_received"] is False for row in report["case_receipt_manifest_template_rows"])
    assert all(row["evidence_received"] is False for row in report["case_receipt_manifest_template_rows"])
    assert all(row["evidence_validated"] is False for row in report["case_receipt_manifest_template_rows"])
    assert all(row["evidence_collected"] is False for row in report["case_receipt_manifest_template_rows"])
    assert all(row["evidence_uploaded"] is False for row in report["case_receipt_manifest_template_rows"])
    assert all(row["evidence_attached"] is False for row in report["case_receipt_manifest_template_rows"])
    assert all(row["ready_to_attach"] is False for row in report["case_receipt_manifest_template_rows"])
    assert all(row["ready_to_mark"] is False for row in report["case_receipt_manifest_template_rows"])
    assert all(row["mark_commands_blocked"] is True for row in report["case_receipt_manifest_template_rows"])
    assert all(row["receipt_manifest_status"] == "not_received" for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["evidence_validation_status"] == "not_started" for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["evidence_file_status"] == "not_attached" for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["evidence_hash_status"] == "not_recorded" for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["evidence_upload_status"] == "not_started" for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["evidence_attachment_status"] == "not_attached" for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["ready_to_attach"] is False for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["ready_to_mark"] is False for row in report["attachment_receipt_manifest_template_rows"])
    assert report["attachment_receipt_manifest_template_rows"][0]["safe_receipt_manifest_label"] == "await_jhora_receipt_manifest"
    assert report["attachment_receipt_manifest_template_rows"][1]["safe_receipt_manifest_label"] == "await_parashara_light_receipt_manifest"
    assert all(
        row["safe_required_manifest_fields"] == REQUIRED_MANIFEST_FIELDS
        for row in report["attachment_receipt_manifest_template_rows"]
    )
    assert report["case_receipt_manifest_template_rows"][0]["safe_validation_command_families"] == [
        "build_witness_core_evidence_external_receipt_manifest_templates_report",
        "build_witness_core_evidence_external_receipt_gate_report",
        "build_witness_core_evidence_external_intake_contract_report",
        "build_witness_core_evidence_operator_packet_attachment_readiness_report",
        "build_witness_core_evidence_attachment_gate_report",
        "preflight_witness_review",
    ]
    assert _serialized_safe(report)


def test_external_receipt_manifest_templates_command_writes_json_without_mutating_p73(tmp_path, monkeypatch):
    receipt_gate_path = tmp_path / "external-receipt-gate.json"
    output_path = tmp_path / "external-receipt-manifest-templates.json"
    receipt_gate_path.write_text(json.dumps(_p73_payload()), encoding="utf-8")
    before = receipt_gate_path.read_text(encoding="utf-8")

    def fail_external_execution(*args, **kwargs):
        raise AssertionError("P75 command must not run external tools")

    monkeypatch.setattr(subprocess, "Popen", fail_external_execution)

    call_command(
        "build_witness_core_evidence_external_receipt_manifest_templates_report",
        "--external-receipt-gate-report",
        str(receipt_gate_path),
        "--output",
        str(output_path),
    )

    written = _read_json(output_path)
    assert written["schema_version"] == "jyotish-core-evidence-external-receipt-manifest-templates-v1"
    assert written["summary"]["case_receipt_manifest_template_rows"] == 5
    assert written["summary"]["attachment_receipt_manifest_template_rows"] == 10
    assert written["summary"]["pending_external_evidence_receipt_manifest_count"] == 10
    assert written["summary"]["pending_jhora_receipt_manifest_count"] == 5
    assert written["summary"]["pending_parashara_light_receipt_manifest_count"] == 5
    assert written["summary"]["receipt_manifest_received_count"] == 0
    assert written["summary"]["evidence_received_count"] == 0
    assert written["summary"]["evidence_validated_count"] == 0
    assert written["summary"]["evidence_file_recorded_count"] == 0
    assert written["summary"]["evidence_hash_recorded_count"] == 0
    assert written["summary"]["evidence_uploaded_count"] == 0
    assert written["summary"]["evidence_attached_count"] == 0
    assert written["summary"]["ready_to_attach_count"] == 0
    assert written["summary"]["ready_to_mark_count"] == 0
    assert _serialized_safe(written)
    assert receipt_gate_path.read_text(encoding="utf-8") == before


def test_p75_committed_external_receipt_manifest_templates_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(
        repo_root
        / ".tmp"
        / "witness-review"
        / "core-evidence-external-receipt-manifest-templates-p75-report.json"
    )
    receipt_gate = _read_json(
        repo_root / ".tmp" / "witness-review" / "core-evidence-external-receipt-gate-p73-report.json"
    )

    assert report["schema_version"] == "jyotish-core-evidence-external-receipt-manifest-templates-v1"
    assert report["stage"] == "P75-A"
    assert report["status"] == "blocked_pending_external_evidence_receipt_manifests"
    assert report["source_schema_version"] == "jyotish-core-evidence-external-receipt-gate-v1"
    assert report["source_stage"] == "P73-A"
    assert report["source_status"] == "blocked_pending_external_evidence_receipts"
    assert report["summary"]["source_case_receipt_gate_rows"] == 5
    assert report["summary"]["source_attachment_receipt_slot_rows"] == 10
    assert report["summary"]["case_receipt_manifest_template_rows"] == 5
    assert report["summary"]["attachment_receipt_manifest_template_rows"] == 10
    assert report["summary"]["pending_external_evidence_receipt_manifest_count"] == 10
    assert report["summary"]["pending_jhora_receipt_manifest_count"] == 5
    assert report["summary"]["pending_parashara_light_receipt_manifest_count"] == 5
    assert report["summary"]["receipt_manifest_received_count"] == 0
    assert report["summary"]["evidence_received_count"] == 0
    assert report["summary"]["evidence_validated_count"] == 0
    assert report["summary"]["evidence_file_recorded_count"] == 0
    assert report["summary"]["evidence_hash_recorded_count"] == 0
    assert report["summary"]["evidence_uploaded_count"] == 0
    assert report["summary"]["evidence_attached_count"] == 0
    assert report["summary"]["ready_to_attach_count"] == 0
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert [row["case_id"] for row in report["case_receipt_manifest_template_rows"]] == CASE_IDS
    assert [row["case_id"] for row in report["attachment_receipt_manifest_template_rows"][::2]] == CASE_IDS
    assert [row["case_id"] for row in receipt_gate["case_receipt_gate_rows"]] == CASE_IDS
    assert all(row["receipt_manifest_status"] == "not_received" for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["evidence_hash_status"] == "not_recorded" for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["ready_to_attach"] is False for row in report["attachment_receipt_manifest_template_rows"])
    assert all(row["ready_to_mark"] is False for row in report["attachment_receipt_manifest_template_rows"])
    assert _serialized_safe(report)


def test_external_receipt_manifest_templates_stage_does_not_change_forbidden_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    allowed = {
        ".tmp/witness-review/core-evidence-external-receipt-manifest-templates-p75-report.json",
        "backend/apps/calculations/witness_core_evidence_external_receipt_manifest_templates.py",
        (
            "backend/apps/calculations/management/commands/"
            "build_witness_core_evidence_external_receipt_manifest_templates_report.py"
        ),
        "backend/apps/calculations/test_witness_core_evidence_external_receipt_manifest_templates.py",
    }
    for path in changed:
        normalized = path.replace("\\", "/")
        assert normalized in allowed
        assert not normalized.startswith("frontend/")
        assert not normalized.startswith("deploy/")
        assert not normalized.startswith(".github/")
        assert "/migrations/" not in normalized
        assert "/fixtures/" not in normalized


def _p73_payload():
    case_rows = []
    slot_rows = []
    for case_index, case_id in enumerate(CASE_IDS, start=1):
        slot_indices = []
        for family in FAMILY_ORDER:
            slot_index = len(slot_rows) + 1
            slot_indices.append(slot_index)
            slot_rows.append(
                {
                    "attachment_receipt_slot_index": slot_index,
                    "case_receipt_gate_index": case_index,
                    "source_attachment_intake_slot_index": slot_index,
                    "case_id": case_id,
                    "evidence_family": family,
                    "receipt_gate_status": "blocked_pending_external_evidence_receipts",
                    "intake_status": "blocked_pending_external_evidence_intake",
                    "evidence_receipt_status": "not_received",
                    "evidence_validation_status": "not_started",
                    "evidence_file_status": "not_attached",
                    "evidence_upload_status": "not_started",
                    "evidence_attachment_status": "not_attached",
                    "ready_to_attach": False,
                    "ready_to_mark": False,
                    "safe_receipt_label": (
                        "await_jhora_screenshot_or_packet_receipt"
                        if family == "jhora_screenshot_or_packet"
                        else "await_parashara_light_manual_values_or_packet_receipt"
                    ),
                }
            )
        case_rows.append(
            {
                "case_receipt_gate_index": case_index,
                "case_id": case_id,
                "source_case_intake_contract_index": case_index,
                "source_attachment_intake_slot_indices": slot_indices,
                "receipt_gate_status": "blocked_pending_external_evidence_receipts",
                "intake_status": "blocked_pending_external_evidence_intake",
                "readiness_status": "blocked_pending_external_evidence_attachment",
                "required_external_evidence_receipts": 2,
                "missing_external_evidence_receipts": 2,
                "jhora_receipt_required": True,
                "parashara_light_receipt_required": True,
                "evidence_received": False,
                "evidence_validated": False,
                "evidence_collected": False,
                "evidence_uploaded": False,
                "evidence_attached": False,
                "ready_to_attach": False,
                "ready_to_mark": False,
                "mark_commands_blocked": True,
            }
        )
    return {
        "schema_version": "jyotish-core-evidence-external-receipt-gate-v1",
        "domain": "witness_core_parity",
        "stage": "P73-A",
        "status": "blocked_pending_external_evidence_receipts",
        "summary": {
            "source_case_intake_contract_rows": 5,
            "source_attachment_intake_slot_rows": 10,
            "case_receipt_gate_rows": 5,
            "attachment_receipt_slot_rows": 10,
            "pending_external_evidence_receipt_count": 10,
            "pending_jhora_receipt_count": 5,
            "pending_parashara_light_receipt_count": 5,
            "evidence_received_count": 0,
            "evidence_validated_count": 0,
            "evidence_uploaded_count": 0,
            "evidence_attached_count": 0,
            "ready_to_attach_count": 0,
            "ready_to_mark_count": 0,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
        },
        "case_receipt_gate_rows": case_rows,
        "attachment_receipt_slot_rows": slot_rows,
    }


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
