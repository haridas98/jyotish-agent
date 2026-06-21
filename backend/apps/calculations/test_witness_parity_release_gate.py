from __future__ import annotations

import json
import subprocess

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.calculations.witness_parity_ops_bundle import build_witness_parity_ops_bundle
from apps.calculations.witness_parity_release_gate import build_witness_parity_release_gate
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


def test_release_gate_accepts_raw_summary_roadmap_and_ops_bundle_input():
    summary = _all_ready_summary(witness_core_parity=_payload(failed=1))
    roadmap = build_witness_parity_roadmap(summary)
    ops_bundle = build_witness_parity_ops_bundle(summary)

    raw_gate = build_witness_parity_release_gate(summary)
    roadmap_gate = build_witness_parity_release_gate(roadmap)
    ops_gate = build_witness_parity_release_gate(ops_bundle)

    assert raw_gate["schema_version"] == "witness-parity-release-gate.v1"
    assert raw_gate["generated_from_schema_version"] == "witness-summary"
    assert roadmap_gate["generated_from_schema_version"] == "witness-parity-roadmap.v1"
    assert ops_gate["generated_from_schema_version"] == "witness-parity-ops-bundle.v1"
    assert raw_gate["blocker_totals"] == roadmap_gate["blocker_totals"] == ops_gate["blocker_totals"]


def test_release_gate_reports_ready_only_when_no_review_waiting_or_high_priority():
    ready_gate = build_witness_parity_release_gate(_all_ready_summary())
    blocked_gate = build_witness_parity_release_gate(
        _all_ready_summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity={"available": False, "summary": {}},
        )
    )

    assert ready_gate["status"] == "ready"
    assert ready_gate["criteria"] == {
        "review_domains": {"threshold": 0, "observed": 0},
        "waiting_domains": {"threshold": 0, "observed": 0},
        "high_priority_domains": {"threshold": 0, "observed": 0},
        "command_smoke_matrix": {"threshold": 0, "observed": 0},
        "command_missing_contracts": {"threshold": 0, "observed": 0},
    }
    assert ready_gate["required_actions"] == []

    assert blocked_gate["status"] == "blocked"
    assert blocked_gate["blocker_totals"] == {
        "review_count": 1,
        "waiting_count": 1,
        "high_priority_count": 1,
        "command_smoke_blocked_count": 0,
        "command_smoke_missing_count": 0,
        "action_count": 2,
    }


def test_release_gate_blocks_on_supplied_command_smoke_matrix_and_respects_limit():
    blocked_smoke_matrix = {
        "schema_version": "witness-parity-command-smoke-matrix.v1",
        "status": "blocked",
        "totals": {
            "domain_count": 19,
            "smoke_ready_count": 18,
            "blocked_count": 1,
            "missing_count": 2,
        },
        "domains": [
            {
                "key": "witness_core_parity",
                "label": "Core parity",
                "backend_command": "build_witness_core_parity_report",
                "frontend_gate_script": "check-accuracy-core-parity-ui.mjs",
                "smoke_ready": False,
                "missing": ["backend_command", "backend_test"],
                "contract": {
                    "command_invocation_hint": "manage.py build_witness_core_parity_report --out <file>",
                },
                "source_report": "C:/Users/Admin/private/raw.json",
                "field_results": [{"expected": 1, "actual": 2}],
            }
        ],
    }

    gate = build_witness_parity_release_gate(
        _all_ready_summary(),
        command_smoke_matrix=blocked_smoke_matrix,
        limit=1,
    )

    assert gate["status"] == "blocked"
    assert gate["criteria"]["command_smoke_matrix"] == {"threshold": 0, "observed": 1}
    assert gate["criteria"]["command_missing_contracts"] == {"threshold": 0, "observed": 2}
    assert gate["blocker_totals"]["command_smoke_blocked_count"] == 1
    assert gate["blocker_totals"]["command_smoke_missing_count"] == 2
    assert gate["blocker_totals"]["action_count"] == 1
    assert gate["required_actions"] == [
        {
            "key": "witness_parity_command_smoke_matrix",
            "label": "Parity command smoke matrix",
            "state": "blocked",
            "priority": "high",
            "reason": "command smoke coverage blocked",
            "next_action": "review parity command manifest",
            "failed_count": 1,
            "blocker_count": 2,
            "readiness_gap_count": 0,
        }
    ]


def test_release_gate_blocks_on_command_smoke_status_even_when_counts_are_zero():
    blocked_smoke_matrix = {
        "schema_version": "witness-parity-command-smoke-matrix.v1",
        "status": "blocked",
        "totals": {
            "domain_count": 19,
            "smoke_ready_count": 19,
            "blocked_count": 0,
            "missing_count": 0,
        },
    }

    gate = build_witness_parity_release_gate(_all_ready_summary(), command_smoke_matrix=blocked_smoke_matrix)

    assert gate["status"] == "blocked"
    assert gate["criteria"]["command_smoke_matrix"] == {"threshold": 0, "observed": 1}
    assert gate["criteria"]["command_missing_contracts"] == {"threshold": 0, "observed": 0}
    assert gate["blocker_totals"]["command_smoke_blocked_count"] == 1
    assert gate["blocker_totals"]["command_smoke_missing_count"] == 0
    assert [row["key"] for row in gate["required_actions"]] == ["witness_parity_command_smoke_matrix"]


def test_release_gate_required_actions_are_ordered_and_limited():
    gate = build_witness_parity_release_gate(
        _all_ready_summary(
            witness_core_parity=_payload(failed=1),
            witness_varga_parity=_payload(missing=3),
            witness_dasha_parity={"available": False, "summary": {}},
        ),
        limit=2,
    )

    assert [row["key"] for row in gate["required_actions"]] == [
        "witness_varga_parity",
        "witness_core_parity",
    ]
    assert all(set(row) == {
        "key",
        "label",
        "state",
        "priority",
        "reason",
        "next_action",
        "failed_count",
        "blocker_count",
        "readiness_gap_count",
    } for row in gate["required_actions"])
    assert gate["blocker_totals"]["action_count"] == 3


def test_release_gate_strips_raw_forbidden_fields():
    gate = build_witness_parity_release_gate(
        _all_ready_summary(
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
        )
    )
    serialized = json.dumps(gate, ensure_ascii=False).lower()

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


def test_build_witness_parity_release_gate_report_command_writes_limited_json(settings, tmp_path):
    out = tmp_path / "release-gate.json"
    _point_summary_settings_to_missing(settings, tmp_path)

    call_command("build_witness_parity_release_gate_report", "--out", str(out), "--limit", "5")

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["schema_version"] == "witness-parity-release-gate.v1"
    assert report["status"] == "blocked"
    assert "command_smoke_matrix" in report["criteria"]
    assert "command_smoke_blocked_count" in report["blocker_totals"]
    assert len(report["required_actions"]) == 5
    assert report["blocker_totals"]["waiting_count"] == 19


def test_build_witness_parity_release_gate_report_fail_if_blocked(settings, tmp_path):
    out = tmp_path / "release-gate.json"
    _point_summary_settings_to_missing(settings, tmp_path)

    with pytest.raises(CommandError):
        call_command("build_witness_parity_release_gate_report", "--out", str(out), "--fail-if-blocked")

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["status"] == "blocked"


def test_release_gate_stage_does_not_change_frontend_workflows_or_settings():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    forbidden_exact = {
        "backend/config/settings.py",
        "backend/apps/calculations/workflows.py",
    }
    for path in changed:
        assert not path.startswith("frontend/")
        assert path not in forbidden_exact


def _point_summary_settings_to_missing(settings, tmp_path):
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
