from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_backlog import build_witness_core_evidence_backlog_report


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
]


def test_core_evidence_backlog_report_builds_safe_actionable_rows(tmp_path):
    preflight_path = tmp_path / "core-review-preflight-report.json"
    batch_path = tmp_path / "core-review-batch-p51-report.json"
    core_path = tmp_path / "core-parity-report.json"
    preflight_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-core-review-preflight-v1",
                "summary": {"case_count": 3, "not_reviewed_count": 2},
                "rows": [
                    {"case_id": "case-1", "source_family": "both"},
                    {"case_id": "case-2", "source_family": "both"},
                ],
            }
        ),
        encoding="utf-8",
    )
    batch_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-core-review-batch-v1",
                "summary": {
                    "candidate_count": 2,
                    "closed_count": 0,
                    "skipped_count": 2,
                    "after_not_reviewed_count": 2,
                    "release_gate_status": "blocked",
                    "command_smoke_matrix_status": "ready",
                },
                "skipped_rows": [
                    {
                        "candidate_index": 1,
                        "case_id": "case-1",
                        "source_family": "both",
                        "safe_blockers": ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"],
                    },
                    {
                        "candidate_index": 2,
                        "case_id": "case-2",
                        "source_family": "both",
                        "safe_blockers": ["jhora_missing_or_blocked"],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    core_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-core-parity-report-v1",
                "summary": {
                    "case_count": 3,
                    "comparable_count": 1,
                    "failed_count": 1,
                    "not_reviewed_count": 2,
                },
            }
        ),
        encoding="utf-8",
    )

    report = build_witness_core_evidence_backlog_report(
        preflight_report_path=preflight_path,
        batch_report_path=batch_path,
        core_report_path=core_path,
    )

    assert report["schema_version"] == "jyotish-core-evidence-backlog-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P53-A"
    assert report["summary"]["candidate_count"] == 2
    assert report["summary"]["blocked_count"] == 2
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 2
    assert report["summary"]["release_gate_status"] == "blocked"
    assert report["summary"]["command_smoke_matrix_status"] == "ready"
    assert report["summary"]["parity_success_claimed"] is False
    assert report["summary"]["release_ready_claimed"] is False
    assert report["core_counts"] == {
        "case_count": 3,
        "comparable_count": 1,
        "failed_count": 1,
        "not_reviewed_count": 2,
    }
    assert report["evidence_family_counts"] == {
        "jhora_screenshot_or_packet": 2,
        "parashara_light_manual_values_or_packet": 2,
    }
    assert [row["case_id"] for row in report["rows"]] == ["case-1", "case-2"]
    assert report["rows"][0]["required_evidence_families"] == [
        "jhora_screenshot_or_packet",
        "parashara_light_manual_values_or_packet",
    ]
    assert report["rows"][0]["next_actions"] == [
        "collect_jhora_screenshot",
        "attach_parashara_light_manual_values",
        "rerun_preflight_witness_review",
    ]
    assert _serialized_safe(report)


def test_core_evidence_backlog_command_writes_safe_json(tmp_path):
    preflight_path = tmp_path / "core-review-preflight-report.json"
    batch_path = tmp_path / "core-review-batch-p51-report.json"
    core_path = tmp_path / "core-parity-report.json"
    output_path = tmp_path / "backlog.json"
    preflight_path.write_text(json.dumps({"summary": {"not_reviewed_count": 0}, "rows": []}), encoding="utf-8")
    batch_path.write_text(
        json.dumps(
            {
                "summary": {
                    "candidate_count": 0,
                    "closed_count": 0,
                    "skipped_count": 0,
                    "after_not_reviewed_count": 0,
                    "release_gate_status": "blocked",
                    "command_smoke_matrix_status": "ready",
                },
                "skipped_rows": [],
            }
        ),
        encoding="utf-8",
    )
    core_path.write_text(
        json.dumps({"summary": {"case_count": 1, "comparable_count": 1, "failed_count": 1, "not_reviewed_count": 0}}),
        encoding="utf-8",
    )

    call_command(
        "build_witness_core_evidence_backlog_report",
        "--preflight-report",
        str(preflight_path),
        "--batch-report",
        str(batch_path),
        "--core-report",
        str(core_path),
        "--output",
        str(output_path),
    )

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["schema_version"] == "jyotish-core-evidence-backlog-v1"
    assert _serialized_safe(written)


def test_p53_committed_core_evidence_backlog_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(repo_root / ".tmp" / "witness-review" / "core-evidence-backlog-p53-report.json")
    preflight = _read_json(repo_root / ".tmp" / "witness-review" / "core-review-preflight-report.json")
    batch = _read_json(repo_root / ".tmp" / "witness-review" / "core-review-batch-p51-report.json")
    core = _read_json(repo_root / ".tmp" / "witness-review" / "core-parity-report.json")

    assert report["schema_version"] == "jyotish-core-evidence-backlog-v1"
    assert report["stage"] == "P53-A"
    assert report["summary"]["candidate_count"] == 20
    assert report["summary"]["blocked_count"] == 20
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert report["summary"]["release_gate_status"] == "blocked"
    assert report["summary"]["command_smoke_matrix_status"] == "ready"
    assert report["evidence_family_counts"] == {
        "jhora_screenshot_or_packet": 20,
        "parashara_light_manual_values_or_packet": 20,
    }
    assert len(report["rows"]) == 20
    assert report["rows"][0]["case_id"] == "vrindavan-1990-08-15-1024"
    assert report["rows"][-1]["case_id"] == "mayapur-2026-01-01-0000"
    assert "sterlitamak-1998-04-30-1345" not in {row["case_id"] for row in report["rows"]}
    assert preflight["summary"]["not_reviewed_count"] == 20
    assert batch["summary"]["closed_count"] == 0
    assert batch["summary"]["skipped_count"] == 20
    assert core["summary"]["comparable_count"] == 1
    assert core["summary"]["failed_count"] == 1
    assert core["summary"]["not_reviewed_count"] == 20
    assert _serialized_safe(report)


def test_core_evidence_backlog_stage_does_not_change_forbidden_files():
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
    allowed_tmp = ".tmp/witness-review/core-evidence-backlog-p53-report.json"
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
