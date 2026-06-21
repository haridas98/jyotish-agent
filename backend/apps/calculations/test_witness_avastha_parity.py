from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _expected_avasthas(*, mismatch: bool = False, optional_unknown: bool = False):
    value = {
        "baladi": [
            {"body": "Sun", "state": "Bala"},
            {"body": "Moon", "state": "Yuva" if not mismatch else "Mrita"},
        ],
    }
    if optional_unknown:
        value["deepta"] = [{"body": "Mars", "state": "Diptha"}]
    return value


def _manual_avasthas():
    return {
        "avasthas": {
            "baladi": [
                {"body": "SU", "avastha": "bala"},
                {"body": "MO", "key": "yuva"},
            ]
        }
    }


def _chart_avasthas(*, missing: bool = False):
    if missing:
        return {}
    return {
        "avasthas": {
            "baladi": [
                {"body": "Surya", "state": "Bala", "strength": 0.25, "degree_band": "0-6"},
                {"body": "Chandra", "state": "Yuva", "strength": 1.0, "degree_band": "12-18"},
            ]
        }
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected=None,
    chart_avasthas=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"avasthas": _expected_avasthas()},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_avasthas if chart_avasthas is not None else _chart_avasthas()}),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_values=None,
    chart_avasthas=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_avasthas(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_avasthas if chart_avasthas is not None else _chart_avasthas()}),
        encoding="utf-8",
    )
    return case_dir


def test_avastha_parity_passes_matching_jhora_baladi_rows(tmp_path):
    from apps.calculations.witness_avastha_parity import build_witness_avastha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_avastha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-avastha-parity-report-v1"
    assert report["metadata"]["layers"] == ["baladi_avastha"]
    assert row["comparison_status"] == "passed"
    assert row["checked_layers"] == ["baladi_avastha"]
    assert row["matched_bodies"] == ["Chandra", "Surya"]
    assert report["layer_summary"]["baladi_avastha"]["passed"] == 1
    assert report["avastha_summary"]["Surya"]["passed"] == 1


def test_avastha_parity_passes_matching_pl_manual_rows_after_normalization(tmp_path):
    from apps.calculations.witness_avastha_parity import build_witness_avastha_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_avastha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["checked_bodies"] == ["Chandra", "Surya"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_avastha_parity_fails_wrong_avastha_name(tmp_path):
    from apps.calculations.witness_avastha_parity import build_witness_avastha_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"avasthas": _expected_avasthas(mismatch=True)},
    )

    row = next(
        item
        for item in build_witness_avastha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert row["failed_bodies"] == ["Chandra"]
    assert "baladi_avastha.Chandra.state" in row["failed_fields"]


def test_avastha_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_avastha_parity import build_witness_avastha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_avasthas=_chart_avasthas(missing=True),
    )

    report = build_witness_avastha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.avasthas.baladi" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.avasthas.baladi" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_avastha_parity_unknown_optional_layer_is_skipped_without_demoting_case(tmp_path):
    from apps.calculations.witness_avastha_parity import build_witness_avastha_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"avasthas": _expected_avasthas(optional_unknown=True)},
    )

    report = build_witness_avastha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "avasthas.deepta" in row["skipped_fields"]
    assert report["avastha_summary"]["deepta"]["skipped"] == 1


def test_avastha_parity_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_avastha_parity import build_witness_avastha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_avastha_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_avastha_parity_command_writes_json_and_markdown_without_unsafe_words(tmp_path):
    _write_jhora_case(tmp_path / "witness", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "avastha-parity.json"
    markdown = tmp_path / "avastha-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_avastha_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-avastha-parity-report-v1"
    assert "Avastha Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_avastha_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_avastha_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_avastha_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/avastha-parity-report.json")


def test_avastha_parity_stage_does_not_change_formula_files():
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
