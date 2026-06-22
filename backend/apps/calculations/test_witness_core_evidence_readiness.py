from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_readiness import build_witness_core_evidence_readiness_report


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


P55_CASE_IDS = [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
]


def test_core_evidence_readiness_preserves_p55_order_and_blocks_all_rows(tmp_path):
    intake_path = tmp_path / "intake.json"
    intake_path.write_text(json.dumps(_p55_intake_payload()), encoding="utf-8")

    report = build_witness_core_evidence_readiness_report(intake_report_path=intake_path)

    assert report["schema_version"] == "jyotish-core-evidence-readiness-preflight-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P57-A"
    assert report["status"] == "blocked_missing_evidence"
    assert report["summary"] == {
        "intake_rows": 5,
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
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }
    assert [row["case_id"] for row in report["rows"]] == P55_CASE_IDS
    assert [row["case_id"] for row in report["operator_packet_manifest"]] == P55_CASE_IDS
    assert all(row["readiness_status"] == "blocked_missing_evidence" for row in report["rows"])
    assert all(row["ready_to_mark"] is False for row in report["rows"])
    assert all(packet["blocked_note"] == "Evidence must be collected and attached before mark commands are attempted." for packet in report["operator_packet_manifest"])
    assert report["rows"][0]["missing_evidence_families"] == [
        "jhora_screenshot_or_packet",
        "parashara_light_manual_values_or_packet",
    ]
    assert report["rows"][0]["evidence_slot_status"] == {
        "jhora_screenshot_or_packet": "missing",
        "parashara_light_manual_values_or_packet": "missing",
    }
    assert report["rows"][0]["safe_next_actions"] == [
        "collect_jhora_screenshot",
        "attach_parashara_light_manual_values",
        "rerun_preflight_witness_review",
    ]
    assert report["rows"][0]["safe_validation_commands"] == [
        "preflight_witness_review",
        "mark_jhora_witness_reviewed",
        "mark_parashara_light_witness_reviewed",
    ]
    assert _serialized_safe(report)


def test_core_evidence_readiness_command_writes_safe_json_without_mutating_intake(tmp_path):
    intake_path = tmp_path / "intake.json"
    output_path = tmp_path / "readiness.json"
    payload = _p55_intake_payload()
    intake_path.write_text(json.dumps(payload), encoding="utf-8")
    before = intake_path.read_text(encoding="utf-8")

    call_command(
        "build_witness_core_evidence_readiness_report",
        "--intake-report",
        str(intake_path),
        "--output",
        str(output_path),
    )

    written = _read_json(output_path)
    assert written["schema_version"] == "jyotish-core-evidence-readiness-preflight-v1"
    assert written["summary"]["readiness_rows"] == 5
    assert written["summary"]["blocked_missing_evidence_count"] == 5
    assert written["summary"]["missing_evidence_slot_count"] == 10
    assert _serialized_safe(written)
    assert intake_path.read_text(encoding="utf-8") == before


def test_p57_committed_core_evidence_readiness_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(repo_root / ".tmp" / "witness-review" / "core-evidence-readiness-p57-report.json")
    intake = _read_json(repo_root / ".tmp" / "witness-review" / "core-evidence-intake-p55-report.json")

    assert report["schema_version"] == "jyotish-core-evidence-readiness-preflight-v1"
    assert report["stage"] == "P57-A"
    assert report["summary"]["intake_rows"] == 5
    assert report["summary"]["readiness_rows"] == 5
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["blocked_missing_evidence_count"] == 5
    assert report["summary"]["missing_evidence_slot_count"] == 10
    assert report["summary"]["jhora_missing_count"] == 5
    assert report["summary"]["parashara_light_missing_count"] == 5
    assert report["summary"]["evidence_files_committed_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert [row["case_id"] for row in report["rows"]] == P55_CASE_IDS
    assert [packet["case_id"] for packet in report["operator_packet_manifest"]] == P55_CASE_IDS
    assert [row["case_id"] for row in intake["rows"]] == P55_CASE_IDS
    assert all(row["ready_to_mark"] is False for row in report["rows"])
    assert _serialized_safe(report)


def test_core_evidence_readiness_stage_does_not_change_forbidden_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    allowed = {
        ".tmp/witness-review/core-evidence-readiness-p57-report.json",
        "backend/apps/calculations/witness_core_evidence_readiness.py",
        "backend/apps/calculations/management/commands/build_witness_core_evidence_readiness_report.py",
        "backend/apps/calculations/test_witness_core_evidence_readiness.py",
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


def _p55_intake_payload():
    return {
        "schema_version": "jyotish-core-evidence-intake-plan-v1",
        "domain": "witness_core_parity",
        "stage": "P55-A",
        "summary": {
            "intake_rows": 5,
            "ready_to_mark_count": 0,
            "evidence_files_committed_count": 0,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
        },
        "rows": [
            {
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
                "safe_next_actions": [
                    "collect_jhora_screenshot",
                    "attach_parashara_light_manual_values",
                    "rerun_preflight_witness_review",
                ],
                "safe_validation_commands": [
                    "preflight_witness_review",
                    "mark_jhora_witness_reviewed",
                    "mark_parashara_light_witness_reviewed",
                ],
                "safe_blockers": [
                    "jhora_missing_or_blocked",
                    "parashara_light_missing_or_blocked",
                ],
            }
            for index, case_id in enumerate(P55_CASE_IDS, start=1)
        ],
    }


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
