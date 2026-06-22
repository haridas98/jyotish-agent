from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_attachment_gate import (
    build_witness_core_evidence_attachment_gate_report,
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


P57_CASE_IDS = [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
]


def test_core_evidence_attachment_gate_preserves_p57_order_and_blocks_all_rows(tmp_path):
    readiness_path = tmp_path / "readiness.json"
    readiness_path.write_text(json.dumps(_p57_readiness_payload()), encoding="utf-8")

    report = build_witness_core_evidence_attachment_gate_report(readiness_report_path=readiness_path)

    assert report["schema_version"] == "jyotish-core-evidence-attachment-gate-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P59-A"
    assert report["status"] == "blocked_no_attached_evidence"
    assert report["summary"] == {
        "readiness_rows": 5,
        "attachment_rows": 5,
        "operator_attachment_manifest_rows": 5,
        "attached_evidence_files_count": 0,
        "attached_evidence_family_count": 0,
        "missing_attachment_slot_count": 10,
        "jhora_attached_count": 0,
        "parashara_light_attached_count": 0,
        "jhora_missing_count": 5,
        "parashara_light_missing_count": 5,
        "ready_to_mark_count": 0,
        "blocked_no_attached_evidence_count": 5,
        "remaining_not_reviewed_count": 20,
        "release_gate_status": "blocked",
        "command_smoke_matrix_status": "ready",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }
    assert [row["case_id"] for row in report["rows"]] == P57_CASE_IDS
    assert [row["case_id"] for row in report["operator_attachment_manifest"]] == P57_CASE_IDS
    assert all(row["attachment_gate_status"] == "blocked_no_attached_evidence" for row in report["rows"])
    assert all(row["ready_to_mark"] is False for row in report["rows"])
    assert all(row["attached_evidence_family_count"] == 0 for row in report["rows"])
    assert report["rows"][0]["attachment_slot_status"] == {
        "jhora_screenshot_or_packet": "not_attached",
        "parashara_light_manual_values_or_packet": "not_attached",
    }
    assert report["rows"][0]["missing_attachment_families"] == [
        "jhora_screenshot_or_packet",
        "parashara_light_manual_values_or_packet",
    ]
    assert report["rows"][0]["safe_next_actions"] == [
        "collect_jhora_screenshot",
        "attach_parashara_light_manual_values",
        "rerun_evidence_attachment_gate",
        "rerun_preflight_witness_review",
    ]
    assert report["rows"][0]["safe_validation_commands"] == [
        "build_witness_core_evidence_attachment_gate_report",
        "preflight_witness_review",
        "mark_jhora_witness_reviewed",
        "mark_parashara_light_witness_reviewed",
    ]
    assert _serialized_safe(report)


def test_core_evidence_attachment_gate_command_writes_safe_json_without_mutating_readiness(tmp_path):
    readiness_path = tmp_path / "readiness.json"
    output_path = tmp_path / "attachment-gate.json"
    readiness_path.write_text(json.dumps(_p57_readiness_payload()), encoding="utf-8")
    before = readiness_path.read_text(encoding="utf-8")

    call_command(
        "build_witness_core_evidence_attachment_gate_report",
        "--readiness-report",
        str(readiness_path),
        "--output",
        str(output_path),
    )

    written = _read_json(output_path)
    assert written["schema_version"] == "jyotish-core-evidence-attachment-gate-v1"
    assert written["summary"]["attachment_rows"] == 5
    assert written["summary"]["operator_attachment_manifest_rows"] == 5
    assert written["summary"]["missing_attachment_slot_count"] == 10
    assert written["summary"]["attached_evidence_files_count"] == 0
    assert _serialized_safe(written)
    assert readiness_path.read_text(encoding="utf-8") == before


def test_p59_committed_core_evidence_attachment_gate_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(repo_root / ".tmp" / "witness-review" / "core-evidence-attachment-gate-p59-report.json")
    readiness = _read_json(repo_root / ".tmp" / "witness-review" / "core-evidence-readiness-p57-report.json")

    assert report["schema_version"] == "jyotish-core-evidence-attachment-gate-v1"
    assert report["stage"] == "P59-A"
    assert report["summary"]["readiness_rows"] == 5
    assert report["summary"]["attachment_rows"] == 5
    assert report["summary"]["operator_attachment_manifest_rows"] == 5
    assert report["summary"]["attached_evidence_files_count"] == 0
    assert report["summary"]["attached_evidence_family_count"] == 0
    assert report["summary"]["missing_attachment_slot_count"] == 10
    assert report["summary"]["jhora_attached_count"] == 0
    assert report["summary"]["parashara_light_attached_count"] == 0
    assert report["summary"]["jhora_missing_count"] == 5
    assert report["summary"]["parashara_light_missing_count"] == 5
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["blocked_no_attached_evidence_count"] == 5
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert [row["case_id"] for row in report["rows"]] == P57_CASE_IDS
    assert [packet["case_id"] for packet in report["operator_attachment_manifest"]] == P57_CASE_IDS
    assert [row["case_id"] for row in readiness["rows"]] == P57_CASE_IDS
    assert all(row["ready_to_mark"] is False for row in report["rows"])
    assert all(row["attachment_slot_status"]["jhora_screenshot_or_packet"] == "not_attached" for row in report["rows"])
    assert all(row["attachment_slot_status"]["parashara_light_manual_values_or_packet"] == "not_attached" for row in report["rows"])
    assert _serialized_safe(report)


def test_core_evidence_attachment_gate_stage_does_not_change_forbidden_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    allowed = {
        ".tmp/witness-review/core-evidence-attachment-gate-p59-report.json",
        "backend/apps/calculations/witness_core_evidence_attachment_gate.py",
        "backend/apps/calculations/management/commands/build_witness_core_evidence_attachment_gate_report.py",
        "backend/apps/calculations/test_witness_core_evidence_attachment_gate.py",
    }
    forbidden_exact = {
        "backend/config/settings.py",
        "backend/apps/calculations/classical.py",
        "backend/apps/calculations/chart.py",
        "backend/apps/calculations/ephemeris.py",
        "backend/apps/calculations/math.py",
        "backend/apps/calculations/panchanga.py",
        "backend/apps/calculations/vimshottari.py",
        "backend/apps/calculations/dasha_systems.py",
        "backend/apps/calculations/vargas.py",
        "backend/apps/calculations/accuracy.py",
        "backend/apps/calculations/graha_drishti.py",
        "backend/apps/calculations/rashi_drishti.py",
        "backend/apps/calculations/transit_coordinates.py",
        "backend/apps/calculations/workflows.py",
    }
    for path in changed:
        normalized = path.replace("\\", "/")
        assert normalized in allowed
        assert normalized not in forbidden_exact
        assert not normalized.startswith("frontend/")
        assert not normalized.startswith("deploy/")
        assert not normalized.startswith(".github/")
        assert "/migrations/" not in normalized
        assert "/fixtures/" not in normalized


def _p57_readiness_payload():
    return {
        "schema_version": "jyotish-core-evidence-readiness-preflight-v1",
        "domain": "witness_core_parity",
        "stage": "P57-A",
        "summary": {
            "readiness_rows": 5,
            "ready_to_mark_count": 0,
            "blocked_missing_evidence_count": 5,
            "missing_evidence_slot_count": 10,
            "jhora_missing_count": 5,
            "parashara_light_missing_count": 5,
            "evidence_files_committed_count": 0,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
        },
        "rows": [
            {
                "readiness_index": index,
                "intake_index": index,
                "candidate_index": index,
                "case_id": case_id,
                "source_family": "both",
                "required_evidence_families": [
                    "jhora_screenshot_or_packet",
                    "parashara_light_manual_values_or_packet",
                ],
                "evidence_slot_status": {
                    "jhora_screenshot_or_packet": "missing",
                    "parashara_light_manual_values_or_packet": "missing",
                },
                "ready_to_mark": False,
                "readiness_status": "blocked_missing_evidence",
                "missing_evidence_families": [
                    "jhora_screenshot_or_packet",
                    "parashara_light_manual_values_or_packet",
                ],
            }
            for index, case_id in enumerate(P57_CASE_IDS, start=1)
        ],
    }


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
