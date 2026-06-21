from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-argala-parity-report-v1"
LAYERS = ("argala_pairs", "argala_rows")
ROW_GROUPS = ("primary", "obstruction", "secondary", "secondary_obstruction")
ARGALA_SUMMARY_KEYS = ("pairs", *ROW_GROUPS)
BODY_ALIASES = {
    "su": "Surya",
    "sun": "Surya",
    "surya": "Surya",
    "mo": "Chandra",
    "moon": "Chandra",
    "chandra": "Chandra",
    "ma": "Mangala",
    "mars": "Mangala",
    "mangala": "Mangala",
    "me": "Budha",
    "mercury": "Budha",
    "budha": "Budha",
    "ju": "Guru",
    "jupiter": "Guru",
    "guru": "Guru",
    "ve": "Shukra",
    "venus": "Shukra",
    "shukra": "Shukra",
    "sa": "Shani",
    "saturn": "Shani",
    "shani": "Shani",
    "rahu": "Rahu",
    "ketu": "Ketu",
}


def build_witness_argala_parity_report(
    *,
    jhora_root: str | Path,
    pl_root: str | Path = "",
    target_reviewed_count: int = 20,
) -> dict[str, Any]:
    audit = audit_jhora_pl_witness_batch(
        jhora_root=jhora_root,
        pl_root=pl_root,
        target_reviewed_count=target_reviewed_count,
    )
    rows = [_case_report(row) for row in audit["cases"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "generated_at": timezone.now().isoformat(),
            "target_reviewed_count": target_reviewed_count,
            "layers": list(LAYERS),
            "witness_sources": ["jhora", "parashara_light"],
            "normalization_notes": [
                "Argala rows compare structural fields only.",
                "Graha names are normalized across Sanskrit and English names and sorted for list comparison.",
                "Unknown optional witness fields are skipped unless no comparable argala fields remain.",
            ],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "argala_summary": _argala_summary(rows),
        "cases": rows,
    }


def render_argala_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Argala Parity Report",
        "",
        "Diagnostic comparison of reviewed witness Argala rows against Jyotish Agent Argala payloads.",
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
        "## Argala summary",
    ]
    for key, row in sorted(report.get("argala_summary", {}).items()):
        lines.append(
            f"- {key}: passed {row['passed']}, failed {row['failed']}, missing {row['missing']}, skipped {row['skipped']}"
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
                f"- Skipped fields: {', '.join(row['skipped_fields']) or 'none'}",
            ]
        )
    return "\n".join(lines) + "\n"


def _case_report(case_row: dict[str, Any]) -> dict[str, Any]:
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
    skipped_fields: list[str] = []
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, source_skipped, missing_kind = _compare_record(record)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        skipped_fields.extend(source_skipped)
        if missing_kind == "witness" and not source_results:
            witness_missing_records += 1

    if not field_results:
        if witness_missing_records == len(reviewed_records):
            row = _empty_case(case_row, "missing", sources_present, review_statuses, sorted(set(missing_fields)))
        else:
            row = _empty_case(
                case_row,
                "not_comparable",
                sources_present,
                review_statuses,
                sorted(set(missing_fields or ["argala"])),
            )
        row["skipped_fields"] = sorted(set(skipped_fields))
        return row

    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
    checked_fields = sorted({str(item["field"]) for item in field_results})
    checked_layers = sorted({str(item["layer"]) for item in field_results})
    failed_layers = sorted({str(item["layer"]) for item in field_results if not item.get("passed")})
    missing_layers = sorted({_layer_from_field(field) for field in missing_fields if _layer_from_field(field)})
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "checked_layers": checked_layers,
        "failed_layers": failed_layers,
        "missing_layers": missing_layers,
        "checked_fields": checked_fields,
        "failed_fields": failed_fields,
        "missing_fields": sorted(set(missing_fields)),
        "skipped_fields": sorted(set(skipped_fields)),
        "field_results": field_results,
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
        "checked_layers": [],
        "failed_layers": [],
        "missing_layers": ["argala"] if missing_fields else [],
        "checked_fields": [],
        "failed_fields": [],
        "missing_fields": missing_fields,
        "skipped_fields": [],
        "field_results": [],
    }


