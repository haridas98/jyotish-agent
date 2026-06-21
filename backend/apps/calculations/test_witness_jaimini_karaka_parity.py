from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


ASSIGNMENTS = {
    "AK": "Surya",
    "AmK": "Chandra",
    "BK": "Mangala",
    "MK": "Budha",
    "PiK": "Guru",
    "GK": "Shukra",
    "DK": "Shani",
}


def _ranking_rows(*, mismatch: bool = False) -> list[dict[str, object]]:
    return [
        {"body": "Surya", "chara_karaka": "AK", "degree_within_sign": 29.1 if not mismatch else 28.0, "rashi": "Mesha", "nakshatra": "Ashwini", "pada": 1},
        {"body": "Chandra", "chara_karaka": "AmK", "degree_within_sign": 25.0, "rashi": "Vrishabha", "nakshatra": "Rohini", "pada": 2},
        {"body": "Mangala", "chara_karaka": "BK", "degree_within_sign": 21.0, "rashi": "Mithuna", "nakshatra": "Mrigashira", "pada": 3},
        {"body": "Budha", "chara_karaka": "MK", "degree_within_sign": 18.0, "rashi": "Karka", "nakshatra": "Pushya", "pada": 4},
        {"body": "Guru", "chara_karaka": "PiK", "degree_within_sign": 14.0, "rashi": "Simha", "nakshatra": "Magha", "pada": 1},
        {"body": "Shukra", "chara_karaka": "GK", "degree_within_sign": 9.0, "rashi": "Kanya", "nakshatra": "Hasta", "pada": 2},
        {"body": "Shani", "chara_karaka": "DK", "degree_within_sign": 4.0, "rashi": "Tula", "nakshatra": "Swati", "pada": 3},
    ]


def _karaka_payload(*, mismatch: bool = False, optional_unknown: bool = False) -> dict[str, object]:
    assignments = dict(ASSIGNMENTS)
    if mismatch:
        assignments.update({"AK": "Chandra", "AmK": "Surya", "DK": "Guru"})
    payload: dict[str, object] = {
        "scheme": "seven-karaka",
        "assignments": assignments,
        "graha_rows": _ranking_rows(mismatch=mismatch),
        "review_gates": {
            "required_factors": ["karaka_scheme", "karaka_assignments", "ranking_inputs"],
            "public_interpretation_status": "blocked_until_jaimini_review",
        },
    }
    if optional_unknown:
        payload["experimental_jaimini_note"] = "operator note"
    return payload


def _row_form_payload() -> dict[str, object]:
    return {
        "scheme": "7 karaka",
        "rows": [{"karaka": role, "body": body} for role, body in ASSIGNMENTS.items()],
    }


def _manual_payload() -> dict[str, object]:
    return {
        "jaimini_karakas": {
            "profile": "seven karaka",
            "karaka_rows": [{"name": body, "chara_karaka": role} for role, body in ASSIGNMENTS.items()],
        }
    }


def _derived_graha_chart() -> dict[str, object]:
    longitudes = {
        "Surya": 29.1,
        "Chandra": 55.0,
        "Mangala": 81.0,
        "Budha": 108.0,
        "Guru": 134.0,
        "Shukra": 159.0,
        "Shani": 184.0,
    }
    return {
        "grahas": [
            {
                "body": body,
                "longitude": longitude,
                "rashi": rashi,
                "nakshatra": nakshatra,
                "pada": pada,
            }
            for (body, longitude), rashi, nakshatra, pada in zip(
                longitudes.items(),
                ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya", "Tula"],
                ["Ashwini", "Rohini", "Mrigashira", "Pushya", "Magha", "Hasta", "Swati"],
                [1, 2, 3, 4, 1, 2, 3],
            )
        ]
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected=None,
    chart_payload=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"chara_karakas": _karaka_payload()},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    if chart_payload is not None:
        (case_dir / "jyotish-agent-chart.json").write_text(json.dumps(chart_payload), encoding="utf-8")
    else:
        (case_dir / "jyotish-agent-chart.json").write_text(
            json.dumps({"chara_karakas": _karaka_payload()}),
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
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_payload(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else {"jaimini_karakas": _karaka_payload()}),
        encoding="utf-8",
    )
    return case_dir


