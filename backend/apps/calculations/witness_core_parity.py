from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.utils import timezone

from .accuracy import compare_longitude
from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-core-parity-report-v1"
CORE_BODIES = ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]
EXACT_FIELDS = ("rashi", "rashi_index", "nakshatra", "pada")
DEFAULT_TOLERANCE_PROFILE = {
    "planet_longitude_arcseconds": 1.0,
    "lagna_arcseconds": 5.0,
}


def build_witness_core_parity_report(
    *,
    jhora_root: str | Path,
    pl_root: str | Path = "",
    target_reviewed_count: int = 20,
    tolerance_profile: dict[str, float] | None = None,
) -> dict[str, Any]:
    tolerances = {**DEFAULT_TOLERANCE_PROFILE, **(tolerance_profile or {})}
    audit = audit_jhora_pl_witness_batch(
        jhora_root=jhora_root,
        pl_root=pl_root,
        target_reviewed_count=target_reviewed_count,
    )
    rows = [_case_report(row, tolerances) for row in audit["cases"]]
    summary = _summary(rows, target_reviewed_count)
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "generated_at": timezone.now().isoformat(),
            "jhora_root": str(jhora_root),
            "pl_root": str(pl_root),
            "target_reviewed_count": target_reviewed_count,
            "tolerance_profile": tolerances,
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": summary,
        "cases": rows,
    }


def render_core_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Core Graha/Lagna Parity Report",
        "",
        f"- Case count: {summary['case_count']}",
        f"- Comparable: {summary['comparable_count']}",
        f"- Passed: {summary['passed_count']}",
        f"- Failed: {summary['failed_count']}",
        f"- Missing witness: {summary['missing_witness_count']}",
        f"- Not reviewed: {summary['not_reviewed_count']}",
        f"- Not comparable: {summary['not_comparable_count']}",
        f"- Target reviewed count: {summary['target_reviewed_count']}",
        f"- Target met: {'yes' if summary['target_met'] else 'no'}",
        "",
        "## Cases",
    ]
    for row in report["cases"]:
        if row["comparison_status"] == "passed":
            continue
        lines.extend(
            [
                "",
                f"### {row['case_id']}",
                f"- Status: {row['comparison_status']}",
                f"- Sources: {', '.join(row['sources_present']) or 'none'}",
                f"- Missing fields: {', '.join(row['missing_fields']) or 'none'}",
                f"- Failed fields: {', '.join(row['failed_fields']) or 'none'}",
            ]
        )
    return "\n".join(lines) + "\n"


def _case_report(case_row: dict[str, Any], tolerances: dict[str, float]) -> dict[str, Any]:
    records = [*_source_records(case_row, "jhora"), *_source_records(case_row, "parashara_light")]
    sources_present = sorted({record["source"] for record in records})
    review_statuses = sorted({str(record.get("review_status") or "") for record in records if record.get("review_status")})
    if not records:
        return _empty_case(case_row, "missing_witness", sources_present, review_statuses, ["jhora_packet_or_pl_packet"])

    reviewed_records = [record for record in records if _is_reviewed(record)]
    if not reviewed_records:
        return _empty_case(case_row, "not_reviewed", sources_present, review_statuses, [])

    field_results: list[dict[str, Any]] = []
    missing_fields: list[str] = []
    failed_fields: list[str] = []
    for record in reviewed_records:
        source_results, source_missing = _compare_record(record, tolerances)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)

    if not field_results:
        return _empty_case(case_row, "not_comparable", sources_present, review_statuses, sorted(set(missing_fields or ["core_expected_fields"])))

    failed_fields = [item["field"] for item in field_results if not item.get("passed")]
    max_delta = max((float(item.get("delta_arcseconds") or 0.0) for item in field_results), default=0.0)
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "field_results": field_results,
        "missing_fields": sorted(set(missing_fields)),
        "failed_fields": sorted(set(failed_fields)),
        "max_abs_delta_arcseconds": round(max_delta, 6),
    }


def _source_records(case_row: dict[str, Any], source: str) -> list[dict[str, Any]]:
    key = "jhora_records" if source == "jhora" else "pl_records"
    return [{**record, "source": source} for record in case_row.get(key, []) if isinstance(record, dict)]


def _empty_case(
    case_row: dict[str, Any],
    status: str,
    sources_present: list[str],
    review_statuses: list[str],
    missing_fields: list[str],
) -> dict[str, Any]:
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": status,
        "field_results": [],
        "missing_fields": missing_fields,
        "failed_fields": [],
        "max_abs_delta_arcseconds": 0.0,
    }


def _is_reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or "")
    if record["source"] == "jhora":
        return status in AUTHORITATIVE_REVIEW_STATUSES
    return status in PL_REVIEW_STATUSES


def _compare_record(record: dict[str, Any], tolerances: dict[str, float]) -> tuple[list[dict[str, Any]], list[str]]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected = _expected_core(fixture, record["source"])
    if not expected:
        return [], [f"{record['source']}.core_expected_fields"]
    if not chart:
        return [], [f"{record['source']}.jyotish_agent_chart"]
    return _compare_core(expected, chart, str(record["source"]), tolerances)


