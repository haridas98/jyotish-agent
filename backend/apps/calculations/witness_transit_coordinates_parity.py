from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .transit_coordinates import transit_coordinate_snapshot
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-transit-coordinate-parity-report-v1"
LONGITUDE_TOLERANCE_ARCSECONDS = 1.0
LAYERS = (
    "transit_context",
    "transit_lagna",
    "transit_graha_longitudes",
    "transit_graha_rashi",
    "transit_graha_nakshatra",
)
SNAPSHOT_KEYS = {
    "schemaVersion",
    "methodId",
    "methodVersion",
    "calculationPreset",
    "ayanamshaId",
    "nodeType",
    "timezone",
    "localDateTime",
    "utcDateTime",
    "location",
    "lagna",
    "grahas",
}
BODY_ALIASES = {
    "lagna": "lagna",
    "ascendant": "lagna",
    "asc": "lagna",
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


def build_witness_transit_coordinates_parity_report(
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
            "tolerance_profile": {"longitude_arcseconds": LONGITUDE_TOLERANCE_ARCSECONDS},
            "diagnostic_policy": "Reviewed witness transit coordinate snapshots are compared with calculated transit coordinate snapshots.",
            "normalization_notes": [
                "Graha and Lagna body names are normalized to stable ids.",
                "Longitude comparison uses circular absolute delta with one arcsecond tolerance.",
                "Unknown optional transit coordinate fields are skipped unless no comparable fields remain.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "body_summary": _body_summary(rows),
        "cases": rows,
    }


def render_transit_coordinates_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    tolerance = ((report.get("metadata") or {}).get("tolerance_profile") or {}).get("longitude_arcseconds")
    lines = [
        "# Transit Coordinate Parity Report",
        "",
        "Diagnostic comparison of reviewed witness transit coordinate snapshots against Jyotish Agent snapshots.",
        "JHora and Parashara Light are used only as witness sources for comparison.",
        "",
        f"- Longitude tolerance: {tolerance} arcseconds",
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
        source_results, source_missing, source_skipped_fields, source_skipped_bodies, missing_kind = _compare_record(
            record
        )
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
                sorted(set(missing_fields or ["transit_coordinates.comparable_fields"])),
            )
        row["skipped_fields"] = sorted(set(skipped_fields))
        row["skipped_bodies"] = sorted(set(skipped_bodies))
        return row

    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
    checked_layers = sorted({str(item["layer"]) for item in field_results})
    failed_layers = sorted({str(item["layer"]) for item in field_results if not item.get("passed")})
    failed_bodies = sorted({str(item["body"]) for item in field_results if item.get("body") != "context" and not item.get("passed")})
    matched_bodies = sorted({str(item["body"]) for item in field_results if item.get("body") != "context" and item.get("passed")})
    checked_bodies = sorted({str(item["body"]) for item in field_results if item.get("body") != "context"})
    return {
        "case_id": str(case_row["id"]),
        "source": ",".join(sources_present),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "checked_layers": checked_layers,
        "failed_layers": failed_layers,
        "missing_layers": sorted({_layer_from_field(field) for field in missing_fields if _layer_from_field(field)}),
        "checked_bodies": checked_bodies,
        "matched_bodies": matched_bodies,
        "failed_bodies": failed_bodies,
        "missing_bodies": sorted({_body_from_field(field) for field in missing_fields if _body_from_field(field)}),
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
        "missing_layers": ["transit_coordinates"] if missing_fields else [],
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
    expected, skipped_fields, skipped_bodies = _expected_snapshot(fixture, str(record["source"]))
    actual = _actual_snapshot(chart)
    if not expected and not skipped_fields:
        return [], [f"{record['source']}.transit_coordinates"], [], [], "witness"
    if not actual:
        return [], ["calculated.transit_coordinates"], skipped_fields, skipped_bodies, "calculated"
    results, missing = _compare_snapshot(expected, actual, str(record["source"]))
    if not results and skipped_fields:
        return [], ["transit_coordinates.comparable_fields"], skipped_fields, skipped_bodies, "unsupported"
    if not results:
        return [], missing or ["calculated.transit_coordinates"], skipped_fields, skipped_bodies, "calculated"
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


def _expected_snapshot(fixture: dict[str, Any], source: str) -> tuple[dict[str, Any], list[str], list[str]]:
    sources: list[Any] = []
    expected = fixture.get("expected") if isinstance(fixture.get("expected"), dict) else {}
    jhora_expected = fixture.get("jhora_expected") if isinstance(fixture.get("jhora_expected"), dict) else {}
    for key in ("transit_coordinates", "transits"):
        if key in expected:
            sources.append(expected.get(key))
        if key in jhora_expected:
            sources.append(jhora_expected.get(key))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        for key in ("transit_coordinates", "transits"):
            if key in manual:
                sources.append(manual.get(key))

    for value in sources:
        snapshot, skipped_fields, skipped_bodies = _coerce_snapshot(value)
        if snapshot or skipped_fields:
            return snapshot, skipped_fields, skipped_bodies
    return {}, [], []


def _actual_snapshot(chart: dict[str, Any]) -> dict[str, Any]:
    for key in ("transit_coordinate_snapshot", "transit_coordinates", "transitCoordinateSnapshot"):
        value = chart.get(key)
        if isinstance(value, dict):
            return value
    if isinstance(chart.get("birth"), dict) and (isinstance(chart.get("grahas"), list) or isinstance(chart.get("ascendant"), dict)):
        return transit_coordinate_snapshot(chart)
    return {}


def _coerce_snapshot(value: Any) -> tuple[dict[str, Any], list[str], list[str]]:
    if not isinstance(value, dict):
        return {}, [], []
    if isinstance(value.get("snapshot"), dict):
        base = dict(value["snapshot"])
        extras = {key: item for key, item in value.items() if key != "snapshot"}
    else:
        base = {key: item for key, item in value.items() if key in SNAPSHOT_KEYS}
        extras = {key: item for key, item in value.items() if key not in SNAPSHOT_KEYS}
    skipped_fields = [f"transit_coordinates.{_normalized_key(key)}" for key in extras]
    skipped_bodies = [_normalized_key(key) for key in extras]
    return base, sorted(set(skipped_fields)), sorted(set(skipped_bodies))


def _compare_snapshot(expected: dict[str, Any], actual: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    results.extend(_compare_context(expected, actual, source))
    expected_lagna = expected.get("lagna") if isinstance(expected.get("lagna"), dict) else {}
    actual_lagna = actual.get("lagna") if isinstance(actual.get("lagna"), dict) else {}
    if expected_lagna:
        if actual_lagna:
            results.extend(_compare_placement(expected_lagna, actual_lagna, source, "lagna", is_lagna=True))
        else:
            missing.append("transit_lagna.lagna")

    actual_grahas = _grahas_by_body(actual.get("grahas"))
    for body, expected_row in _grahas_by_body(expected.get("grahas")).items():
        actual_row = actual_grahas.get(body)
        if not actual_row:
            missing.append(f"transit_graha_longitudes.{body}")
            continue
        results.extend(_compare_placement(expected_row, actual_row, source, body, is_lagna=False))
    return results, missing


def _compare_context(expected: dict[str, Any], actual: dict[str, Any], source: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for key in ("calculationPreset", "ayanamshaId", "nodeType", "timezone", "localDateTime", "utcDateTime"):
        if expected.get(key) is None:
            continue
        expected_value = _normalized_key(expected.get(key))
        actual_value = _normalized_key(actual.get(key))
        field = f"transit_context.{key}"
        results.append(
            {
                "source": source,
                "layer": "transit_context",
                "body": "context",
                "field": field,
                "expected": expected_value,
                "actual": actual_value,
                "passed": expected_value == actual_value,
            }
        )
    return results


def _compare_placement(
    expected: dict[str, Any],
    actual: dict[str, Any],
    source: str,
    body: str,
    *,
    is_lagna: bool,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    longitude_layer = "transit_lagna" if is_lagna else "transit_graha_longitudes"
    if expected.get("longitude") is not None:
        delta = _longitude_delta_arcseconds(expected.get("longitude"), actual.get("longitude"))
        results.append(
            {
                "source": source,
                "layer": longitude_layer,
                "body": body,
                "field": f"{longitude_layer}.{body}.longitude",
                "expected": _safe_float(expected.get("longitude")),
                "actual": _safe_float(actual.get("longitude")),
                "delta_arcseconds": delta,
                "tolerance_arcseconds": LONGITUDE_TOLERANCE_ARCSECONDS,
                "passed": delta <= LONGITUDE_TOLERANCE_ARCSECONDS,
            }
        )
    rashi_layer = "transit_lagna" if is_lagna else "transit_graha_rashi"
    for key in ("rashi", "rashiIndex"):
        if expected.get(key) is None:
            continue
        expected_value = _normalize_rashi(expected.get(key)) if key == "rashi" else _normalized_key(expected.get(key))
        actual_value = _normalize_rashi(actual.get(key)) if key == "rashi" else _normalized_key(actual.get(key))
        results.append(
            {
                "source": source,
                "layer": rashi_layer,
                "body": body,
                "field": f"{rashi_layer}.{body}.{key}",
                "expected": expected_value,
                "actual": actual_value,
                "passed": expected_value == actual_value,
            }
        )
    nakshatra_layer = "transit_lagna" if is_lagna else "transit_graha_nakshatra"
    for key in ("nakshatra", "nakshatraIndex", "pada"):
        if expected.get(key) is None:
            continue
        expected_value = _normalized_key(expected.get(key))
        actual_value = _normalized_key(actual.get(key))
        results.append(
            {
                "source": source,
                "layer": nakshatra_layer,
                "body": body,
                "field": f"{nakshatra_layer}.{body}.{key}",
                "expected": expected_value,
                "actual": actual_value,
                "passed": expected_value == actual_value,
            }
        )
    return results


def _grahas_by_body(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for row in value:
        if not isinstance(row, dict):
            continue
        body = _normalize_body(row.get("body"))
        if body:
            result[body] = row
    return result


def _normalize_body(value: Any) -> str:
    key = _normalized_key(value)
    return BODY_ALIASES.get(key, key)


def _normalize_rashi(value: Any) -> str:
    key = _normalized_key(value)
    return SIGN_ALIASES.get(key, key)


def _normalized_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _longitude_delta_arcseconds(expected: Any, actual: Any) -> float:
    expected_float = _safe_float(expected)
    actual_float = _safe_float(actual)
    if expected_float is None or actual_float is None:
        return math.inf
    delta = abs((expected_float - actual_float + 180.0) % 360.0 - 180.0)
    return delta * 3600.0


def _layer_from_field(field: str) -> str:
    parts = field.split(".")
    return parts[0] if parts and parts[0] in LAYERS else ""


def _body_from_field(field: str) -> str:
    parts = field.split(".")
    return parts[1] if len(parts) > 1 and parts[0] in LAYERS else ""


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
                if layer in row.get("failed_layers", []):
                    summary[layer]["failed"] += 1
                else:
                    summary[layer]["passed"] += 1
            elif status in {"missing", "missing_witness"}:
                summary[layer]["missing"] += 1
            elif status in {"not_comparable", "not_reviewed"}:
                summary[layer]["not_comparable"] += 1
    return summary


def _body_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
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
    return summary
