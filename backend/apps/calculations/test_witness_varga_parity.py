from __future__ import annotations

import json
from io import StringIO

from django.core.management import call_command


BODIES = ["Lagna", "Surya", "Chandra"]
VARGA_CODES = ("D7", "D9", "D10")


def _placement(body: str, rashi: str = "Mesha", rashi_index: int = 0) -> dict[str, object]:
    return {"body": body, "rashi": rashi, "rashi_index": rashi_index}


def _expected_vargas(*, mismatch: bool = False) -> dict[str, object]:
    result: dict[str, object] = {}
    for code in VARGA_CODES:
        result[code] = {body: _placement(body) for body in BODIES}
    if mismatch:
        result["D9"]["Surya"] = _placement("Surya", "Vrishabha", 1)
    return result


def _chart_vargas(*, missing_code: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {}
    for code in VARGA_CODES:
        if code == missing_code:
            continue
        result[code] = {"code": code, "placements": [_placement(body) for body in BODIES]}
    return result


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected_vargas=None,
    chart_vargas=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": {"vargas": expected_vargas if expected_vargas is not None else _expected_vargas()},
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps({"vargas": chart_vargas if chart_vargas is not None else _chart_vargas()}),
        encoding="utf-8",
    )
    return case_dir


def test_varga_parity_report_passes_reviewed_matching_d7_d9_d10(tmp_path):
    from apps.calculations.witness_varga_parity import build_witness_varga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_varga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-varga-parity-report-v1"
    assert report["metadata"]["varga_codes"] == ["D7", "D9", "D10"]
    assert row["comparison_status"] == "passed"
    assert row["checked_vargas"] == ["D10", "D7", "D9"]
    assert row["failed_fields"] == []
    assert report["varga_summary"]["D9"]["passed"] == 1


def test_varga_parity_report_records_mismatch_without_formula_changes(tmp_path):
    from apps.calculations.witness_varga_parity import build_witness_varga_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_vargas=_expected_vargas(mismatch=True),
    )

    row = next(
        item
        for item in build_witness_varga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "D9.Surya.rashi" in row["failed_fields"]
    assert "D9" in row["failed_vargas"]


def test_varga_parity_report_missing_expected_or_actual_is_not_comparable(tmp_path):
    from apps.calculations.witness_varga_parity import build_witness_varga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected_vargas={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_vargas=_chart_vargas(missing_code="D10"),
    )

    report = build_witness_varga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "not_comparable"
    assert "jhora.vargas.D7" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "failed"
    assert "calculated.vargas.D10" in rows["mayapur-2001-02-03-0910"]["missing_fields"]


def test_varga_parity_report_keeps_draft_case_out_of_passed(tmp_path):
    from apps.calculations.witness_varga_parity import build_witness_varga_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_varga_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_varga_parity_command_writes_json_and_markdown_without_unsafe_authority(tmp_path):
    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "varga-parity.json"
    markdown = tmp_path / "varga-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_varga_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-varga-parity-report-v1"
    assert "Varga Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    for forbidden in ["source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in serialized
    assert "witness_sources" in serialized
