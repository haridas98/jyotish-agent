from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-avastha-parity-report-v1"
LAYERS = ("baladi_avastha",)
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


def build_witness_avastha_parity_report(
    *,
    witness_dir: str | Path,
    pl_root: str | Path = "",
    target_reviewed_count: int = 20,
) -> dict[str, Any]:
    audit = audit_jhora_pl_witness_batch(
        jhora_root=witness_dir,
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
            "diagnostic_policy": "Reviewed witness Baladi avastha rows are compared with calculated Baladi rows.",
            "normalization_notes": [
                "Body names are normalized across English, abbreviations and Sanskrit names.",
                "Baladi avastha states are compared as stable case-insensitive keys.",
                "Other avastha layers are skipped until a separate comparison contract is introduced.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "avastha_summary": _avastha_summary(rows),
        "cases": rows,
    }


def render_avastha_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Avastha Parity Report",
        "",
        "Diagnostic comparison of reviewed witness Baladi avastha rows against Jyotish Agent avastha payloads.",
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
        "## Layer summary",
    ]
    for layer, row in sorted(report.get("layer_summary", {}).items()):
        lines.append(
            f"- {layer}: passed {row['passed']}, failed {row['failed']}, missing {row['missing']}, not comparable {row['not_comparable']}"
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
                f"- Failed bodies: {', '.join(row['failed_bodies']) or 'none'}",
                f"- Missing bodies: {', '.join(row['missing_bodies']) or 'none'}",
                f"- Skipped bodies: {', '.join(row['skipped_bodies']) or 'none'}",
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
    skipped_fields: list[str] = []
    skipped_bodies: list[str] = []
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, source_skipped_fields, source_skipped_bodies, missing_kind = _compare_record(record)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        skipped_fields.extend(source_skipped_fields)
        skipped_bodies.extend(source_skipped_bodies)
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
                sorted(set(missing_fields or ["avasthas.baladi"])),
            )
        row["skipped_fields"] = sorted(set(skipped_fields))
        row["skipped_bodies"] = sorted(set(skipped_bodies))
        return row

    failed_bodies = sorted({str(item["body"]) for item in field_results if not item.get("passed")})
    matched_bodies = sorted({str(item["body"]) for item in field_results if item.get("passed")})
    checked_bodies = sorted({str(item["body"]) for item in field_results})
    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
    return {
        "case_id": str(case_row["id"]),
        "source": ",".join(sources_present),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "checked_layers": ["baladi_avastha"],
        "failed_layers": ["baladi_avastha"] if failed_fields else [],
        "missing_layers": [],
        "checked_bodies": checked_bodies,
        "matched_bodies": matched_bodies,
        "failed_bodies": failed_bodies,
        "missing_bodies": sorted({_body_from_missing_field(field) for field in missing_fields if _body_from_missing_field(field)}),
        "skipped_bodies": sorted(set(skipped_bodies)),
        "checked_fields": sorted({str(item["field"]) for item in field_results}),
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
        "source": ",".join(sources_present),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": status,
        "checked_layers": [],
        "failed_layers": [],
        "missing_layers": ["baladi_avastha"] if missing_fields else [],
        "checked_bodies": [],
        "matched_bodies": [],
        "failed_bodies": [],
        "missing_bodies": [],
        "skipped_bodies": [],
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


def _compare_record(
    record: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], list[str], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected_rows, skipped_fields, skipped_bodies = _expected_baladi_rows(fixture, str(record["source"]))
    actual = _actual_baladi_rows(chart)
    if not expected_rows and not skipped_fields:
        return [], [f"{record['source']}.avasthas.baladi"], [], [], "witness"
    if not actual:
        return [], ["calculated.avasthas.baladi"], skipped_fields, skipped_bodies, "calculated"
    results, missing = _compare_baladi(expected_rows, actual, str(record["source"]))
    if not results and skipped_fields:
        return [], ["avasthas.baladi.comparable_rows"], skipped_fields, skipped_bodies, "unsupported"
    if not results:
        return [], missing or ["calculated.avasthas.baladi"], skipped_fields, skipped_bodies, "calculated"
    return results, missing, skipped_fields, skipped_bodies, ""


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


def _expected_baladi_rows(fixture: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    sources: list[dict[str, Any]] = []
    expected = fixture.get("expected") if isinstance(fixture.get("expected"), dict) else {}
    jhora_expected = fixture.get("jhora_expected") if isinstance(fixture.get("jhora_expected"), dict) else {}
    for container in (expected.get("avasthas"), jhora_expected.get("avasthas")):
        if isinstance(container, dict):
            sources.append(container)
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        container = manual.get("avasthas")
        if isinstance(container, dict):
            sources.append(container)

    rows: list[dict[str, Any]] = []
    skipped_fields: list[str] = []
    skipped_bodies: list[str] = []
    for container in sources:
        for key in container:
            if key not in {"baladi", "baladi_avastha"}:
                skipped_fields.append(f"avasthas.{_normalized_key(key)}")
                skipped_bodies.extend(_body_keys_from_rows(container.get(key)))
        rows.extend(_generic_baladi_rows(container.get("baladi")))
        rows.extend(_generic_baladi_rows(container.get("baladi_avastha")))
    return rows, sorted(set(skipped_fields)), sorted(set(skipped_bodies))


def _actual_baladi_rows(chart: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = (((chart.get("classical") or {}).get("avasthas") or {}).get("baladi") or [])
    output: dict[str, dict[str, Any]] = {}
    for row in _generic_baladi_rows(rows):
        body = _normalize_body(row.get("body"))
        if body:
            output[body] = row
    return output


def _generic_baladi_rows(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        iterable = value.items()
        rows: list[dict[str, Any]] = []
        for key, item in iterable:
            if isinstance(item, dict):
                rows.append({"body": key, **item})
            elif isinstance(item, str):
                rows.append({"body": key, "state": item})
        return rows
    if isinstance(value, list):
        rows = []
        for item in value:
            if isinstance(item, dict):
                rows.append(dict(item))
            elif isinstance(item, list) and len(item) >= 2:
                rows.append({"body": item[0], "state": item[1]})
        return rows
    return []


def _body_keys_from_rows(value: Any) -> list[str]:
    return [_normalize_body(row.get("body")) for row in _generic_baladi_rows(value) if _normalize_body(row.get("body"))]


def _compare_baladi(
    expected_rows: list[dict[str, Any]],
    actual_by_body: dict[str, dict[str, Any]],
    source: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for expected in expected_rows:
        body = _normalize_body(expected.get("body"))
        state = _normalize_state(expected)
        if not body or not state:
            continue
        actual = actual_by_body.get(body)
        if not actual:
            missing.append(f"baladi_avastha.{body}")
            continue
        actual_state = _normalize_state(actual)
        results.append(
            {
                "source": source,
                "layer": "baladi_avastha",
                "body": body,
                "field": f"baladi_avastha.{body}.state",
                "expected": state,
                "actual": actual_state,
                "passed": state == actual_state,
            }
        )
    return results, missing


def _normalize_state(row: dict[str, Any]) -> str:
    for key in ("state", "avastha", "key", "name"):
        normalized = _normalized_key(row.get(key))
        if normalized:
            return normalized
    return ""


def _normalize_body(value: Any) -> str:
    key = _normalized_key(value)
    return BODY_ALIASES.get(key, str(value or "").strip())


def _normalized_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def _body_from_missing_field(field: str) -> str:
    parts = field.split(".")
    return parts[1] if len(parts) > 1 and parts[0] == "baladi_avastha" else ""


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
    summary = {"baladi_avastha": {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0}}
    for row in rows:
        status = row["comparison_status"]
        if status == "passed":
            summary["baladi_avastha"]["passed"] += 1
        elif status == "failed":
            summary["baladi_avastha"]["failed"] += 1
        elif status in {"missing", "missing_witness"}:
            summary["baladi_avastha"]["missing"] += 1
        elif status in {"not_comparable", "not_reviewed"}:
            summary["baladi_avastha"]["not_comparable"] += 1
    return summary


def _avastha_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        for body in row.get("checked_bodies", []):
            bucket = summary.setdefault(str(body), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            if body in row.get("failed_bodies", []):
                bucket["failed"] += 1
                bucket["missing"] += 1
            else:
                bucket["passed"] += 1
        for body in row.get("missing_bodies", []):
            bucket = summary.setdefault(str(body), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["missing"] += 1
        for body in row.get("skipped_bodies", []):
            bucket = summary.setdefault(str(body), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["skipped"] += 1
        for field in row.get("skipped_fields", []):
            key = str(field).split(".", 1)[1] if "." in str(field) else str(field)
            bucket = summary.setdefault(key, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["skipped"] += 1
    return summary
