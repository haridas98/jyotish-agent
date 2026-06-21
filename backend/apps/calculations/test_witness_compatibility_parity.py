from __future__ import annotations

import json
import subprocess
from io import StringIO

from django.core.management import call_command


KUTAS = (
    ("varna", 1.0, 1.0, "matched"),
    ("vashya", 2.0, 2.0, "matched"),
    ("tara", 3.0, 3.0, "matched"),
    ("yoni", 4.0, 4.0, "matched"),
    ("graha_maitri", 5.0, 5.0, "matched"),
    ("gana", 6.0, 6.0, "matched"),
    ("bhakoot", 7.0, 7.0, "matched"),
    ("nadi", 8.0, 8.0, "matched"),
)


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _compatibility_payload(*, mismatch: bool = False, optional_unknown: bool = False) -> dict:
    kuta = {
        key: {
            "score": (0.0 if mismatch and key == "tara" else score),
            "max_score": max_score,
            "status": ("mismatch" if mismatch and key == "tara" else status),
        }
        for key, score, max_score, status in KUTAS
    }
    total = round(sum(float(item["score"]) for item in kuta.values()), 2)
    payload = {
        "score": {"total": 30.0 if mismatch else total, "max": 36.0, "percent": round(total / 36.0 * 100, 2)},
        "kuta": kuta,
        "moon": {
            "person_a": {"rashi": "Mesha", "nakshatra": "Ashwini", "pada": 1},
            "person_b": {"rashi": "Simha", "nakshatra": "Magha", "pada": 2},
            "rashi_distance_a_to_b": 5,
            "rashi_distance_b_to_a": 9,
        },
        "relationship_context": {"role": "partner", "label": "partner"},
    }
    if optional_unknown:
        payload["experimental_note"] = {"score": 99}
    return payload


def _manual_ashtakuta() -> dict:
    return {
        "ashtakuta": {
            "total_score": 36,
            "max_score": 36,
            "kutas": [
                {"name": "Varna", "score": 1, "max": 1, "status": "matched"},
                {"name": "Vashya", "score": 2, "max": 2, "status": "matched"},
                {"name": "Tara", "score": 3, "max": 3, "status": "matched"},
                {"name": "Yoni", "score": 4, "max": 4, "status": "matched"},
                {"name": "Graha Maitri", "score": 5, "max": 5, "status": "matched"},
                {"name": "Gana", "score": 6, "max": 6, "status": "matched"},
                {"name": "Bhakoot", "score": 7, "max": 7, "status": "matched"},
                {"name": "Nadi", "score": 8, "max": 8, "status": "matched"},
            ],
            "moon_pair": {
                "person_a": {"rashi": "Aries", "nakshatra": "Ashwini", "pada": 1},
                "person_b": {"rashi": "Leo", "nakshatra": "Magha", "pada": 2},
                "distance": 5,
            },
        }
    }


def _chart_payload(*, missing: bool = False) -> dict:
    if missing:
        return {}
    return {"compatibility_report": _compatibility_payload()}


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
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else {"compatibility": _compatibility_payload()},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else _chart_payload()),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_values=None,
    chart_payload=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": manual_values if manual_values is not None else _manual_ashtakuta(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(chart_payload if chart_payload is not None else _chart_payload()),
        encoding="utf-8",
    )
    return case_dir


def test_compatibility_parity_passes_total_score_and_all_kutas(tmp_path):
    from apps.calculations.witness_compatibility_parity import build_witness_compatibility_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_compatibility_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-compatibility-parity-report-v1"
    assert row["comparison_status"] == "passed"
    assert row["checked_layers"] == ["ashtakuta_total", "kuta_breakdown", "moon_pair", "relationship_context"]
    assert row["matched_kutas"] == ["bhakoot", "gana", "graha_maitri", "nadi", "tara", "varna", "vashya", "yoni"]
    assert report["summary"]["passed_count"] == 1
    assert report["kuta_summary"]["tara"]["passed"] == 1


def test_compatibility_parity_fails_wrong_total_and_kuta(tmp_path):
    from apps.calculations.witness_compatibility_parity import build_witness_compatibility_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"compatibility": _compatibility_payload(mismatch=True)},
    )

    row = next(
        item
        for item in build_witness_compatibility_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert row["failed_kutas"] == ["tara"]
    assert "ashtakuta_total.total" in row["failed_fields"]
    assert "kuta_breakdown.tara.score" in row["failed_fields"]


def test_compatibility_parity_passes_pl_manual_normalized_ashtakuta(tmp_path):
    from apps.calculations.witness_compatibility_parity import build_witness_compatibility_parity_report

    _write_pl_case(tmp_path / "pl7", "sterlitamak-1998-04-30-1345")

    report = build_witness_compatibility_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert report["summary"]["comparable_count"] == 1
    assert report["layer_summary"]["kuta_breakdown"]["passed"] == 1


def test_compatibility_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_compatibility_parity import build_witness_compatibility_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_payload=_chart_payload(missing=True),
    )

    report = build_witness_compatibility_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.compatibility" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.compatibility" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_compatibility_parity_skips_unknown_optional_fields_without_demoting_case(tmp_path):
    from apps.calculations.witness_compatibility_parity import build_witness_compatibility_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected={"compatibility": _compatibility_payload(optional_unknown=True)},
    )

    report = build_witness_compatibility_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert row["comparison_status"] == "passed"
    assert "compatibility.experimental_note" in row["skipped_fields"]
    assert report["kuta_summary"]["experimental_note"]["skipped"] == 1


def test_compatibility_parity_compares_moon_pair_fields(tmp_path):
    from apps.calculations.witness_compatibility_parity import build_witness_compatibility_parity_report

    expected = _compatibility_payload()
    expected["moon"]["person_b"]["pada"] = 3
    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected={"ashtakuta": expected})

    row = next(
        item
        for item in build_witness_compatibility_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "moon_pair.person_b.pada" in row["failed_fields"]


def test_compatibility_parity_unreviewed_case_is_not_counted_as_passed(tmp_path):
    from apps.calculations.witness_compatibility_parity import build_witness_compatibility_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_compatibility_parity_report(witness_dir=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_compatibility_parity_command_writes_json_markdown_and_safe_json_stdout(tmp_path):
    _write_jhora_case(tmp_path / "witness", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "compatibility-parity.json"
    markdown = tmp_path / "compatibility-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_compatibility_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-compatibility-parity-report-v1"
    assert "Compatibility Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered


def test_compatibility_parity_command_default_output_path_matches_contract():
    from apps.calculations.management.commands.build_witness_compatibility_parity_report import Command

    parser = Command().create_parser("manage.py", "build_witness_compatibility_parity_report")
    options = parser.parse_args([])
    normalized = str(options.output).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/compatibility-parity-report.json")


def test_compatibility_parity_stage_does_not_change_formula_or_workflow_files():
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
        "backend/apps/calculations/workflows.py",
    }

    assert not (formula_files & set(changed))
