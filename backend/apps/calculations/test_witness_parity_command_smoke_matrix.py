from __future__ import annotations

import json
import subprocess

from django.core.management import call_command

from apps.calculations.witness_parity_command_manifest import build_witness_parity_command_manifest
from apps.calculations.witness_parity_command_smoke_matrix import build_witness_parity_command_smoke_matrix


def test_smoke_matrix_includes_all_manifest_domains_in_order():
    manifest = build_witness_parity_command_manifest()
    matrix = build_witness_parity_command_smoke_matrix()

    assert matrix["schema_version"] == "witness-parity-command-smoke-matrix.v1"
    assert matrix["generated_from_schema_version"] == "witness-parity-command-manifest.v1"
    assert [row["key"] for row in matrix["domains"]] == [row["key"] for row in manifest["domains"]]
    assert [row["label"] for row in matrix["domains"]] == [row["label"] for row in manifest["domains"]]


def test_smoke_matrix_current_repo_is_ready():
    matrix = build_witness_parity_command_smoke_matrix()

    assert matrix["status"] == "ready"
    assert matrix["totals"] == {
        "domain_count": 19,
        "smoke_ready_count": 19,
        "blocked_count": 0,
        "missing_count": 0,
    }


def test_smoke_matrix_rows_have_safe_invocation_hints():
    matrix = build_witness_parity_command_smoke_matrix()

    for row in matrix["domains"]:
        assert row["smoke_ready"] is True
        assert row["missing"] == []
        assert set(row) == {
            "key",
            "label",
            "backend_command",
            "frontend_gate_script",
            "smoke_ready",
            "missing",
            "contract",
        }
        assert row["contract"] == {
            "has_backend_command": True,
            "has_backend_test": True,
            "has_frontend_gate": True,
            "command_invocation_hint": f"manage.py {row['backend_command']} --out <file>",
        }


def test_smoke_matrix_serialization_exposes_no_paths_or_raw_markers():
    matrix = build_witness_parity_command_smoke_matrix()
    serialized = json.dumps(matrix, ensure_ascii=False).lower()

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


def test_build_witness_parity_command_smoke_matrix_report_writes_json(tmp_path):
    out = tmp_path / "smoke-matrix.json"

    call_command("build_witness_parity_command_smoke_matrix_report", "--out", str(out))

    matrix = json.loads(out.read_text(encoding="utf-8"))
    assert matrix["schema_version"] == "witness-parity-command-smoke-matrix.v1"
    assert matrix["status"] == "ready"
    assert matrix["totals"]["smoke_ready_count"] == 19


def test_build_witness_parity_command_smoke_matrix_report_fail_if_blocked_passes_current_repo(tmp_path):
    out = tmp_path / "smoke-matrix.json"

    call_command("build_witness_parity_command_smoke_matrix_report", "--out", str(out), "--fail-if-blocked")

    matrix = json.loads(out.read_text(encoding="utf-8"))
    assert matrix["status"] == "ready"


def test_smoke_matrix_stage_does_not_change_frontend_workflows_settings_or_deploy():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    forbidden_prefixes = ("frontend/", "deploy/")
    forbidden_exact = {
        "backend/config/settings.py",
        "backend/apps/calculations/workflows.py",
    }
    for path in changed:
        assert not path.startswith(forbidden_prefixes)
        assert path not in forbidden_exact
