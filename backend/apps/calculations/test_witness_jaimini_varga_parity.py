from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


DEFAULT_EXPECTED = {
    "D5": {"Surya": "Mesha", "Chandra": "Vrishabha"},
    "D6": {"placements": [{"body": "Surya", "rashi": "Mithuna"}, {"body": "Lagna", "rashi": "Karka"}]},
    "D8": [{"body": "Mangala", "rashi": "Simha"}],
    "D11": {"placements": [{"body": "Guru", "rashi": "Kanya"}]},
}


def _actual_vargas(*, mismatch: bool = False) -> dict[str, object]:
    d5_surya = "Tula" if mismatch else "Aries"
    d11_guru = "Mesha" if mismatch else "Virgo"
    return {
        "vargas": {
            "D5": {
                "placements": [
                    {"body": "Sun", "rashi": d5_surya},
                    {"body": "Moon", "rashi": "Taurus"},
                ]
            },
            "D6": {
                "placements": [
                    {"body": "Surya", "rashi": "Gemini"},
                    {"body": "Ascendant", "rashi": "Cancer"},
                ]
            },
            "D8": {"placements": [{"body": "Mars", "rashi": "Leo"}]},
            "D11": {"placements": [{"body": "Jupiter", "rashi": d11_guru}]},
        }
    }


def _write_jhora_case(root, case_id: str, *, expected=None, chart_payload=None, review_status="jhora_verified"):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"jaimini_vargas": DEFAULT_EXPECTED},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else _actual_vargas()),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(root, case_id: str, *, manual_values=None, chart_payload=None, review_status="reviewed"):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else {"vargas": DEFAULT_EXPECTED},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else _actual_vargas()),
        encoding="utf-8",
    )
    return case_dir


def test_jaimini_varga_parity_passes_when_expected_and_actual_d5_d6_d8_d11_exist(tmp_path):
    from apps.calculations.witness_jaimini_varga_parity import build_witness_jaimini_varga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_jaimini_varga_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-jaimini-varga-parity-report-v1"
    assert report["metadata"]["varga_codes"] == ["D5", "D6", "D8", "D11"]
    assert row["comparison_status"] == "passed"
    assert row["checked_vargas"] == ["D5", "D6", "D8", "D11"]
    assert report["summary"]["passed_count"] == 1
    assert report["varga_summary"]["D5"]["passed"] == 1
    assert report["field_summary"]["D5.Surya.rashi"]["passed"] == 1
    assert report["readiness_summary"]["D5"]["compared"] == 1


def test_jaimini_varga_parity_fails_wrong_d5_and_d11_placements(tmp_path):
    from apps.calculations.witness_jaimini_varga_parity import build_witness_jaimini_varga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", chart_payload=_actual_vargas(mismatch=True))

    report = build_witness_jaimini_varga_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "failed"
    assert row["failed_vargas"] == ["D5", "D11"]
    assert "D5.Surya.rashi" in row["failed_fields"]
    assert "D11.Guru.rashi" in row["failed_fields"]
    assert report["varga_summary"]["D5"]["failed"] == 1


def test_jaimini_varga_parity_accepts_row_and_mapping_forms(tmp_path):
    from apps.calculations.witness_jaimini_varga_parity import build_witness_jaimini_varga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"varga_rows": [{"varga": "d5", "body": "Sun", "rashi": "Aries"}]},
        chart_payload={"varga_rows": [{"varga": "D5", "body": "Surya", "rashi": "Mesha"}]},
    )
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        expected={"divisional_charts": {"D6": {"Surya": {"rashi_index": 2}}}},
        chart_payload={"divisional_charts": {"D6": {"placements": [{"body": "Sun", "rashi_index": 2}]}}},
    )

    report = build_witness_jaimini_varga_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "passed"
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "passed"
    assert report["summary"]["passed_count"] == 2


def test_jaimini_varga_parity_passes_pl_manual_normalized_rows(tmp_path):
    from apps.calculations.witness_jaimini_varga_parity import build_witness_jaimini_varga_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_jaimini_varga_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert report["summary"]["comparable_count"] == 1
    assert report["varga_summary"]["D11"]["passed"] == 1


def test_jaimini_varga_parity_missing_witness_and_actual_gap_are_not_formula_failures(tmp_path):
    from apps.calculations.witness_jaimini_varga_parity import build_witness_jaimini_varga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(tmp_path / "jhora", "mayapur-2001-02-03-0910", chart_payload={"vargas": {"D9": {}}})

    report = build_witness_jaimini_varga_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing_witness"
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.vargas.D5" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["readiness_summary"]["D5"]["actual_missing"] == 1
    assert report["summary"]["failed_count"] == 0


def test_jaimini_varga_parity_skips_unknown_optional_fields_without_demoting_case(tmp_path):
    from apps.calculations.witness_jaimini_varga_parity import build_witness_jaimini_varga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"jaimini_vargas": {"D5": {"placements": [{"body": "Surya", "rashi": "Mesha"}], "experimental_note": "x"}}},
        chart_payload={"vargas": {"D5": {"placements": [{"body": "Sun", "rashi": "Aries"}]}}},
    )

    report = build_witness_jaimini_varga_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "D5.experimental_note" in row["skipped_fields"]
    assert report["field_summary"]["experimental_note"]["skipped"] == 1


def test_jaimini_varga_parity_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_jaimini_varga_parity import build_witness_jaimini_varga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_jaimini_varga_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_jaimini_varga_parity_command_writes_json_markdown_and_safe_json_stdout(tmp_path):
    _write_jhora_case(tmp_path / "witness", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "jaimini-varga-parity.json"
    markdown = tmp_path / "jaimini-varga-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_jaimini_varga_parity_report",
        "--witness-dir",
        str(tmp_path / "witness"),
        "--output",
        str(output),
        "--markdown-output",
        str(markdown),
        "--varga-codes",
        "d5,d11",
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    markdown_text = markdown.read_text(encoding="utf-8")
    serialized = json.dumps(payload, ensure_ascii=False) + markdown_text
    report = json.loads(output.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "jyotish-jaimini-varga-parity-report-v1"
    assert payload["summary"]["passed_count"] == 1
    assert "cases" not in payload
    assert "field_results" not in serialized
    assert report["metadata"]["varga_codes"] == ["D5", "D11"]
    assert "Jaimini Varga Parity Gap Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_jaimini_varga_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_jaimini_varga_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_jaimini_varga_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/jaimini-varga-parity-report.json")


def test_jaimini_varga_parity_stage_does_not_change_formula_workflow_api_frontend_summary_settings_or_existing_reports():
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
        "backend/apps/calculations/views.py",
        "backend/apps/calculations/witness_summary.py",
        "backend/config/settings.py",
        "backend/apps/calculations/witness_jaimini_karaka_parity.py",
        "frontend/src/app/page.tsx",
        "frontend/src/lib/api.ts",
        "frontend/package.json",
    }

    assert not (forbidden_files & set(changed))
