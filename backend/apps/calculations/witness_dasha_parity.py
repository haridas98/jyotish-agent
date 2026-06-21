from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-dasha-parity-report-v1"
DASHA_SYSTEM = "vimshottari"
LEVELS = ("mahadasha", "antardasha")
DATE_TOLERANCE_DAYS = 1


def build_witness_dasha_parity_report(
    *,
    jhora_root: str | Path,
    pl_root: str | Path = "",
    target_reviewed_count: int = 20,
    sequence_limit: int = 9,
    date_tolerance_days: int = DATE_TOLERANCE_DAYS,
) -> dict[str, Any]:
    audit = audit_jhora_pl_witness_batch(
        jhora_root=jhora_root,
        pl_root=pl_root,
        target_reviewed_count=target_reviewed_count,
    )
    rows = [
        _case_report(
            row,
            sequence_limit=sequence_limit,
            date_tolerance_days=date_tolerance_days,
        )
        for row in audit["cases"]
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "generated_at": timezone.now().isoformat(),
            "target_reviewed_count": target_reviewed_count,
            "dasha_system": DASHA_SYSTEM,
            "levels": list(LEVELS),
            "date_tolerance_days": date_tolerance_days,
            "sequence_limit": sequence_limit,
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "level_summary": _level_summary(rows),
        "cases": rows,
    }


def render_dasha_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Vimshottari Dasha Parity Report",
        "",
        "Diagnostic comparison of reviewed witness packets against Jyotish Agent Vimshottari dasha payloads.",
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
        "## Level summary",
    ]
    for level, row in sorted(report.get("level_summary", {}).items()):
        lines.append(
            f"- {level}: passed {row['passed']}, failed {row['failed']}, missing {row['missing']}, not comparable {row['not_comparable']}"
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
                f"- Failed levels: {', '.join(row['failed_levels']) or 'none'}",
                f"- Missing levels: {', '.join(row['missing_levels']) or 'none'}",
                f"- Failed fields: {', '.join(row['failed_fields']) or 'none'}",
                f"- Missing fields: {', '.join(row['missing_fields']) or 'none'}",
            ]
        )
    return "\n".join(lines) + "\n"


def _case_report(
    case_row: dict[str, Any],
    *,
    sequence_limit: int,
    date_tolerance_days: int,
) -> dict[str, Any]:
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
        source_results, source_missing, missing_kind = _compare_record(
            record,
            sequence_limit=sequence_limit,
            date_tolerance_days=date_tolerance_days,
        )
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        if missing_kind == "witness" and not source_results:
            return _empty_case(case_row, "missing", sources_present, review_statuses, sorted(set(source_missing)))

    if not field_results:
        return _empty_case(case_row, "not_comparable", sources_present, review_statuses, sorted(set(missing_fields or ["dashas.vimshottari"])))

    failed_fields = sorted({item["field"] for item in field_results if not item.get("passed")})
    checked_levels = sorted({str(item["level"]) for item in field_results})
    failed_levels = sorted({str(item["level"]) for item in field_results if not item.get("passed")})
    missing_levels = sorted({_level_from_missing_field(item) for item in missing_fields if _level_from_missing_field(item)})
    if failed_fields:
        comparison_status = "failed"
    elif missing_fields:
        comparison_status = "not_comparable"
    else:
        comparison_status = "passed"
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": comparison_status,
        "checked_levels": checked_levels,
        "failed_levels": failed_levels,
        "missing_levels": missing_levels,
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
        "checked_levels": [],
        "failed_levels": [],
        "missing_levels": sorted({_level_from_missing_field(item) for item in missing_fields if _level_from_missing_field(item)}),
        "field_results": [],
        "missing_fields": missing_fields,
        "failed_fields": [],
    }


def _is_reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or "")
    if record["source"] == "jhora":
        return status in AUTHORITATIVE_REVIEW_STATUSES
    return status in PL_REVIEW_STATUSES