def test_jaimini_karaka_parity_passes_assignments_and_ranking_inputs(tmp_path):
    from apps.calculations.witness_jaimini_karaka_parity import build_witness_jaimini_karaka_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_jaimini_karaka_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-jaimini-karaka-parity-report-v1"
    assert row["comparison_status"] == "passed"
    assert "karaka_assignments" in row["checked_layers"]
    assert "ranking_inputs" in row["checked_layers"]
    assert report["summary"]["passed_count"] == 1
    assert report["field_summary"]["assignment.AK"]["passed"] == 1
    assert report["field_summary"]["graha.Surya.degree_within_sign"]["passed"] == 1


def test_jaimini_karaka_parity_fails_wrong_assignments_and_ranking_input(tmp_path):
    from apps.calculations.witness_jaimini_karaka_parity import build_witness_jaimini_karaka_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"jaimini": _karaka_payload(mismatch=True)},
    )

    row = next(
        item
        for item in build_witness_jaimini_karaka_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "assignment.AK" in row["failed_fields"]
    assert "assignment.AmK" in row["failed_fields"]
    assert "assignment.DK" in row["failed_fields"]
    assert "graha.Surya.degree_within_sign" in row["failed_fields"]


def test_jaimini_karaka_parity_accepts_row_and_mapping_forms(tmp_path):
    from apps.calculations.witness_jaimini_karaka_parity import build_witness_jaimini_karaka_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={"karaka_rows": _row_form_payload()["rows"]})
    _write_jhora_case(tmp_path / "jhora", "mayapur-2001-02-03-0910", expected={"karakas": ASSIGNMENTS})

    report = build_witness_jaimini_karaka_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "passed"
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "passed"
    assert report["summary"]["passed_count"] == 2


def test_jaimini_karaka_parity_passes_pl_manual_normalized_rows(tmp_path):
    from apps.calculations.witness_jaimini_karaka_parity import build_witness_jaimini_karaka_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_jaimini_karaka_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert report["summary"]["comparable_count"] == 1
    assert report["layer_summary"]["karaka_assignments"]["passed"] == 1


def test_jaimini_karaka_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_jaimini_karaka_parity import build_witness_jaimini_karaka_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(tmp_path / "jhora", "mayapur-2001-02-03-0910", chart_payload={})

    report = build_witness_jaimini_karaka_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing_witness"
    assert "jhora.jaimini_karakas" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.jaimini_karakas" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_jaimini_karaka_parity_skips_unknown_optional_fields_without_demoting_case(tmp_path):
    from apps.calculations.witness_jaimini_karaka_parity import build_witness_jaimini_karaka_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"jaimini_karakas": _karaka_payload(optional_unknown=True)},
    )

    report = build_witness_jaimini_karaka_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "jaimini_karakas.experimental_jaimini_note" in row["skipped_fields"]
    assert report["field_summary"]["experimental_jaimini_note"]["skipped"] == 1


def test_jaimini_karaka_parity_derives_actual_from_existing_graha_longitudes(tmp_path):
    from apps.calculations.witness_jaimini_karaka_parity import build_witness_jaimini_karaka_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"chara_karakas": _karaka_payload()},
        chart_payload=_derived_graha_chart(),
    )

    report = build_witness_jaimini_karaka_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "derived_from_existing_graha_longitudes" in row["checked_fields"]


def test_jaimini_karaka_parity_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_jaimini_karaka_parity import build_witness_jaimini_karaka_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_jaimini_karaka_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_jaimini_karaka_parity_command_writes_json_markdown_and_safe_json_stdout(tmp_path):
    _write_jhora_case(tmp_path / "witness", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "jaimini-karaka-parity.json"
    markdown = tmp_path / "jaimini-karaka-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_jaimini_karaka_parity_report",
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

    assert payload["schema_version"] == "jyotish-jaimini-karaka-parity-report-v1"
    assert payload["summary"]["passed_count"] == 1
    assert "cases" not in payload
    assert "field_results" not in serialized
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["schema_version"] == "jyotish-jaimini-karaka-parity-report-v1"
    assert "cases" in report
    assert "Jaimini Karaka Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_jaimini_karaka_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_jaimini_karaka_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_jaimini_karaka_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/jaimini-karaka-parity-report.json")


def test_jaimini_karaka_parity_stage_does_not_change_formula_workflow_or_report_builder_files():
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
        "backend/apps/calculations/witness_jaimini_karaka_parity.py",
        "backend/apps/calculations/witness_prashna_parity.py",
    }

    assert not (forbidden_files & set(changed))
