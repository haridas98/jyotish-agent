from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_external_intake_contract import (
    build_witness_core_evidence_external_intake_contract_report,
)


FORBIDDEN_MARKERS = [
    "source_report",
    "field_results",
    "expected",
    "actual",
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


def test_external_intake_contract_preserves_p69_order_and_blocks_intake(tmp_path):
    readiness_path = tmp_path / "attachment-readiness.json"
    readiness_path.write_text(json.dumps(_p69_payload()), encoding="utf-8")

    report = build_witness_core_evidence_external_intake_contract_report(
        attachment_readiness_report_path=readiness_path,
    )

    assert report["schema_version"] == "jyotish-core-evidence-external-intake-contract-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P71-A"
    assert report["status"] == "blocked_pending_external_evidence_intake"
    assert report["summary"] == {
        "source_case_attachment_readiness_rows": 5,
        "source_attachment_readiness_slot_rows": 10,
        "case_intake_contract_rows": 5,
        "attachment_intake_slot_rows": 10,
        "pending_external_evidence_intake_count": 10,
        "pending_jhora_external_intake_count": 5,
        "pending_parashara_light_external_intake_count": 5,
        "evidence_collected_count": 0,
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
    assert [row["case_id"] for row in report["case_intake_contract_rows"]] == CASE_IDS
    assert [row["case_id"] for row in report["attachment_intake_slot_rows"][::2]] == CASE_IDS
    assert [row["evidence_family"] for row in report["attachment_intake_slot_rows"][:4]] == FAMILY_ORDER + FAMILY_ORDER
    assert report["case_intake_contract_rows"][0]["source_attachment_readiness_slot_indices"] == [1, 2]
    assert report["case_intake_contract_rows"][-1]["source_attachment_readiness_slot_indices"] == [9, 10]
    assert all(row["intake_status"] == "blocked_pending_external_evidence_intake" for row in report["case_intake_contract_rows"])
    assert all(row["readiness_status"] == "blocked_pending_external_evidence_attachment" for row in report["case_intake_contract_rows"])
    assert all(row["qa_status"] == "blocked_pending_operator_packet_qa" for row in report["case_intake_contract_rows"])
    assert all(row["packet_status"] == "blocked_pending_operator_packet_evidence" for row in report["case_intake_contract_rows"])
    assert all(row["required_external_evidence_slots"] == 2 for row in report["case_intake_contract_rows"])
    assert all(row["pending_external_evidence_slots"] == 2 for row in report["case_intake_contract_rows"])
    assert all(row["jhora_external_evidence_required"] is True for row in report["case_intake_contract_rows"])
    assert all(row["parashara_light_external_evidence_required"] is True for row in report["case_intake_contract_rows"])
    assert all(row["evidence_collected"] is False for row in report["case_intake_contract_rows"])
    assert all(row["evidence_uploaded"] is False for row in report["case_intake_contract_rows"])
    assert all(row["evidence_attached"] is False for row in report["case_intake_contract_rows"])
    assert all(row["ready_to_attach"] is False for row in report["case_intake_contract_rows"])
    assert all(row["ready_to_mark"] is False for row in report["case_intake_contract_rows"])
    assert all(row["mark_commands_blocked"] is True for row in report["case_intake_contract_rows"])
    assert all(row["evidence_collection_status"] == "not_started" for row in report["attachment_intake_slot_rows"])
    assert all(row["evidence_upload_status"] == "not_started" for row in report["attachment_intake_slot_rows"])
    assert all(row["evidence_attachment_status"] == "not_attached" for row in report["attachment_intake_slot_rows"])
    assert all(row["ready_to_attach"] is False for row in report["attachment_intake_slot_rows"])
    assert all(row["ready_to_mark"] is False for row in report["attachment_intake_slot_rows"])
    assert report["attachment_intake_slot_rows"][0]["safe_request_label"] == "request_jhora_screenshot_or_packet"
    assert report["attachment_intake_slot_rows"][1]["safe_request_label"] == "request_parashara_light_manual_values_or_packet"
    assert report["attachment_intake_slot_rows"][0]["safe_validation_label"] == "validate_jhora_screenshot_or_packet"
    assert report["attachment_intake_slot_rows"][1]["safe_validation_label"] == "validate_parashara_light_manual_values_or_packet"
    assert report["case_intake_contract_rows"][0]["safe_validation_command_families"] == [
        "build_witness_core_evidence_external_intake_contract_report",
        "build_witness_core_evidence_operator_packet_attachment_readiness_report",
        "build_witness_core_evidence_operator_packet_qa_report",
        "build_witness_core_evidence_attachment_gate_report",
        "preflight_witness_review",
    ]
    assert _serialized_safe(report)


def test_external_intake_contract_command_writes_json_without_mutating_p69(tmp_path, monkeypatch):
    readiness_path = tmp_path / "attachment-readiness.json"
    output_path = tmp_path / "external-intake-contract.json"
    readiness_path.write_text(json.dumps(_p69_payload()), encoding="utf-8")
    before = readiness_path.read_text(encoding="utf-8")

    def fail_external_execution(*args, **kwargs):
        raise AssertionError("P71 command must not run external tools")

    monkeypatch.setattr(subprocess, "Popen", fail_external_execution)

    call_command(
        "build_witness_core_evidence_external_intake_contract_report",
        "--attachment-readiness-report",
        str(readiness_path),
        "--output",
        str(output_path),
    )

    written = _read_json(output_path)
    assert written["schema_version"] == "jyotish-core-evidence-external-intake-contract-v1"
    assert written["summary"]["case_intake_contract_rows"] == 5
    assert written["summary"]["attachment_intake_slot_rows"] == 10
    assert written["summary"]["pending_external_evidence_intake_count"] == 10
    assert written["summary"]["pending_jhora_external_intake_count"] == 5
    assert written["summary"]["pending_parashara_light_external_intake_count"] == 5
    assert written["summary"]["evidence_collected_count"] == 0
    assert written["summary"]["evidence_uploaded_count"] == 0
    assert written["summary"]["evidence_attached_count"] == 0
    assert written["summary"]["ready_to_attach_count"] == 0
    assert written["summary"]["ready_to_mark_count"] == 0
    assert _serialized_safe(written)
    assert readiness_path.read_text(encoding="utf-8") == before


def test_p71_committed_external_intake_contract_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(
        repo_root / ".tmp" / "witness-review" / "core-evidence-external-intake-contract-p71-report.json"
    )
    readiness = _read_json(
        repo_root
        / ".tmp"
        / "witness-review"
        / "core-evidence-operator-packet-attachment-readiness-p69-report.json"
    )

    assert report["schema_version"] == "jyotish-core-evidence-external-intake-contract-v1"
    assert report["stage"] == "P71-A"
    assert report["status"] == "blocked_pending_external_evidence_intake"
    assert report["summary"]["source_case_attachment_readiness_rows"] == 5
    assert report["summary"]["source_attachment_readiness_slot_rows"] == 10
    assert report["summary"]["case_intake_contract_rows"] == 5
    assert report["summary"]["attachment_intake_slot_rows"] == 10
    assert report["summary"]["pending_external_evidence_intake_count"] == 10
    assert report["summary"]["pending_jhora_external_intake_count"] == 5
    assert report["summary"]["pending_parashara_light_external_intake_count"] == 5
    assert report["summary"]["evidence_collected_count"] == 0
    assert report["summary"]["evidence_uploaded_count"] == 0
    assert report["summary"]["evidence_attached_count"] == 0
    assert report["summary"]["ready_to_attach_count"] == 0
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert [row["case_id"] for row in report["case_intake_contract_rows"]] == CASE_IDS
    assert [row["case_id"] for row in report["attachment_intake_slot_rows"][::2]] == CASE_IDS
    assert [row["case_id"] for row in readiness["case_attachment_readiness_rows"]] == CASE_IDS
    assert all(row["ready_to_attach"] is False for row in report["attachment_intake_slot_rows"])
    assert all(row["ready_to_mark"] is False for row in report["attachment_intake_slot_rows"])
    assert _serialized_safe(report)


def test_external_intake_contract_stage_does_not_change_forbidden_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    allowed = {
        ".tmp/witness-review/core-evidence-external-intake-contract-p71-report.json",
        "backend/apps/calculations/witness_core_evidence_external_intake_contract.py",
        "backend/apps/calculations/management/commands/build_witness_core_evidence_external_intake_contract_report.py",
        "backend/apps/calculations/test_witness_core_evidence_external_intake_contract.py",
    }
    for path in changed:
        normalized = path.replace("\\", "/")
        assert normalized in allowed
        assert not normalized.startswith("frontend/")
        assert not normalized.startswith("deploy/")
        assert not normalized.startswith(".github/")
        assert "/migrations/" not in normalized
        assert "/fixtures/" not in normalized


def _p69_payload():
    case_rows = []
    slot_rows = []
    for case_index, case_id in enumerate(CASE_IDS, start=1):
        slot_indices = []
        for family in FAMILY_ORDER:
            slot_index = len(slot_rows) + 1
            slot_indices.append(slot_index)
            slot_rows.append(
                {
                    "attachment_readiness_slot_index": slot_index,
                    "case_attachment_readiness_index": case_index,
                    "source_attachment_slot_qa_index": slot_index,
                    "source_operator_packet_qa_index": case_index,
                    "case_id": case_id,
                    "evidence_family": family,
                    "readiness_status": "blocked_pending_external_evidence_attachment",
                    "qa_status": "blocked_pending_operator_packet_qa",
                    "packet_status": "blocked_pending_operator_packet_evidence",
                    "evidence_file_status": "not_attached",
                    "ready_to_attach": False,
                    "ready_to_mark": False,
                    "safe_attachment_label": (
                        "collect_jhora_screenshot"
                        if family == "jhora_screenshot_or_packet"
                        else "attach_parashara_light_manual_values"
                    ),
                }
            )
        case_rows.append(
            {
                "case_attachment_readiness_index": case_index,
                "case_id": case_id,
                "source_operator_packet_qa_index": case_index,
                "source_attachment_slot_qa_indices": slot_indices,
                "readiness_status": "blocked_pending_external_evidence_attachment",
                "qa_status": "blocked_pending_operator_packet_qa",
                "packet_status": "blocked_pending_operator_packet_evidence",
                "ready_to_attach": False,
                "ready_to_mark": False,
                "required_jhora_slot_qa_present": True,
                "required_parashara_light_slot_qa_present": True,
                "all_slots_not_attached": True,
                "external_evidence_attached": False,
                "evidence_collection_required": True,
                "attachment_required": True,
                "mark_commands_blocked": True,
            }
        )
    return {
        "schema_version": "jyotish-core-evidence-operator-packet-attachment-readiness-v1",
        "domain": "witness_core_parity",
        "stage": "P69-A",
        "status": "blocked_pending_external_evidence_attachment",
        "summary": {
            "source_operator_packet_qa_rows": 5,
            "source_attachment_slot_qa_rows": 10,
            "case_attachment_readiness_rows": 5,
            "attachment_readiness_slot_rows": 10,
            "blocked_case_attachment_count": 5,
            "pending_external_evidence_attachment_count": 10,
            "pending_jhora_external_attachment_count": 5,
            "pending_parashara_light_external_attachment_count": 5,
            "ready_to_attach_count": 0,
            "ready_to_mark_count": 0,
            "external_evidence_attached_count": 0,
            "attached_evidence_files_count": 0,
            "missing_attachment_slot_count": 10,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
        },
        "case_attachment_readiness_rows": case_rows,
        "attachment_readiness_slot_rows": slot_rows,
    }


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
