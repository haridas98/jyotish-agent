from __future__ import annotations

import json
import subprocess

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.calculations.witness_parity_ops_bundle import build_witness_parity_ops_bundle
from apps.calculations.witness_parity_report_availability import build_witness_parity_report_availability
from apps.calculations.witness_parity_roadmap import PARITY_ROADMAP_DOMAINS, build_witness_parity_roadmap


DOMAIN_KEYS = [key for key, _label in PARITY_ROADMAP_DOMAINS]


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


def _all_ready_summary(**overrides):
    summary = {key: _payload() for key in DOMAIN_KEYS}
    summary.update(overrides)
    return summary


def test_ops_bundle_accepts_raw_summary_and_roadmap_input():
    summary = _all_ready_summary(
        witness_core_parity=_payload(failed=2),
        witness_varga_parity={"available": False, "summary": {}},
    )
    raw_bundle = build_witness_parity_ops_bundle(summary)
    roadmap_bundle = build_witness_parity_ops_bundle(build_witness_parity_roadmap(summary))

    assert raw_bundle["schema_version"] == "witness-parity-ops-bundle.v1"
    assert raw_bundle["generated_from_schema_version"] == "witness-summary"
    assert roadmap_bundle["generated_from_schema_version"] == "witness-parity-roadmap.v1"
    assert raw_bundle["roadmap_totals"] == roadmap_bundle["roadmap_totals"]
    assert raw_bundle["gap_queue_totals"] == roadmap_bundle["gap_queue_totals"]
    assert raw_bundle["next_actions"][0]["key"] == "witness_core_parity"


def test_ops_bundle_priority_state_totals_are_deterministic():
    bundle = build_witness_parity_ops_bundle(
        _all_ready_summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity=_payload(missing=2),
            witness_dasha_parity={"available": False, "summary": {}},
            witness_panchanga_parity={"available": False, "summary": {}},
        )
    )

    assert bundle["priority_totals"] == {"high": 2, "medium": 2, "low": 15}
    assert bundle["state_totals"] == {"ready": 15, "review": 2, "waiting": 2}
    assert bundle["next_actions"][:4] == [
        {
            "key": "witness_varga_parity",
            "label": "Varga parity",
            "state": "review",
            "priority": "high",
            "reason": "needs witness review",
            "next_action": "review witness rows",
            "failed_count": 0,
            "blocker_count": 2,
            "readiness_gap_count": 0,
            "target_reviewed_count": 1,
            "passed_count": 1,
        },
        {
            "key": "witness_core_parity",
            "label": "Core parity",
            "state": "review",
            "priority": "high",
            "reason": "needs witness review",
            "next_action": "review witness rows",
            "failed_count": 1,
            "blocker_count": 0,
            "readiness_gap_count": 0,
            "target_reviewed_count": 1,
            "passed_count": 1,
        },
        {
            "key": "witness_dasha_parity",
            "label": "Dasha parity",
            "state": "waiting",
            "priority": "medium",
            "reason": "collect report",
            "next_action": "collect report",
            "failed_count": 0,
            "blocker_count": 0,
            "readiness_gap_count": 0,
            "target_reviewed_count": 0,
            "passed_count": 0,
            "collection_hint": "manage.py build_witness_dasha_parity_report --output <report-json>",
        },
        {
            "key": "witness_panchanga_parity",
            "label": "Panchanga parity",
            "state": "waiting",
            "priority": "medium",
            "reason": "collect report",
            "next_action": "collect report",
            "failed_count": 0,
            "blocker_count": 0,
            "readiness_gap_count": 0,
            "target_reviewed_count": 0,
            "passed_count": 0,
            "collection_hint": "manage.py build_witness_panchanga_parity_report --output <report-json>",
        },
    ]


def test_ops_bundle_limit_and_state_filter():
    bundle = build_witness_parity_ops_bundle(
        _all_ready_summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity={"available": False, "summary": {}},
        ),
        limit=1,
        states={"waiting"},
    )

    assert bundle["gap_queue_totals"]["queued_count"] == 19
    assert len(bundle["next_actions"]) == 1
    assert bundle["next_actions"][0]["key"] == "witness_varga_parity"
    assert bundle["next_actions"][0]["state"] == "waiting"


