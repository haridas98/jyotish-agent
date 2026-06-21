from __future__ import annotations

import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.calculations.witness_parity_roadmap import (
    PARITY_ROADMAP_DOMAINS,
    build_witness_parity_roadmap,
)


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


def _summary(**overrides):
    summary = {key: {"available": False, "summary": {}} for key in DOMAIN_KEYS}
    summary.update(overrides)
    return summary


def test_witness_parity_roadmap_has_all_domains_in_stable_order():
    roadmap = build_witness_parity_roadmap(_summary())

    assert roadmap["schema_version"] == "witness-parity-roadmap.v1"
    assert [row["key"] for row in roadmap["domains"]] == DOMAIN_KEYS
    assert [row["label"] for row in roadmap["domains"]] == [
        "Core parity",
        "Varga parity",
        "Dasha parity",
        "Panchanga parity",
        "Ashtakavarga parity",
        "Strengths parity",
        "Yoga parity",
        "Special points parity",
        "Argala parity",
        "Avastha parity",
        "Drishti parity",
        "Transit coordinate parity",
        "Compatibility parity",
        "Muhurta parity",
        "Tithi Pravesha parity",
        "Tajaka parity",
        "Prashna parity",
        "Jaimini karaka parity",
        "Jaimini varga parity",
    ]
    assert roadmap["totals"]["integrated_count"] == 19
    assert roadmap["totals"]["waiting_count"] == 19


def test_witness_parity_roadmap_derives_ready_review_waiting_states():
    roadmap = build_witness_parity_roadmap(
        _summary(
            witness_core_parity=_payload(passed=3, target=3),
            witness_varga_parity=_payload(target_met=True, failed=2, passed=1, target=3),
            witness_dasha_parity=_payload(target_met=False, passed=1, target=3),
            witness_panchanga_parity={"available": False, "summary": {}},
        )
    )
    rows = {row["key"]: row for row in roadmap["domains"]}

    assert rows["witness_core_parity"]["state"] == "ready"
    assert rows["witness_core_parity"]["next_action"] == "ready for demo"
    assert rows["witness_varga_parity"]["state"] == "review"
    assert rows["witness_varga_parity"]["failed_count"] == 2
    assert rows["witness_dasha_parity"]["state"] == "review"
    assert rows["witness_panchanga_parity"]["state"] == "waiting"
    assert rows["witness_panchanga_parity"]["next_action"] == "collect report"
    assert roadmap["totals"]["ready_count"] == 1
    assert roadmap["totals"]["review_count"] == 2
    assert roadmap["totals"]["waiting_count"] == 16


def test_witness_parity_roadmap_counts_blockers_skipped_and_readiness_gaps():
    roadmap = build_witness_parity_roadmap(
        _summary(
            witness_yoga_parity=_payload(
                target_met=True,
                missing=2,
                not_reviewed=3,
                not_comparable=4,
                extra={"yoga_summary": {"unknown": {"passed": 0, "failed": 0, "missing": 0, "skipped": 5}}},
            ),
            witness_jaimini_varga_parity=_payload(
                target_met=True,
                extra={"readiness_summary": {"D5": {"compared": 1, "actual_missing": 6}}},
            ),
        )
    )
    rows = {row["key"]: row for row in roadmap["domains"]}

    assert rows["witness_yoga_parity"]["blocker_count"] == 9
    assert rows["witness_yoga_parity"]["skipped_count"] == 5
    assert rows["witness_jaimini_varga_parity"]["readiness_gap_count"] == 6


def test_witness_parity_roadmap_strips_raw_forbidden_fields():
    roadmap = build_witness_parity_roadmap(
        _summary(
            witness_core_parity=_payload(
                extra={
                    "source_report": "C:/tmp/raw.json",
                    "cases": [{"expected": "x", "actual": "y", "field_results": [], "sources_present": ["jhora"]}],
                    "field_results": [{"expected": 1, "actual": 2}],
                    "next_actions": [{"seal_witness_case": "no"}],
                    "authority": "bad",
                }
            )
        )
    )
    serialized = json.dumps(roadmap, ensure_ascii=False).lower()

    for forbidden in [
        "source_report",
        "c:/tmp",
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


def test_build_witness_parity_roadmap_report_command_writes_json(settings, tmp_path):
    out = tmp_path / "roadmap.json"
    _point_roadmap_settings_to_missing(settings, tmp_path)

    call_command("build_witness_parity_roadmap_report", "--out", str(out))

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema_version"] == "witness-parity-roadmap.v1"
    assert len(report["domains"]) == 19
    assert report["totals"]["waiting_count"] == 19


def test_build_witness_parity_roadmap_report_fail_if_waiting(settings, tmp_path):
    out = tmp_path / "roadmap.json"
    _point_roadmap_settings_to_missing(settings, tmp_path)

    with pytest.raises(CommandError):
        call_command("build_witness_parity_roadmap_report", "--out", str(out), "--fail-if-waiting")

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["totals"]["waiting_count"] == 19


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
