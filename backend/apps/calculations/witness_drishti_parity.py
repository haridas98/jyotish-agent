from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-drishti-parity-report-v1"
LAYERS = ("graha_drishti", "rashi_drishti")
LAYER_ALIASES = {
    "graha": "graha_drishti",
    "graha_drishti": "graha_drishti",
    "grahadrishti": "graha_drishti",
    "graha_aspects": "graha_drishti",
    "planetary": "graha_drishti",
    "rashi": "rashi_drishti",
    "rashi_drishti": "rashi_drishti",
    "rashidrishti": "rashi_drishti",
    "rashi_aspects": "rashi_drishti",
    "sign": "rashi_drishti",
}
BODY_ALIASES = {
    "su": "surya",
    "sun": "surya",
    "surya": "surya",
    "mo": "chandra",
    "moon": "chandra",
    "chandra": "chandra",
    "ma": "mangala",
    "mars": "mangala",
    "mangala": "mangala",
    "me": "budha",
    "mercury": "budha",
    "budha": "budha",
    "ju": "guru",
    "jupiter": "guru",
    "guru": "guru",
    "ve": "shukra",
    "venus": "shukra",
    "shukra": "shukra",
    "sa": "shani",
    "saturn": "shani",
    "shani": "shani",
    "rahu": "rahu",
    "ketu": "ketu",
}
SIGN_ALIASES = {
    "1": "mesha",
    "aries": "mesha",
    "mesha": "mesha",
    "2": "vrishabha",
    "taurus": "vrishabha",
    "vrishabha": "vrishabha",
    "3": "mithuna",
    "gemini": "mithuna",
    "mithuna": "mithuna",
    "4": "karka",
    "cancer": "karka",
    "karka": "karka",
    "5": "simha",
    "leo": "simha",
    "simha": "simha",
    "6": "kanya",
    "virgo": "kanya",
    "kanya": "kanya",
    "7": "tula",
    "libra": "tula",
    "tula": "tula",
    "8": "vrischika",
    "scorpio": "vrischika",
    "vrischika": "vrischika",
    "9": "dhanu",
    "sagittarius": "dhanu",
    "dhanu": "dhanu",
    "10": "makara",
    "capricorn": "makara",
    "makara": "makara",
    "11": "kumbha",
    "aquarius": "kumbha",
    "kumbha": "kumbha",
    "12": "meena",
    "pisces": "meena",
    "meena": "meena",
}


