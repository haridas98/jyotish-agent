from __future__ import annotations

import json
from io import StringIO

from django.core.management import call_command


def _period(lord: str, starts_at: str, ends_at: str) -> dict[str, object]:
    return {
        "lord": lord,
        "starts_at": starts_at,
        "ends_at": ends_at,
    }


def _expected_vimshottari(*, mismatch: bool = False) -> dict[str, object]:
    mahadashas = [
        _period("Rahu", "1998-04-30", "2016-04-30"),
        _period("Guru", "2016-04-30", "2032-04-30"),
    ]
    antardashas = [
        _period("Rahu", "1998-04-30", "2000-12-15"),
        _period("Guru", "2000-12-15", "2003-05-10"),
    ]
    if mismatch:
        mahadashas[1] = _period("Shani", "2016-05-03", "2032-04-30")
    return {
        "current": {"mahadasha_lord": "Rahu", "antardasha_lord": "Rahu"},
        "birth": {"mahadasha_lord": "Rahu"},
        "mahadashas": mahadashas,
        "antardashas": antardashas,
    }


def _chart_vimshottari(*, missing: bool = False) -> dict[str, object]:
    if missing:
        return {}
    return {
        "current": {"mahadasha_lord": "Rahu", "antardasha_lord": "Rahu"},
        "birth": {"mahadasha_lord": "Rahu"},
        "mahadashas": [
            {
                **_period("Rahu", "1998-04-30T13:45:00+06:00", "2016-04-30T13:45:00+06:00"),
                "antardashas": [
                    _period("Rahu", "1998-04-30T13:45:00+06:00", "2000-12-15T13:45:00+06:00"),
                    _period("Guru", "2000-12-15T13:45:00+06:00", "2003-05-10T13:45:00+06:00"),
                ],
            },
            _period("Guru", "2016-04-30T13:45:00+06:00", "2032-04-30T13:45:00+06:00"),
        ],
    }


def _case_input(case_id: str) -> dict[str, str]:
    if case_id == "mayapur-2001-02-03-0910":
        return {"birth_date": "2001-02-03", "birth_time": "09:10:00", "place_name": "Mayapur"}
    return {"birth_date": "1998-04-30", "birth_time": "13:45:00", "place_name": "Sterlitamak"}


def _write_jhora_case(
    root,
    case_id: str,
    *,
    review_status: str = "jhora_verified",
    expected_vimshottari=None,
    chart_vimshottari=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "jhora_complete_calculations_clipboard",
        "review_status": review_status,
        "input": _case_input(case_id),
        "jhora_metadata": {"capture_status": "export_parsed"},
        "expected": {
            "dashas": {
                "vimshottari": expected_vimshottari
                if expected_vimshottari is not None
                else _expected_vimshottari()
            }
        },
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(
            {
                "dashas": {
                    "vimshottari": chart_vimshottari
                    if chart_vimshottari is not None
                    else _chart_vimshottari()
                }
            }
        ),
        encoding="utf-8",
    )
    return case_dir


def _write_pl_case(
    root,
    case_id: str,
    *,
    review_status: str = "reviewed",
    manual_vimshottari=None,
    chart_vimshottari=None,
):
    case_dir = root / "batch-queue" / case_id
    case_dir.mkdir(parents=True)
    fixture = {
        "id": case_id,
        "source": "parashara_light_manual_values",
        "review_status": review_status,
        "input": _case_input(case_id),
        "pl_metadata": {"capture_status": "manual_values_captured"},
        "manual_witness_values": {
            "dashas": {
                "vimshottari": manual_vimshottari
                if manual_vimshottari is not None
                else _expected_vimshottari()
            }
        },
    }
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")
    (case_dir / "jyotish-agent-chart.json").write_text(
        json.dumps(
            {
                "dashas": {
                    "vimshottari": chart_vimshottari
                    if chart_vimshottari is not None
                    else _chart_vimshottari()
                }
            }
        ),
        encoding="utf-8",
    )
    return case_dir


