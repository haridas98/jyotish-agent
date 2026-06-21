from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-prashna-parity-report-v1"
NUMERIC_TOLERANCE = 0.01
LAYERS = (
    "prashna_context",
    "question_chart",
    "question_lagna",
    "lagna_lord",
    "moon",
    "seventh_house",
    "panchanga",
    "review_gates",
)
PAYLOAD_KEYS = ("prashna", "prashna_report", "horary", "question_chart")
PANCHANGA_FIELDS = ("tithi", "nakshatra", "yoga", "karana", "vara")
KNOWN_PRASHNA_KEYS = {
    "status",
    "question",
    "asked_at",
    "indicators",
    "chart",
    "prashna",
    "prashna_report",
    "horary",
    "question_chart",
    "question_lagna",
    "lagna",
    "lagna_lord",
    "lagna_lord_placement",
    "moon",
    "moon_house_from_lagna",
    "seventh_house_rashi",
    "panchanga",
    "interpretation_plan",
    "audit",
    "required_factors",
    "public_interpretation_status",
}
RASHI_ALIASES = {
    "aries": "mesha",
    "taurus": "vrishabha",
    "gemini": "mithuna",
    "cancer": "karka",
    "leo": "simha",
    "virgo": "kanya",
    "libra": "tula",
    "scorpio": "vrischika",
    "sagittarius": "dhanu",
    "capricorn": "makara",
    "aquarius": "kumbha",
    "pisces": "meena",
}
BODY_ALIASES = {
    "sun": "surya",
    "moon": "chandra",
    "mars": "mangala",
    "mercury": "budha",
    "jupiter": "guru",
    "venus": "shukra",
    "saturn": "shani",
}


def build_witness_prashna_parity_report(
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
                "Reviewed witness Prashna rows are compared with Jyotish Agent Prashna payloads."
            ),
            "normalization_notes": [
                "Prashna, horary and question chart payloads are normalized.",
                "Lagna, Moon and placement degree fields use 0.01 degree tolerance.",
                "Unknown optional Prashna fields are skipped unless no comparable fields remain.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "field_summary": _field_summary(rows),
        "cases": rows,
    }


def render_prashna_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Prashna Parity Report",
        "",
        "Diagnostic comparison of reviewed witness Prashna rows against Jyotish Agent Prashna payloads.",
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
                sorted(set(missing_fields or ["prashna.comparable_fields"])),
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
        "missing_layers": list(LAYERS) if missing_fields else [],
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
    expected, skipped_fields = _expected_prashna(fixture, str(record["source"]))
    actual = _actual_prashna(chart, fixture)
    if not expected and not skipped_fields:
        return [], [f"{record['source']}.prashna"], [], "witness"
    if not actual:
        return [], ["calculated.prashna"], skipped_fields, "calculated"
    results, missing = _compare_prashna(expected, actual, str(record["source"]))
    if not results and skipped_fields:
        return [], ["prashna.comparable_fields"], skipped_fields, "unsupported"
    if not results:
        return [], missing or ["calculated.prashna"], skipped_fields, "calculated"
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


def _expected_prashna(fixture: dict[str, Any], source: str) -> tuple[dict[str, Any], list[str]]:
    candidates: list[Any] = []
    for container_name in ("expected", "jhora_expected", "pl_expected"):
        container = fixture.get(container_name) if isinstance(fixture.get(container_name), dict) else {}
        candidates.extend(_payload_candidates(container))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        candidates.extend(_payload_candidates(manual))

    for value in candidates:
        payload, skipped_fields = _coerce_prashna(value)
        if payload or skipped_fields:
            return payload, skipped_fields
    return {}, []


def _payload_candidates(container: dict[str, Any]) -> list[Any]:
    if not isinstance(container, dict):
        return []
    candidates: list[Any] = []
    for key in PAYLOAD_KEYS:
        if key in container:
            candidates.append(container.get(key))
    return candidates


