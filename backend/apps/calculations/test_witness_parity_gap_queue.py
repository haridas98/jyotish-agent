from __future__ import annotations

import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.calculations.witness_parity_gap_queue import build_witness_parity_gap_queue
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


def test_gap_queue_accepts_raw_summary_and_roadmap_payload():
    raw_queue = build_witness_parity_gap_queue(
        _all_ready_summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity={"available": False, "summary": {}},
        )
    )
    roadmap_queue = build_witness_parity_gap_queue(build_witness_parity_roadmap(_all_ready_summary()))

    assert raw_queue["schema_version"] == "witness-parity-gap-queue.v1"
    assert raw_queue["generated_from_schema_version"] == "witness-summary"
    assert raw_queue["queue"][0]["key"] == "witness_core_parity"
    assert raw_queue["queue"][0]["priority"] == "high"
    assert raw_queue["queue"][1]["key"] == "witness_varga_parity"
    assert raw_queue["queue"][1]["priority"] == "medium"
    assert roadmap_queue["generated_from_schema_version"] == "witness-parity-roadmap.v1"
    assert len(roadmap_queue["queue"]) == 19


def test_gap_queue_orders_review_waiting_ready_by_severity_then_canonical_order():
    queue = build_witness_parity_gap_queue(
        _all_ready_summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity=_payload(missing=2),
            witness_dasha_parity=_payload(
                failed=1,
                extra={"readiness_summary": {"D5": {"compared": 0, "actual_missing": 4}}},
            ),
            witness_panchanga_parity={"available": False, "summary": {}},
            witness_ashtakavarga_parity={"available": False, "summary": {}},
        )
    )
    rows = queue["queue"]

    assert [row["key"] for row in rows[:5]] == [
        "witness_dasha_parity",
        "witness_varga_parity",
        "witness_core_parity",
        "witness_panchanga_parity",
        "witness_ashtakavarga_parity",
    ]
    assert [row["state"] for row in rows[:5]] == ["review", "review", "review", "waiting", "waiting"]
    assert rows[0]["priority"] == "high"
    assert rows[3]["priority"] == "medium"
    assert rows[-1]["priority"] == "low"
    assert queue["totals"] == {"queued_count": 19, "review_count": 3, "waiting_count": 2, "ready_count": 14}


def test_gap_queue_uses_canonical_order_as_tiebreaker():
    queue = build_witness_parity_gap_queue(
        _all_ready_summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity=_payload(failed=1),
            witness_dasha_parity=_payload(failed=1),
        )
    )

    assert [row["key"] for row in queue["queue"][:3]] == [
        "witness_core_parity",
        "witness_varga_parity",
        "witness_dasha_parity",
    ]


def test_gap_queue_strips_raw_forbidden_fields():
    queue = build_witness_parity_gap_queue(
        _all_ready_summary(
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
    serialized = json.dumps(queue, ensure_ascii=False).lower()

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


def test_build_witness_parity_gap_queue_report_command_writes_limited_json(settings, tmp_path):
    out = tmp_path / "gap-queue.json"
    _point_roadmap_settings_to_missing(settings, tmp_path)

    call_command("build_witness_parity_gap_queue_report", "--out", str(out), "--limit", "3")

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema_version"] == "witness-parity-gap-queue.v1"
    assert len(report["queue"]) == 3
    assert report["totals"]["waiting_count"] == 19
    assert {row["state"] for row in report["queue"]} == {"waiting"}


def test_build_witness_parity_gap_queue_report_fail_if_waiting(settings, tmp_path):
    out = tmp_path / "gap-queue.json"
    _point_roadmap_settings_to_missing(settings, tmp_path)

    with pytest.raises(CommandError):
        call_command("build_witness_parity_gap_queue_report", "--out", str(out), "--fail-if-waiting")

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema_version"] == "witness-parity-gap-queue.v1"
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
