from __future__ import annotations

import json
import subprocess

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings

from apps.calculations.witness_parity_report_availability import (
    SCHEMA_VERSION,
    build_witness_parity_report_availability,
)
from apps.calculations.witness_parity_roadmap import PARITY_ROADMAP_DOMAINS


DOMAIN_KEYS = [key for key, _label in PARITY_ROADMAP_DOMAINS]
SETTING_NAMES = [
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


def test_availability_includes_all_domains_in_canonical_order(tmp_path):
    report_paths = _report_paths(tmp_path)
    availability = build_witness_parity_report_availability(
        report_paths=report_paths,
        path_exists=lambda _path: True,
    )

    assert availability["schema_version"] == SCHEMA_VERSION
    assert [row["key"] for row in availability["domains"]] == DOMAIN_KEYS
    assert [row["report_setting"] for row in availability["domains"]] == SETTING_NAMES


def test_availability_all_present_is_ready(tmp_path):
    availability = build_witness_parity_report_availability(
        report_paths=_report_paths(tmp_path),
        path_exists=lambda _path: True,
    )

    assert availability["status"] == "ready"
    assert availability["totals"] == {
        "domain_count": 19,
        "present_count": 19,
        "missing_count": 0,
    }
    assert all(row["report_present"] is True and row["state"] == "present" for row in availability["domains"])


def test_availability_missing_reports_have_safe_collection_hints(tmp_path):
    report_paths = _report_paths(tmp_path)
    present_settings = set(SETTING_NAMES[:2])
    availability = build_witness_parity_report_availability(
        report_paths=report_paths,
        path_exists=lambda path: path in {str(report_paths[name]) for name in present_settings},
    )

    assert availability["status"] == "missing_reports"
    assert availability["totals"]["present_count"] == 2
    assert availability["totals"]["missing_count"] == 17
    missing_rows = [row for row in availability["domains"] if row["state"] == "missing"]
    assert missing_rows
    assert missing_rows[0]["collection_hint"].startswith("manage.py build_witness_")
    assert missing_rows[0]["collection_hint"].endswith("--output <report-json>")
    assert missing_rows[0]["report_filename"].endswith(".json")
    assert "/" not in missing_rows[0]["report_filename"]
    assert "\\" not in missing_rows[0]["report_filename"]


def test_availability_output_is_safe(tmp_path):
    report_paths = _report_paths(tmp_path)
    report_paths["WITNESS_CORE_PARITY_REPORT_PATH"] = tmp_path / "private" / "source_report" / "core-parity-report.json"
    availability = build_witness_parity_report_availability(report_paths=report_paths, path_exists=lambda _path: False)
    serialized = json.dumps(availability, ensure_ascii=False).lower()

    for forbidden in [
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
        str(tmp_path).lower(),
    ]:
        assert forbidden not in serialized


def test_build_witness_parity_report_availability_report_command_writes_json(tmp_path):
    out = tmp_path / "availability.json"
    settings_overrides = {name: str(path) for name, path in _report_paths(tmp_path).items()}

    with override_settings(**settings_overrides):
        call_command("build_witness_parity_report_availability_report", "--out", str(out))

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema_version"] == SCHEMA_VERSION
    assert report["totals"]["domain_count"] == 19
    assert len(report["domains"]) == 19


def test_build_witness_parity_report_availability_report_fail_if_missing(tmp_path):
    out = tmp_path / "availability.json"
    settings_overrides = {name: str(tmp_path / f"missing-{name}.json") for name in SETTING_NAMES}

    with override_settings(**settings_overrides), pytest.raises(CommandError):
        call_command("build_witness_parity_report_availability_report", "--out", str(out), "--fail-if-missing")

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["status"] == "missing_reports"


def test_availability_stage_does_not_change_frontend_workflows_settings_or_deploy():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    forbidden_exact = {
        "backend/config/settings.py",
        "backend/apps/calculations/workflows.py",
    }
    for path in changed:
        assert not path.startswith("frontend/")
        assert not path.startswith("deploy/")
        assert path not in forbidden_exact


def _report_paths(tmp_path):
    return {name: tmp_path / f"{name.lower().replace('_', '-')}.json" for name in SETTING_NAMES}
