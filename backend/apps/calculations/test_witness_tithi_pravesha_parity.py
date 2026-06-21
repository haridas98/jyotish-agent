from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, object]:
    return {
        "birth_date": "2000-01-01",
        "birth_time": "10:00:00",
        "place_name": "Vrindavan",
        "target_year": 2026,
        "search_days": 3,
    }


def _annual_return_payload(*, mismatch: bool = False, optional_unknown: bool = False) -> dict:
    payload = {
        "target_year": 2026,
        "return_context": {"type": "tithi_pravesha"},
        "natal": {"solar_lunar_angle": 24.0},
        "return": {
            "date": "2026-01-01",
            "time": "23:59:00" if not mismatch else "21:30:00",
            "local_datetime": "2026-01-01T23:59:00+05:30",
            "timezone": "Asia/Kolkata",
            "solar_lunar_angle": 24.0 if not mismatch else 25.5,
            "delta_degrees": 0.001,
        },
        "annual_context": {
            "lagna": {"rashi": "Karka" if not mismatch else "Simha", "degree": 12.5},
            "sun": {"rashi": "Dhanu", "degree": 17.2},
            "moon": {"rashi": "Makara", "degree": 11.2},
            "panchanga": {
                "tithi": {"name": "Dvitiya" if not mismatch else "Amavasya"},
                "nakshatra": {"name": "Shravana"},
                "yoga": {"name": "Siddha"},
                "karana": {"name": "Bava"},
                "vara": {"name": "Thursday"},
            },
            "tajaka": {
                "status": "baseline_calculated_needs_tajaka_review",
                "muntha": {"rashi": "Kanya", "house_from_annual_lagna": 3},
            },
        },
    }
    if optional_unknown:
        payload["experimental_return_note"] = "operator note"
    return payload


def _manual_return_payload() -> dict:
    return {
        "annual_return": {
            "target_year": 2026,
            "return_moment": {
                "date": "2026-01-01",
                "time": "23:59:00",
                "timezone": "Asia/Kolkata",
                "local_datetime": "2026-01-01T23:59:00+05:30",
            },
            "solar_lunar_angle": {"natal": 24.0, "return": 24.0, "delta_degrees": 0.001},
            "return_chart": {
                "lagna": {"rashi": "Karka", "degree": 12.5},
                "sun": {"rashi": "Dhanu", "degree": 17.2},
                "moon": {"rashi": "Makara", "degree": 11.2},
            },
            "annual_panchanga": {
                "tithi": "Dvitiya",
                "nakshatra": "Shravana",
                "yoga": "Siddha",
                "karana": "Bava",
                "vara": "Thursday",
            },
            "tajaka": {"muntha": {"rashi": "Kanya", "house_from_annual_lagna": 3}},
        }
    }


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
        "expected": expected if expected is not None else {"tithi_pravesha": _annual_return_payload()},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else {"tithi_pravesha_report": _annual_return_payload()}),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(root, case_id: str, *, review_status: str = "reviewed", manual_values=None, chart_payload=None):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_return_payload(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else {"tithi_pravesha_report": _annual_return_payload()}),
        encoding="utf-8",
    )
    return case_dir


def test_tithi_pravesha_parity_passes_context_angle_return_chart_panchanga_and_tajaka(tmp_path):
    from apps.calculations.witness_tithi_pravesha_parity import build_witness_tithi_pravesha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_tithi_pravesha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-tithi-pravesha-parity-report-v1"
    assert row["comparison_status"] == "passed"
    assert row["checked_layers"] == [
        "annual_panchanga",
        "return_chart",
        "return_context",
        "return_moment",
        "solar_lunar_angle",
        "tajaka_baseline",
        "target_year",
    ]
    assert report["summary"]["passed_count"] == 1
    assert report["field_summary"]["target_year"]["passed"] == 1
    assert report["field_summary"]["annual_panchanga.tithi"]["passed"] == 1


