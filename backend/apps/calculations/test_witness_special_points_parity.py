from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _expected_special_points(*, mismatch: bool = False, optional_unknown: bool = False):
    value = {
        "Gulika": {"longitude": 110.0},
        "Dhooma": {"longitude": 50.0},
        "Indu Lagna": {"longitude": 220.0},
    }
    if mismatch:
        value["Gulika"] = {"longitude": 111.0}
    if optional_unknown:
        value["Unlisted Point"] = {"longitude": 10.0}
    return value


def _manual_special_points():
    return {
        "special_points": [
            {"key": "gulika", "longitude": 110.0},
            {"name": "Indu Lagna", "longitude": 220.0},
        ]
    }


def _chart_special_points(*, missing: bool = False, gulika_longitude: float = 110.0):
    if missing:
        return {}
    return {
        "special_points": {
            "upagrahas": {
                "items": [
                    {"key": "gulika", "name": "Gulika", "longitude": gulika_longitude},
                    {"key": "dhuma", "name": "Dhuma", "longitude": 50.0},
                ]
            },
            "vedic_points": {
                "items": [
                    {"key": "indu_lagna", "name": "Indu/Dhana Lagna", "longitude": 220.0},
                    {"key": "bhava_lagna", "name": "Bhava Lagna", "longitude": 10.0},
                ]
            },
        }
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected=None,
    jhora_expected=None,
    chart_special=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"special_points": _expected_special_points()},
    }
    if jhora_expected is not None:
        fixture["jhora_expected"] = jhora_expected
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_special if chart_special is not None else _chart_special_points()}),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_values=None,
    chart_special=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_special_points(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_special if chart_special is not None else _chart_special_points()}),
        encoding="utf-8",
    )
    return case_dir


def test_special_points_parity_passes_matching_jhora_expected_points(tmp_path):
    from apps.calculations.witness_special_points_parity import build_witness_special_points_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_special_points_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-special-points-parity-report-v1"
    assert row["comparison_status"] == "passed"
    assert row["checked_layers"] == ["special_points"]
    assert row["matched_points"] == ["dhuma", "gulika", "indu_lagna"]
    assert report["layer_summary"]["special_points"]["passed"] == 1
    assert report["group_summary"]["upagrahas"]["passed"] == 1
    assert report["group_summary"]["vedic_points"]["passed"] == 1
    assert report["point_summary"]["gulika"]["passed"] == 1


def test_special_points_parity_supports_jhora_expected_export_shape(tmp_path):
    from apps.calculations.witness_special_points_parity import build_witness_special_points_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={},
        jhora_expected={"special_points": _expected_special_points()},
    )

    row = next(
        item
        for item in build_witness_special_points_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "passed"
    assert "gulika" in row["matched_points"]


def test_special_points_parity_passes_matching_pl_manual_points(tmp_path):
    from apps.calculations.witness_special_points_parity import build_witness_special_points_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_special_points_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["matched_points"] == ["gulika", "indu_lagna"]
    assert report["summary"]["passed_count"] == 1


def test_special_points_parity_respects_longitude_tolerance(tmp_path):
    from apps.calculations.witness_special_points_parity import build_witness_special_points_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        chart_special=_chart_special_points(gulika_longitude=110.01),
    )
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        expected={"special_points": {"Gulika": {"longitude": 110.0}}},
        chart_special=_chart_special_points(gulika_longitude=111.0),
    )

    report = build_witness_special_points_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "passed"
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "failed"
    assert rows["mayapur-2001-02-03-0910"]["failed_points"] == ["gulika"]
    assert "special_points.gulika.longitude" in rows["mayapur-2001-02-03-0910"]["failed_fields"]


def test_special_points_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_special_points_parity import build_witness_special_points_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_special=_chart_special_points(missing=True),
    )

    report = build_witness_special_points_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.special_points" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.special_points" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_special_points_unknown_optional_point_is_skipped_without_demoting_case(tmp_path):
    from apps.calculations.witness_special_points_parity import build_witness_special_points_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"special_points": _expected_special_points(optional_unknown=True)},
    )

    report = build_witness_special_points_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "unlisted_point" in row["skipped_points"]
    assert report["point_summary"]["unlisted_point"]["skipped"] == 1


def test_special_points_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_special_points_parity import build_witness_special_points_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_special_points_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_special_points_command_writes_json_and_markdown_without_unsafe_words(tmp_path):
    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "special-points-parity.json"
    markdown = tmp_path / "special-points-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_special_points_parity_report",
        "--jhora-root",
        str(tmp_path / "jhora"),
        "--pl-root",
        str(tmp_path / "pl7"),
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
    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-special-points-parity-report-v1"
    assert "Special Points Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_special_points_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_special_points_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_special_points_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/special-points-parity-report.json")


def test_special_points_parity_stage_does_not_change_formula_files():
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
    }

    assert not (formula_files & set(changed))