def build_witness_drishti_parity_report(
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
            "diagnostic_policy": "Reviewed witness drishti rows are compared with calculated aspect payloads.",
            "normalization_notes": [
                "Graha and sign names are normalized to stable ids.",
                "Comparable keys use layer, source, target and aspect kind.",
                "Unknown optional aspect layers are skipped unless no comparable drishti rows remain.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "drishti_summary": _drishti_summary(rows),
        "cases": rows,
    }


def render_drishti_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Drishti Parity Report",
        "",
        "Diagnostic comparison of reviewed witness drishti rows against Jyotish Agent aspect payloads.",
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
        "## Drishti summary",
    ]
    for key, row in sorted(report.get("drishti_summary", {}).items()):
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
                f"- Failed aspects: {', '.join(row['failed_aspects']) or 'none'}",
                f"- Missing aspects: {', '.join(row['missing_aspects']) or 'none'}",
                f"- Skipped aspects: {', '.join(row['skipped_aspects']) or 'none'}",
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
    skipped_aspects: list[str] = []
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, source_skipped_fields, source_skipped_aspects, missing_kind = _compare_record(
            record
        )
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        skipped_fields.extend(source_skipped_fields)
        skipped_aspects.extend(source_skipped_aspects)
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
                sorted(set(missing_fields or ["drishti.comparable_rows"])),
            )
        row["skipped_fields"] = sorted(set(skipped_fields))
        row["skipped_aspects"] = sorted(set(skipped_aspects))
        return row

    failed_aspects = sorted({str(item["aspect_key"]) for item in field_results if not item.get("passed")})
    matched_aspects = sorted({str(item["aspect_key"]) for item in field_results if item.get("passed")})
    checked_aspects = sorted({str(item["aspect_key"]) for item in field_results})
    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
    checked_layers = sorted({str(item["layer"]) for item in field_results})
    failed_layers = sorted({str(item["layer"]) for item in field_results if not item.get("passed")})
    missing_layers = sorted({_layer_from_field(field) for field in missing_fields if _layer_from_field(field)})
    return {
        "case_id": str(case_row["id"]),
        "source": ",".join(sources_present),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "checked_layers": checked_layers,
        "failed_layers": failed_layers,
        "missing_layers": missing_layers,
        "checked_aspects": checked_aspects,
        "matched_aspects": matched_aspects,
        "failed_aspects": failed_aspects,
        "missing_aspects": sorted(set(missing_fields)),
        "skipped_aspects": sorted(set(skipped_aspects)),
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
        "missing_layers": ["drishti"] if missing_fields else [],
        "checked_aspects": [],
        "matched_aspects": [],
        "failed_aspects": [],
        "missing_aspects": missing_fields,
        "skipped_aspects": [],
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
    expected_rows, skipped_fields, skipped_aspects = _expected_drishti_rows(fixture, str(record["source"]))
    actual_rows = _actual_drishti_rows(chart)
    if not expected_rows and not skipped_fields:
        return [], [f"{record['source']}.drishti"], [], [], "witness"
    if not actual_rows:
        return [], ["calculated.drishti"], skipped_fields, skipped_aspects, "calculated"
    results, missing = _compare_drishti(expected_rows, actual_rows, str(record["source"]))
    if not results and skipped_fields:
        return [], ["drishti.comparable_rows"], skipped_fields, skipped_aspects, "unsupported"
    if not results:
        return [], missing or ["calculated.drishti"], skipped_fields, skipped_aspects, "calculated"
    return results, missing, skipped_fields, skipped_aspects, ""


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


def _expected_drishti_rows(
    fixture: dict[str, Any],
    source: str,
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    sources: list[Any] = []
    expected = fixture.get("expected") if isinstance(fixture.get("expected"), dict) else {}
    jhora_expected = fixture.get("jhora_expected") if isinstance(fixture.get("jhora_expected"), dict) else {}
    for key in ("drishti", "aspects"):
        if key in expected:
            sources.append(expected.get(key))
        if key in jhora_expected:
            sources.append(jhora_expected.get(key))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        for key in ("drishti", "aspects"):
            if key in manual:
                sources.append(manual.get(key))

    rows: list[dict[str, Any]] = []
    skipped_fields: list[str] = []
    skipped_aspects: list[str] = []
    for container in sources:
        layer_rows, skipped = _rows_by_layer(container)
        for layer, items in layer_rows.items():
            rows.extend({"layer": layer, **item} for item in items)
        for skipped_key in skipped:
            skipped_fields.append(f"drishti.{skipped_key}")
            skipped_aspects.append(skipped_key)
    return rows, sorted(set(skipped_fields)), sorted(set(skipped_aspects))


def _actual_drishti_rows(chart: dict[str, Any]) -> dict[str, set[str]]:
    sources = [
        chart.get("drishti"),
        chart.get("aspects"),
        (chart.get("classical") or {}).get("drishti") if isinstance(chart.get("classical"), dict) else None,
        (chart.get("classical") or {}).get("aspects") if isinstance(chart.get("classical"), dict) else None,
    ]
    output: dict[str, set[str]] = {}
    for container in sources:
        layer_rows, _skipped = _rows_by_layer(container)
        for layer, rows in layer_rows.items():
            for row in rows:
                aspect_key = _aspect_key({**row, "layer": layer})
                if aspect_key:
                    output.setdefault(layer, set()).add(aspect_key)
    return output


def _rows_by_layer(value: Any) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    if value is None:
        return {}, []
    if isinstance(value, list):
        rows: dict[str, list[dict[str, Any]]] = {}
        skipped: list[str] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            layer = _normalize_layer(item.get("layer") or item.get("method") or item.get("methodId"))
            if layer in LAYERS:
                rows.setdefault(layer, []).append(dict(item))
            else:
                skipped.append(_normalized_key(item.get("layer") or item.get("method") or "unknown"))
        return rows, skipped
    if not isinstance(value, dict):
        return {}, []

    rows: dict[str, list[dict[str, Any]]] = {}
    skipped: list[str] = []
    for raw_key, raw_rows in value.items():
        layer = _normalize_layer(raw_key)
        if layer not in LAYERS:
            skipped.append(_normalized_key(raw_key))
            continue
        rows.setdefault(layer, []).extend(_generic_rows(raw_rows))
    return rows, skipped


def _generic_rows(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        rows: list[dict[str, Any]] = []
        for key, item in value.items():
            if isinstance(item, dict):
                rows.append({"id": key, **item})
            elif isinstance(item, str):
                rows.append({"id": key, "aspect_kind": item})
        return rows
    if isinstance(value, list):
        rows = []
        for item in value:
            if isinstance(item, dict):
                rows.append(dict(item))
            elif isinstance(item, list) and len(item) >= 3:
                rows.append({"source": item[0], "target": item[1], "aspect_kind": item[2]})
        return rows
    return []


def _compare_drishti(
    expected_rows: list[dict[str, Any]],
    actual_by_layer: dict[str, set[str]],
    source: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for expected in expected_rows:
        layer = str(expected.get("layer") or "")
        aspect_key = _aspect_key(expected)
        if not layer or not aspect_key:
            continue
        actual_keys = actual_by_layer.get(layer)
        if not actual_keys:
            missing.append(f"calculated.{layer}")
            continue
        passed = aspect_key in actual_keys
        results.append(
            {
                "source": source,
                "layer": layer,
                "aspect_key": aspect_key,
                "field": aspect_key,
                "expected": aspect_key,
                "actual": aspect_key if passed else sorted(actual_keys),
                "passed": passed,
            }
        )
    return results, missing


def _aspect_key(row: dict[str, Any]) -> str:
    layer = _normalize_layer(row.get("layer") or row.get("method") or row.get("methodId"))
    if layer not in LAYERS:
        return ""
    source = _entity_ref(
        row,
        ref_keys=("sourceEntityRef", "source_entity_ref", "source_ref", "source"),
        body_keys=("source_body", "sourceBody", "body", "source_graha", "sourceGraha"),
        sign_keys=("source_sign", "sourceSign", "source_rashi", "sourceRashi"),
    )
    target = _entity_ref(
        row,
        ref_keys=("targetEntityRef", "target_entity_ref", "target_ref", "target"),
        body_keys=("target_body", "targetBody", "target_graha", "targetGraha"),
        sign_keys=("target_sign", "targetSign", "target_rashi", "targetRashi"),
    )
    kind = _normalize_aspect_kind(row)
    if not source or not target:
        return ""
    return f"{layer}.{source}.{target}.{kind or 'aspect'}"


def _entity_ref(
    row: dict[str, Any],
    *,
    ref_keys: tuple[str, ...],
    body_keys: tuple[str, ...],
    sign_keys: tuple[str, ...],
) -> str:
    for key in ref_keys:
        if row.get(key):
            return _normalized_key(row.get(key))
    for key in body_keys:
        body = _normalize_body(row.get(key))
        if body:
            return body
    for key in sign_keys:
        sign = _normalize_sign(row.get(key))
        if sign:
            return sign
    return ""


def _normalize_layer(value: Any) -> str:
    key = _normalized_key(value)
    if key in LAYER_ALIASES:
        return LAYER_ALIASES[key]
    if "graha_drishti" in key or "grahadrishti" in key:
        return "graha_drishti"
    if "rashi_drishti" in key or "rashidrishti" in key:
        return "rashi_drishti"
    return key


def _normalize_aspect_kind(row: dict[str, Any]) -> str:
    for key in ("aspectKind", "aspect_kind", "kind", "rule", "aspect", "method", "methodId"):
        value = row.get(key)
        if value:
            normalized = _normalized_key(value)
            if normalized in {"special_10th", "special_10"}:
                return "special_10th"
            if normalized in {"special_9th", "special_9"}:
                return "special_9th"
            if normalized in {"special_8th", "special_8"}:
                return "special_8th"
            if normalized in {"special_7th", "general_7th", "general_7"}:
                return "general_7th" if normalized.startswith("general") else normalized
            if normalized.startswith("aspect_"):
                return normalized
            if normalized in LAYER_ALIASES.values():
                continue
            return normalized
    return ""


def _normalize_body(value: Any) -> str:
    key = _normalized_key(value)
    return BODY_ALIASES.get(key, key)


def _normalize_sign(value: Any) -> str:
    key = _normalized_key(value)
    return SIGN_ALIASES.get(key, key)


def _normalized_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def _layer_from_field(field: str) -> str:
    parts = field.split(".")
    if parts and parts[0] in LAYERS:
        return parts[0]
    if len(parts) > 1 and parts[1] in LAYERS:
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
        status = row["comparison_status"]
        layers = row.get("checked_layers") or row.get("missing_layers") or list(LAYERS)
        for layer in layers:
            if layer not in summary:
                continue
            if status == "passed":
                summary[layer]["passed"] += 1
            elif status == "failed":
                summary[layer]["failed"] += 1
            elif status in {"missing", "missing_witness"}:
                summary[layer]["missing"] += 1
            elif status in {"not_comparable", "not_reviewed"}:
                summary[layer]["not_comparable"] += 1
    return summary


def _drishti_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        for item in row.get("field_results", []):
            key = f"{item.get('layer')}.{_aspect_kind_from_key(str(item.get('aspect_key') or ''))}"
            bucket = summary.setdefault(key, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            if item.get("passed"):
                bucket["passed"] += 1
            else:
                bucket["failed"] += 1
                bucket["missing"] += 1
        for field in row.get("missing_fields", []):
            layer = _layer_from_field(str(field))
            if layer:
                bucket = summary.setdefault(layer, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
                bucket["missing"] += 1
        for aspect in row.get("skipped_aspects", []):
            bucket = summary.setdefault(str(aspect), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["skipped"] += 1
    return summary


def _aspect_kind_from_key(aspect_key: str) -> str:
    parts = aspect_key.split(".")
    return parts[-1] if parts else "aspect"