def _load_fixture_and_chart(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = _read_json(path)
    fixture = raw.get("fixture") if isinstance(raw.get("fixture"), dict) else raw
    chart = raw.get("jyotish_agent_chart") if isinstance(raw.get("jyotish_agent_chart"), dict) else {}
    if not chart:
        chart = _read_json(path.parent / "jyotish-agent-chart.json")
    return fixture if isinstance(fixture, dict) else {}, chart if isinstance(chart, dict) else {}


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _expected_core(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    expected = fixture.get("expected")
    if isinstance(expected, dict) and (expected.get("ascendant") or expected.get("grahas")):
        return expected
    if source == "parashara_light":
        return _manual_values_expected(fixture.get("manual_witness_values"))
    return {}


def _manual_values_expected(values: Any) -> dict[str, Any]:
    if not isinstance(values, list):
        return {}
    expected: dict[str, Any] = {"grahas": {}}
    for row in values:
        if not isinstance(row, dict):
            continue
        body = str(row.get("body") or "")
        payload = row.get("witness") if isinstance(row.get("witness"), dict) else row
        point = {field: payload[field] for field in ("longitude", "rashi", "rashi_index", "nakshatra", "pada") if field in payload}
        if "longitude_dms" in payload and "longitude" not in point:
            continue
        if body == "Lagna":
            expected["ascendant"] = {"body": "Lagna", **point}
        elif body:
            expected["grahas"][body] = {"body": body, **point}
    return expected if expected.get("ascendant") or expected.get("grahas") else {}


def _compare_core(
    expected: dict[str, Any],
    chart: dict[str, Any],
    source: str,
    tolerances: dict[str, float],
) -> tuple[list[dict[str, Any]], list[str]]:
    actual_index = _chart_index(chart)
    expected_index = _expected_index(expected)
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for body in ["Lagna", *CORE_BODIES]:
        expected_point = expected_index.get(body)
        actual_point = actual_index.get(body)
        prefix = "ascendant" if body == "Lagna" else f"grahas.{body}"
        if not isinstance(expected_point, dict):
            missing.append(f"{source}.{prefix}")
            continue
        if not isinstance(actual_point, dict):
            missing.append(f"calculated.{prefix}")
            continue
        if "longitude" in expected_point and "longitude" in actual_point:
            tolerance = tolerances["lagna_arcseconds"] if body == "Lagna" else tolerances["planet_longitude_arcseconds"]
            comparison = compare_longitude(
                body,
                expected_degrees=float(expected_point["longitude"]),
                actual_degrees=float(actual_point["longitude"]),
                tolerance_arcseconds=float(tolerance),
            )
            results.append(
                {
                    "source": source,
                    "field": f"{prefix}.longitude",
                    "body": body,
                    "expected": comparison.expected_degrees,
                    "actual": comparison.actual_degrees,
                    "delta_arcseconds": comparison.delta_arcseconds,
                    "signed_delta_arcseconds": comparison.signed_delta_arcseconds,
                    "tolerance_arcseconds": comparison.tolerance_arcseconds,
                    "passed": comparison.passed,
                }
            )
        else:
            missing.append(f"{source}.{prefix}.longitude")
        for field in EXACT_FIELDS:
            if field not in expected_point:
                missing.append(f"{source}.{prefix}.{field}")
                continue
            if field not in actual_point:
                missing.append(f"calculated.{prefix}.{field}")
                continue
            expected_value = expected_point.get(field)
            actual_value = actual_point.get(field)
            results.append(
                {
                    "source": source,
                    "field": f"{prefix}.{field}",
                    "body": body,
                    "expected": expected_value,
                    "actual": actual_value,
                    "passed": str(expected_value) == str(actual_value),
                }
            )
    return results, missing


def _chart_index(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    ascendant = chart.get("ascendant")
    if isinstance(ascendant, dict):
        index["Lagna"] = ascendant
    for graha in chart.get("grahas") or []:
        if isinstance(graha, dict) and graha.get("body"):
            index[str(graha["body"])] = graha
    return index


def _expected_index(expected: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    ascendant = expected.get("ascendant")
    if isinstance(ascendant, dict):
        index["Lagna"] = ascendant
    grahas = expected.get("grahas")
    if isinstance(grahas, dict):
        for body, row in grahas.items():
            if isinstance(row, dict):
                index[str(body)] = row
    return index


def _summary(rows: list[dict[str, Any]], target_reviewed_count: int) -> dict[str, Any]:
    comparable = [row for row in rows if row["comparison_status"] in {"passed", "failed"}]
    passed_count = sum(1 for row in rows if row["comparison_status"] == "passed")
    return {
        "case_count": len(rows),
        "comparable_count": len(comparable),
        "passed_count": passed_count,
        "failed_count": sum(1 for row in rows if row["comparison_status"] == "failed"),
        "missing_witness_count": sum(1 for row in rows if row["comparison_status"] == "missing_witness"),
        "not_reviewed_count": sum(1 for row in rows if row["comparison_status"] == "not_reviewed"),
        "not_comparable_count": sum(1 for row in rows if row["comparison_status"] == "not_comparable"),
        "target_reviewed_count": target_reviewed_count,
        "target_met": passed_count >= target_reviewed_count,
    }
