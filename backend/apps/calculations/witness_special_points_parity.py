from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .accuracy import (
    JHORA_SPECIAL_POINT_ALIASES,
    _apply_special_time_lagna_family_correction,
    angular_delta_arcseconds,
    signed_angular_delta_arcseconds,
)
from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .primitives import normalize_degrees
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-special-points-parity-report-v1"
LAYERS = ("special_points",)
GROUPS = ("upagrahas", "vedic_points")
TOLERANCE_ARCSECONDS = 60.0
ALIASES_BY_CANONICAL = {
    alias: aliases
    for aliases in JHORA_SPECIAL_POINT_ALIASES.values()
    for alias in aliases
}
CANONICAL_BY_ALIAS = {
    alias: aliases[0]
    for aliases in JHORA_SPECIAL_POINT_ALIASES.values()
    for alias in aliases
}


def build_witness_special_points_parity_report(
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
            "groups": list(GROUPS),
            "witness_sources": ["jhora", "parashara_light"],
            "tolerance_arcseconds": TOLERANCE_ARCSECONDS,
            "normalization_notes": [
                "Point names are normalized through the accepted JHora special-point aliases.",
                "Only longitude is compared in this report contract.",
                "Bhava, Hora and Ghati Lagna reuse the existing JHora time-lagna family correction profile.",
            ],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "group_summary": _group_summary(rows),
        "point_summary": _point_summary(rows),
        "cases": rows,
    }


def render_special_points_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Special Points Parity Report",
        "",
        "Diagnostic comparison of reviewed witness special-point rows against Jyotish Agent special-point payloads.",
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
        "## Group summary",
    ]
    for group, row in sorted(report.get("group_summary", {}).items()):
        lines.append(
            f"- {group}: passed {row['passed']}, failed {row['failed']}, missing {row['missing']}, not comparable {row['not_comparable']}"
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
                f"- Failed points: {', '.join(row['failed_points']) or 'none'}",
                f"- Missing points: {', '.join(row['missing_points']) or 'none'}",
                f"- Skipped points: {', '.join(row['skipped_points']) or 'none'}",
                f"- Failed fields: {', '.join(row['failed_fields']) or 'none'}",
                f"- Missing fields: {', '.join(row['missing_fields']) or 'none'}",
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
    skipped_points: list[str] = []
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, source_skipped, missing_kind = _compare_record(record)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        skipped_points.extend(source_skipped)
        if missing_kind == "witness" and not source_results:
            witness_missing_records += 1

    if not field_results:
        if witness_missing_records == len(reviewed_records):
            return _empty_case(case_row, "missing", sources_present, review_statuses, sorted(set(missing_fields)))
        row = _empty_case(
            case_row,
            "not_comparable",
            sources_present,
            review_statuses,
            sorted(set(missing_fields or ["special_points"])),
        )
        row["skipped_points"] = sorted(set(skipped_points))
        return row

    failed_points = sorted({str(item["point_key"]) for item in field_results if not item.get("passed")})
    matched_points = sorted({str(item["point_key"]) for item in field_results if item.get("passed")})
    checked_points = sorted({str(item["point_key"]) for item in field_results})
    failed_fields = [f"special_points.{point}.longitude" for point in failed_points]
    missing_points = sorted({_point_from_missing_field(field) for field in missing_fields if _point_from_missing_field(field)})
    missing_groups = sorted({_group_from_missing_field(field) for field in missing_fields if _group_from_missing_field(field)})
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_points else "passed",
        "checked_layers": ["special_points"],
        "failed_layers": ["special_points"] if failed_points else [],
        "missing_layers": [] if field_results else ["special_points"],
        "checked_points": checked_points,
        "matched_points": matched_points,
        "failed_points": failed_points,
        "missing_points": missing_points or failed_points,
        "skipped_points": sorted(set(skipped_points)),
        "checked_groups": sorted({str(item["group"]) for item in field_results if item.get("group")}),
        "failed_groups": sorted({str(item["group"]) for item in field_results if item.get("group") and not item.get("passed")}),
        "missing_groups": missing_groups,
        "failed_fields": failed_fields,
        "missing_fields": sorted(set(missing_fields)),
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
        "missing_layers": ["special_points"] if missing_fields else [],
        "checked_points": [],
        "matched_points": [],
        "failed_points": [],
        "missing_points": [],
        "skipped_points": [],
        "checked_groups": [],
        "failed_groups": [],
        "missing_groups": [],
        "failed_fields": [],
        "missing_fields": missing_fields,
        "field_results": [],
    }


