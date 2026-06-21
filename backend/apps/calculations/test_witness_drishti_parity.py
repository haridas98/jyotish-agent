from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _expected_drishti(*, mismatch: bool = False, optional_unknown: bool = False):
    value = {
        "graha_drishti": [
            {
                "sourceEntityRef": "transit:graha.SA",
                "targetEntityRef": "natal:house.10" if not mismatch else "natal:house.9",
                "aspectKind": "special_10th",
            }
        ],
        "rashi_drishti": [
            {
                "source_sign": "Mesha",
                "target_sign": "Simha",
                "aspect_kind": "movable_to_fixed",
            }
        ],
    }
    if optional_unknown:
        value["tajika_aspects"] = [{"source": "Sun", "target": "Moon", "kind": "sextile"}]
    return value


def _manual_drishti():
    return {
        "drishti": {
            "graha": [
                {
                    "source_entity_ref": "transit:graha.SA",
                    "target_entity_ref": "natal:house.10",
                    "kind": "special 10th",
                }
            ]
        }
    }


def _chart_drishti(*, missing: bool = False):
    if missing:
        return {}
    return {
        "drishti": {
            "graha_drishti": [
                {
                    "sourceEntityRef": "transit:graha.SA",
                    "targetEntityRef": "natal:house.10",
                    "aspectKind": "special_10th",
                }
            ],
            "rashi_drishti": [
                {
                    "source_sign": "Aries",
                    "target_sign": "Leo",
                    "aspect_kind": "movable_to_fixed",
                }
            ],
        }
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected=None,
    chart_drishti=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"drishti": _expected_drishti()},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_drishti if chart_drishti is not None else _chart_drishti()),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_values=None,
    chart_drishti=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_drishti(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_drishti if chart_drishti is not None else _chart_drishti()),
        encoding="utf-8",
    )
    return case_dir


def test_drishti_parity_passes_matching_jhora_graha_drishti_rows(tmp_path):
    from apps.calculations.witness_drishti_parity import build_witness_drishti_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_drishti_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-drishti-parity-report-v1"
    assert report["metadata"]["layers"] == ["graha_drishti", "rashi_drishti"]
    assert row["comparison_status"] == "passed"
    assert "graha_drishti" in row["checked_layers"]
    assert "graha_drishti.transit_graha_sa.natal_house_10.special_10th" in row["matched_aspects"]
    assert report["layer_summary"]["graha_drishti"]["passed"] == 1
    assert report["drishti_summary"]["graha_drishti.special_10th"]["passed"] == 1


def test_drishti_parity_passes_matching_jhora_rashi_drishti_rows(tmp_path):
    from apps.calculations.witness_drishti_parity import build_witness_drishti_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_drishti_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "rashi_drishti" in row["checked_layers"]
    assert "rashi_drishti.mesha.simha.movable_to_fixed" in row["matched_aspects"]
    assert report["drishti_summary"]["rashi_drishti.movable_to_fixed"]["passed"] == 1


def test_drishti_parity_passes_matching_pl_manual_rows_after_normalization(tmp_path):
    from apps.calculations.witness_drishti_parity import build_witness_drishti_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_drishti_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["checked_aspects"] == ["graha_drishti.transit_graha_sa.natal_house_10.special_10th"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_drishti_parity_fails_wrong_target_or_aspect_kind(tmp_path):
    from apps.calculations.witness_drishti_parity import build_witness_drishti_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"drishti": _expected_drishti(mismatch=True)},
    )

    row = next(
        item
        for item in build_witness_drishti_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "graha_drishti.transit_graha_sa.natal_house_9.special_10th" in row["failed_aspects"]
    assert "graha_drishti.transit_graha_sa.natal_house_9.special_10th" in row["failed_fields"]


def test_drishti_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_drishti_parity import build_witness_drishti_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_drishti=_chart_drishti(missing=True),
    )

    report = build_witness_drishti_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.drishti" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.drishti" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_drishti_unknown_optional_layer_is_skipped_without_demoting_case(tmp_path):
    from apps.calculations.witness_drishti_parity import build_witness_drishti_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"drishti": _expected_drishti(optional_unknown=True)},
    )

    report = build_witness_drishti_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "drishti.tajika_aspects" in row["skipped_fields"]
    assert report["drishti_summary"]["tajika_aspects"]["skipped"] == 1


def test_drishti_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_drishti_parity import build_witness_drishti_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_drishti_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_drishti_parity_command_writes_json_and_markdown_without_unsafe_words(tmp_path):
    _write_jhora_case(tmp_path / "witness", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "drishti-parity.json"
    markdown = tmp_path / "drishti-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_drishti_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-drishti-parity-report-v1"
    assert "Drishti Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_drishti_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_drishti_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_drishti_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/drishti-parity-report.json")


def test_drishti_parity_stage_does_not_change_formula_files():
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
    }

    assert not (formula_files & set(changed))
