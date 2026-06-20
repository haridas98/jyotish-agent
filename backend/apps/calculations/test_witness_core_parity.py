from __future__ import annotations

import json
from io import StringIO

from django.core.management import call_command


BODIES = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]


def _core_point(body: str, longitude: float) -> dict[str, object]:
    return {
        "body": body,
        "longitude": longitude,
        "rashi": "Mesha",
        "rashi_index": 0,
        "nakshatra": "Ashwini",
        "pada": 1,
    }


def _chart(longitudes: dict[str, float] | None = None) -> dict[str, object]:
    values = longitudes or {}
    return {
        "ascendant": _core_point("Lagna", values.get("Lagna", 10.0)),
        "grahas": [_core_point(body, values.get(body, 20.0 + index)) for index, body in enumerate(BODIES)],
    }


def _expected(longitudes: dict[str, float] | None = None) -> dict[str, object]:
    chart = _chart(longitudes)
    return {
        "ascendant": chart["ascendant"],
        "grahas": {row["body"]: row for row in chart["grahas"]},
    }


def _write_jhora_case(root, case_id: str, *, review_status: str = "jhora_verified", expected=None, chart=None):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": expected if expected is not None else _expected(),
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(json.dumps(chart or _chart()), encoding="utf-8")
    return case_dir


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def test_core_parity_report_passes_reviewed_matching_core_fields(tmp_path):
    from apps.calculations.witness_core_parity import build_witness_core_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_core_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-core-parity-report-v1"
    assert row["comparison_status"] == "passed"
    assert row["sources_present"] == ["jhora"]
    assert row["max_abs_delta_arcseconds"] == 0.0
    assert row["failed_fields"] == []


def test_core_parity_report_handles_longitude_wraparound(tmp_path):
    from apps.calculations.witness_core_parity import build_witness_core_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected=_expected({"Surya": 359.9999}),
        chart=_chart({"Surya": 0.0001}),
    )

    row = next(
        item
        for item in build_witness_core_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")["cases"]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )
    surya = next(item for item in row["field_results"] if item["field"] == "grahas.Surya.longitude")

    assert row["comparison_status"] == "passed"
    assert surya["delta_arcseconds"] < 1.0
    assert abs(surya["signed_delta_arcseconds"]) < 1.0


def test_core_parity_report_fails_longitude_beyond_tolerance(tmp_path):
    from apps.calculations.witness_core_parity import build_witness_core_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected=_expected({"Surya": 10.0}),
        chart=_chart({"Surya": 10.1}),
    )

    row = next(
        item
        for item in build_witness_core_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")["cases"]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "grahas.Surya.longitude" in row["failed_fields"]
    assert row["max_abs_delta_arcseconds"] == 360.0


def test_core_parity_report_keeps_missing_and_draft_cases_out_of_passed(tmp_path):
    from apps.calculations.witness_core_parity import build_witness_core_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")
    _write_jhora_case(tmp_path / "jhora", "mayapur-2001-02-03-0910", expected={})

    report = build_witness_core_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "not_reviewed"
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert report["summary"]["passed_count"] == 0


def test_core_parity_command_writes_json_and_markdown_without_unsafe_commands(tmp_path):
    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "core-parity.json"
    markdown = tmp_path / "core-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_core_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-core-parity-report-v1"
    assert "Core Graha/Lagna Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    for forbidden in ["source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in serialized
    assert "witness_sources" in serialized