def _is_reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or "")
    if record["source"] == "jhora":
        return status in AUTHORITATIVE_REVIEW_STATUSES
    return status in PL_REVIEW_STATUSES


def _compare_record(record: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected = _expected_argala(fixture, str(record["source"]))
    actual = _actual_argala(chart)
    if not expected:
        return [], [f"{record['source']}.argala"], [], "witness"
    if not actual:
        return [], ["calculated.argala"], [], "calculated"
    results, missing, skipped = _compare_argala(expected, actual, str(record["source"]))
    if not results and skipped:
        return [], ["argala.comparable_fields"], skipped, "unsupported"
    if not results:
        return [], missing or ["calculated.argala"], skipped, "calculated"
    return results, missing, skipped, ""


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


def _expected_argala(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    expected = fixture.get("expected") if isinstance(fixture.get("expected"), dict) else {}
    jhora_expected = fixture.get("jhora_expected") if isinstance(fixture.get("jhora_expected"), dict) else {}
    for value in (expected.get("argala"), jhora_expected.get("argala")):
        if isinstance(value, dict) and value:
            return dict(value)
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        value = manual.get("argala")
        if isinstance(value, dict) and value:
            return dict(value)
    return {}


def _actual_argala(chart: dict[str, Any]) -> dict[str, Any]:
    value = ((chart.get("classical") or {}).get("argala") or {})
    return dict(value) if isinstance(value, dict) and value else {}


def _compare_argala(
    expected: dict[str, Any],
    actual: dict[str, Any],
    source: str,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    skipped: list[str] = []

    for key in expected:
        if key not in {"pairs", *ROW_GROUPS}:
            skipped.append(f"argala.{_normalized_key(key)}")

    pair_results, pair_missing = _compare_pairs(expected.get("pairs"), actual.get("pairs"), source)
    results.extend(pair_results)
    missing.extend(pair_missing)

    for group in ROW_GROUPS:
        group_results, group_missing = _compare_row_group(group, expected.get(group), actual.get(group), source)
        results.extend(group_results)
        missing.extend(group_missing)

    return results, missing, skipped


def _compare_pairs(expected_value: Any, actual_value: Any, source: str) -> tuple[list[dict[str, Any]], list[str]]:
    expected_rows = _list_of_dicts(expected_value)
    if not expected_rows:
        return [], []
    actual_rows = _list_of_dicts(actual_value)
    actual_index = {_pair_key(row): row for row in actual_rows if _pair_key(row)}
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for expected in expected_rows:
        key = _pair_key(expected)
        if not key or key not in actual_index:
            missing.append(f"argala_pairs.{_pair_label(expected)}")
            continue
        actual = actual_index[key]
        label = _pair_label(expected)
        comparisons = {
            "level": (str(expected.get("level") or ""), str(actual.get("level") or "")),
            "argala_house": (_int_or_none(expected.get("argala_house")), _int_or_none(actual.get("argala_house"))),
            "obstruction_house": (
                _int_or_none(expected.get("obstruction_house")),
                _int_or_none(actual.get("obstruction_house")),
            ),
            "argala_bodies": (_normalize_body_list(expected.get("argala_bodies")), _normalize_body_list(actual.get("argala_bodies"))),
            "obstruction_bodies": (
                _normalize_body_list(expected.get("obstruction_bodies")),
                _normalize_body_list(actual.get("obstruction_bodies")),
            ),
            "net_effect": (str(expected.get("net_effect") or ""), str(actual.get("net_effect") or "")),
        }
        for field, (expected_normalized, actual_normalized) in comparisons.items():
            results.append(
                {
                    "source": source,
                    "layer": "argala_pairs",
                    "summary_key": "pairs",
                    "field": f"argala_pairs.{label}.{field}",
                    "expected": expected_normalized,
                    "actual": actual_normalized,
                    "passed": expected_normalized == actual_normalized,
                }
            )
    return results, missing


def _compare_row_group(group: str, expected_value: Any, actual_value: Any, source: str) -> tuple[list[dict[str, Any]], list[str]]:
    expected_rows = _list_of_dicts(expected_value)
    if not expected_rows:
        return [], []
    actual_rows = _list_of_dicts(actual_value)
    actual_index = {_int_or_none(row.get("house")): row for row in actual_rows if _int_or_none(row.get("house")) is not None}
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for expected in expected_rows:
        house = _int_or_none(expected.get("house"))
        if house is None or house not in actual_index:
            missing.append(f"argala_rows.{group}.{house or 'unknown'}")
            continue
        actual = actual_index[house]
        comparisons = {
            "house": (house, _int_or_none(actual.get("house"))),
            "bodies": (_normalize_body_list(expected.get("bodies")), _normalize_body_list(actual.get("bodies"))),
        }
        for field, (expected_normalized, actual_normalized) in comparisons.items():
            results.append(
                {
                    "source": source,
                    "layer": "argala_rows",
                    "summary_key": group,
                    "field": f"argala_rows.{group}.{house}.{field}",
                    "expected": expected_normalized,
                    "actual": actual_normalized,
                    "passed": expected_normalized == actual_normalized,
                }
            )
    return results, missing


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, dict):
        iterable = value.values()
    elif isinstance(value, list):
        iterable = value
    else:
        return []
    return [dict(item) for item in iterable if isinstance(item, dict)]


def _pair_key(row: dict[str, Any]) -> tuple[str, int, int] | None:
    level = str(row.get("level") or "")
    argala_house = _int_or_none(row.get("argala_house"))
    obstruction_house = _int_or_none(row.get("obstruction_house"))
    if not level or argala_house is None or obstruction_house is None:
        return None
    return (level, argala_house, obstruction_house)


def _pair_label(row: dict[str, Any]) -> str:
    level = str(row.get("level") or "unknown")
    house = _int_or_none(row.get("argala_house"))
    return f"{level}.{house or 'unknown'}"


def _normalize_body_list(value: Any) -> list[str]:
    if isinstance(value, list):
        items = value
    elif value in (None, ""):
        items = []
    else:
        items = [value]
    normalized = [_normalize_body(item) for item in items]
    return sorted(item for item in normalized if item)


def _normalize_body(value: Any) -> str:
    key = _normalized_key(value)
    return BODY_ALIASES.get(key, str(value or "").strip())


def _normalized_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _layer_from_field(field: str) -> str:
    if field.startswith("argala_pairs"):
        return "argala_pairs"
    if field.startswith("argala_rows"):
        return "argala_rows"
    return ""


def _summary_key_from_field(field: str) -> str:
    parts = field.split(".")
    if not parts:
        return ""
    if parts[0] == "argala_pairs":
        return "pairs"
    if parts[0] == "argala_rows" and len(parts) > 1:
        return parts[1]
    if parts[0] == "argala" and len(parts) > 1:
        return parts[1]
    return ""


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


def _layer_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary = {layer: {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0} for layer in LAYERS}
    for row in rows:
        for layer in LAYERS:
            if row["comparison_status"] == "passed" and layer in row.get("checked_layers", []):
                summary[layer]["passed"] += 1
            elif layer in row.get("failed_layers", []):
                summary[layer]["failed"] += 1
            elif row["comparison_status"] in {"missing", "missing_witness"}:
                summary[layer]["missing"] += 1
            elif row["comparison_status"] in {"not_comparable", "not_reviewed"}:
                summary[layer]["not_comparable"] += 1
    return summary


def _argala_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary = {key: {"passed": 0, "failed": 0, "missing": 0, "skipped": 0} for key in ARGALA_SUMMARY_KEYS}
    for row in rows:
        row_results = row.get("field_results", [])
        keys = sorted({str(item.get("summary_key") or "") for item in row_results if item.get("summary_key")})
        for key in keys:
            bucket = summary.setdefault(key, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            failed = any(item.get("summary_key") == key and not item.get("passed") for item in row_results)
            bucket["failed" if failed else "passed"] += 1
        for field in row.get("missing_fields", []):
            key = _summary_key_from_field(str(field))
            if key:
                bucket = summary.setdefault(key, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
                bucket["missing"] += 1
        for field in row.get("skipped_fields", []):
            key = _summary_key_from_field(str(field))
            if key:
                bucket = summary.setdefault(key, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
                bucket["skipped"] += 1
    return summary
