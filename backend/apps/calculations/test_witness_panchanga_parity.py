from __future__ import annotations

import json
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _expected_panchanga(*, mismatch: bool = False) -> dict[str, object]:
    payload = {
        "tithi": "Sukla Panchami",
        "vara": "Thursday",
        "yoga": "Sukarman",
        "karana": "Bava",
        "nakshatra": "Rohini",
    }
    if mismatch:
        payload["tithi"] = "Krishna Shashthi"
    return payload


def _chart_panchanga(*, missing: bool = False) -> dict[str, object]:
    if missing:
        return {}
    return {
        "tithi": {"name": "Panchami", "paksha": "Shukla"},
        "vara": {"name": "Guruvara"},
        "yoga": {"name": "Sukarma"},
        "karana": {"name": "Bava"},
        "nakshatra": {"name": "Rohini"},
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected_panchanga=None,
    chart_panchanga=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": {
            "panchanga": expected_panchanga if expected_panchanga is not None else _expected_panchanga()
        },
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"panchanga": chart_panchanga if chart_panchanga is not None else _chart_panchanga()}),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_panchanga=None,
    chart_panchanga=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": {
            "panchanga": manual_panchanga if manual_panchanga is not None else _expected_panchanga()
        },
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"panchanga": chart_panchanga if chart_panchanga is not None else _chart_panchanga()}),
        encoding="utf-8",
    )
    return case_dir


def test_panchanga_parity_report_passes_reviewed_matching_fields(tmp_path):
    from apps.calculations.witness_panchanga_parity import build_witness_panchanga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_panchanga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-panchanga-parity-report-v1"
    assert report["metadata"]["fields"] == ["tithi", "vara", "yoga", "karana", "nakshatra"]
    assert row["comparison_status"] == "passed"
    assert row["checked_fields"] == ["karana", "nakshatra", "tithi", "vara", "yoga"]
    assert row["failed_fields"] == []
    assert report["summary"]["passed_count"] == 1
    assert report["field_summary"]["tithi"]["passed"] == 1


def test_panchanga_parity_report_records_field_mismatch(tmp_path):
    from apps.calculations.witness_panchanga_parity import build_witness_panchanga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_panchanga=_expected_panchanga(mismatch=True),
    )

    row = next(
        item
        for item in build_witness_panchanga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert row["failed_fields"] == ["panchanga.tithi"]
    assert "tithi" in row["failed_panchanga_fields"]


def test_panchanga_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_panchanga_parity import build_witness_panchanga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected_panchanga={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_panchanga=_chart_panchanga(missing=True),
    )

    report = build_witness_panchanga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.panchanga" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.panchanga" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_panchanga_parity_partial_comparable_field_still_passes_case(tmp_path):
    from apps.calculations.witness_panchanga_parity import build_witness_panchanga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_panchanga={"tithi": "Sukla Panchami"},
        chart_panchanga={"tithi": {"name": "Panchami", "paksha": "Shukla"}},
    )

    report = build_witness_panchanga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["checked_fields"] == ["tithi"]
    assert "jhora.panchanga.vara" in row["missing_fields"]
    assert "calculated.panchanga.vara" not in row["missing_fields"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1
    assert report["field_summary"]["tithi"]["passed"] == 1
    assert report["field_summary"]["vara"]["missing"] == 1


def test_panchanga_parity_missing_one_source_does_not_hide_comparable_reviewed_source(tmp_path):
    from apps.calculations.witness_panchanga_parity import build_witness_panchanga_parity_report

    case_id = "sterlitamak-1998-04-30-1345"
    _write_jhora_case(tmp_path / "jhora", case_id, expected_panchanga={})
    _write_pl_case(tmp_path / "pl7", case_id, manual_panchanga={"tithi": "Sukla Panchami"}, chart_panchanga={"tithi": {"name": "Panchami", "paksha": "Shukla"}})

    report = build_witness_panchanga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == case_id)

    assert row["comparison_status"] == "passed"
    assert row["checked_fields"] == ["tithi"]
    assert "jhora.panchanga" in row["missing_fields"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_panchanga_parity_report_keeps_unreviewed_case_out_of_passed(tmp_path):
    from apps.calculations.witness_panchanga_parity import build_witness_panchanga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_panchanga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_panchanga_parity_command_writes_json_and_markdown_without_unsafe_authority(tmp_path):
    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "panchanga-parity.json"
    markdown = tmp_path / "panchanga-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_panchanga_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-panchanga-parity-report-v1"
    assert "Panchanga Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered
    assert "witness_sources" in serialized


def test_panchanga_parity_command_default_output_path_matches_contract(settings):
    from apps.calculations.management.commands.build_witness_panchanga_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_panchanga_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/panchanga-parity-report.json")
