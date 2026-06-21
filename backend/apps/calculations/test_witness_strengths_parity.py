from __future__ import annotations

import json
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _expected_strengths(*, vimshopaka_mismatch: bool = False, shadbala_mismatch: bool = False, partial: bool = False):
    if partial:
        return {"vimsopaka": {"Sun": {"shad_varga": {"score": 12.5}}}}
    return {
        "vimsopaka": {
            "Sun": {
                "shad_varga": {"score": 12.52 if vimshopaka_mismatch else 12.5},
                "sapta_varga": {"score": 13.25},
                "dasa_varga": {"score": 14.0},
                "shodasa_varga": {"score": 15.0},
            },
            "Moon": {"shad_varga": {"score": 11.0}},
        },
        "shadbala": {
            "Sun": {"shadbala": 181.02 if shadbala_mismatch else 181.0},
            "Moon": {"rupas": 3.0},
        },
    }


def _chart_strengths(*, missing: bool = False, partial: bool = False):
    if missing:
        return {}
    if partial:
        return {
            "vimshopaka_bala": {
                "items": [{"body": "Surya", "scheme_scores": {"shadvarga": 12.5}}]
            }
        }
    return {
        "vimshopaka_bala": {
            "items": [
                {
                    "body": "Surya",
                    "scheme_scores": {
                        "shadvarga": 12.5,
                        "saptavarga": 13.25,
                        "dashavarga": 14.0,
                        "shodasha": 15.0,
                    },
                },
                {"body": "Chandra", "scheme_scores": {"shadvarga": 11.0}},
            ]
        },
        "shadbala": {
            "items": [
                {"body": "Surya", "known_total": 181.0, "rupas": 3.02},
                {"body": "Chandra", "known_total": 180.0, "rupas": 3.0},
            ]
        },
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected_strengths=None,
    chart_strengths=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected_strengths if expected_strengths is not None else _expected_strengths(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_strengths if chart_strengths is not None else _chart_strengths()}),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_strengths=None,
    chart_strengths=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_strengths if manual_strengths is not None else _expected_strengths(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_strengths if chart_strengths is not None else _chart_strengths()}),
        encoding="utf-8",
    )
    return case_dir


def test_strengths_parity_report_passes_reviewed_matching_vimshopaka(tmp_path):
    from apps.calculations.witness_strengths_parity import build_witness_strengths_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected_strengths={"vimsopaka": _expected_strengths()["vimsopaka"]})

    report = build_witness_strengths_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-strengths-parity-report-v1"
    assert report["metadata"]["layers"] == ["vimshopaka", "shadbala"]
    assert row["comparison_status"] == "passed"
    assert "vimshopaka" in row["checked_layers"]
    assert report["layer_summary"]["vimshopaka"]["passed"] == 1
    assert report["body_summary"]["Surya"]["passed"] == 1


def test_strengths_parity_report_passes_reviewed_matching_shadbala_virupas(tmp_path):
    from apps.calculations.witness_strengths_parity import build_witness_strengths_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected_strengths={"shadbala": _expected_strengths()["shadbala"]})

    report = build_witness_strengths_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "shadbala" in row["checked_layers"]
    assert report["metadata"]["profile_sensitive_layers"] == ["shadbala"]
    assert report["layer_summary"]["shadbala"]["passed"] == 1


def test_strengths_parity_report_records_vimshopaka_mismatch(tmp_path):
    from apps.calculations.witness_strengths_parity import build_witness_strengths_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_strengths=_expected_strengths(vimshopaka_mismatch=True),
    )

    row = next(
        item
        for item in build_witness_strengths_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "vimshopaka.Surya.shadvarga" in row["failed_fields"]
    assert "vimshopaka" in row["failed_layers"]


def test_strengths_parity_report_records_shadbala_mismatch_as_profile_sensitive_diff(tmp_path):
    from apps.calculations.witness_strengths_parity import build_witness_strengths_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_strengths=_expected_strengths(shadbala_mismatch=True),
    )

    report = build_witness_strengths_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "failed"
    assert "shadbala.Surya.total_virupas" in row["failed_fields"]
    assert "shadbala" in row["failed_layers"]
    assert "shadbala" in report["metadata"]["profile_sensitive_layers"]


def test_strengths_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_strengths_parity import build_witness_strengths_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected_strengths={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_strengths=_chart_strengths(missing=True),
    )

    report = build_witness_strengths_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.strengths" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.strengths" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_strengths_parity_partial_comparable_field_still_passes_case(tmp_path):
    from apps.calculations.witness_strengths_parity import build_witness_strengths_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_strengths=_expected_strengths(partial=True),
        chart_strengths=_chart_strengths(partial=True),
    )

    report = build_witness_strengths_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["checked_fields"] == ["vimshopaka.Surya.shadvarga"]
    assert "jhora.shadbala" in row["missing_fields"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_strengths_parity_report_keeps_unreviewed_case_out_of_passed(tmp_path):
    from apps.calculations.witness_strengths_parity import build_witness_strengths_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_strengths_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_strengths_parity_command_writes_json_and_markdown_without_unsafe_authority(tmp_path):
    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "strengths-parity.json"
    markdown = tmp_path / "strengths-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_strengths_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-strengths-parity-report-v1"
    assert "Strengths Parity Report" in markdown_text
    assert "profile-sensitive" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered
    assert "witness_sources" in serialized


def test_strengths_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_strengths_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_strengths_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/strengths-parity-report.json")
