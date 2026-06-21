from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.utils import timezone

from .accuracy import _panchanga_name_keys
from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-panchanga-parity-report-v1"
DEFAULT_FIELDS = ("tithi", "vara", "yoga", "karana", "nakshatra")


def build_witness_panchanga_parity_report(
    *,
    jhora_root: str | Path,
    pl_root: str | Path = "",
    target_reviewed_count: int = 20,
    fields: tuple[str, ...] | list[str] = DEFAULT_FIELDS,
) -> dict[str, Any]:
    panchanga_fields = tuple(str(field).strip() for field in fields if str(field).strip())
    audit = audit_jhora_pl_witness_batch(
        jhora_root=jhora_root,
        pl_root=pl_root,
        target_reviewed_count=target_reviewed_count,
    )
    rows = [_case_report(row, panchanga_fields) for row in audit["cases"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "generated_at": timezone.now().isoformat(),
            "target_reviewed_count": target_reviewed_count,
            "fields": list(panchanga_fields),
            "normalization_notes": [
                "String values are compared through conservative panchanga name keys.",
                "Tithi compares paksha+name when paksha is present in calculated payload.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "field_summary": _field_summary(rows, panchanga_fields),
        "cases": rows,
    }


def render_panchanga_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Panchanga Parity Report",
        "",
        "Diagnostic comparison of reviewed witness packets against Jyotish Agent panchanga payloads.",
        "JHora and Parashara Light are used only as witness sources for comparison.",
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
        "## Field summary",
    ]
    for field, row in sorted(report.get("field_summary", {}).items()):
        lines.append(
            f"- {field}: passed {row['passed']}, failed {row['failed']}, missing {row['missing']}, not comparable {row['not_comparable']}"
        )
    lines.append("")
    lines.append("## Cases")
    for row in report["cases"]:
        if row["comparison_status"] == "passed":
            continue
        lines.extend(
            [
                "",
                f"### {row['case_id']}",
                f"- Status: {row['comparison_status']}",
                f"- Sources: {', '.join(row['sources_present']) or 'none'}",
                f"- Failed fields: {', '.join(row['failed_fields']) or 'none'}",
                f"- Missing fields: {', '.join(row['missing_fields']) or 'none'}",
            ]
        )
    return "\n".join(lines) + "\n"


def _case_report(case_row: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
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
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, missing_kind = _compare_record(record, fields)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        if missing_kind == "witness" and not source_results:
            witness_missing_records += 1

    if not field_results:
        if witness_missing_records == len(reviewed_records):
            return _empty_case(case_row, "missing", sources_present, review_statuses, sorted(set(missing_fields)))
        return _empty_case(case_row, "not_comparable", sources_present, review_statuses, sorted(set(missing_fields or ["panchanga"])))

    failed_fields = sorted({item["field"] for item in field_results if not item.get("passed")})
    checked_fields = sorted({str(item["panchanga_field"]) for item in field_results})
    failed_panchanga_fields = sorted({str(item["panchanga_field"]) for item in field_results if not item.get("passed")})
    missing_panchanga_fields = sorted({_field_from_missing_field(item, fields) for item in missing_fields if _field_from_missing_field(item, fields)})
    if failed_fields:
        comparison_status = "failed"
    else:
        comparison_status = "passed"
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": comparison_status,
        "checked_fields": checked_fields,
        "failed_panchanga_fields": failed_panchanga_fields,
        "missing_panchanga_fields": missing_panchanga_fields,
        "field_results": field_results,
        "missing_fields": sorted(set(missing_fields)),
        "failed_fields": failed_fields,
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
    fields = sorted({_field_from_missing_field(item, DEFAULT_FIELDS) for item in missing_fields if _field_from_missing_field(item, DEFAULT_FIELDS)})
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": status,
        "checked_fields": [],
        "failed_panchanga_fields": [],
        "missing_panchanga_fields": fields,
        "field_results": [],
        "missing_fields": missing_fields,
        "failed_fields": [],
    }


def _is_reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or "")
    if record["source"] == "jhora":
        return status in AUTHORITATIVE_REVIEW_STATUSES
    return status in PL_REVIEW_STATUSES


