from __future__ import annotations

import json
import subprocess

from django.core.management import call_command

from apps.calculations.witness_parity_command_manifest import build_witness_parity_command_manifest
from apps.calculations.witness_parity_roadmap import PARITY_ROADMAP_DOMAINS


def test_manifest_includes_all_roadmap_domains_in_order():
    manifest = build_witness_parity_command_manifest()

    assert manifest["schema_version"] == "witness-parity-command-manifest.v1"
    assert [row["key"] for row in manifest["domains"]] == [key for key, _label in PARITY_ROADMAP_DOMAINS]
    assert [row["label"] for row in manifest["domains"]] == [label for _key, label in PARITY_ROADMAP_DOMAINS]


def test_manifest_current_repo_is_ready_and_totals_match_domain_count():
    manifest = build_witness_parity_command_manifest()
    domain_count = len(PARITY_ROADMAP_DOMAINS)

    assert manifest["status"] == "ready"
    assert manifest["totals"] == {
        "integrated_count": domain_count,
        "backend_module_count": domain_count,
        "backend_command_count": domain_count,
        "backend_test_count": domain_count,
        "frontend_gate_count": domain_count,
        "missing_count": 0,
    }
    assert all(row["missing"] == [] for row in manifest["domains"])


def test_manifest_handles_transit_coordinate_backend_naming_exception():
    manifest = build_witness_parity_command_manifest()
    row = next(item for item in manifest["domains"] if item["key"] == "witness_transit_coordinate_parity")

    assert row["backend_module"] == "witness_transit_coordinates_parity"
    assert row["backend_command"] == "build_witness_transit_coordinates_parity_report"
    assert row["backend_test_module"] == "test_witness_transit_coordinates_parity"
    assert row["frontend_gate_script"] == "check-accuracy-transit-coordinate-parity-ui.mjs"
    assert row["backend_module_exists"]
    assert row["backend_command_exists"]
    assert row["backend_test_exists"]
    assert row["frontend_gate_exists"]


def test_manifest_serialization_exposes_no_paths_or_raw_markers():
    manifest = build_witness_parity_command_manifest()
    serialized = json.dumps(manifest, ensure_ascii=False).lower()

    for forbidden in [
        "c:/",
        "c:\\",
        "/users/",
        "\\users\\",
        "source_report",
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


def test_build_witness_parity_command_manifest_report_writes_json(tmp_path):
    out = tmp_path / "manifest.json"

    call_command("build_witness_parity_command_manifest_report", "--out", str(out))

    manifest = json.loads(out.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "witness-parity-command-manifest.v1"
    assert manifest["status"] == "ready"
    assert manifest["totals"]["missing_count"] == 0


def test_build_witness_parity_command_manifest_report_fail_if_missing_passes_current_repo(tmp_path):
    out = tmp_path / "manifest.json"

    call_command("build_witness_parity_command_manifest_report", "--out", str(out), "--fail-if-missing")

    manifest = json.loads(out.read_text(encoding="utf-8"))
    assert manifest["status"] == "ready"


def test_command_manifest_stage_does_not_change_frontend_workflows_settings_or_deploy():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    forbidden_prefixes = ("frontend/", "deploy/")
    forbidden_exact = {
        "backend/config/settings.py",
        "backend/apps/calculations/workflows.py",
    }
    for path in changed:
        assert not path.startswith(forbidden_prefixes)
        assert path not in forbidden_exact
