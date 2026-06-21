from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-tajaka-parity-report-v1"
NUMERIC_TOLERANCE = 0.01
LAYERS = (
    "tajaka_context",
    "tithi_pravesha_link",
    "annual_lagna",
    "muntha",
    "annual_bodies",
    "annual_panchanga",
    "open_items",
)
PAYLOAD_KEYS = ("tajaka", "tajaka_report", "varshaphala")
PANCHANGA_FIELDS = ("tithi", "nakshatra", "yoga", "karana", "vara")
KNOWN_RETURN_KEYS = {
    "status",
    "target_year",
    "tithi_pravesha",
    "tithi_pravesha_report",
    "annual_return",
    "annual_context",
    "tajaka",
    "varshaphala",
    "annual_lagna",
    "annual_sun",
    "annual_moon",
    "muntha",
    "panchanga",
    "annual_panchanga",
    "open_items",
}


def build_witness_tajaka_parity_report(
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
            "tolerance_profile": {"degrees": NUMERIC_TOLERANCE},
            "diagnostic_policy": (
                "Reviewed witness Tajaka rows are compared with Jyotish Agent Tajaka payloads."
            ),
            "normalization_notes": [
                "Tajaka, Varshaphala and nested Tithi Pravesha Tajaka payloads are normalized.",
                "Annual lagna, Sun and Moon degree fields use 0.01 degree tolerance.",
                "Unknown optional Tajaka fields are skipped unless no comparable fields remain.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "field_summary": _field_summary(rows),
        "cases": rows,
    }


def render_tajaka_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Tajaka Parity Report",
        "",
        "Diagnostic comparison of reviewed witness Tajaka rows against Jyotish Agent Tajaka payloads.",
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
            f"- {layer}: passed {row['passed']}, failed {row['failed']}, "
            f"missing {row['missing']}, not comparable {row['not_comparable']}"
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
            row = _empty_case(case_row, "missing_witness", sources_present, review_statuses, sorted(set(missing_fields)))
        else:
            row = _empty_case(
                case_row,
                "not_comparable",
                sources_present,
                review_statuses,
                sorted(set(missing_fields or ["tajaka.comparable_fields"])),
            )
        row["skipped_fields"] = sorted(set(skipped_fields))
        return row

    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
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
        "missing_layers": ["tajaka"] if missing_fields else [],
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
    expected, skipped_fields = _expected_return(fixture, str(record["source"]))
    actual = _actual_return(chart, fixture)
    if not expected and not skipped_fields:
        return [], [f"{record['source']}.tajaka"], [], "witness"
    if not actual:
        return [], ["calculated.tajaka"], skipped_fields, "calculated"
    results, missing = _compare_return(expected, actual, str(record["source"]))
    if not results and skipped_fields:
        return [], ["tajaka.comparable_fields"], skipped_fields, "unsupported"
    if not results:
        return [], missing or ["calculated.tajaka"], skipped_fields, "calculated"
    return results, missing, skipped_fields, ""


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


def _expected_return(fixture: dict[str, Any], source: str) -> tuple[dict[str, Any], list[str]]:
    sources: list[Any] = []
    for container_name in ("expected", "jhora_expected", "pl_expected"):
        container = fixture.get(container_name) if isinstance(fixture.get(container_name), dict) else {}
        sources.extend(_tajaka_payload_candidates(container))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        sources.extend(_tajaka_payload_candidates(manual))

    for value in sources:
        payload, skipped_fields = _coerce_return(value)
        if payload or skipped_fields:
            return payload, skipped_fields
    return {}, []


def _tajaka_payload_candidates(container: dict[str, Any]) -> list[Any]:
    if not isinstance(container, dict):
        return []
    candidates: list[Any] = []
    for key in PAYLOAD_KEYS:
        if key in container:
            candidates.append(container.get(key))
    for key in ("annual_return", "tithi_pravesha", "tithi_pravesha_report"):
        nested = container.get(key) if isinstance(container.get(key), dict) else {}
        if "tajaka" in nested:
            candidates.append(nested.get("tajaka"))
    return candidates


def _actual_return(chart: dict[str, Any], fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    containers: list[dict[str, Any]] = [chart]
    if isinstance(fixture, dict):
        nested_chart = fixture.get("jyotish_agent_chart") if isinstance(fixture.get("jyotish_agent_chart"), dict) else {}
        containers.extend([nested_chart, fixture])
    for container in containers:
        payload = _return_from_container(container)
        if payload:
            return payload
    fallback_inputs = [chart]
    if isinstance(fixture, dict):
        fixture_input = fixture.get("input") if isinstance(fixture.get("input"), dict) else {}
        fallback_inputs.extend([fixture, fixture_input])
    for candidate in fallback_inputs:
        if not _has_return_input(candidate):
            continue
        try:
            from .workflows import build_tajaka_report

            payload, _skipped = _coerce_return(build_tajaka_report(candidate))
            if payload:
                return payload
        except Exception:
            continue
    return {}


def _return_from_container(container: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(container, dict):
        return {}
    for key in ("tajaka", "tajaka_report", "varshaphala"):
        payload, _skipped = _coerce_return(container.get(key))
        if payload:
            return payload
    tajaka_report = container.get("tajaka_report") if isinstance(container.get("tajaka_report"), dict) else {}
    payload, _skipped = _coerce_return(tajaka_report.get("tajaka"))
    if payload:
        return payload
    tithi_report = container.get("tithi_pravesha_report") if isinstance(container.get("tithi_pravesha_report"), dict) else {}
    payload, _skipped = _coerce_return((tithi_report.get("annual_context") or {}).get("tajaka") if isinstance(tithi_report.get("annual_context"), dict) else {})
    if payload:
        return payload
    payload, _skipped = _coerce_return((tajaka_report.get("tithi_pravesha") or {}).get("annual_context", {}).get("tajaka") if isinstance(tajaka_report.get("tithi_pravesha"), dict) else {})
    return payload


def _has_return_input(value: Any) -> bool:
    return isinstance(value, dict) and {"birth_date", "birth_time", "place_name", "target_year"} <= set(value)


def _coerce_return(value: Any) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(value, dict):
        return {}, []
    output: dict[str, Any] = {}
    tajaka = value.get("tajaka") if isinstance(value.get("tajaka"), dict) else {}
    tithi_pravesha = value.get("tithi_pravesha") if isinstance(value.get("tithi_pravesha"), dict) else {}
    if not tithi_pravesha:
        tithi_pravesha = value.get("tithi_pravesha_report") if isinstance(value.get("tithi_pravesha_report"), dict) else {}
    annual_context = value.get("annual_context") if isinstance(value.get("annual_context"), dict) else {}
    if not annual_context:
        annual_context = tithi_pravesha.get("annual_context") if isinstance(tithi_pravesha.get("annual_context"), dict) else {}

    target_year = _safe_int(value.get("target_year"))
    if target_year is None:
        target_year = _safe_int(tithi_pravesha.get("target_year"))
    if target_year is not None:
        output["target_year"] = target_year
    status = _normalized_text(value.get("status") or tajaka.get("status"))
    if status:
        output["status"] = status
    output["annual_lagna"] = _coerce_placement(
        tajaka.get("annual_lagna") or value.get("annual_lagna") or annual_context.get("lagna")
    )
    output["annual_sun"] = _coerce_placement(
        tajaka.get("annual_sun") or value.get("annual_sun") or annual_context.get("sun")
    )
    output["annual_moon"] = _coerce_placement(
        tajaka.get("annual_moon") or value.get("annual_moon") or annual_context.get("moon")
    )
    annual_tajaka = annual_context.get("tajaka") if isinstance(annual_context.get("tajaka"), dict) else {}
    output["muntha"] = _coerce_muntha(tajaka.get("muntha") or value.get("muntha") or annual_tajaka.get("muntha"))
    output["panchanga"] = _coerce_panchanga(
        tajaka.get("panchanga") or value.get("annual_panchanga") or value.get("panchanga") or annual_context.get("panchanga") or {}
    )
    output["open_items"] = _coerce_open_items(tajaka.get("open_items") or value.get("open_items"))
    skipped = [
        f"tajaka.{_normalized_key(key)}"
        for key in value
        if _normalized_key(key) and _normalized_key(key) not in KNOWN_RETURN_KEYS
    ]
    return _drop_empty(output), skipped


def _coerce_muntha(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    output: dict[str, Any] = {}
    rashi = _normalized_text(value.get("rashi") or value.get("sign"))
    if rashi:
        output["rashi"] = rashi
    house = _safe_int(
        value.get("house_from_annual_lagna") if value.get("house_from_annual_lagna") is not None else value.get("house")
    )
    if house is not None:
        output["house_from_annual_lagna"] = house
    return output


def _coerce_open_items(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_normalized_key(item) for item in value if _normalized_key(item)]
    if isinstance(value, dict):
        return [_normalized_key(key) for key, present in value.items() if present and _normalized_key(key)]
    return []


def _coerce_return_moment(primary: Any, alternate: Any, solar: dict[str, Any]) -> dict[str, Any]:
    source = primary if isinstance(primary, dict) else alternate if isinstance(alternate, dict) else {}
    output: dict[str, Any] = {}
    for key in ("date", "time", "local_datetime", "timezone"):
        text = _normalized_text(source.get(key))
        if text:
            output[key] = text
    for key, source_key in {
        "solar_lunar_angle": "return",
        "delta_degrees": "delta_degrees",
    }.items():
        number = _safe_float(source.get(key))
        if number is None and solar:
            number = _safe_float(solar.get(source_key))
        if number is not None:
            output[key] = number
    return output


def _coerce_placement(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    output: dict[str, Any] = {}
    rashi = _normalized_text(value.get("rashi") or value.get("sign"))
    if rashi:
        output["rashi"] = rashi
    degree = _safe_float(value.get("degree") if value.get("degree") is not None else value.get("longitude"))
    if degree is not None:
        output["degree"] = degree
    return output


def _coerce_panchanga(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    output: dict[str, str] = {}
    for key in PANCHANGA_FIELDS:
        item = value.get(key)
        if isinstance(item, dict):
            item = _first_present(item, ("name", "key", "label", "number"))
        text = _normalized_text(item)
        if text:
            output[key] = text
    return output


def _coerce_tajaka(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    muntha = value.get("muntha") if isinstance(value.get("muntha"), dict) else {}
    output: dict[str, Any] = {"muntha": {}}
    rashi = _normalized_text(muntha.get("rashi") or muntha.get("sign"))
    if rashi:
        output["muntha"]["rashi"] = rashi
    house = _safe_int(muntha.get("house_from_annual_lagna") if muntha.get("house_from_annual_lagna") is not None else muntha.get("house"))
    if house is not None:
        output["muntha"]["house_from_annual_lagna"] = house
    status = _normalized_text(value.get("status"))
    if status:
        output["status"] = status
    return _drop_empty(output)


def _compare_return(expected: dict[str, Any], actual: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    _compare_scalar(results, source, "tajaka_context", "status", expected.get("status"), actual.get("status"))
    _compare_scalar(
        results,
        source,
        "tithi_pravesha_link",
        "target_year",
        expected.get("target_year"),
        actual.get("target_year"),
    )
    for key in ("rashi", "degree"):
        _compare_scalar(
            results,
            source,
            "annual_lagna",
            f"annual_lagna.{key}",
            (expected.get("annual_lagna") or {}).get(key),
            (actual.get("annual_lagna") or {}).get(key),
        )
    for body in ("annual_sun", "annual_moon"):
        for key in ("rashi", "degree"):
            _compare_scalar(
                results,
                source,
                "annual_bodies",
                f"{body}.{key}",
                (expected.get(body) or {}).get(key),
                (actual.get(body) or {}).get(key),
            )
    for key in ("rashi", "house_from_annual_lagna"):
        _compare_scalar(
            results,
            source,
            "muntha",
            f"muntha.{key}",
            (expected.get("muntha") or {}).get(key),
            (actual.get("muntha") or {}).get(key),
        )
    for key in PANCHANGA_FIELDS:
        _compare_scalar(
            results,
            source,
            "annual_panchanga",
            f"annual_panchanga.{key}",
            (expected.get("panchanga") or {}).get(key),
            (actual.get("panchanga") or {}).get(key),
        )
    _compare_scalar(results, source, "open_items", "open_items", expected.get("open_items"), actual.get("open_items"))
    return results, missing


def _compare_scalar(
    results: list[dict[str, Any]],
    source: str,
    layer: str,
    field: str,
    expected: Any,
    actual: Any,
) -> None:
    if expected in (None, "", []):
        return
    if isinstance(expected, (int, float)) or isinstance(actual, (int, float)):
        expected_value = _safe_float(expected)
        actual_value = _safe_float(actual)
        passed = _numbers_equal(expected_value, actual_value)
    else:
        expected_value = _normalized_value(expected)
        actual_value = _normalized_value(actual)
        passed = expected_value == actual_value
    results.append(
        {
            "source": source,
            "layer": layer,
            "field": field,
            "expected": expected_value,
            "actual": actual_value,
            "passed": passed,
            "tolerance": NUMERIC_TOLERANCE if isinstance(expected_value, (int, float)) or isinstance(actual_value, (int, float)) else None,
        }
    )


def _numbers_equal(expected: Any, actual: Any) -> bool:
    expected_float = _safe_float(expected)
    actual_float = _safe_float(actual)
    if expected_float is None or actual_float is None:
        return False
    return math.isclose(expected_float, actual_float, abs_tol=NUMERIC_TOLERANCE)


def _angle_from_value(value: Any, key: str) -> float | None:
    if isinstance(value, dict):
        return _safe_float(value.get(key))
    return None


def _drop_empty(value: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, item in value.items():
        if isinstance(item, dict):
            nested = _drop_empty(item)
            if nested:
                output[key] = nested
        elif item not in (None, "", []):
            output[key] = item
    return output


def _normalized_value(value: Any) -> Any:
    if isinstance(value, list):
        return [_normalized_text(item) for item in value]
    return _normalized_text(value)


def _normalized_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    return re.sub(r"\s+", " ", text)


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


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _first_present(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in row and row.get(key) is not None:
            return row.get(key)
    return None


def _layer_from_field(field: str) -> str:
    if field == "status":
        return "tajaka_context"
    if field == "target_year":
        return "tithi_pravesha_link"
    if field.startswith("annual_lagna."):
        return "annual_lagna"
    if field.startswith("annual_sun.") or field.startswith("annual_moon."):
        return "annual_bodies"
    if field.startswith("muntha."):
        return "muntha"
    if field.startswith("annual_panchanga."):
        return "annual_panchanga"
    if field == "open_items":
        return "open_items"
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
                if layer in row.get("failed_layers", []):
                    summary[layer]["failed"] += 1
                else:
                    summary[layer]["passed"] += 1
            elif status in {"missing", "missing_witness"}:
                summary[layer]["missing"] += 1
            elif status in {"not_comparable", "not_reviewed"}:
                summary[layer]["not_comparable"] += 1
    return summary


def _field_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        for result in row.get("field_results", []):
            field = str(result.get("field") or "")
            bucket = summary.setdefault(field, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["passed" if result.get("passed") else "failed"] += 1
        for field in row.get("missing_fields", []):
            bucket = summary.setdefault(str(field), {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["missing"] += 1
        for field in row.get("skipped_fields", []):
            key = str(field).split(".")[-1]
            bucket = summary.setdefault(key, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["skipped"] += 1
    return summary