def _compare_record(record: dict[str, Any], fields: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected = _expected_panchanga(fixture, str(record["source"]))
    actual = chart.get("panchanga") if isinstance(chart.get("panchanga"), dict) else {}
    if not expected:
        return [], [f"{record['source']}.panchanga"], "witness"
    if not actual:
        return [], ["calculated.panchanga"], "calculated"
    return (*_compare_panchanga(expected, actual, str(record["source"]), fields), "")


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


def _expected_panchanga(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    expected = fixture.get("expected")
    if isinstance(expected, dict) and isinstance(expected.get("panchanga"), dict):
        return expected["panchanga"]
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values")
        if isinstance(manual, dict) and isinstance(manual.get("panchanga"), dict):
            return manual["panchanga"]
    return {}


def _compare_panchanga(
    expected: dict[str, Any],
    actual: dict[str, Any],
    source: str,
    fields: tuple[str, ...],
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for field in fields:
        if field not in expected:
            missing.append(f"{source}.panchanga.{field}")
            continue
        if field not in actual:
            missing.append(f"calculated.panchanga.{field}")
            continue
        expected_keys = _panchanga_keys(field, expected[field])
        actual_keys = _panchanga_keys(field, actual[field])
        if not expected_keys:
            missing.append(f"{source}.panchanga.{field}")
            continue
        if not actual_keys:
            missing.append(f"calculated.panchanga.{field}")
            continue
        results.append(
            {
                "source": source,
                "panchanga_field": field,
                "field": f"panchanga.{field}",
                "expected": sorted(expected_keys),
                "actual": sorted(actual_keys),
                "passed": bool(expected_keys & actual_keys),
            }
        )
    return results, missing


def _panchanga_keys(field: str, value: Any) -> set[str]:
    if isinstance(value, dict):
        row = value
        candidates = [row.get(key) for key in ("name", "key", "number") if row.get(key) is not None]
        keys: set[str] = set()
        for candidate in candidates:
            keys.update(_panchanga_name_keys(field, row, candidate))
        return keys
    return _panchanga_name_keys(field, {}, value)


def _summary(rows: list[dict[str, Any]], target_reviewed_count: int) -> dict[str, Any]:
    comparable = [row for row in rows if row["comparison_status"] in {"passed", "failed"}]
    passed_count = sum(1 for row in rows if row["comparison_status"] == "passed")
    return {
        "case_count": len(rows),
        "comparable_count": len(comparable),
        "passed_count": passed_count,
        "failed_count": sum(1 for row in rows if row["comparison_status"] == "failed"),
        "missing_witness_count": sum(1 for row in rows if row["comparison_status"] in {"missing_witness", "missing"}),
        "not_reviewed_count": sum(1 for row in rows if row["comparison_status"] == "not_reviewed"),
        "not_comparable_count": sum(1 for row in rows if row["comparison_status"] == "not_comparable"),
        "target_reviewed_count": target_reviewed_count,
        "target_met": passed_count >= target_reviewed_count,
    }


def _field_summary(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> dict[str, dict[str, int]]:
    summary = {field: {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0} for field in fields}
    for row in rows:
        for field in fields:
            if field in row["failed_panchanga_fields"]:
                summary[field]["failed"] += 1
            elif field in row["missing_panchanga_fields"]:
                if row["comparison_status"] == "missing" or _has_witness_missing_field(row.get("missing_fields"), field):
                    summary[field]["missing"] += 1
                else:
                    summary[field]["not_comparable"] += 1
            elif field in row["checked_fields"]:
                summary[field]["passed"] += 1
            elif row["comparison_status"] in {"missing", "not_comparable", "not_reviewed", "missing_witness"}:
                summary[field]["not_comparable"] += 1
    return summary


def _has_witness_missing_field(missing_fields: Any, field: str) -> bool:
    if not isinstance(missing_fields, list):
        return False
    suffix = f".panchanga.{field}"
    return any(str(item).endswith(suffix) and not str(item).startswith("calculated.") for item in missing_fields)


def _field_from_missing_field(value: str, fields: tuple[str, ...] | list[str]) -> str:
    text = str(value)
    for field in fields:
        if field in text:
            return field
    if text.endswith("panchanga"):
        return ""
    return ""
