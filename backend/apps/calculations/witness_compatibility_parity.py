from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-compatibility-parity-report-v1"
NUMERIC_TOLERANCE = 0.01
LAYERS = ("ashtakuta_total", "kuta_breakdown", "moon_pair", "relationship_context")
KUTA_ORDER = ("varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi")
KUTA_ALIASES = {
    "varna": "varna",
    "varnam": "varna",
    "vashya": "vashya",
    "vasya": "vashya",
    "tara": "tara",
    "dina": "tara",
    "yoni": "yoni",
    "graha_maitri": "graha_maitri",
    "grahamaitri": "graha_maitri",
    "graha_mitri": "graha_maitri",
    "maitri": "graha_maitri",
    "gana": "gana",
    "bhakoot": "bhakoot",
    "bhakuta": "bhakoot",
    "rashi": "bhakoot",
    "nadi": "nadi",
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


def build_witness_compatibility_parity_report(
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
            "tolerance_profile": {"score": NUMERIC_TOLERANCE},
            "diagnostic_policy": "Reviewed witness compatibility rows are compared with Jyotish Agent compatibility payloads.",
            "normalization_notes": [
                "Ashtakuta kuta names are normalized to stable ids.",
                "Score, max score and percent use 0.01 tolerance.",
                "Unknown optional compatibility fields are skipped unless no comparable fields remain.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "kuta_summary": _kuta_summary(rows),
        "cases": rows,
    }


def render_compatibility_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Compatibility Parity Report",
        "",
        "Diagnostic comparison of reviewed witness Ashtakuta rows against Jyotish Agent compatibility payloads.",
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
        "## Kuta summary",
    ]
    for key, row in sorted(report.get("kuta_summary", {}).items()):
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
                f"- Failed kutas: {', '.join(row['failed_kutas']) or 'none'}",
                f"- Missing kutas: {', '.join(row['missing_kutas']) or 'none'}",
                f"- Skipped kutas: {', '.join(row['skipped_kutas']) or 'none'}",
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
    skipped_kutas: list[str] = []
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, source_skipped_fields, source_skipped_kutas, missing_kind = _compare_record(record)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        skipped_fields.extend(source_skipped_fields)
        skipped_kutas.extend(source_skipped_kutas)
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
                sorted(set(missing_fields or ["compatibility.comparable_fields"])),
            )
        row["skipped_fields"] = sorted(set(skipped_fields))
        row["skipped_kutas"] = sorted(set(skipped_kutas))
        return row

    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
    failed_kutas = sorted({str(item["kuta"]) for item in field_results if item.get("kuta") and not item.get("passed")})
    matched_kutas = sorted({str(item["kuta"]) for item in field_results if item.get("kuta") and item.get("passed")})
    checked_kutas = sorted({str(item["kuta"]) for item in field_results if item.get("kuta")})
    checked_layers = sorted({str(item["layer"]) for item in field_results})
    failed_layers = sorted({str(item["layer"]) for item in field_results if not item.get("passed")})
    return {
        "case_id": str(case_row["id"]),
        "source": ",".join(sources_present),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "checked_layers": checked_layers,
        "failed_layers": failed_layers,
        "missing_layers": sorted({_layer_from_field(field) for field in missing_fields if _layer_from_field(field)}),
        "checked_kutas": checked_kutas,
        "matched_kutas": matched_kutas,
        "failed_kutas": failed_kutas,
        "missing_kutas": sorted({_kuta_from_field(field) for field in missing_fields if _kuta_from_field(field)}),
        "skipped_kutas": sorted(set(skipped_kutas)),
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
        "missing_layers": ["compatibility"] if missing_fields else [],
        "checked_kutas": [],
        "matched_kutas": [],
        "failed_kutas": [],
        "missing_kutas": [],
        "skipped_kutas": [],
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


def _compare_record(record: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected, skipped_fields, skipped_kutas = _expected_compatibility(fixture, str(record["source"]))
    actual = _actual_compatibility(chart, fixture)
    if not expected and not skipped_fields:
        return [], [f"{record['source']}.compatibility"], [], [], "witness"
    if not actual:
        return [], ["calculated.compatibility"], skipped_fields, skipped_kutas, "calculated"
    results, missing = _compare_compatibility(expected, actual, str(record["source"]))
    if not results and skipped_fields:
        return [], ["compatibility.comparable_fields"], skipped_fields, skipped_kutas, "unsupported"
    if not results:
        return [], missing or ["calculated.compatibility"], skipped_fields, skipped_kutas, "calculated"
    return results, missing, skipped_fields, skipped_kutas, ""


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


def _expected_compatibility(fixture: dict[str, Any], source: str) -> tuple[dict[str, Any], list[str], list[str]]:
    sources: list[Any] = []
    expected = fixture.get("expected") if isinstance(fixture.get("expected"), dict) else {}
    jhora_expected = fixture.get("jhora_expected") if isinstance(fixture.get("jhora_expected"), dict) else {}
    pl_expected = fixture.get("pl_expected") if isinstance(fixture.get("pl_expected"), dict) else {}
    for container in (expected, jhora_expected, pl_expected):
        for key in ("compatibility", "ashtakuta"):
            if key in container:
                sources.append(container.get(key))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        for key in ("compatibility", "ashtakuta"):
            if key in manual:
                sources.append(manual.get(key))

    for value in sources:
        payload, skipped_fields, skipped_kutas = _coerce_compatibility(value)
        if payload or skipped_fields:
            return payload, skipped_fields, skipped_kutas
    return {}, [], []


def _actual_compatibility(chart: dict[str, Any], fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    for key in ("compatibility", "compatibility_report", "ashtakuta"):
        value = chart.get(key)
        payload, _skipped_fields, _skipped_kutas = _coerce_compatibility(value)
        if payload:
            return payload
    fallback_inputs = [chart]
    if isinstance(fixture, dict):
        fixture_input = fixture.get("input") if isinstance(fixture.get("input"), dict) else {}
        fallback_inputs.extend([fixture, fixture_input])
    for candidate in fallback_inputs:
        if not (isinstance(candidate.get("person_a"), dict) and isinstance(candidate.get("person_b"), dict)):
            continue
        try:
            from .workflows import build_compatibility_report

            payload, _skipped_fields, _skipped_kutas = _coerce_compatibility(build_compatibility_report(candidate))
            return payload
        except Exception:
            continue
    return {}


def _coerce_compatibility(value: Any) -> tuple[dict[str, Any], list[str], list[str]]:
    if not isinstance(value, dict):
        return {}, [], []
    score = _coerce_score(value)
    kutas = _coerce_kutas(value)
    moon_pair = _coerce_moon_pair(value)
    relationship_context = value.get("relationship_context") if isinstance(value.get("relationship_context"), dict) else {}
    payload: dict[str, Any] = {}
    if score:
        payload["score"] = score
    if kutas:
        payload["kutas"] = kutas
    if moon_pair:
        payload["moon_pair"] = moon_pair
    if relationship_context:
        payload["relationship_context"] = relationship_context
    known = {
        "score",
        "total",
        "total_score",
        "max",
        "max_score",
        "percent",
        "percentage",
        "kuta",
        "kutas",
        "kuta_rows",
        "moon",
        "moon_pair",
        "relationship_context",
    }
    skipped_keys = [_normalized_key(key) for key in value if _normalized_key(key) not in known]
    return payload, [f"compatibility.{key}" for key in skipped_keys], skipped_keys


def _coerce_score(value: dict[str, Any]) -> dict[str, float]:
    score = value.get("score") if isinstance(value.get("score"), dict) else value
    output: dict[str, float] = {}
    for target, keys in {
        "total": ("total", "total_score", "score"),
        "max": ("max", "max_score", "maximum"),
        "percent": ("percent", "percentage"),
    }.items():
        for key in keys:
            number = _safe_float(score.get(key) if isinstance(score, dict) else None)
            if number is not None:
                output[target] = number
                break
    return output


def _coerce_kutas(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = [value.get("kuta"), value.get("kutas"), value.get("kuta_rows")]
    for source in sources:
        output = _kutas_from_value(source)
        if output:
            return output
    return {}


def _kutas_from_value(value: Any) -> dict[str, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, dict):
                rows.append({"name": key, **item})
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                rows.append(dict(item))
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        kuta = _normalize_kuta(row.get("id") or row.get("key") or row.get("name") or row.get("kuta"))
        if not kuta:
            continue
        output[kuta] = {
            "score": _safe_float(_first_present(row, ("score", "points"))),
            "max": _safe_float(_first_present(row, ("max_score", "max", "maximum"))),
            "status": _normalized_key(row.get("status") or row.get("result")),
        }
    return output


def _coerce_moon_pair(value: dict[str, Any]) -> dict[str, Any]:
    moon = value.get("moon_pair") if isinstance(value.get("moon_pair"), dict) else value.get("moon")
    if not isinstance(moon, dict):
        return {}
    person_a = moon.get("person_a") if isinstance(moon.get("person_a"), dict) else {}
    person_b = moon.get("person_b") if isinstance(moon.get("person_b"), dict) else {}
    return {
        "person_a": _coerce_moon_placement(person_a),
        "person_b": _coerce_moon_placement(person_b),
        "rashi_distance_a_to_b": _safe_int(
            moon.get("rashi_distance_a_to_b") if moon.get("rashi_distance_a_to_b") is not None else moon.get("distance")
        ),
        "rashi_distance_b_to_a": _safe_int(moon.get("rashi_distance_b_to_a")),
    }


def _coerce_moon_placement(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "rashi": _normalize_rashi(value.get("rashi") or value.get("sign")),
        "nakshatra": _normalized_key(value.get("nakshatra")),
        "pada": _safe_int(value.get("pada")),
    }


def _compare_compatibility(expected: dict[str, Any], actual: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    results.extend(_compare_score(expected.get("score") or {}, actual.get("score") or {}, source))
    kuta_results, kuta_missing = _compare_kutas(expected.get("kutas") or {}, actual.get("kutas") or {}, source)
    results.extend(kuta_results)
    missing.extend(kuta_missing)
    results.extend(_compare_moon_pair(expected.get("moon_pair") or {}, actual.get("moon_pair") or {}, source))
    if expected.get("relationship_context") and not actual.get("relationship_context"):
        missing.append("relationship_context")
    elif expected.get("relationship_context"):
        for key, expected_value in sorted(expected["relationship_context"].items()):
            actual_value = (actual["relationship_context"] or {}).get(key)
            results.append(
                _result(
                    source=source,
                    layer="relationship_context",
                    field=f"relationship_context.{_normalized_key(key)}",
                    expected=_normalized_key(expected_value),
                    actual=_normalized_key(actual_value),
                    passed=_normalized_key(expected_value) == _normalized_key(actual_value),
                )
            )
    return results, missing


def _compare_score(expected: dict[str, Any], actual: dict[str, Any], source: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for key in ("total", "max", "percent"):
        if expected.get(key) is None:
            continue
        expected_value = _safe_float(expected.get(key))
        actual_value = _safe_float(actual.get(key))
        results.append(
            _result(
                source=source,
                layer="ashtakuta_total",
                field=f"ashtakuta_total.{key}",
                expected=expected_value,
                actual=actual_value,
                passed=_numbers_equal(expected_value, actual_value),
            )
        )
    return results


def _compare_kutas(expected: dict[str, dict[str, Any]], actual: dict[str, dict[str, Any]], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for kuta, expected_row in expected.items():
        actual_row = actual.get(kuta)
        if not actual_row:
            missing.append(f"kuta_breakdown.{kuta}")
            continue
        for key in ("score", "max", "status"):
            if expected_row.get(key) in (None, ""):
                continue
            expected_value = expected_row.get(key)
            actual_value = actual_row.get(key)
            passed = _numbers_equal(expected_value, actual_value) if key in {"score", "max"} else expected_value == actual_value
            results.append(
                _result(
                    source=source,
                    layer="kuta_breakdown",
                    field=f"kuta_breakdown.{kuta}.{key}",
                    expected=expected_value,
                    actual=actual_value,
                    passed=passed,
                    kuta=kuta,
                )
            )
    return results, missing


def _compare_moon_pair(expected: dict[str, Any], actual: dict[str, Any], source: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for person in ("person_a", "person_b"):
        expected_person = expected.get(person) if isinstance(expected.get(person), dict) else {}
        actual_person = actual.get(person) if isinstance(actual.get(person), dict) else {}
        for key in ("rashi", "nakshatra", "pada"):
            if expected_person.get(key) in (None, ""):
                continue
            results.append(
                _result(
                    source=source,
                    layer="moon_pair",
                    field=f"moon_pair.{person}.{key}",
                    expected=expected_person.get(key),
                    actual=actual_person.get(key),
                    passed=expected_person.get(key) == actual_person.get(key),
                )
            )
    for key in ("rashi_distance_a_to_b", "rashi_distance_b_to_a"):
        if expected.get(key) is None:
            continue
        results.append(
            _result(
                source=source,
                layer="moon_pair",
                field=f"moon_pair.{key}",
                expected=expected.get(key),
                actual=actual.get(key),
                passed=expected.get(key) == actual.get(key),
            )
        )
    return results


def _result(
    *,
    source: str,
    layer: str,
    field: str,
    expected: Any,
    actual: Any,
    passed: bool,
    kuta: str = "",
) -> dict[str, Any]:
    return {
        "source": source,
        "layer": layer,
        "field": field,
        "kuta": kuta,
        "expected": expected,
        "actual": actual,
        "passed": passed,
    }


def _numbers_equal(expected: Any, actual: Any) -> bool:
    expected_float = _safe_float(expected)
    actual_float = _safe_float(actual)
    if expected_float is None or actual_float is None:
        return False
    return math.isclose(expected_float, actual_float, abs_tol=NUMERIC_TOLERANCE)


def _normalize_kuta(value: Any) -> str:
    key = _normalized_key(value)
    return KUTA_ALIASES.get(key, key if key in KUTA_ORDER else "")


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


def _first_present(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in row and row.get(key) is not None:
            return row.get(key)
    return None


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _layer_from_field(field: str) -> str:
    parts = field.split(".")
    return parts[0] if parts and parts[0] in LAYERS else ""


def _kuta_from_field(field: str) -> str:
    parts = field.split(".")
    return parts[1] if len(parts) > 1 and parts[0] == "kuta_breakdown" else ""


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


def _kuta_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        for kuta in row.get("checked_kutas", []):
            bucket = summary.setdefault(kuta, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            if kuta in row.get("failed_kutas", []):
                bucket["failed"] += 1
            else:
                bucket["passed"] += 1
        for kuta in row.get("missing_kutas", []):
            bucket = summary.setdefault(str(kuta), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["missing"] += 1
        for kuta in row.get("skipped_kutas", []):
            bucket = summary.setdefault(str(kuta), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["skipped"] += 1
    return summary