def _actual_prashna(chart: dict[str, Any], fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    containers: list[dict[str, Any]] = [chart]
    if isinstance(fixture, dict):
        nested_chart = fixture.get("jyotish_agent_chart") if isinstance(fixture.get("jyotish_agent_chart"), dict) else {}
        containers.extend([nested_chart, fixture])
    for container in containers:
        payload = _prashna_from_container(container)
        if payload:
            return payload

    fallback_inputs = [chart]
    if isinstance(fixture, dict):
        fixture_input = fixture.get("input") if isinstance(fixture.get("input"), dict) else {}
        fallback_inputs.extend([fixture, fixture_input])
    for candidate in fallback_inputs:
        if not _has_prashna_input(candidate):
            continue
        try:
            from . import workflows

            payload, _skipped = _coerce_prashna(workflows.build_prashna_report(candidate))
            if payload:
                return payload
        except Exception:
            continue
    return {}


def _prashna_from_container(container: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(container, dict):
        return {}
    for key in PAYLOAD_KEYS:
        payload, _skipped = _coerce_prashna(container.get(key))
        if payload:
            return payload
    if _looks_like_prashna_payload(container):
        payload, _skipped = _coerce_prashna(container)
        if payload:
            return payload
    return {}


def _looks_like_prashna_payload(value: dict[str, Any]) -> bool:
    return any(
        key in value
        for key in (
            "indicators",
            "question_lagna",
            "asked_at",
            "lagna_lord",
            "lagna_lord_placement",
            "moon",
            "seventh_house_rashi",
            "panchanga",
            "interpretation_plan",
        )
    )


def _has_prashna_input(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    has_question = bool(value.get("question"))
    has_place = bool(value.get("place_name") or value.get("location") or (value.get("place") if isinstance(value.get("place"), str) else ""))
    has_time = bool(
        (value.get("question_date") and value.get("question_time"))
        or value.get("asked_at")
        or (value.get("birth_date") and value.get("birth_time"))
    )
    return has_question and has_place and has_time


def _coerce_prashna(value: Any) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(value, dict):
        return {}, []
    if not _looks_like_prashna_payload(value):
        for key in PAYLOAD_KEYS:
            nested = value.get(key) if isinstance(value.get(key), dict) else {}
            if nested:
                return _coerce_prashna(nested)

    output: dict[str, Any] = {}
    indicators = value.get("indicators") if isinstance(value.get("indicators"), dict) else {}
    question = value.get("question") if isinstance(value.get("question"), dict) else {}
    plan = value.get("interpretation_plan") if isinstance(value.get("interpretation_plan"), dict) else {}
    audit = value.get("audit") if isinstance(value.get("audit"), dict) else {}

    status = _normalized_text(value.get("status"))
    if status:
        output["status"] = status
    output["asked_at"] = _coerce_asked_at(question.get("asked_at") or value.get("asked_at"))
    output["lagna"] = _coerce_placement(indicators.get("lagna") or value.get("question_lagna") or value.get("lagna"))
    lagna_lord = _normalized_body(indicators.get("lagna_lord") or value.get("lagna_lord"))
    if lagna_lord:
        output["lagna_lord"] = lagna_lord
    output["lagna_lord_placement"] = _coerce_placement(
        indicators.get("lagna_lord_placement") or value.get("lagna_lord_placement")
    )
    moon = indicators.get("moon") or value.get("moon")
    output["moon"] = _coerce_placement(moon)
    moon_house = _safe_int(
        indicators.get("moon_house_from_lagna")
        if indicators.get("moon_house_from_lagna") is not None
        else value.get("moon_house_from_lagna")
    )
    if moon_house is None and isinstance(moon, dict):
        moon_house = _safe_int(moon.get("house_from_lagna"))
    if moon_house is not None:
        output["moon_house_from_lagna"] = moon_house
    seventh = _normalized_rashi(indicators.get("seventh_house_rashi") or value.get("seventh_house_rashi"))
    if seventh:
        output["seventh_house_rashi"] = seventh
    output["panchanga"] = _coerce_panchanga(
        indicators.get("panchanga")
        or value.get("panchanga")
        or ((value.get("chart") or {}).get("panchanga") if isinstance(value.get("chart"), dict) else {})
        or {}
    )
    required = _coerce_string_list(plan.get("required_factors") or value.get("required_factors"))
    if required:
        output["required_factors"] = required
    public_status = _normalized_text(audit.get("public_interpretation_status") or value.get("public_interpretation_status"))
    if public_status:
        output["public_interpretation_status"] = public_status

    skipped = [
        f"prashna.{_normalized_key(key)}"
        for key in value
        if _normalized_key(key) and _normalized_key(key) not in KNOWN_PRASHNA_KEYS
    ]
    return _drop_empty(output), skipped


def _coerce_asked_at(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    output: dict[str, str] = {}
    for key in ("date", "time", "timezone", "local_datetime"):
        text = _normalized_text(value.get(key))
        if text:
            output[key] = text
    return output


def _coerce_placement(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    output: dict[str, Any] = {}
    rashi = _normalized_rashi(value.get("rashi") or value.get("sign"))
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


def _coerce_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return sorted({_normalized_key(item) for item in value if _normalized_key(item)})
    if isinstance(value, dict):
        return sorted({_normalized_key(key) for key, present in value.items() if present and _normalized_key(key)})
    text = _normalized_key(value)
    return [text] if text else []


def _compare_prashna(expected: dict[str, Any], actual: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    _compare_scalar(results, missing, source, "prashna_context", "status", expected.get("status"), actual.get("status"))
    for key in ("date", "time", "timezone", "local_datetime"):
        _compare_scalar(
            results,
            missing,
            source,
            "question_chart",
            f"asked_at.{key}",
            (expected.get("asked_at") or {}).get(key),
            (actual.get("asked_at") or {}).get(key),
        )
    for key in ("rashi", "degree"):
        _compare_scalar(
            results,
            missing,
            source,
            "question_lagna",
            f"question_lagna.{key}",
            (expected.get("lagna") or {}).get(key),
            (actual.get("lagna") or {}).get(key),
        )
    _compare_scalar(results, missing, source, "lagna_lord", "lagna_lord", expected.get("lagna_lord"), actual.get("lagna_lord"))
    for key in ("rashi", "degree"):
        _compare_scalar(
            results,
            missing,
            source,
            "lagna_lord",
            f"lagna_lord_placement.{key}",
            (expected.get("lagna_lord_placement") or {}).get(key),
            (actual.get("lagna_lord_placement") or {}).get(key),
        )
    for key in ("rashi", "degree"):
        _compare_scalar(
            results,
            missing,
            source,
            "moon",
            f"moon.{key}",
            (expected.get("moon") or {}).get(key),
            (actual.get("moon") or {}).get(key),
        )
    _compare_scalar(
        results,
        missing,
        source,
        "moon",
        "moon_house_from_lagna",
        expected.get("moon_house_from_lagna"),
        actual.get("moon_house_from_lagna"),
    )
    _compare_scalar(
        results,
        missing,
        source,
        "seventh_house",
        "seventh_house_rashi",
        expected.get("seventh_house_rashi"),
        actual.get("seventh_house_rashi"),
    )
    for key in PANCHANGA_FIELDS:
        _compare_scalar(
            results,
            missing,
            source,
            "panchanga",
            f"panchanga.{key}",
            (expected.get("panchanga") or {}).get(key),
            (actual.get("panchanga") or {}).get(key),
        )
    _compare_scalar(
        results,
        missing,
        source,
        "review_gates",
        "required_factors",
        expected.get("required_factors"),
        actual.get("required_factors"),
    )
    _compare_scalar(
        results,
        missing,
        source,
        "review_gates",
        "public_interpretation_status",
        expected.get("public_interpretation_status"),
        actual.get("public_interpretation_status"),
    )
    return results, missing


def _compare_scalar(
    results: list[dict[str, Any]],
    missing: list[str],
    source: str,
    layer: str,
    field: str,
    expected: Any,
    actual: Any,
) -> None:
    if expected in (None, "", []):
        return
    if actual in (None, "", []):
        missing.append(field)
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
            "tolerance": NUMERIC_TOLERANCE
            if isinstance(expected_value, (int, float)) or isinstance(actual_value, (int, float))
            else None,
        }
    )


def _numbers_equal(expected: Any, actual: Any) -> bool:
    expected_float = _safe_float(expected)
    actual_float = _safe_float(actual)
    if expected_float is None or actual_float is None:
        return False
    return math.isclose(expected_float, actual_float, abs_tol=NUMERIC_TOLERANCE)


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
        return sorted({_normalized_text(item) for item in value})
    return _normalized_text(value)


def _normalized_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    return re.sub(r"\s+", " ", text)


def _normalized_rashi(value: Any) -> str:
    text = _normalized_text(value)
    return RASHI_ALIASES.get(text, text)


def _normalized_body(value: Any) -> str:
    text = _normalized_text(value)
    return BODY_ALIASES.get(text, text)


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
        return "prashna_context"
    if field.startswith("asked_at."):
        return "question_chart"
    if field.startswith("question_lagna."):
        return "question_lagna"
    if field == "lagna_lord" or field.startswith("lagna_lord_placement."):
        return "lagna_lord"
    if field.startswith("moon.") or field == "moon_house_from_lagna":
        return "moon"
    if field == "seventh_house_rashi":
        return "seventh_house"
    if field.startswith("panchanga."):
        return "panchanga"
    if field in {"required_factors", "public_interpretation_status"}:
        return "review_gates"
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
            key = str(field)
            bucket = summary.setdefault(key, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["missing"] += 1
        for field in row.get("skipped_fields", []):
            key = str(field).split(".")[-1]
            bucket = summary.setdefault(key, {"passed": 0, "failed": 0, "missing": 0, "skipped": 0})
            bucket["skipped"] += 1
    return summary
