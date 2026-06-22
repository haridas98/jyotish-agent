from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_review_batch import build_witness_core_review_batch_report


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


def test_core_review_batch_report_records_safe_blocked_candidates(tmp_path):
    preflight_path = tmp_path / "core-review-preflight-report.json"
    core_path = tmp_path / "core-parity-report.json"
    preflight_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-core-review-preflight-v1",
                "summary": {"case_count": 2, "not_reviewed_count": 2},
                "rows": [
                    {
                        "case_id": "case-1",
                        "source_family": "both",
                        "jhora_evidence_paths": ["missing-jhora/packet.json"],
                        "parashara_light_evidence_paths": ["missing-pl/packet.json"],
                    },
                    {
                        "case_id": "case-2",
                        "source_family": "jhora",
                        "jhora_evidence_paths": ["missing-jhora-2/packet.json"],
                        "parashara_light_evidence_paths": [],
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
                    "case_count": 2,
                    "comparable_count": 1,
                    "passed_count": 0,
                    "failed_count": 1,
                    "not_reviewed_count": 2,
                },
            }
        ),
        encoding="utf-8",
    )

    report = build_witness_core_review_batch_report(
        preflight_report_path=preflight_path,
        core_report_path=core_path,
        repo_root=tmp_path,
        requested_close_count=5,
    )

    assert report["schema_version"] == "jyotish-core-review-batch-v1"
    assert report["status"] == "blocked_no_reviewable_rows"
    assert report["summary"]["requested_close_count"] == 5
    assert report["summary"]["closed_count"] == 0
    assert report["summary"]["skipped_count"] == 2
    assert report["core_counts"] == {
        "case_count": 2,
        "comparable_count": 1,
        "failed_count": 1,
        "not_reviewed_count": 2,
    }
    assert [row["case_id"] for row in report["skipped_rows"]] == ["case-1", "case-2"]
    assert report["skipped_rows"][0]["safe_blockers"] == ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"]
    assert _serialized_safe(report)


def test_core_review_batch_command_writes_safe_json(tmp_path):
    preflight_path = tmp_path / "core-review-preflight-report.json"
    core_path = tmp_path / "core-parity-report.json"
    output_path = tmp_path / "batch.json"
    preflight_path.write_text(
        json.dumps({"summary": {"case_count": 1, "not_reviewed_count": 0}, "rows": []}),
        encoding="utf-8",
    )
    core_path.write_text(
        json.dumps({"summary": {"case_count": 1, "comparable_count": 1, "failed_count": 1, "not_reviewed_count": 0}}),
        encoding="utf-8",
    )

    call_command(
        "build_witness_core_review_batch_report",
        "--preflight-report",
        str(preflight_path),
        "--core-report",
        str(core_path),
        "--output",
        str(output_path),
    )

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["schema_version"] == "jyotish-core-review-batch-v1"
    assert _serialized_safe(written)


def test_p51_committed_core_review_batch_artifact_and_reports_are_safe():
    repo_root = Path(__file__).resolve().parents[3]
    batch = _read_json(repo_root / ".tmp" / "witness-review" / "core-review-batch-p51-report.json")
    preflight = _read_json(repo_root / ".tmp" / "witness-review" / "core-review-preflight-report.json")
    core = _read_json(repo_root / ".tmp" / "witness-review" / "core-parity-report.json")

    assert batch["schema_version"] == "jyotish-core-review-batch-v1"
    assert batch["status"] == "blocked_no_reviewable_rows"
    assert batch["summary"]["requested_close_count"] == 5
    assert batch["summary"]["closed_count"] == 0
    assert batch["summary"]["skipped_count"] == 20
    assert batch["summary"]["before_not_reviewed_count"] == 20
    assert batch["summary"]["after_not_reviewed_count"] == 20
    assert batch["safe_command_families"] == [
        "preflight_witness_review",
        "mark_jhora_witness_reviewed",
        "mark_parashara_light_witness_reviewed",
    ]
    assert batch["closed_rows"] == []
    assert len(batch["skipped_rows"]) == 20
    assert preflight["summary"]["not_reviewed_count"] == 20
    assert core["summary"]["comparable_count"] == 1
    assert core["summary"]["failed_count"] == 1
    assert core["summary"]["not_reviewed_count"] == 20
    assert _serialized_safe(batch)
    assert _serialized_safe(preflight)
    assert _serialized_safe(core)


def test_core_review_batch_stage_does_not_change_forbidden_files():
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
    for path in changed:
        normalized = path.replace("\\", "/")
        assert not normalized.startswith("frontend/")
        assert not normalized.startswith("deploy/")
        assert not normalized.startswith(".github/")
        assert "/migrations/" not in normalized
        assert "/fixtures/" not in normalized
        assert normalized not in forbidden_exact


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
