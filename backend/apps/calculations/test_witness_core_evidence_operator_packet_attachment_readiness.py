from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_operator_packet_attachment_readiness import (
    build_witness_core_evidence_operator_packet_attachment_readiness_report,
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
    "evidence available",
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


def test_operator_packet_attachment_readiness_preserves_p67_order_and_blocks_attachment(tmp_path):
    qa_path = tmp_path / "operator-packet-qa.json"
    qa_path.write_text(json.dumps(_p67_payload()), encoding="utf-8")

    report = build_witness_core_evidence_operator_packet_attachment_readiness_report(
        operator_packet_qa_report_path=qa_path,
    )

    assert report["schema_version"] == "jyotish-core-evidence-operator-packet-attachment-readiness-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P69-A"
    assert report["status"] == "blocked_pending_external_evidence_attachment"
    assert report["summary"] == {
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
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }
    assert [row["case_id"] for row in report["case_attachment_readiness_rows"]] == CASE_IDS
    assert [row["case_id"] for row in report["attachment_readiness_slot_rows"][::2]] == CASE_IDS
    assert [row["evidence_family"] for row in report["attachment_readiness_slot_rows"][:4]] == FAMILY_ORDER + FAMILY_ORDER
    assert report["case_attachment_readiness_rows"][0]["source_attachment_slot_qa_indices"] == [1, 2]
    assert report["case_attachment_readiness_rows"][-1]["source_attachment_slot_qa_indices"] == [9, 10]
    assert all(row["readiness_status"] == "blocked_pending_external_evidence_attachment" for row in report["case_attachment_readiness_rows"])
    assert all(row["qa_status"] == "blocked_pending_operator_packet_qa" for row in report["case_attachment_readiness_rows"])
    assert all(row["packet_status"] == "blocked_pending_operator_packet_evidence" for row in report["case_attachment_readiness_rows"])
    assert all(row["ready_to_attach"] is False for row in report["case_attachment_readiness_rows"])
    assert all(row["ready_to_mark"] is False for row in report["case_attachment_readiness_rows"])
    assert all(row["required_jhora_slot_qa_present"] is True for row in report["case_attachment_readiness_rows"])
    assert all(row["required_parashara_light_slot_qa_present"] is True for row in report["case_attachment_readiness_rows"])
    assert all(row["all_slots_not_attached"] is True for row in report["case_attachment_readiness_rows"])
    assert all(row["external_evidence_attached"] is False for row in report["case_attachment_readiness_rows"])
    assert all(row["evidence_collection_required"] is True for row in report["case_attachment_readiness_rows"])
    assert all(row["attachment_required"] is True for row in report["case_attachment_readiness_rows"])
    assert all(row["mark_commands_blocked"] is True for row in report["case_attachment_readiness_rows"])
    assert all(row["readiness_status"] == "blocked_pending_external_evidence_attachment" for row in report["attachment_readiness_slot_rows"])
    assert all(row["evidence_file_status"] == "not_attached" for row in report["attachment_readiness_slot_rows"])
    assert all(row["ready_to_attach"] is False for row in report["attachment_readiness_slot_rows"])
    assert all(row["ready_to_mark"] is False for row in report["attachment_readiness_slot_rows"])
    assert report["attachment_readiness_slot_rows"][0]["safe_attachment_label"] == "collect_jhora_screenshot"
    assert report["attachment_readiness_slot_rows"][1]["safe_attachment_label"] == "attach_parashara_light_manual_values"
    assert report["case_attachment_readiness_rows"][0]["safe_validation_command_families"] == [
        "build_witness_core_evidence_operator_packet_attachment_readiness_report",
        "build_witness_core_evidence_operator_packet_qa_report",
        "build_witness_core_evidence_operator_packets_report",
        "build_witness_core_evidence_attachment_handoff_report",
        "build_witness_core_evidence_attachment_work_orders_report",
        "build_witness_core_evidence_attachment_gate_report",
        "preflight_witness_review",
    ]
    assert _serialized_safe(report)


def test_operator_packet_attachment_readiness_command_writes_json_without_mutating_p67(tmp_path, monkeypatch):
    qa_path = tmp_path / "operator-packet-qa.json"
    output_path = tmp_path / "attachment-readiness.json"
    qa_path.write_text(json.dumps(_p67_payload()), encoding="utf-8")
    before = qa_path.read_text(encoding="utf-8")

    def fail_external_execution(*args, **kwargs):
        raise AssertionError("P69 command must not run external tools")

    monkeypatch.setattr(subprocess, "Popen", fail_external_execution)

    call_command(
        "build_witness_core_evidence_operator_packet_attachment_readiness_report",
        "--operator-packet-qa-report",
        str(qa_path),
        "--output",
        str(output_path),
    )

    written = _read_json(output_path)
    assert written["schema_version"] == "jyotish-core-evidence-operator-packet-attachment-readiness-v1"
    assert written["summary"]["case_attachment_readiness_rows"] == 5
    assert written["summary"]["attachment_readiness_slot_rows"] == 10
    assert written["summary"]["blocked_case_attachment_count"] == 5
    assert written["summary"]["pending_external_evidence_attachment_count"] == 10
    assert written["summary"]["pending_jhora_external_attachment_count"] == 5
    assert written["summary"]["pending_parashara_light_external_attachment_count"] == 5
    assert written["summary"]["ready_to_attach_count"] == 0
    assert written["summary"]["ready_to_mark_count"] == 0
    assert _serialized_safe(written)
    assert qa_path.read_text(encoding="utf-8") == before


def test_p69_committed_attachment_readiness_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(
        repo_root / ".tmp" / "witness-review" / "core-evidence-operator-packet-attachment-readiness-p69-report.json"
    )
    qa = _read_json(
        repo_root / ".tmp" / "witness-review" / "core-evidence-operator-packet-qa-p67-report.json"
    )

    assert report["schema_version"] == "jyotish-core-evidence-operator-packet-attachment-readiness-v1"
    assert report["stage"] == "P69-A"
    assert report["status"] == "blocked_pending_external_evidence_attachment"
    assert report["summary"]["source_operator_packet_qa_rows"] == 5
    assert report["summary"]["source_attachment_slot_qa_rows"] == 10
    assert report["summary"]["case_attachment_readiness_rows"] == 5
    assert report["summary"]["attachment_readiness_slot_rows"] == 10
    assert report["summary"]["blocked_case_attachment_count"] == 5
    assert report["summary"]["pending_external_evidence_attachment_count"] == 10
    assert report["summary"]["pending_jhora_external_attachment_count"] == 5
    assert report["summary"]["pending_parashara_light_external_attachment_count"] == 5
    assert report["summary"]["ready_to_attach_count"] == 0
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert [row["case_id"] for row in report["case_attachment_readiness_rows"]] == CASE_IDS
    assert [row["case_id"] for row in report["attachment_readiness_slot_rows"][::2]] == CASE_IDS
    assert [row["case_id"] for row in qa["operator_packet_qa_rows"]] == CASE_IDS
    assert all(row["ready_to_attach"] is False for row in report["attachment_readiness_slot_rows"])
    assert all(row["ready_to_mark"] is False for row in report["attachment_readiness_slot_rows"])
    assert _serialized_safe(report)


def test_operator_packet_attachment_readiness_stage_does_not_change_forbidden_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    allowed = {
        ".tmp/witness-review/core-evidence-operator-packet-attachment-readiness-p69-report.json",
        "backend/apps/calculations/witness_core_evidence_operator_packet_attachment_readiness.py",
        "backend/apps/calculations/management/commands/build_witness_core_evidence_operator_packet_attachment_readiness_report.py",
        "backend/apps/calculations/test_witness_core_evidence_operator_packet_attachment_readiness.py",
    }
    for path in changed:
        normalized = path.replace("\\", "/")
        assert normalized in allowed
        assert not normalized.startswith("frontend/")
        assert not normalized.startswith("deploy/")
        assert not normalized.startswith(".github/")
        assert "/migrations/" not in normalized
        assert "/fixtures/" not in normalized


def _p67_payload():
    packet_rows = []
    slot_rows = []
    for packet_index, case_id in enumerate(CASE_IDS, start=1):
        slot_indices = []
        for family in FAMILY_ORDER:
            slot_index = len(slot_rows) + 1
            slot_indices.append(slot_index)
            slot_rows.append(
                {
                    "attachment_slot_qa_index": slot_index,
                    "source_operator_attachment_slot_index": slot_index,
                    "operator_packet_index": packet_index,
                    "case_id": case_id,
                    "evidence_family": family,
                    "p57_evidence_slot_status": "missing",
                    "p59_attachment_slot_status": "not_attached",
                    "p61_work_order_status": "pending_not_attached",
                    "p63_handoff_status": "blocked_pending_operator_evidence",
                    "p65_packet_status": "blocked_pending_operator_packet_evidence",
                    "evidence_file_status": "not_attached",
                    "qa_status": "blocked_pending_operator_packet_qa",
                    "ready_to_mark": False,
                    "safe_action_label": (
                        "collect_jhora_screenshot"
                        if family == "jhora_screenshot_or_packet"
                        else "attach_parashara_light_manual_values"
                    ),
                }
            )
        packet_rows.append(
            {
                "operator_packet_qa_index": packet_index,
                "case_id": case_id,
                "source_operator_packet_index": packet_index,
                "source_attachment_slot_indices": slot_indices,
                "qa_status": "blocked_pending_operator_packet_qa",
                "packet_status": "blocked_pending_operator_packet_evidence",
                "ready_to_mark": False,
                "required_jhora_slot_present": True,
                "required_parashara_light_slot_present": True,
                "all_attachment_slots_not_attached": True,
                "no_external_evidence_attached": True,
                "release_gate_blocked": True,
            }
        )
    return {
        "schema_version": "jyotish-core-evidence-operator-packet-qa-v1",
        "domain": "witness_core_parity",
        "stage": "P67-A",
        "status": "blocked_pending_operator_packet_qa",
        "summary": {
            "source_operator_packet_rows": 5,
            "source_operator_attachment_slot_rows": 10,
            "operator_packet_qa_rows": 5,
            "attachment_slot_qa_rows": 10,
            "blocked_packet_qa_count": 5,
            "pending_attachment_slot_qa_count": 10,
            "pending_jhora_attachment_slot_qa_count": 5,
            "pending_parashara_light_attachment_slot_qa_count": 5,
            "ready_to_mark_count": 0,
            "attached_evidence_files_count": 0,
            "missing_attachment_slot_count": 10,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
        },
        "operator_packet_qa_rows": packet_rows,
        "attachment_slot_qa_rows": slot_rows,
    }


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
