from __future__ import annotations

import json
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _jhora_expected_rows(rows=None):
    return {
        "ui_tables": {
            "identified": {
                "active_yogas": {
                    "rows": rows
                    if rows is not None
                    else [
                        ["Ruchaka", "D1", "Mars", "Strong initiative", "Mars in kendra"],
                    ]
                }
            }
        }
    }


def _manual_yogas(values=None):
    return {
        "active_yogas": values
        if values is not None
        else [
            {"key": "budha_aditya"},
            {"name": "Gaja Kesari Yoga"},
        ]
    }


def _chart_yogas(*, missing: bool = False, items=None):
    if missing:
        return {}
    return {
        "yogas": {
            "items": items
            if items is not None
            else [
                {"key": "ruchaka_mahapurusha", "name": "Ruchaka Yoga", "present": True},
                {"key": "budha_aditya", "name": "Budha Aditya Yoga", "present": True},
                {"key": "gaja_kesari", "name": "Gaja Kesari Yoga", "present": True},
                {"key": "catalog_only", "name": "Catalog Only", "present": False},
            ]
        }
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected=None,
    chart_yogas=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else _jhora_expected_rows(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_yogas if chart_yogas is not None else _chart_yogas()}),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_yogas=None,
    chart_yogas=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_yogas if manual_yogas is not None else _manual_yogas(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_yogas if chart_yogas is not None else _chart_yogas()}),
        encoding="utf-8",
    )
    return case_dir


def test_yoga_parity_report_passes_matching_jhora_ui_active_yogas(tmp_path):
    from apps.calculations.witness_yoga_parity import build_witness_yoga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_yoga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-yoga-parity-report-v1"
    assert report["metadata"]["layers"] == ["active_yogas"]
    assert row["comparison_status"] == "passed"
    assert row["checked_layers"] == ["active_yogas"]
    assert "ruchaka" in row["matched_yogas"]
    assert report["layer_summary"]["active_yogas"]["passed"] == 1
    assert report["yoga_summary"]["ruchaka"]["passed"] == 1


def test_yoga_parity_report_passes_normalized_manual_active_yogas(tmp_path):
    from apps.calculations.witness_yoga_parity import build_witness_yoga_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_yoga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["matched_yogas"] == ["budha_aditya", "gaja_kesari"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_yoga_parity_report_records_comparable_active_yoga_mismatch(tmp_path):
    from apps.calculations.witness_yoga_parity import build_witness_yoga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected=_jhora_expected_rows(rows=[["Viparita Raja Yoga", "D1", "", "", ""]]),
    )

    row = next(
        item
        for item in build_witness_yoga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "viparita_raja_yoga" in row["failed_yogas"]
    assert "active_yogas.viparita_raja_yoga" in row["failed_fields"]


def test_yoga_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_yoga_parity import build_witness_yoga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_yogas=_chart_yogas(missing=True),
    )

    report = build_witness_yoga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.active_yogas" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.active_yogas" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_yoga_parity_partial_comparable_unknown_yoga_still_passes_case(tmp_path):
    from apps.calculations.witness_yoga_parity import build_witness_yoga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected=_jhora_expected_rows(
            rows=[
                ["Ruchaka", "D1", "", "", ""],
                ["Unpublished Regional Yoga", "D1", "", "", ""],
            ]
        ),
    )

    report = build_witness_yoga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["checked_yogas"] == ["ruchaka"]
    assert "unpublished_regional_yoga" in row["skipped_yogas"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_yoga_parity_report_keeps_unreviewed_case_out_of_passed(tmp_path):
    from apps.calculations.witness_yoga_parity import build_witness_yoga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_yoga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_yoga_parity_command_writes_json_and_markdown_without_unsafe_words(tmp_path):
    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "yoga-parity.json"
    markdown = tmp_path / "yoga-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_yoga_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-yoga-parity-report-v1"
    assert "Yoga Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered
    assert "witness_sources" in serialized


def test_yoga_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_yoga_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_yoga_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/yoga-parity-report.json")
