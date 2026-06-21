from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _muhurta_payload(*, mismatch: bool = False, optional_unknown: bool = False) -> dict:
    payload = {
        "purpose": "general",
        "purpose_profile": "General",
        "candidates": [
            {
                "date": "2026-06-01",
                "time": "09:00",
                "rank": 1,
                "window_label": "morning",
                "score": 88.0 if not mismatch else 61.0,
                "panchanga": {
                    "tithi": {"name": "Ekadashi" if not mismatch else "Amavasya"},
                    "nakshatra": {"name": "Rohini"},
                    "yoga": {"name": "Siddha"},
                    "karana": {"name": "Bava"},
                    "vara": {"name": "Monday"},
                },
                "blocked_periods": [{"key": "rahu_kalam", "status": "clear"}],
            },
            {
                "date": "2026-06-02",
                "time": "09:00",
                "rank": 2,
                "window_label": "morning",
                "score": 70.0,
                "panchanga": {
                    "tithi": {"name": "Dvadashi"},
                    "nakshatra": {"name": "Mrigashira"},
                    "yoga": {"name": "Subha"},
                    "karana": {"name": "Balava"},
                    "vara": {"name": "Tuesday"},
                },
                "blocked_periods": [{"key": "yamaganda", "status": "clear"}],
            },
        ],
        "avoidance_flags": {"rahu_kalam": "clear", "yamaganda": "clear", "gulika_kala": "clear"},
    }
    if optional_unknown:
        payload["experimental_window"] = {"score": 99}
    return payload


def _manual_muhurta() -> dict:
    return {
        "electional_timing": {
            "purpose": "general",
            "profile": "General",
            "candidate_count": 2,
            "top_candidate": {
                "date": "2026-06-01",
                "time": "09:00",
                "rank": 1,
                "score": 88,
                "tithi": "Ekadashi",
                "nakshatra": "Rohini",
                "yoga": "Siddha",
                "karana": "Bava",
                "vara": "Monday",
                "avoidance_flags": {"rahu_kalam": "clear", "yamaganda": "clear", "gulika_kala": "clear"},
            },
            "candidate_order": ["2026-06-01T09:00", "2026-06-02T09:00"],
        }
    }


def _chart_payload(*, missing: bool = False) -> dict:
    if missing:
        return {}
    return {"muhurta_report": _muhurta_payload()}


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected=None,
    chart_payload=None,
    input_payload=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": input_payload if input_payload is not None else _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"muhurta": _muhurta_payload()},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else _chart_payload()),
        encoding="utf-8",
    )
    return case_dir


def _write_jhora_top_level_actual_case(root, case_id: str):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": "jhora_verified",
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": {"muhurta": _muhurta_payload()},
        "muhurta_report": _muhurta_payload(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_values=None,
    chart_payload=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_muhurta(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else _chart_payload()),
        encoding="utf-8",
    )
    return case_dir


def test_muhurta_parity_passes_context_candidates_panchanga_and_avoidance(tmp_path):
    from apps.calculations.witness_muhurta_parity import build_witness_muhurta_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_muhurta_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-muhurta-parity-report-v1"
    assert row["comparison_status"] == "passed"
    assert row["checked_layers"] == [
        "avoidance_flags",
        "candidate_count",
        "candidate_ranking",
        "muhurta_context",
        "panchanga_factors",
        "purpose_profile",
    ]
    assert report["summary"]["passed_count"] == 1
    assert report["field_summary"]["top_candidate.date"]["passed"] == 1
    assert report["field_summary"]["panchanga.tithi"]["passed"] == 1


def test_muhurta_parity_fails_wrong_top_candidate_score_and_panchanga(tmp_path):
    from apps.calculations.witness_muhurta_parity import build_witness_muhurta_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"muhurta": _muhurta_payload(mismatch=True)},
    )

    row = next(
        item
        for item in build_witness_muhurta_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "top_candidate.score" in row["failed_fields"]
    assert "panchanga.tithi" in row["failed_fields"]
    assert "candidate_ranking.top_candidate.score" in row["failed_fields"]


def test_muhurta_parity_passes_pl_manual_normalized_electional_timing(tmp_path):
    from apps.calculations.witness_muhurta_parity import build_witness_muhurta_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_muhurta_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert report["summary"]["comparable_count"] == 1
    assert report["layer_summary"]["panchanga_factors"]["passed"] == 1


def test_muhurta_parity_uses_top_level_actual_payload_without_sibling_chart(tmp_path):
    from apps.calculations.witness_muhurta_parity import build_witness_muhurta_parity_report

    _write_jhora_top_level_actual_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_muhurta_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["missing_fields"] == []
    assert report["summary"]["comparable_count"] == 1


def test_muhurta_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_muhurta_parity import build_witness_muhurta_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_payload=_chart_payload(missing=True),
    )

    report = build_witness_muhurta_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing_witness"
    assert "jhora.muhurta" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.muhurta" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_muhurta_parity_skips_unknown_optional_fields_without_demoting_case(tmp_path):
    from apps.calculations.witness_muhurta_parity import build_witness_muhurta_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"muhurta": _muhurta_payload(optional_unknown=True)},
    )

    report = build_witness_muhurta_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "muhurta.experimental_window" in row["skipped_fields"]
    assert report["field_summary"]["experimental_window"]["skipped"] == 1


def test_muhurta_parity_computes_actual_from_fixture_muhurta_inputs(tmp_path, monkeypatch):
    from apps.calculations import workflows
    from apps.calculations.witness_muhurta_parity import build_witness_muhurta_parity_report

    def fake_build_muhurta_report(data):
        assert {"place_name", "start_date", "end_date"} <= set(data)
        return _muhurta_payload()

    monkeypatch.setattr(workflows, "build_muhurta_report", fake_build_muhurta_report)
    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        input_payload={
            "place_name": "Vrindavan",
            "start_date": "2026-06-01",
            "end_date": "2026-06-02",
            "time": "09:00",
            "purpose": "general",
        },
        chart_payload={},
    )

    report = build_witness_muhurta_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert report["summary"]["comparable_count"] == 1


def test_muhurta_parity_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_muhurta_parity import build_witness_muhurta_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_muhurta_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_muhurta_parity_command_writes_json_markdown_and_safe_json_stdout(tmp_path):
    _write_jhora_case(tmp_path / "witness", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "muhurta-parity.json"
    markdown = tmp_path / "muhurta-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_muhurta_parity_report",
        "--witness-dir",
        str(tmp_path / "witness"),
        "--output",
        str(output),
        "--markdown-output",
        str(markdown),
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    markdown_text = markdown.read_text(encoding="utf-8")
    serialized = json.dumps(payload, ensure_ascii=False) + markdown_text

    assert payload["summary"]["passed_count"] == 1
    assert payload["schema_version"] == "jyotish-muhurta-parity-report-v1"
    assert "cases" not in payload
    assert "field_results" not in serialized
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["schema_version"] == "jyotish-muhurta-parity-report-v1"
    assert "cases" in report
    assert "Muhurta Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_muhurta_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_muhurta_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_muhurta_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/muhurta-parity-report.json")


def test_muhurta_parity_stage_does_not_change_formula_or_workflow_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    formula_files = {
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

    assert not (formula_files & set(changed))