def test_tithi_pravesha_parity_fails_wrong_return_moment_angle_ascendant_and_panchanga(tmp_path):
    from apps.calculations.witness_tithi_pravesha_parity import build_witness_tithi_pravesha_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"tithi_pravesha": _annual_return_payload(mismatch=True)},
    )

    row = next(
        item
        for item in build_witness_tithi_pravesha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "return.time" in row["failed_fields"]
    assert "return.solar_lunar_angle" in row["failed_fields"]
    assert "annual_context.lagna.rashi" in row["failed_fields"]
    assert "annual_panchanga.tithi" in row["failed_fields"]


def test_tithi_pravesha_parity_passes_pl_manual_normalized_annual_return(tmp_path):
    from apps.calculations.witness_tithi_pravesha_parity import build_witness_tithi_pravesha_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_tithi_pravesha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert report["summary"]["comparable_count"] == 1
    assert report["layer_summary"]["tajaka_baseline"]["passed"] == 1


def test_tithi_pravesha_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_tithi_pravesha_parity import build_witness_tithi_pravesha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_payload={},
        input_payload={"target_year": 2026},
    )

    report = build_witness_tithi_pravesha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing_witness"
    assert "jhora.tithi_pravesha" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.tithi_pravesha" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_tithi_pravesha_parity_skips_unknown_optional_fields_without_demoting_case(tmp_path):
    from apps.calculations.witness_tithi_pravesha_parity import build_witness_tithi_pravesha_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"annual_return": _annual_return_payload(optional_unknown=True)},
    )

    report = build_witness_tithi_pravesha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "tithi_pravesha.experimental_return_note" in row["skipped_fields"]
    assert report["field_summary"]["experimental_return_note"]["skipped"] == 1


def test_tithi_pravesha_parity_computes_actual_from_fixture_annual_return_inputs(tmp_path, monkeypatch):
    from apps.calculations import workflows
    from apps.calculations.witness_tithi_pravesha_parity import build_witness_tithi_pravesha_parity_report

    def fake_build_tithi_pravesha_report(data):
        assert {"birth_date", "birth_time", "place_name", "target_year"} <= set(data)
        return _annual_return_payload()

    monkeypatch.setattr(workflows, "build_tithi_pravesha_report", fake_build_tithi_pravesha_report)
    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        input_payload=_case_input("sterlitamak-1998-04-30-1345"),
        chart_payload={},
    )

    report = build_witness_tithi_pravesha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert report["summary"]["comparable_count"] == 1


def test_tithi_pravesha_parity_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_tithi_pravesha_parity import build_witness_tithi_pravesha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_tithi_pravesha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_tithi_pravesha_parity_command_writes_json_markdown_and_safe_json_stdout(tmp_path):
    _write_jhora_case(tmp_path / "witness", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "tithi-pravesha-parity.json"
    markdown = tmp_path / "tithi-pravesha-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_tithi_pravesha_parity_report",
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

    assert payload["schema_version"] == "jyotish-tithi-pravesha-parity-report-v1"
    assert payload["summary"]["passed_count"] == 1
    assert "cases" not in payload
    assert "field_results" not in serialized
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["schema_version"] == "jyotish-tithi-pravesha-parity-report-v1"
    assert "cases" in report
    assert "Tithi Pravesha Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_tithi_pravesha_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_tithi_pravesha_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_tithi_pravesha_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/tithi-pravesha-parity-report.json")


def test_tithi_pravesha_parity_stage_does_not_change_formula_workflow_or_existing_report_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    forbidden_files = {
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
        "backend/apps/calculations/witness_muhurta_parity.py",
        "backend/apps/calculations/witness_compatibility_parity.py",
        "backend/apps/calculations/witness_transit_coordinates_parity.py",
        "backend/apps/calculations/witness_drishti_parity.py",
        "backend/apps/calculations/witness_avastha_parity.py",
        "backend/apps/calculations/witness_argala_parity.py",
        "backend/apps/calculations/witness_special_points_parity.py",
        "backend/apps/calculations/witness_yoga_parity.py",
        "backend/apps/calculations/witness_strengths_parity.py",
        "backend/apps/calculations/witness_ashtakavarga_parity.py",
        "backend/apps/calculations/witness_panchanga_parity.py",
        "backend/apps/calculations/witness_dasha_parity.py",
        "backend/apps/calculations/witness_core_parity.py",
        "backend/apps/calculations/witness_varga_parity.py",
    }

    assert not (forbidden_files & set(changed))
