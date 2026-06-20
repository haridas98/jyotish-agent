from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-varga-parity-report-v1"
DEFAULT_VARGA_CODES = ("D7", "D9", "D10")
EXACT_FIELDS = ("rashi", "rashi_index")


def build_witness_varga_parity_report(
    *,
    jhora_root: str | Path,
    pl_root: str | Path = "",
    target_reviewed_count: int = 20,
    varga_codes: tuple[str, ...] | list[str] = DEFAULT_VARGA_CODES,
) -> dict[str, Any]:
    codes = tuple(_normalize_varga_code(code) for code in varga_codes if str(code).strip())
    audit = audit_jhora_pl_witness_batch(
        jhora_root=jhora_root,
        pl_root=pl_root,
        target_reviewed_count=target_reviewed_count,
    )
    rows = [_case_report(row, codes) for row in audit["cases"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "generated_at": timezone.now().isoformat(),
            "jhora_root": str(jhora_root),
            "pl_root": str(pl_root),
            "target_reviewed_count": target_reviewed_count,
            "varga_codes": list(codes),
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "varga_summary": _varga_summary(rows, codes),
        "cases": rows,
    }


def render_varga_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Varga Parity Report",
        "",
        "Diagnostic comparison of reviewed witness packets against Jyotish Agent varga placements.",
        "JHora and Parashara Light are treated as witness sources, not calculation authority.",
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
        "## Varga summary",
    ]
    for code, row in sorted(report.get("varga_summary", {}).items()):
        lines.append(
            f"- {code}: passed {row['passed']}, failed {row['failed']}, missing {row['missing']}, not comparable {row['not_comparable']}"
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
                f"- Failed vargas: {', '.join(row['failed_vargas']) or 'none'}",
                f"- Missing vargas: {', '.join(row['missing_vargas']) or 'none'}",
                f"- Failed fields: {', '.join(row['failed_fields']) or 'none'}",
                f"- Missing fields: {', '.join(row['missing_fields']) or 'none'}",
            ]
        )
    return "\n".join(lines) + "\n"


def _case_report(case_row: dict[str, Any], codes: tuple[str, ...]) -> dict[str, Any]:
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
    for record in reviewed_records:
        source_results, source_missing = _compare_record(record, codes)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)

    if not field_results:
        return _empty_case(case_row, "not_comparable", sources_present, review_statuses, sorted(set(missing_fields or ["vargas"])))

    failed_fields = sorted({item["field"] for item in field_results if not item.get("passed")})
    checked_vargas = sorted({str(item["varga"]) for item in field_results})
    failed_vargas = sorted({str(item["varga"]) for item in field_results if not item.get("passed")})
    missing_vargas = sorted({_varga_from_missing_field(item) for item in missing_fields if _varga_from_missing_field(item)})
    comparison_status = "failed" if failed_fields or missing_fields else "passed"
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": comparison_status,
        "checked_vargas": checked_vargas,
        "failed_vargas": failed_vargas,
        "missing_vargas": missing_vargas,
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
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": status,
        "checked_vargas": [],
        "failed_vargas": [],
        "missing_vargas": sorted({_varga_from_missing_field(item) for item in missing_fields if _varga_from_missing_field(item)}),
        "field_results": [],
        "missing_fields": missing_fields,
        "failed_fields": [],
    }


def _is_reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or "")
    if record["source"] == "jhora":
        return status in AUTHORITATIVE_REVIEW_STATUSES
    return status in PL_REVIEW_STATUSES


def _compare_record(record: dict[str, Any], codes: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[str]]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected_vargas = _expected_vargas(fixture, record["source"])
    actual_vargas = chart.get("vargas") if isinstance(chart.get("vargas"), dict) else {}
    if not expected_vargas:
        return [], [f"{record['source']}.vargas.{code}" for code in codes]
    if not actual_vargas:
        return [], [f"calculated.vargas.{code}" for code in codes]
    return _compare_vargas(expected_vargas, actual_vargas, str(record["source"]), codes)


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


def _expected_vargas(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    expected = fixture.get("expected")
    if isinstance(expected, dict) and isinstance(expected.get("vargas"), dict):
        return expected["vargas"]
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values")
        if isinstance(manual, dict) and isinstance(manual.get("vargas"), dict):
            return manual["vargas"]
    return {}


def _compare_vargas(
    expected_vargas: dict[str, Any],
    actual_vargas: dict[str, Any],
    source: str,
    codes: tuple[str, ...],
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for code in codes:
        expected_index = _expected_placement_index(expected_vargas.get(code))
        actual_index = _actual_placement_index(actual_vargas.get(code))
        if not expected_index:
            missing.append(f"{source}.vargas.{code}")
            continue
        if not actual_index:
            missing.append(f"calculated.vargas.{code}")
            continue
        for body, expected_placement in expected_index.items():
            actual_placement = actual_index.get(body)
            if not isinstance(actual_placement, dict):
                missing.append(f"calculated.vargas.{code}.{body}")
                continue
            for field in EXACT_FIELDS:
                if field not in expected_placement:
                    continue
                if field not in actual_placement:
                    missing.append(f"calculated.vargas.{code}.{body}.{field}")
                    continue
                expected_value = expected_placement.get(field)
                actual_value = actual_placement.get(field)
                results.append(
                    {
                        "source": source,
                        "varga": code,
                        "field": f"{code}.{body}.{field}",
                        "body": body,
                        "expected": expected_value,
                        "actual": actual_value,
                        "passed": str(expected_value) == str(actual_value),
                    }
                )
    return results, missing


def _expected_placement_index(value: Any) -> dict[str, dict[str, Any]]:
    if isinstance(value, dict) and isinstance(value.get("placements"), list):
        return _placement_list_index(value.get("placements"))
    if isinstance(value, dict):
        return {str(body): row for body, row in value.items() if isinstance(row, dict)}
    if isinstance(value, list):
        return _placement_list_index(value)
    return {}


def _actual_placement_index(value: Any) -> dict[str, dict[str, Any]]:
    if isinstance(value, dict):
        return _placement_list_index(value.get("placements"))
    if isinstance(value, list):
        return _placement_list_index(value)
    return {}


def _placement_list_index(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        return {}
    return {str(row["body"]): row for row in value if isinstance(row, dict) and row.get("body")}


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


def _varga_summary(rows: list[dict[str, Any]], codes: tuple[str, ...]) -> dict[str, dict[str, int]]:
    summary = {code: {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0} for code in codes}
    for row in rows:
        for code in codes:
            if code in row["failed_vargas"]:
                summary[code]["failed"] += 1
            elif code in row["missing_vargas"]:
                summary[code]["missing"] += 1
            elif code in row["checked_vargas"] and row["comparison_status"] == "passed":
                summary[code]["passed"] += 1
            elif row["comparison_status"] in {"not_comparable", "not_reviewed", "missing_witness"}:
                summary[code]["not_comparable"] += 1
    return summary


def _varga_from_missing_field(value: str) -> str:
    for part in str(value).split("."):
        normalized = _normalize_varga_code(part)
        if normalized.startswith("D") and normalized[1:].isdigit():
            return normalized
    return ""


def _normalize_varga_code(value: object) -> str:
    return str(value).strip().upper()
