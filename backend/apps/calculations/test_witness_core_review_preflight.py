from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


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


def test_core_review_preflight_identifies_not_reviewed_rows_and_safe_paths(tmp_path):
    from apps.calculations.witness_core_review_preflight import build_witness_core_review_preflight

    jhora_root, pl_root = _write_review_inputs(tmp_path)
    core_report = tmp_path / "core-parity-report.json"
    core_report.write_text(json.dumps(_core_report()), encoding="utf-8")
    collection_plan = _collection_plan()

    report = build_witness_core_review_preflight(
        jhora_root=jhora_root,
        pl_root=pl_root,
        core_report_path=core_report,
        collection_plan=collection_plan,
        repo_root=tmp_path,
    )

    assert report["schema_version"] == "jyotish-core-review-preflight-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["artifact_availability"] == {"domain_count": 19, "present_count": 19, "missing_count": 0}
    assert report["release_gate_status"] == "blocked"
    assert report["command_smoke_matrix_status"] == "ready"
    assert report["summary"] == {
        "case_count": 1,
        "not_reviewed_count": 1,
        "blocked_by": "review_witness_rows",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }
    assert report["safe_command_families"] == [
        "preflight_witness_review",
        "mark_jhora_witness_reviewed",
        "mark_parashara_light_witness_reviewed",
    ]
    assert report["rows"] == [
        {
            "case_id": "case-1",
            "review_status": "draft",
            "comparison_status": "not_reviewed",
            "source_family": "both",
            "jhora_evidence_paths": ["jhora/case-1/packet.json"],
            "parashara_light_evidence_paths": ["pl7/case-1/packet.json"],
            "review_blockers": {
                "jhora": ["jhora_review_status", "reviewer", "reviewed_at"],
                "parashara_light": ["pl_reviewer_note", "pl_review_status"],
            },
            "next_command_families": [
                "preflight_witness_review",
                "mark_jhora_witness_reviewed",
                "mark_parashara_light_witness_reviewed",
            ],
        }
    ]
    assert _serialized_safe(report)


def test_core_review_preflight_is_deterministic_and_non_mutating(tmp_path):
    from apps.calculations.witness_core_review_preflight import build_witness_core_review_preflight

    jhora_root, pl_root = _write_review_inputs(tmp_path)
    core_report = tmp_path / "core-parity-report.json"
    core_report.write_text(json.dumps(_core_report()), encoding="utf-8")
    before = {path: path.read_text(encoding="utf-8") for path in sorted(tmp_path.rglob("*.json"))}

    first = build_witness_core_review_preflight(
        jhora_root=jhora_root,
        pl_root=pl_root,
        core_report_path=core_report,
        collection_plan=_collection_plan(),
        repo_root=tmp_path,
    )
    second = build_witness_core_review_preflight(
        jhora_root=jhora_root,
        pl_root=pl_root,
        core_report_path=core_report,
        collection_plan=_collection_plan(),
        repo_root=tmp_path,
    )
    after = {path: path.read_text(encoding="utf-8") for path in sorted(tmp_path.rglob("*.json"))}

    assert first == second
    assert before == after


def test_core_review_preflight_command_writes_json(tmp_path):
    jhora_root, pl_root = _write_review_inputs(tmp_path)
    core_report = tmp_path / "core-parity-report.json"
    core_report.write_text(json.dumps(_core_report()), encoding="utf-8")
    collection_plan = tmp_path / "collection-plan.json"
    collection_plan.write_text(json.dumps(_collection_plan()), encoding="utf-8")
    output = tmp_path / "core-review-preflight-report.json"
    stdout = StringIO()

    call_command(
        "build_witness_core_review_preflight_report",
        "--jhora-root",
        str(jhora_root),
        "--pl-root",
        str(pl_root),
        "--core-report",
        str(core_report),
        "--collection-plan",
        str(collection_plan),
        "--output",
        str(output),
        stdout=stdout,
    )

    written = json.loads(output.read_text(encoding="utf-8"))
    summary = json.loads(stdout.getvalue())
    assert written["schema_version"] == "jyotish-core-review-preflight-v1"
    assert summary == {
        "schema_version": "jyotish-core-review-preflight-v1",
        "domain": "witness_core_parity",
        "not_reviewed_count": 1,
        "release_gate_status": "blocked",
        "command_smoke_matrix_status": "ready",
    }
    assert _serialized_safe(written)


def test_core_review_preflight_stage_does_not_change_forbidden_files():
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


def _write_review_inputs(tmp_path):
    jhora_dir = tmp_path / "jhora" / "case-1"
    pl_dir = tmp_path / "pl7" / "case-1"
    jhora_dir.mkdir(parents=True)
    pl_dir.mkdir(parents=True)
    fixture = {
        "id": "case-1",
        "review_status": "draft",
        "input": {
            "birth_date": "2026-01-01",
            "birth_time": "10:00:00",
            "place_name": "Test",
        },
        "jhora_metadata": {
            "capture_status": "export_parsed",
            "ayanamsa": "lahiri",
            "timezone_offset": "+00:00",
        },
        "capture_files": {"complete_calculations_text": "calc.txt", "screenshots": ["screen.png"]},
        "expected": {"ascendant": {"longitude": 10.0, "rashi": "Mesha"}},
        "jhora_expected": {"core": {}},
    }
    pl_fixture = {
        "id": "case-1",
        "review_status": "draft",
        "input": fixture["input"],
        "pl_metadata": {
            "capture_status": "ui_state_captured",
            "ayanamsa": "lahiri",
            "timezone_offset": "+00:00",
        },
        "capture_files": {"ui_state": "state.json", "screenshots": ["screen.png"]},
        "manual_witness_values": [{"body": "Lagna", "witness": {"rashi": "Mesha"}}],
    }
    (jhora_dir / "packet.json").write_text(json.dumps({"fixture": fixture}), encoding="utf-8")
    (pl_dir / "packet.json").write_text(json.dumps({"fixture": pl_fixture}), encoding="utf-8")
    return tmp_path / "jhora", tmp_path / "pl7"


def _core_report():
    return {
        "schema_version": "jyotish-core-parity-report-v1",
        "summary": {
            "case_count": 1,
            "comparable_count": 0,
            "passed_count": 0,
            "failed_count": 0,
            "missing_witness_count": 0,
            "not_reviewed_count": 1,
            "not_comparable_count": 0,
            "target_reviewed_count": 20,
            "target_met": False,
        },
        "cases": [{"case_id": "case-1", "review_status": "draft", "comparison_status": "not_reviewed"}],
    }


def _collection_plan():
    return {
        "schema_version": "witness-parity-collection-plan.v1",
        "report_availability": {"domain_count": 19, "present_count": 19, "missing_count": 0},
        "release_gate_status": "blocked",
        "command_smoke_matrix_status": "ready",
        "groups": {"collect_report": [], "review_witness_rows": [], "ready_for_demo": []},
    }


def _serialized_safe(payload):
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
