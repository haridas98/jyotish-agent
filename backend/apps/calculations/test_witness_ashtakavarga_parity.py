from __future__ import annotations

import json
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _expected_ashtakavarga(*, bav_mismatch: bool = False, sav_mismatch: bool = False, partial: bool = False) -> dict[str, object]:
    if partial:
        return {"bhinna": {"Surya": {"Mesha": 3, "Vrishabha": 4}}}
    return {
        "bhinna": {
            "Surya": {"Mesha": 4 if bav_mismatch else 3, "Vrishabha": 4},
            "Chandra": {"Mesha": 2},
        },
        "sarva": {"Mesha": 20, "total": 338 if sav_mismatch else 337},
    }


def _chart_ashtakavarga(*, missing: bool = False, partial: bool = False) -> dict[str, object]:
    if missing:
        return {}
    if partial:
        return {"bhinna": {"Surya": {"scores": [3], "total": 3}}, "sarva": {"scores": [], "total": 0}}
    return {
        "bhinna": {
            "Surya": {"scores": [3, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "total": 7},
            "Chandra": {"scores": [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "total": 2},
        },
        "sarva": {"scores": [20, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "total": 337},
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected_ashtakavarga=None,
    chart_ashtakavarga=None,
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
            "ashtakavarga": expected_ashtakavarga
            if expected_ashtakavarga is not None
            else _expected_ashtakavarga()
        },
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(
            {
                "classical": {
                    "ashtakavarga": chart_ashtakavarga
                    if chart_ashtakavarga is not None
                    else _chart_ashtakavarga()
                }
            }
        ),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_ashtakavarga=None,
    chart_ashtakavarga=None,
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
            "ashtakavarga": manual_ashtakavarga
            if manual_ashtakavarga is not None
            else _expected_ashtakavarga()
        },
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(
            {
                "classical": {
                    "ashtakavarga": chart_ashtakavarga
                    if chart_ashtakavarga is not None
                    else _chart_ashtakavarga()
                }
            }
        ),
        encoding="utf-8",
    )
    return case_dir


def test_ashtakavarga_parity_report_passes_reviewed_matching_bav_and_sav(tmp_path):
    from apps.calculations.witness_ashtakavarga_parity import build_witness_ashtakavarga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_ashtakavarga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-ashtakavarga-parity-report-v1"
    assert report["metadata"]["layers"] == ["bhinna", "sarva"]
    assert row["comparison_status"] == "passed"
    assert row["checked_layers"] == ["bhinna", "sarva"]
    assert row["failed_cells"] == []
    assert report["summary"]["passed_count"] == 1
    assert report["layer_summary"]["bhinna"]["passed"] == 1
    assert report["body_summary"]["Surya"]["passed"] == 1


def test_ashtakavarga_parity_report_records_bav_cell_mismatch(tmp_path):
    from apps.calculations.witness_ashtakavarga_parity import build_witness_ashtakavarga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_ashtakavarga=_expected_ashtakavarga(bav_mismatch=True),
    )

    row = next(
        item
        for item in build_witness_ashtakavarga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "bhinna.Surya.Mesha" in row["failed_cells"]
    assert "bhinna" in row["failed_layers"]


def test_ashtakavarga_parity_report_records_sav_total_mismatch(tmp_path):
    from apps.calculations.witness_ashtakavarga_parity import build_witness_ashtakavarga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_ashtakavarga=_expected_ashtakavarga(sav_mismatch=True),
    )

    row = next(
        item
        for item in build_witness_ashtakavarga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "sarva.total" in row["failed_cells"]
    assert "sarva" in row["failed_layers"]


def test_ashtakavarga_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_ashtakavarga_parity import build_witness_ashtakavarga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected_ashtakavarga={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_ashtakavarga=_chart_ashtakavarga(missing=True),
    )

    report = build_witness_ashtakavarga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.ashtakavarga" in rows["sterlitamak-1998-04-30-1345"]["missing_cells"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.ashtakavarga" in rows["mayapur-2001-02-03-0910"]["missing_cells"]
    assert report["summary"]["failed_count"] == 0


def test_ashtakavarga_parity_partial_comparable_cell_still_passes_case(tmp_path):
    from apps.calculations.witness_ashtakavarga_parity import build_witness_ashtakavarga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_ashtakavarga=_expected_ashtakavarga(partial=True),
        chart_ashtakavarga=_chart_ashtakavarga(partial=True),
    )

    report = build_witness_ashtakavarga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["checked_cells"] == ["bhinna.Surya.Mesha"]
    assert "calculated.bhinna.Surya.Vrishabha" in row["missing_cells"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_ashtakavarga_parity_report_keeps_unreviewed_case_out_of_passed(tmp_path):
    from apps.calculations.witness_ashtakavarga_parity import build_witness_ashtakavarga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_ashtakavarga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_ashtakavarga_parity_command_writes_json_and_markdown_without_unsafe_authority(tmp_path):
    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "ashtakavarga-parity.json"
    markdown = tmp_path / "ashtakavarga-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_ashtakavarga_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-ashtakavarga-parity-report-v1"
    assert "Ashtakavarga Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered
    assert "witness_sources" in serialized


def test_ashtakavarga_parity_command_default_output_path_matches_contract(settings):
    from apps.calculations.management.commands.build_witness_ashtakavarga_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_ashtakavarga_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/ashtakavarga-parity-report.json")
