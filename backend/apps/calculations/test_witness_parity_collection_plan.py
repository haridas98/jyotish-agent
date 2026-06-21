from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command

from apps.calculations.witness_parity_collection_plan import build_witness_parity_collection_plan
from apps.calculations.witness_parity_report_availability import build_witness_parity_report_availability
from apps.calculations.witness_parity_roadmap import PARITY_ROADMAP_DOMAINS


DOMAIN_KEYS = [key for key, _label in PARITY_ROADMAP_DOMAINS]
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
    "c:/users",
]


def _payload(
    *,
    available=True,
    target_met=True,
    passed=1,
    target=1,
    failed=0,
    missing=0,
    not_reviewed=0,
    not_comparable=0,
    extra=None,
):
    payload = {
        "available": available,
        "target_met": target_met,
        "summary": {
            "case_count": 1,
            "comparable_count": 1 if available else 0,
            "passed_count": passed,
            "failed_count": failed,
            "missing_witness_count": missing,
            "not_reviewed_count": not_reviewed,
            "not_comparable_count": not_comparable,
            "target_reviewed_count": target,
            "target_met": target_met,
        },
    }
    if extra:
        payload.update(extra)
    return payload


def _summary(**overrides):
    summary = {key: _payload() for key in DOMAIN_KEYS}
    summary.update(overrides)
    return summary


def test_collection_plan_snapshot_has_expected_totals_statuses_and_groups(tmp_path):
    availability = _availability_with_present_count(tmp_path, present_count=2)
    plan = build_witness_parity_collection_plan(
        _summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity=_payload(),
        ),
        report_availability=availability,
    )

    assert plan["schema_version"] == "witness-parity-collection-plan.v1"
    assert plan["report_availability"] == {"domain_count": 19, "present_count": 2, "missing_count": 17}
    assert plan["release_gate_status"] == "blocked"
    assert plan["command_smoke_matrix_status"] == "ready"
    assert len(plan["groups"]["collect_report"]) == 17
    assert [row["key"] for row in plan["groups"]["collect_report"]] == DOMAIN_KEYS[2:]
    assert [row["key"] for row in plan["groups"]["review_witness_rows"]] == ["witness_core_parity"]
    assert [row["key"] for row in plan["groups"]["ready_for_demo"]] == ["witness_varga_parity"]


def test_collect_report_rows_are_safe_release_blockers(tmp_path):
    plan = build_witness_parity_collection_plan(_summary(), report_availability=_availability_with_present_count(tmp_path, present_count=2))
    collect_rows = plan["groups"]["collect_report"]

    assert len(collect_rows) == 17
    assert collect_rows[0] == {
        "key": "witness_dasha_parity",
        "label": "Dasha parity",
        "status": "missing_report",
        "action": "collect report",
        "release_blocker": True,
        "command_hint": "manage.py build_witness_dasha_parity_report --output <report-json>",
    }
    assert all(row["command_hint"].endswith("--output <report-json>") for row in collect_rows)
    assert all(row["status"] == "missing_report" for row in collect_rows)


def test_collection_plan_strips_raw_internal_markers(tmp_path):
    plan = build_witness_parity_collection_plan(
        _summary(
            witness_core_parity=_payload(
                failed=1,
                extra={
                    "source_report": "C:/Users/Admin/private/raw.json",
                    "cases": [{"expected": "x", "actual": "y", "field_results": [], "sources_present": ["jhora"]}],
                    "field_results": [{"expected": 1, "actual": 2}],
                    "next_actions": [{"seal_witness_case": "no"}],
                    "authority": "bad",
                },
            )
        ),
        report_availability=_availability_with_present_count(tmp_path, present_count=2),
    )
    serialized = json.dumps(plan, ensure_ascii=False).lower()

    for marker in FORBIDDEN_MARKERS:
        assert marker not in serialized


def test_collection_plan_ordering_is_deterministic(tmp_path):
    first = build_witness_parity_collection_plan(_summary(), report_availability=_availability_with_present_count(tmp_path, present_count=2))
    second = build_witness_parity_collection_plan(_summary(), report_availability=_availability_with_present_count(tmp_path, present_count=2))

    assert first == second
    assert [row["key"] for row in first["groups"]["collect_report"]] == DOMAIN_KEYS[2:]


