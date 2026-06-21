from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _snapshot(*, mismatch: bool = False, optional_unknown: bool = False) -> dict:
    payload = {
        "schemaVersion": "transit-coordinate-snapshot.v1",
        "methodId": "transit.coordinates.swiss_lahiri.v1",
        "methodVersion": "1",
        "calculationPreset": "drik_siddhanta",
        "ayanamshaId": "lahiri",
        "nodeType": "true",
        "timezone": "Asia/Yekaterinburg",
        "localDateTime": "2026-06-21T15:00:00+05:00",
        "utcDateTime": "2026-06-21T10:00:00+00:00",
        "location": {"latitude": 53.6304, "longitude": 55.9502},
        "lagna": {
            "body": "Lagna",
            "longitude": 10.0,
            "rashi": "Mesha",
            "rashiIndex": 1,
            "nakshatra": "Ashwini",
            "nakshatraIndex": 1,
            "pada": 4,
        },
        "grahas": [
            {
                "body": "Sun",
                "longitude": 72.5 if not mismatch else 72.502,
                "rashi": "Mithuna" if not mismatch else "Karka",
                "rashiIndex": 3 if not mismatch else 4,
                "nakshatra": "Mrigashira" if not mismatch else "Ardra",
                "nakshatraIndex": 5 if not mismatch else 6,
                "pada": 3,
            },
            {
                "body": "Moon",
                "longitude": 181.25,
                "rashi": "Tula",
                "rashiIndex": 7,
                "nakshatra": "Chitra",
                "nakshatraIndex": 14,
                "pada": 2,
            },
        ],
    }
    if optional_unknown:
        payload["experimental_layer"] = {"note": "skip me"}
    return payload


def _manual_transits():
    return {
        "transits": {
            "timezone": "Asia/Yekaterinburg",
            "ayanamshaId": "lahiri",
            "nodeType": "true",
            "lagna": {
                "longitude": 10.0,
                "rashi": "Aries",
                "rashiIndex": 1,
                "nakshatra": "Ashwini",
                "nakshatraIndex": 1,
                "pada": 4,
            },
            "grahas": [
                {
                    "body": "SU",
                    "longitude": 72.5,
                    "rashi": "Gemini",
                    "rashiIndex": 3,
                    "nakshatra": "Mrigashira",
                    "nakshatraIndex": 5,
                    "pada": 3,
                }
            ],
        }
    }


def _chart_snapshot(*, missing: bool = False):
    if missing:
        return {}
    return {"transit_coordinate_snapshot": _snapshot()}


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected=None,
    chart_snapshot=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"transit_coordinates": _snapshot()},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_snapshot if chart_snapshot is not None else _chart_snapshot()),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_values=None,
    chart_snapshot=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_transits(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_snapshot if chart_snapshot is not None else _chart_snapshot()),
        encoding="utf-8",
    )
    return case_dir


def test_transit_coordinate_parity_passes_matching_jhora_rows(tmp_path):
    from apps.calculations.witness_transit_coordinates_parity import build_witness_transit_coordinates_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_transit_coordinates_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-transit-coordinate-parity-report-v1"
    assert report["metadata"]["tolerance_profile"]["longitude_arcseconds"] == 1.0
    assert row["comparison_status"] == "passed"
    assert "transit_lagna" in row["checked_layers"]
    assert "transit_graha_longitudes" in row["checked_layers"]
    assert row["matched_bodies"] == ["chandra", "lagna", "surya"]
    assert report["layer_summary"]["transit_graha_longitudes"]["passed"] == 1
    assert report["body_summary"]["surya"]["passed"] == 1


def test_transit_coordinate_parity_passes_matching_pl_manual_rows_after_normalization(tmp_path):
    from apps.calculations.witness_transit_coordinates_parity import build_witness_transit_coordinates_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_transit_coordinates_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert row["checked_bodies"] == ["lagna", "surya"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_transit_coordinate_parity_fails_wrong_longitude_rashi_and_nakshatra(tmp_path):
    from apps.calculations.witness_transit_coordinates_parity import build_witness_transit_coordinates_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"transit_coordinates": _snapshot(mismatch=True)},
    )

    row = next(
        item
        for item in build_witness_transit_coordinates_parity_report(
            witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7"
        )["cases"]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert row["failed_bodies"] == ["surya"]
    assert "transit_graha_longitudes.surya.longitude" in row["failed_fields"]
    assert "transit_graha_rashi.surya.rashi" in row["failed_fields"]
    assert "transit_graha_nakshatra.surya.nakshatra" in row["failed_fields"]


def test_transit_coordinate_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_transit_coordinates_parity import build_witness_transit_coordinates_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_snapshot=_chart_snapshot(missing=True),
    )

    report = build_witness_transit_coordinates_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.transit_coordinates" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.transit_coordinates" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_transit_coordinate_unknown_optional_layer_is_skipped_without_demoting_case(tmp_path):
    from apps.calculations.witness_transit_coordinates_parity import build_witness_transit_coordinates_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"transit_coordinates": _snapshot(optional_unknown=True)},
    )

    report = build_witness_transit_coordinates_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "transit_coordinates.experimental_layer" in row["skipped_fields"]
    assert report["body_summary"]["experimental_layer"]["skipped"] == 1


def test_transit_coordinate_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_transit_coordinates_parity import build_witness_transit_coordinates_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_transit_coordinates_parity_report(
            witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7"
        )["cases"]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_transit_coordinate_parity_command_writes_json_and_markdown_without_unsafe_words(tmp_path):
    _write_jhora_case(tmp_path / "witness", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "transit-coordinate-parity.json"
    markdown = tmp_path / "transit-coordinate-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_transit_coordinates_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-transit-coordinate-parity-report-v1"
    assert "Transit Coordinate Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_transit_coordinate_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_transit_coordinates_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_transit_coordinates_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/transit-coordinate-parity-report.json")


def test_transit_coordinate_parity_stage_does_not_change_formula_files():
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
    }

    assert not (formula_files & set(changed))