def test_ops_bundle_adds_report_availability_totals_and_collection_hints(tmp_path):
    availability = _availability_with_present_count(tmp_path, present_count=2)
    bundle = build_witness_parity_ops_bundle(
        _all_ready_summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity=_payload(missing=2),
            witness_dasha_parity={"available": False, "summary": {}},
            witness_panchanga_parity={"available": False, "summary": {}},
        ),
        report_availability=availability,
    )

    assert bundle["report_availability_domain_count"] == 19
    assert bundle["report_availability_present_count"] == 2
    assert bundle["report_availability_missing_count"] == 17
    waiting_actions = [row for row in bundle["next_actions"] if row["state"] == "waiting"]
    assert [row["key"] for row in waiting_actions[:2]] == ["witness_dasha_parity", "witness_panchanga_parity"]
    assert waiting_actions[0]["collection_hint"] == "manage.py build_witness_dasha_parity_report --output <report-json>"
    assert waiting_actions[0]["next_action"] == "collect report"


def test_ops_bundle_strips_raw_forbidden_fields():
    bundle = build_witness_parity_ops_bundle(
        _all_ready_summary(
            witness_core_parity=_payload(
                extra={
                    "source_report": "C:/Users/Admin/private/raw.json",
                    "cases": [{"expected": "x", "actual": "y", "field_results": [], "sources_present": ["jhora"]}],
                    "field_results": [{"expected": 1, "actual": 2}],
                    "next_actions": [{"seal_witness_case": "no"}],
                    "authority": "bad",
                }
            )
        )
    )
    serialized = json.dumps(bundle, ensure_ascii=False).lower()

    for forbidden in [
        "source_report",
        "c:/users",
        "cases",
        "field_results",
        "expected",
        "actual",
        "sources_present",
        "seal_witness_case",
        "--ack-diff-open",
        "authority",
        "authoritative",
    ]:
        assert forbidden not in serialized


def test_build_witness_parity_ops_bundle_report_command_writes_limited_json(settings, tmp_path):
    out = tmp_path / "ops-bundle.json"
    _point_roadmap_settings_to_missing(settings, tmp_path)

    call_command("build_witness_parity_ops_bundle_report", "--out", str(out))

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema_version"] == "witness-parity-ops-bundle.v1"
    assert len(report["next_actions"]) == 10
    assert report["gap_queue_totals"]["waiting_count"] == 19


def test_build_witness_parity_ops_bundle_report_state_filter(settings, tmp_path):
    out = tmp_path / "ops-bundle-ready.json"
    _point_roadmap_settings_to_missing(settings, tmp_path)

    call_command("build_witness_parity_ops_bundle_report", "--out", str(out), "--state", "ready", "--limit", "0")

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema_version"] == "witness-parity-ops-bundle.v1"
    assert report["next_actions"] == []
    assert report["gap_queue_totals"]["waiting_count"] == 19


def test_build_witness_parity_ops_bundle_report_fail_if_high_priority(settings, tmp_path):
    out = tmp_path / "ops-bundle.json"
    _point_roadmap_settings_to_missing(settings, tmp_path)
    settings.WITNESS_CORE_PARITY_REPORT_PATH = _write_parity_report(tmp_path / "core-parity.json", failed=1)

    with pytest.raises(CommandError):
        call_command("build_witness_parity_ops_bundle_report", "--out", str(out), "--fail-if-high-priority")

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["priority_totals"]["high"] == 1


def test_ops_bundle_stage_does_not_change_frontend_workflows_or_settings():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    forbidden_exact = {
        "backend/config/settings.py",
        "backend/apps/calculations/workflows.py",
    }
    for path in changed:
        assert not path.startswith("frontend/")
        assert path not in forbidden_exact


def _write_parity_report(path, *, failed=0):
    report = {
        "schema_version": "synthetic-parity-report.v1",
        "metadata": {"generated_at": "2026-01-01T00:00:00Z"},
        "summary": {
            "case_count": 1,
            "comparable_count": 1,
            "passed_count": 0 if failed else 1,
            "failed_count": failed,
            "missing_witness_count": 0,
            "not_reviewed_count": 0,
            "not_comparable_count": 0,
            "target_reviewed_count": 1,
            "target_met": True,
        },
        "layer_summary": {},
        "cases": [
            {
                "case_id": "case-1",
                "comparison_status": "failed" if failed else "passed",
                "failed_layers": ["core"] if failed else [],
            }
        ],
    }
    path.write_text(json.dumps(report), encoding="utf-8")
    return path


def _availability_with_present_count(tmp_path, *, present_count):
    report_paths = {
        name: tmp_path / f"{name.lower().replace('_', '-')}.json"
        for name in [
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
    }
    present_paths = {str(path) for path in list(report_paths.values())[:present_count]}
    return build_witness_parity_report_availability(
        report_paths=report_paths,
        path_exists=lambda path: path in present_paths,
    )


def _point_roadmap_settings_to_missing(settings, tmp_path):
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    for name in [
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
    ]:
        setattr(settings, name, tmp_path / f"missing-{name.lower()}.json")