def _compare_record(
    record: dict[str, Any],
    *,
    sequence_limit: int,
    date_tolerance_days: int,
) -> tuple[list[dict[str, Any]], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected = _expected_vimshottari(fixture, str(record["source"]))
    actual = _actual_vimshottari(chart)
    if not expected:
        return [], [f"{record['source']}.dashas.vimshottari"], "witness"
    if not actual:
        return [], ["calculated.dashas.vimshottari"], "calculated"
    results, missing = _compare_vimshottari(
        expected,
        actual,
        str(record["source"]),
        sequence_limit=sequence_limit,
        date_tolerance_days=date_tolerance_days,
    )
    return results, missing, ""


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


def _expected_vimshottari(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    expected = fixture.get("expected")
    if isinstance(expected, dict):
        dashas = expected.get("dashas")
        if isinstance(dashas, dict) and isinstance(dashas.get(DASHA_SYSTEM), dict):
            return dashas[DASHA_SYSTEM]
        if isinstance(expected.get(DASHA_SYSTEM), dict):
            return expected[DASHA_SYSTEM]
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values")
        if isinstance(manual, dict):
            dashas = manual.get("dashas")
            if isinstance(dashas, dict) and isinstance(dashas.get(DASHA_SYSTEM), dict):
                return dashas[DASHA_SYSTEM]
            if isinstance(manual.get(DASHA_SYSTEM), dict):
                return manual[DASHA_SYSTEM]
    return {}


def _actual_vimshottari(chart: dict[str, Any]) -> dict[str, Any]:
    dashas = chart.get("dashas") if isinstance(chart.get("dashas"), dict) else {}
    value = dashas.get(DASHA_SYSTEM) if isinstance(dashas.get(DASHA_SYSTEM), dict) else {}
    return value if isinstance(value, dict) else {}


def _compare_vimshottari(
    expected: dict[str, Any],
    actual: dict[str, Any],
    source: str,
    *,
    sequence_limit: int,
    date_tolerance_days: int,
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    _compare_current_lords(results, missing, expected, actual, source)
    _compare_sequence(
        results,
        missing,
        _periods(expected, "mahadashas"),
        _periods(actual, "mahadashas"),
        source,
        level="mahadasha",
        sequence_limit=sequence_limit,
        date_tolerance_days=date_tolerance_days,
    )
    _compare_sequence(
        results,
        missing,
        _periods(expected, "antardashas"),
        _actual_antardashas(actual),
        source,
        level="antardasha",
        sequence_limit=sequence_limit,
        date_tolerance_days=date_tolerance_days,
    )
    return results, missing


def _compare_current_lords(
    results: list[dict[str, Any]],
    missing: list[str],
    expected: dict[str, Any],
    actual: dict[str, Any],
    source: str,
) -> None:
    for field, level in [
        ("mahadasha_lord", "mahadasha"),
        ("antardasha_lord", "antardasha"),
    ]:
        expected_value = _current_lord(expected, field)
        actual_value = _current_lord(actual, field)
        if expected_value is None:
            continue
        if actual_value is None:
            missing.append(f"calculated.current.{field}")
            continue
        results.append(
            {
                "source": source,
                "level": level,
                "field": f"current.{field}",
                "expected": expected_value,
                "actual": actual_value,
                "passed": str(expected_value) == str(actual_value),
            }
        )

    expected_birth = _birth_mahadasha_lord(expected)
    actual_birth = _birth_mahadasha_lord(actual)
    if expected_birth is not None:
        if actual_birth is None:
            missing.append("calculated.birth.mahadasha_lord")
        else:
            results.append(
                {
                    "source": source,
                    "level": "mahadasha",
                    "field": "birth.mahadasha_lord",
                    "expected": expected_birth,
                    "actual": actual_birth,
                    "passed": str(expected_birth) == str(actual_birth),
                }
            )


def _current_lord(payload: dict[str, Any], field: str) -> str | None:
    current = payload.get("current") if isinstance(payload.get("current"), dict) else {}
    if field in current:
        return str(current[field])
    key = "mahadasha" if field == "mahadasha_lord" else "antardasha"
    period = payload.get(key) if isinstance(payload.get(key), dict) else {}
    if period.get("lord"):
        return str(period["lord"])
    if field in payload:
        return str(payload[field])
    return None


def _birth_mahadasha_lord(payload: dict[str, Any]) -> str | None:
    birth = payload.get("birth") if isinstance(payload.get("birth"), dict) else {}
    if birth.get("mahadasha_lord"):
        return str(birth["mahadasha_lord"])
    if payload.get("birth_mahadasha_lord"):
        return str(payload["birth_mahadasha_lord"])
    periods = _periods(payload, "mahadashas")
    if periods and periods[0].get("lord"):
        return str(periods[0]["lord"])
    return None


def _compare_sequence(
    results: list[dict[str, Any]],
    missing: list[str],
    expected_periods: list[dict[str, Any]],
    actual_periods: list[dict[str, Any]],
    source: str,
    *,
    level: str,
    sequence_limit: int,
    date_tolerance_days: int,
) -> None:
    if not expected_periods:
        return
    if not actual_periods:
        missing.append(f"calculated.{level}")
        return
    for index, expected_period in enumerate(expected_periods[:sequence_limit]):
        if index >= len(actual_periods):
            missing.append(f"calculated.{level}[{index}]")
            continue
        actual_period = actual_periods[index]
        for field in ("lord", "starts_at", "ends_at"):
            if field not in expected_period:
                continue
            if field not in actual_period:
                missing.append(f"calculated.{level}[{index}].{field}")
                continue
            expected_value = expected_period[field]
            actual_value = actual_period[field]
            passed = (
                _date_within_tolerance(expected_value, actual_value, date_tolerance_days)
                if field in {"starts_at", "ends_at"}
                else str(expected_value) == str(actual_value)
            )
            results.append(
                {
                    "source": source,
                    "level": level,
                    "field": f"{level}[{index}].{field}",
                    "expected": expected_value,
                    "actual": actual_value,
                    "date_tolerance_days": date_tolerance_days if field in {"starts_at", "ends_at"} else None,
                    "passed": passed,
                }
            )


def _periods(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key)
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    return []


def _actual_antardashas(actual: dict[str, Any]) -> list[dict[str, Any]]:
    direct = _periods(actual, "antardashas")
    if direct:
        return direct
    mahadashas = _periods(actual, "mahadashas")
    if mahadashas and isinstance(mahadashas[0].get("antardashas"), list):
        return [row for row in mahadashas[0]["antardashas"] if isinstance(row, dict)]
    return []


def _date_within_tolerance(expected: Any, actual: Any, tolerance_days: int) -> bool:
    expected_dt = _parse_date(expected)
    actual_dt = _parse_date(actual)
    if expected_dt is None or actual_dt is None:
        return str(expected) == str(actual)
    return abs((actual_dt.date() - expected_dt.date()).days) <= tolerance_days


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        try:
            return datetime.fromisoformat(text[:10])
        except ValueError:
            return None


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


def _level_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary = {level: {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0} for level in LEVELS}
    for row in rows:
        for level in LEVELS:
            if level in row["failed_levels"]:
                summary[level]["failed"] += 1
            elif level in row["missing_levels"]:
                summary[level]["missing"] += 1
            elif level in row["checked_levels"]:
                summary[level]["passed"] += 1
            elif row["comparison_status"] in {"missing", "not_comparable", "not_reviewed", "missing_witness"}:
                summary[level]["not_comparable"] += 1
    return summary


def _level_from_missing_field(value: str) -> str:
    text = str(value)
    if "antardasha" in text:
        return "antardasha"
    if "mahadasha" in text or "vimshottari" in text:
        return "mahadasha"
    return ""