def test_dasha_parity_report_passes_reviewed_matching_md_ad(tmp_path):
    from apps.calculations.witness_dasha_parity import build_witness_dasha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")

    report = build_witness_dasha_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == "sterlitamak-1998-04-30-1345")

    assert report["schema_version"] == "jyotish-dasha-parity-report-v1"
    assert report["metadata"]["dasha_system"] == "vimshottari"
    assert report["metadata"]["levels"] == ["mahadasha", "antardasha"]
    assert row["comparison_status"] == "passed"
    assert row["checked_levels"] == ["antardasha", "mahadasha"]
    assert row["failed_fields"] == []
    assert report["summary"]["passed_count"] == 1


def test_dasha_parity_report_records_lord_and_date_mismatch(tmp_path):
    from apps.calculations.witness_dasha_parity import build_witness_dasha_parity_report

    _write_jhora_case(
        tmp_path / "jhora",
        "sterlitamak-1998-04-30-1345",
        expected_vimshottari=_expected_vimshottari(mismatch=True),
    )

    row = next(
        item
        for item in build_witness_dasha_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "failed"
    assert "mahadasha[1].lord" in row["failed_fields"]
    assert "mahadasha[1].starts_at" in row["failed_fields"]
    assert "mahadasha" in row["failed_levels"]


def test_dasha_parity_missing_witness_or_actual_is_not_formula_failure(tmp_path):
    from apps.calculations.witness_dasha_parity import build_witness_dasha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", expected_vimshottari={})
    _write_jhora_case(
        tmp_path / "jhora",
        "mayapur-2001-02-03-0910",
        chart_vimshottari=_chart_vimshottari(missing=True),
    )

    report = build_witness_dasha_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    rows = {item["case_id"]: item for item in report["cases"]}

    assert rows["sterlitamak-1998-04-30-1345"]["comparison_status"] == "missing"
    assert "jhora.dashas.vimshottari" in rows["sterlitamak-1998-04-30-1345"]["missing_fields"]
    assert rows["mayapur-2001-02-03-0910"]["comparison_status"] == "not_comparable"
    assert "calculated.dashas.vimshottari" in rows["mayapur-2001-02-03-0910"]["missing_fields"]
    assert report["summary"]["failed_count"] == 0


def test_dasha_parity_missing_one_source_does_not_hide_comparable_reviewed_source(tmp_path):
    from apps.calculations.witness_dasha_parity import build_witness_dasha_parity_report

    case_id = "sterlitamak-1998-04-30-1345"
    _write_jhora_case(tmp_path / "jhora", case_id, expected_vimshottari={})
    _write_pl_case(tmp_path / "pl7", case_id)

    report = build_witness_dasha_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    row = next(item for item in report["cases"] if item["case_id"] == case_id)

    assert row["comparison_status"] == "passed"
    assert row["checked_levels"] == ["antardasha", "mahadasha"]
    assert "jhora.dashas.vimshottari" in row["missing_fields"]
    assert report["summary"]["comparable_count"] == 1
    assert report["summary"]["passed_count"] == 1


def test_dasha_parity_report_keeps_unreviewed_case_out_of_passed(tmp_path):
    from apps.calculations.witness_dasha_parity import build_witness_dasha_parity_report

    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345", review_status="draft")

    row = next(
        item
        for item in build_witness_dasha_parity_report(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")[
            "cases"
        ]
        if item["case_id"] == "sterlitamak-1998-04-30-1345"
    )

    assert row["comparison_status"] == "not_reviewed"
    assert row["field_results"] == []


def test_dasha_parity_command_writes_json_and_markdown_without_unsafe_authority(tmp_path):
    _write_jhora_case(tmp_path / "jhora", "sterlitamak-1998-04-30-1345")
    output = tmp_path / "dasha-parity.json"
    markdown = tmp_path / "dasha-parity.md"
    stdout = StringIO()

    call_command(
        "build_witness_dasha_parity_report",
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
    assert json.loads(output.read_text(encoding="utf-8"))["schema_version"] == "jyotish-dasha-parity-report-v1"
    assert "Vimshottari Dasha Parity Report" in markdown_text
    for forbidden in ["mark_jhora_witness_reviewed", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    lowered = serialized.lower()
    for forbidden in ["authority", "authoritative", "source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in lowered
    assert "witness_sources" in serialized
