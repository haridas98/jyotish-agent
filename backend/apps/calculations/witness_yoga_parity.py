from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-yoga-parity-report-v1"
LAYERS = ("active_yogas",)
YOGA_ALIASES = {
    "ruchaka": ("ruchaka", "ruchaka_yoga", "ruchaka_mahapurusha"),
    "budha_aditya": ("budha_aditya", "budha_aditya_yoga", "budhaditya", "budhaditya_yoga"),
    "gaja_kesari": ("gaja_kesari", "gaja_kesari_yoga", "gajakesari", "gajakesari_yoga"),
    "chandra_mangala": (
        "chandra_mangala",
        "chandra_mangala_yoga",
        "chandramangala",
        "chandramangala_yoga",
    ),
    "viparita_raja_yoga": (
        "viparita_raja_yoga",
        "vipareeta_raja_yoga",
        "viparita",
        "vipareeta",
        "viparita_harsha",
        "viparita_sarala",
        "viparita_vimala",
        "dusthana_lord_exchange_viparita",
    ),
    "yogada_gl": ("yogada_gl", "yogada_gulika_lagna", "yogada_gulika", "yogada"),
    "yogada_hl": ("yogada_hl", "yogada_hora_lagna", "yogada_hora"),
    "raja_yoga": (
        "raja_yoga",
        "rajayoga",
        "kendra_trikona_raja",
        "dharma_karmadhipati_raja",
        "lagna_lord_kendra_trikona_raja",
    ),
}
ALIAS_TO_CANONICAL = {
    alias: canonical
    for canonical, aliases in YOGA_ALIASES.items()
    for alias in aliases
}


def build_witness_yoga_parity_report(
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
            "alias_policy": "Witness active yoga names are compared through stable normalized aliases.",
            "normalization_notes": [
                "JHora active-yoga table rows use the visible yoga name as witness input.",
                "Manual witness rows may provide key, name or yoga fields.",
                "Calculated catalog rows with present=false are not active matches.",
                "Unknown witness yoga names are skipped unless another comparable active yoga exists.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "yoga_summary": _yoga_summary(rows),
        "cases": rows,
    }


def render_yoga_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Yoga Parity Report",
        "",
        "Diagnostic comparison of reviewed witness active-yoga rows against Jyotish Agent yoga payloads.",
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
                f"- Failed yogas: {', '.join(row['failed_yogas']) or 'none'}",
                f"- Missing yogas: {', '.join(row['missing_yogas']) or 'none'}",
                f"- Skipped yogas: {', '.join(row['skipped_yogas']) or 'none'}",
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
    skipped_yogas: list[str] = []
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, source_skipped, missing_kind = _compare_record(record)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        skipped_yogas.extend(source_skipped)
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
            sorted(set(missing_fields or ["active_yogas"])),
        )
        row["skipped_yogas"] = sorted(set(skipped_yogas))
        return row

    failed_yogas = sorted({str(item["expected_key"]) for item in field_results if not item.get("passed")})
    matched_yogas = sorted({str(item["expected_key"]) for item in field_results if item.get("passed")})
    checked_yogas = sorted({str(item["expected_key"]) for item in field_results})
    failed_fields = [f"active_yogas.{item}" for item in failed_yogas]
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_yogas else "passed",
        "checked_layers": ["active_yogas"],
        "failed_layers": ["active_yogas"] if failed_yogas else [],
        "missing_layers": [],
        "checked_yogas": checked_yogas,
        "matched_yogas": matched_yogas,
        "failed_yogas": failed_yogas,
        "missing_yogas": failed_yogas,
        "skipped_yogas": sorted(set(skipped_yogas)),
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
        "missing_layers": ["active_yogas"] if missing_fields else [],
        "checked_yogas": [],
        "matched_yogas": [],
        "failed_yogas": [],
        "missing_yogas": [],
        "skipped_yogas": [],
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
    rows = _expected_active_yogas(fixture, str(record["source"]))
    actual = _actual_active_yogas(chart)
    if not rows:
        return [], [f"{record['source']}.active_yogas"], [], "witness"
    if not actual:
        return [], ["calculated.active_yogas"], [], "calculated"
    results, skipped = _compare_active_yogas(rows, actual, str(record["source"]))
    if not results and skipped:
        return [], ["active_yogas.comparable_name"], skipped, "unsupported"
    return results, [], skipped, ""


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


