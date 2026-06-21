from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _expected_argala(*, mismatch: bool = False, body_mismatch: bool = False, optional_unknown: bool = False):
    value = {
        "pairs": [
            {
                "level": "primary",
                "argala_house": 2,
                "obstruction_house": 12,
                "argala_bodies": ["Sun", "Mars"],
                "obstruction_bodies": ["Saturn"],
                "net_effect": "active" if not mismatch else "obstructed",
            },
            {
                "level": "secondary",
                "argala_house": 5,
                "obstruction_house": 9,
                "argala_bodies": ["Jupiter"],
                "obstruction_bodies": [],
                "net_effect": "active",
            },
        ],
        "primary": [{"house": 2, "bodies": ["Sun", "Mars"]}],
        "obstruction": [{"house": 12, "bodies": ["Saturn" if not body_mismatch else "Moon"]}],
        "secondary": [{"house": 5, "bodies": ["Jupiter"]}],
        "secondary_obstruction": [{"house": 9, "bodies": []}],
    }
    if optional_unknown:
        value["experimental_note"] = {"text": "operator note"}
    return value


def _manual_argala():
    return {
        "argala": {
            "pairs": [
                {
                    "level": "primary",
                    "argala_house": 2,
                    "obstruction_house": 12,
                    "argala_bodies": ["MA", "SU"],
                    "obstruction_bodies": ["SA"],
                    "net_effect": "active",
                }
            ],
            "primary": [{"house": 2, "bodies": ["Mangala", "Surya"]}],
            "obstruction": [{"house": 12, "bodies": ["Shani"]}],
        }
    }


def _chart_argala(*, missing: bool = False):
    if missing:
        return {}
    return {
        "argala": {
            "pairs": [
                {
                    "level": "primary",
                    "argala_house": 2,
                    "obstruction_house": 12,
                    "argala_bodies": ["Surya", "Mangala"],
                    "obstruction_bodies": ["Shani"],
                    "net_effect": "active",
                },
                {
                    "level": "secondary",
                    "argala_house": 5,
                    "obstruction_house": 9,
                    "argala_bodies": ["Guru"],
                    "obstruction_bodies": [],
                    "net_effect": "active",
                },
            ],
            "primary": [{"house": 2, "bodies": ["Surya", "Mangala"]}],
            "obstruction": [{"house": 12, "bodies": ["Shani"]}],
            "secondary": [{"house": 5, "bodies": ["Guru"]}],
            "secondary_obstruction": [{"house": 9, "bodies": []}],
        }
    }


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected=None,
    jhora_expected=None,
    chart_argala=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"argala": _expected_argala()},
    }
    if jhora_expected is not None:
        fixture["jhora_expected"] = jhora_expected
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_argala if chart_argala is not None else _chart_argala()}),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_values=None,
    chart_argala=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_argala(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"classical": chart_argala if chart_argala is not None else _chart_argala()}),
        encoding="utf-8",
    )
    return case_dir


def test_argala_parity_passes_matching_jhora_expected_rows(tmp_path):
    from apps.calculations.witness_argala_parity import build_witness_argala_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_argala_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-argala-parity-report-v1"
    assert row["comparison_status"] == "passed"
    assert row["checked_layers"] == ["argala_pairs", "argala_rows"]
    assert report["layer_summary"]["argala_pairs"]["passed"] == 1
    assert report["layer_summary"]["argala_rows"]["passed"] == 1
    assert report["argala_summary"]["pairs"]["passed"] == 1
    assert report["argala_summary"]["primary"]["passed"] == 1


def test_argala_parity_supports_jhora_expected_export_shape(tmp_path):
    from apps.calculations.witness_argala_parity import build_witness_argala_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={},
        jhora_expected={"argala": _expected_argala()},
    )

    row = next(
        item
        for item in build_witness_argala_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "passed"
    assert "argala_pairs.primary.2.net_effect" in row["checked_fields"]


def test_argala_parity_passes_matching_pl_manual_rows_after_body_normalization(tmp_path):
    from apps.calculations.witness_argala_parity import build_witness_argala_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_argala_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_argala_parity_fails_structural_net_effect_and_body_mismatches(tmp_path):
    from apps.calculations.witness_argala_parity import build_witness_argala_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"argala": _expected_argala(mismatch=True, body_mismatch=True)},
    )

    row = next(
        item
        for item in build_witness_argala_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "argala_pairs.primary.2.net_effect" in row["failed_fields"]
    assert "argala_rows.obstruction.12.bodies" in row["failed_fields"]


def test_argala_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_argala_parity import build_witness_argala_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_argala=_chart_argala(missing=True),
    )

    report = build_witness_argala_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.argala" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.argala" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_argala_parity_unknown_optional_field_is_skipped_without_demoting_case(tmp_path):
    from apps.calculations.witness_argala_parity import build_witness_argala_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"argala": _expected_argala(optional_unknown=True)},
    )

    report = build_witness_argala_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "argala.experimental_note" in row["skipped_fields"]
    assert report["argala_summary"]["experimental_note"]["skipped"] == 1


def test_argala_parity_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_argala_parity import build_witness_argala_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_argala_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_argala_parity_command_writes_json_and_markdown_without_unsafe_words(tmp_path):
    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "argala-parity.json"
    markdown = tmp_path / "argala-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_argala_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-argala-parity-report-v1"
    assert "Argala Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_argala_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_argala_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_argala_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/argala-parity-report.json")


def test_argala_parity_stage_does_not_change_formula_files():
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