def test_build_witness_parity_collection_plan_report_stdout_and_output(settings, tmp_path):
    _point_summary_settings_to_first_two_present(settings, tmp_path)
    out = tmp_path / "collection-plan.json"
    stdout = StringIO()

    call_command("build_witness_parity_collection_plan_report", stdout=stdout)
    call_command("build_witness_parity_collection_plan_report", "--output", str(out))

    stdout_report = json.loads(stdout.getvalue())
    file_report = json.loads(out.read_text(encoding="utf-8"))
    assert stdout_report == file_report
    assert file_report["schema_version"] == "witness-parity-collection-plan.v1"
    assert file_report["report_availability"] == {"domain_count": 19, "present_count": 2, "missing_count": 17}
    assert file_report["release_gate_status"] == "blocked"
    assert file_report["command_smoke_matrix_status"] == "ready"
    assert len(file_report["groups"]["collect_report"]) == 17


def test_collection_plan_stage_does_not_change_frontend_workflows_settings_or_migrations():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    forbidden_exact = {
        "backend/config/settings.py",
        "backend/apps/calculations/workflows.py",
    }
    for path in changed:
        assert not path.startswith("frontend/")
        assert not path.startswith(".github/")
        assert not path.startswith("deploy/")
        assert "/migrations/" not in path.replace("\\", "/")
        assert path not in forbidden_exact


def _availability_with_present_count(tmp_path, *, present_count):
    report_paths = {
        name: tmp_path / f"{name.lower().replace('_', '-')}.json"
        for name in _report_setting_names()
    }
    present_paths = {str(path) for path in list(report_paths.values())[:present_count]}
    return build_witness_parity_report_availability(
        report_paths=report_paths,
        path_exists=lambda path: path in present_paths,
    )


def _point_summary_settings_to_first_two_present(settings, tmp_path):
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    for index, name in enumerate(_report_setting_names()):
        path = tmp_path / f"{name.lower().replace('_', '-')}.json"
        if index < 2:
            path.write_text(json.dumps(_safe_report()), encoding="utf-8")
        setattr(settings, name, path)


def _safe_report():
    return {
        "schema_version": "synthetic-parity-report.v1",
        "metadata": {"generated_at": "2026-01-01T00:00:00Z"},
        "summary": {
            "case_count": 1,
            "comparable_count": 1,
            "passed_count": 1,
            "failed_count": 0,
            "missing_witness_count": 0,
            "not_reviewed_count": 0,
            "not_comparable_count": 0,
            "target_reviewed_count": 1,
            "target_met": True,
        },
        "cases": [{"case_id": "case-1", "comparison_status": "passed"}],
    }


def _report_setting_names():
    return [
        "WITNESS_CORE_PARITY_REPORT_PATH",
        "WITNESS_VARGA_PARITY_REPORT_PATH",
        "WITNESS_DASHA_PARITY_REPORT_PATH",
        "WITNESS_PANCHANGA_PARITY_REPORT_PATH",
        "WITNESS_ASHTAKAVARGA_PARITY_REPORT_PATH",
        "WITNESS_STRENGTHS_PARITY_REPORT_PATH",
        "WITNESS_YOGA_PARITY_REPORT_PATH",
        "WITNESS_SPECIAL_POINTS_PARITY_REPORT_PATH",
        "WITNESS_ARGALA_PARITY_REPORT_PATH",
        "WITNESS_AVASTHA_PARITY_REPORT_PATH",
        "WITNESS_DRISHTI_PARITY_REPORT_PATH",
        "WITNESS_TRANSIT_COORDINATE_PARITY_REPORT_PATH",
        "WITNESS_COMPATIBILITY_PARITY_REPORT_PATH",
        "WITNESS_MUHURTA_PARITY_REPORT_PATH",
        "WITNESS_TITHI_PRAVESHA_PARITY_REPORT_PATH",
        "WITNESS_TAJAKA_PARITY_REPORT_PATH",
        "WITNESS_PRASHNA_PARITY_REPORT_PATH",
        "WITNESS_JAIMINI_KARAKA_PARITY_REPORT_PATH",
        "WITNESS_JAIMINI_VARGA_PARITY_REPORT_PATH",
    ]