def _expected_active_yogas(fixture: dict[str, Any], source: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    expected = fixture.get("expected") if isinstance(fixture.get("expected"), dict) else {}
    rows.extend(_jhora_ui_active_yoga_rows(expected))
    rows.extend(_generic_active_yoga_rows(expected.get("active_yogas") if isinstance(expected, dict) else None))
    yogas = expected.get("yogas") if isinstance(expected.get("yogas"), dict) else {}
    rows.extend(_generic_active_yoga_rows(yogas.get("active") if isinstance(yogas, dict) else None))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        rows.extend(_generic_active_yoga_rows(manual.get("active_yogas") if isinstance(manual, dict) else None))
        manual_yogas = manual.get("yogas") if isinstance(manual.get("yogas"), dict) else {}
        rows.extend(_generic_active_yoga_rows(manual_yogas.get("active") if isinstance(manual_yogas, dict) else None))
    return rows


def _jhora_ui_active_yoga_rows(expected: dict[str, Any]) -> list[dict[str, Any]]:
    ui_tables = expected.get("ui_tables") if isinstance(expected.get("ui_tables"), dict) else {}
    identified = ui_tables.get("identified") if isinstance(ui_tables.get("identified"), dict) else {}
    active_yogas = identified.get("active_yogas") if isinstance(identified.get("active_yogas"), dict) else {}
    rows = active_yogas.get("rows")
    if not isinstance(rows, list):
        return []
    output = []
    for row in rows:
        if not isinstance(row, list) or len(row) < 1:
            continue
        output.append(
            {
                "yoga": row[0],
                "varga": row[1] if len(row) > 1 else "",
                "givers": row[2] if len(row) > 2 else "",
                "result": row[3] if len(row) > 3 else "",
                "definition": row[4] if len(row) > 4 else "",
                "name_only": True,
            }
        )
    return output


def _generic_active_yoga_rows(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        iterable = value.values()
    elif isinstance(value, list):
        iterable = value
    else:
        iterable = [value]
    rows: list[dict[str, Any]] = []
    for item in iterable:
        if isinstance(item, dict):
            rows.append(dict(item))
        elif isinstance(item, list) and item:
            rows.append({"yoga": item[0], "name_only": True})
        elif isinstance(item, str):
            rows.append({"yoga": item, "name_only": True})
    return rows


def _actual_active_yogas(chart: dict[str, Any]) -> set[str]:
    items = ((chart.get("classical") or {}).get("yogas") or {}).get("items")
    if not isinstance(items, list):
        return set()
    keys: set[str] = set()
    for yoga in items:
        if not isinstance(yoga, dict) or yoga.get("present") is False:
            continue
        for field in ("key", "name"):
            normalized = _normalized_key(yoga.get(field))
            if not normalized:
                continue
            keys.add(normalized)
            canonical = ALIAS_TO_CANONICAL.get(normalized)
            if canonical:
                keys.add(canonical)
    return keys


def _compare_active_yogas(
    rows: list[dict[str, Any]],
    actual_yogas: set[str],
    source: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    skipped: list[str] = []
    for row in rows:
        comparable_key = _expected_comparable_key(row)
        display_key = _expected_display_key(row)
        if not comparable_key:
            if display_key:
                skipped.append(display_key)
            continue
        matched_key = comparable_key if comparable_key in actual_yogas else ""
        aliases = _aliases_for(comparable_key)
        if not matched_key:
            matched_key = next((alias for alias in aliases if alias in actual_yogas), "")
        results.append(
            {
                "source": source,
                "layer": "active_yogas",
                "field": f"active_yogas.{comparable_key}",
                "expected_key": comparable_key,
                "expected_name": str(row.get("name") or row.get("yoga") or row.get("key") or ""),
                "aliases": aliases,
                "matched_key": matched_key,
                "varga": str(row.get("varga") or ""),
                "givers": str(row.get("givers") or ""),
                "definition": str(row.get("definition") or ""),
                "result": str(row.get("result") or ""),
                "passed": bool(matched_key),
            }
        )
    return results, skipped


def _expected_comparable_key(row: dict[str, Any]) -> str:
    key = _normalized_key(row.get("key"))
    if key:
        return ALIAS_TO_CANONICAL.get(key, key)
    name = _normalized_key(row.get("name") or row.get("yoga"))
    return ALIAS_TO_CANONICAL.get(name, "")


def _expected_display_key(row: dict[str, Any]) -> str:
    return _normalized_key(row.get("key") or row.get("name") or row.get("yoga"))


def _aliases_for(key: str) -> list[str]:
    aliases = set(YOGA_ALIASES.get(key, (key,)))
    aliases.add(key)
    return sorted(aliases)


def _normalized_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


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
    summary = {"active_yogas": {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0}}
    for row in rows:
        if row["comparison_status"] == "passed":
            summary["active_yogas"]["passed"] += 1
        elif row["comparison_status"] == "failed":
            summary["active_yogas"]["failed"] += 1
        elif row["comparison_status"] in {"missing", "missing_witness"}:
            summary["active_yogas"]["missing"] += 1
        elif row["comparison_status"] in {"not_comparable", "not_reviewed"}:
            summary["active_yogas"]["not_comparable"] += 1
    return summary


def _yoga_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        for key in row.get("checked_yogas", []):
            bucket = summary.setdefault(str(key), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            if key in row.get("failed_yogas", []):
                bucket["failed"] += 1
                bucket["missing"] += 1
            else:
                bucket["passed"] += 1
        for key in row.get("skipped_yogas", []):
            bucket = summary.setdefault(str(key), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["skipped"] += 1
    return summary