def _is_reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or "")
    if record["source"] == "jhora":
        return status in AUTHORITATIVE_REVIEW_STATUSES
    return status in PL_REVIEW_STATUSES


def _compare_record(record: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    rows = _expected_special_points(fixture, str(record["source"]))
    actual = _actual_special_points(chart)
    if not rows:
        return [], [f"{record['source']}.special_points"], [], "witness"
    if not actual:
        return [], ["calculated.special_points"], [], "calculated"
    results, missing, skipped = _compare_special_points(rows, actual, str(record["source"]))
    if not results and skipped:
        return [], ["special_points.comparable_name"], skipped, "unsupported"
    if not results:
        return [], missing or ["calculated.special_points"], skipped, "calculated"
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


def _expected_special_points(fixture: dict[str, Any], source: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    expected = fixture.get("expected") if isinstance(fixture.get("expected"), dict) else {}
    jhora_expected = fixture.get("jhora_expected") if isinstance(fixture.get("jhora_expected"), dict) else {}
    rows.extend(_map_special_points(expected.get("special_points"), source))
    rows.extend(_map_special_points(jhora_expected.get("special_points"), source))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        rows.extend(_map_special_points(manual.get("special_points"), source))
    return rows


def _map_special_points(value: Any, source: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, dict):
        iterable = value.items()
        for name, row in iterable:
            if isinstance(row, dict):
                rows.append({**row, "name": row.get("name") or name, "source": source})
    elif isinstance(value, list):
        for row in value:
            if isinstance(row, dict):
                rows.append({**row, "source": source})
    return rows


def _actual_special_points(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    special = ((chart.get("classical") or {}).get("special_points") or {})
    output: dict[str, dict[str, Any]] = {}
    for group_name in GROUPS:
        group = special.get(group_name)
        items = group.get("items") if isinstance(group, dict) else []
        for item in items or []:
            if not isinstance(item, dict):
                continue
            normalized = _normalized_point_key(item.get("key") or item.get("name"))
            if not normalized:
                continue
            aliases = {normalized, *_aliases_for(normalized)}
            name = str(item.get("name") or "")
            for part in re.split(r"[/()]+", name):
                part_key = _normalized_point_key(part)
                if part_key:
                    aliases.add(part_key)
            for alias in aliases:
                output[alias] = {**item, "group": group_name}
    return output


def _compare_special_points(
    rows: list[dict[str, Any]],
    actual_points: dict[str, dict[str, Any]],
    source: str,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    skipped: list[str] = []
    correction_rows: list[dict[str, Any]] = []
    correction_keys: list[int] = []
    for row in rows:
        point_key = _expected_point_key(row)
        display_key = _expected_display_key(row)
        if not point_key:
            if display_key:
                skipped.append(display_key)
            continue
        actual = _actual_point(point_key, actual_points)
        if not actual:
            missing.append(f"calculated.special_points.{point_key}")
            continue
        expected_value = _float_or_none(row.get("longitude"))
        actual_value = _float_or_none(actual.get("longitude"))
        if expected_value is None:
            missing.append(f"{source}.special_points.{point_key}.longitude")
            continue
        if actual_value is None:
            missing.append(f"calculated.special_points.{point_key}.longitude")
            continue
        delta = angular_delta_arcseconds(expected_value, actual_value)
        signed_delta = signed_angular_delta_arcseconds(expected_value, actual_value)
        result = {
            "source": source,
            "layer": "special_points",
            "group": str(actual.get("group") or ""),
            "point_key": point_key,
            "expected_name": str(row.get("name") or row.get("key") or ""),
            "actual_key": str(actual.get("key") or ""),
            "field": f"special_points.{point_key}.longitude",
            "expected": round(normalize_degrees(expected_value), 6),
            "actual": round(normalize_degrees(actual_value), 6),
            "delta_arcseconds": round(delta, 6),
            "signed_delta_arcseconds": round(signed_delta, 6),
            "raw_passed": delta <= TOLERANCE_ARCSECONDS,
            "passed": delta <= TOLERANCE_ARCSECONDS,
        }
        results.append(result)
        correction_rows.append(result)
        correction_keys.append(len(results) - 1)
    correction_profile = _apply_special_time_lagna_family_correction(correction_rows, TOLERANCE_ARCSECONDS)
    if correction_profile:
        for index in correction_keys:
            results[index]["correction_profile"] = correction_profile
    return results, missing, skipped


def _actual_point(point_key: str, actual_points: dict[str, dict[str, Any]]) -> dict[str, Any]:
    for alias in _aliases_for(point_key):
        row = actual_points.get(alias)
        if isinstance(row, dict):
            return row
    row = actual_points.get(point_key)
    return row if isinstance(row, dict) else {}


def _expected_point_key(row: dict[str, Any]) -> str:
    key = _normalized_point_key(row.get("key"))
    if key:
        return CANONICAL_BY_ALIAS.get(key, key)
    name = _normalized_point_key(row.get("name"))
    return CANONICAL_BY_ALIAS.get(name, "")


def _expected_display_key(row: dict[str, Any]) -> str:
    return _normalized_point_key(row.get("key") or row.get("name"))


def _aliases_for(key: str) -> list[str]:
    aliases = set(ALIASES_BY_CANONICAL.get(key, (key,)))
    aliases.add(key)
    return sorted(aliases)


def _normalized_point_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    replacements = {"dhooma": "dhuma", "maandi": "maandi", "mandi": "mandi"}
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return replacements.get(text, text)


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
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


def _layer_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary = {"special_points": {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0}}
    for row in rows:
        if row["comparison_status"] == "passed":
            summary["special_points"]["passed"] += 1
        elif row["comparison_status"] == "failed":
            summary["special_points"]["failed"] += 1
        elif row["comparison_status"] in {"missing", "missing_witness"}:
            summary["special_points"]["missing"] += 1
        elif row["comparison_status"] in {"not_comparable", "not_reviewed"}:
            summary["special_points"]["not_comparable"] += 1
    return summary


def _group_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary = {group: {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0} for group in GROUPS}
    for row in rows:
        checked = set(row.get("checked_groups", []))
        failed = set(row.get("failed_groups", []))
        missing = set(row.get("missing_groups", []))
        for group in GROUPS:
            if group in failed:
                summary[group]["failed"] += 1
            elif group in missing and group not in checked:
                summary[group]["missing"] += 1
            elif group in checked:
                summary[group]["passed"] += 1
            elif row["comparison_status"] in {"missing", "not_comparable", "not_reviewed", "missing_witness"}:
                summary[group]["not_comparable"] += 1
    return summary


def _point_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        for key in row.get("checked_points", []):
            bucket = summary.setdefault(str(key), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            if key in row.get("failed_points", []):
                bucket["failed"] += 1
            else:
                bucket["passed"] += 1
        for key in row.get("missing_points", []):
            bucket = summary.setdefault(str(key), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            if key not in row.get("checked_points", []):
                bucket["missing"] += 1
        for key in row.get("skipped_points", []):
            bucket = summary.setdefault(str(key), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["skipped"] += 1
    return summary


def _point_from_missing_field(value: str) -> str:
    parts = str(value).split(".")
    if len(parts) >= 3 and parts[0] == "calculated" and parts[1] == "special_points":
        return parts[2]
    return ""


def _group_from_missing_field(value: str) -> str:
    point = _point_from_missing_field(value)
    if point in {"gulika", "maandi", "mandi", "dhuma", "vyatipata", "parivesha", "indrachapa", "upaketu"}:
        return "upagrahas"
    if point:
        return "vedic_points"
    return ""
