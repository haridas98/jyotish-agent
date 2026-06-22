from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_intake_plan import build_witness_core_evidence_intake_plan_report


FORBIDDEN_MARKERS = [
    "source_report",
    "field_results",
    "expected",
    "actual",
    "sources_present",
    "seal_witness_case",
    "--ack-diff-open",
    "authority",
    "authoritative",
    "C:\\",
    "C:/Users",
    "/Users/",
    "/home/",
    ".env",
    "evidence available",
    "parity success",
    "release ready",
]


FIRST_FIVE_CASE_IDS = [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
]


def test_core_evidence_intake_plan_selects_first_five_safe_rows(tmp_path):
    backlog_path = tmp_path / "core-evidence-backlog-p53-report.json"
    preflight_path = tmp_path / "core-review-preflight-report.json"
    batch_path = tmp_path / "core-review-batch-p51-report.json"
    plan_rows = [
        {
            "candidate_index": index,
            "case_id": case_id,
            "source_family": "both",
            "required_evidence_families": ["jhora_screenshot_or_packet", "parashara_light_manual_values_or_packet"],
            "safe_blockers": ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"],
        }
        for index, case_id in enumerate(FIRST_FIVE_CASE_IDS + ["later-case"], start=1)
    ]
    backlog_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-core-evidence-backlog-v1",
                "summary": {
                    "candidate_count": 6,
                    "blocked_count": 6,
                    "ready_to_mark_count": 0,
                    "remaining_not_reviewed_count": 20,
                    "release_gate_status": "blocked",
                    "command_smoke_matrix_status": "ready",
                },
                "rows": plan_rows,
            }
        ),
        encoding="utf-8",
    )
    preflight_path.write_text(json.dumps({"summary": {"not_reviewed_count": 20}}), encoding="utf-8")
    batch_path.write_text(json.dumps({"summary": {"closed_count": 0, "skipped_count": 20}}), encoding="utf-8")

    report = build_witness_core_evidence_intake_plan_report(
        backlog_report_path=backlog_path,
        preflight_report_path=preflight_path,
        batch_report_path=batch_path,
        intake_batch_size=5,
    )

    assert report["schema_version"] == "jyotish-core-evidence-intake-plan-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P55-A"
    assert report["summary"]["backlog_rows"] == 6
    assert report["summary"]["intake_batch_size"] == 5
    assert report["summary"]["intake_rows"] == 5
    assert report["summary"]["blocked_rows"] == 6
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["evidence_files_committed_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert report["summary"]["release_gate_status"] == "blocked"
    assert report["summary"]["command_smoke_matrix_status"] == "ready"
    assert report["summary"]["parity_success_claimed"] is False
    assert report["summary"]["release_ready_claimed"] is False
    assert [row["case_id"] for row in report["rows"]] == FIRST_FIVE_CASE_IDS
    assert report["rows"][0]["intake_index"] == 1
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
    assert "before mark commands are attempted" in report["operator_note"]
    assert _serialized_safe(report)


def test_core_evidence_intake_plan_command_writes_json_without_mutating_inputs(tmp_path):
    backlog_path = tmp_path / "backlog.json"
    preflight_path = tmp_path / "preflight.json"
    batch_path = tmp_path / "batch.json"
    output_path = tmp_path / "intake.json"
    backlog_payload = {
        "summary": {
            "candidate_count": 1,
            "blocked_count": 1,
            "ready_to_mark_count": 0,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
        },
        "rows": [
            {
                "candidate_index": 1,
                "case_id": "case-1",
                "source_family": "both",
                "required_evidence_families": ["jhora_screenshot_or_packet", "parashara_light_manual_values_or_packet"],
                "safe_blockers": ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"],
            }
        ],
    }
    preflight_payload = {"summary": {"not_reviewed_count": 20}}
    batch_payload = {"summary": {"closed_count": 0, "skipped_count": 1}}
    backlog_path.write_text(json.dumps(backlog_payload), encoding="utf-8")
    preflight_path.write_text(json.dumps(preflight_payload), encoding="utf-8")
    batch_path.write_text(json.dumps(batch_payload), encoding="utf-8")
    before = {
        backlog_path: backlog_path.read_text(encoding="utf-8"),
        preflight_path: preflight_path.read_text(encoding="utf-8"),
        batch_path: batch_path.read_text(encoding="utf-8"),
    }

    call_command(
        "build_witness_core_evidence_intake_plan_report",
        "--backlog-report",
        str(backlog_path),
        "--preflight-report",
        str(preflight_path),
        "--batch-report",
        str(batch_path),
        "--output",
        str(output_path),
    )

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["schema_version"] == "jyotish-core-evidence-intake-plan-v1"
    assert _serialized_safe(written)
    assert {path: path.read_text(encoding="utf-8") for path in before} == before


def test_p55_committed_core_evidence_intake_plan_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(repo_root / ".tmp" / "witness-review" / "core-evidence-intake-p55-report.json")
    backlog = _read_json(repo_root / ".tmp" / "witness-review" / "core-evidence-backlog-p53-report.json")
    preflight = _read_json(repo_root / ".tmp" / "witness-review" / "core-review-preflight-report.json")
    batch = _read_json(repo_root / ".tmp" / "witness-review" / "core-review-batch-p51-report.json")

    assert report["schema_version"] == "jyotish-core-evidence-intake-plan-v1"
    assert report["stage"] == "P55-A"
    assert report["summary"]["backlog_rows"] == 20
    assert report["summary"]["intake_batch_size"] == 5
    assert report["summary"]["intake_rows"] == 5
    assert report["summary"]["blocked_rows"] == 20
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["evidence_files_committed_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert [row["case_id"] for row in report["rows"]] == FIRST_FIVE_CASE_IDS
    assert all(set(row["evidence_slot_status"].values()) == {"missing"} for row in report["rows"])
    assert backlog["summary"]["candidate_count"] == 20
    assert backlog["rows"][0]["case_id"] == FIRST_FIVE_CASE_IDS[0]
    assert preflight["summary"]["not_reviewed_count"] == 20
    assert batch["summary"]["closed_count"] == 0
    assert batch["summary"]["skipped_count"] == 20
    assert _serialized_safe(report)


def test_core_evidence_intake_plan_stage_does_not_change_forbidden_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
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
    allowed_tmp = ".tmp/witness-review/core-evidence-intake-p55-report.json"
    for path in changed:
        normalized = path.replace("\\", "/")
        assert not normalized.startswith("frontend/")
        assert not normalized.startswith("deploy/")
        assert not normalized.startswith(".github/")
        assert not normalized.startswith(".tmp/") or normalized == allowed_tmp
        assert "/migrations/" not in normalized
        assert "/fixtures/" not in normalized
        assert normalized not in forbidden_exact


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
