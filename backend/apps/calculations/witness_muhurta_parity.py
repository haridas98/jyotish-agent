from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-muhurta-parity-report-v1"
NUMERIC_TOLERANCE = 0.01
LAYERS = (
    "muhurta_context",
    "candidate_count",
    "candidate_ranking",
    "panchanga_factors",
    "avoidance_flags",
    "purpose_profile",
)
PANCHANGA_FIELDS = ("tithi", "nakshatra", "yoga", "karana", "vara")
AVOIDANCE_FLAGS = ("rahu_kalam", "yamaganda", "gulika_kala")
KNOWN_MUHURTA_KEYS = {
    "purpose",
    "task_type",
    "purpose_profile",
    "profile",
    "candidates",
    "candidate_count",
    "top_candidate",
    "candidate_order",
    "avoidance_flags",
}


def build_witness_muhurta_parity_report(
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
            "diagnostic_policy": (
                "Reviewed witness muhurta rows are compared with Jyotish Agent electional timing payloads."
            ),
            "normalization_notes": [
                "Muhurta and electional_timing witness payloads are normalized to stable field ids.",
                "Candidate score comparison uses 0.01 tolerance.",
                "Unknown optional muhurta fields are skipped unless no comparable fields remain.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "field_summary": _field_summary(rows),
        "cases": rows,
    }


def render_muhurta_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Muhurta Parity Report",
        "",
        "Diagnostic comparison of reviewed witness electional timing rows against Jyotish Agent muhurta payloads.",
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
                sorted(set(missing_fields or ["muhurta.comparable_fields"])),
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
        "missing_layers": ["muhurta"] if missing_fields else [],
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
    expected, skipped_fields = _expected_muhurta(fixture, str(record["source"]))
    actual = _actual_muhurta(chart, fixture)
    if not expected and not skipped_fields:
        return [], [f"{record['source']}.muhurta"], [], "witness"
    if not actual:
        return [], ["calculated.muhurta"], skipped_fields, "calculated"
    results, missing = _compare_muhurta(expected, actual, str(record["source"]))
    if not results and skipped_fields:
        return [], ["muhurta.comparable_fields"], skipped_fields, "unsupported"
    if not results:
        return [], missing or ["calculated.muhurta"], skipped_fields, "calculated"
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


def _expected_muhurta(fixture: dict[str, Any], source: str) -> tuple[dict[str, Any], list[str]]:
    sources: list[Any] = []
    for container_name in ("expected", "jhora_expected", "pl_expected"):
        container = fixture.get(container_name) if isinstance(fixture.get(container_name), dict) else {}
        for key in ("muhurta", "electional_timing"):
            if key in container:
                sources.append(container.get(key))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        for key in ("muhurta", "electional_timing"):
            if key in manual:
                sources.append(manual.get(key))

    for value in sources:
        payload, skipped_fields = _coerce_muhurta(value)
        if payload or skipped_fields:
            return payload, skipped_fields
    return {}, []


def _actual_muhurta(chart: dict[str, Any], fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    containers: list[dict[str, Any]] = [chart]
    if isinstance(fixture, dict):
        nested_chart = fixture.get("jyotish_agent_chart") if isinstance(fixture.get("jyotish_agent_chart"), dict) else {}
        containers.extend([nested_chart, fixture])
    for container in containers:
        payload = _muhurta_from_container(container)
        if payload:
            return payload
    fallback_inputs = [chart]
    if isinstance(fixture, dict):
        fixture_input = fixture.get("input") if isinstance(fixture.get("input"), dict) else {}
        fallback_inputs.extend([fixture, fixture_input])
    for candidate in fallback_inputs:
        if not _has_muhurta_input(candidate):
            continue
        try:
            from .workflows import build_muhurta_report

            payload, _skipped = _coerce_muhurta(build_muhurta_report(candidate))
            if payload:
                return payload
        except Exception:
            continue
    return {}


def _muhurta_from_container(container: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(container, dict):
        return {}
    for key in ("muhurta", "muhurta_report", "electional_timing"):
        payload, _skipped = _coerce_muhurta(container.get(key))
        if payload:
            return payload
    return {}


def _has_muhurta_input(value: Any) -> bool:
    return isinstance(value, dict) and {"place_name", "start_date", "end_date"} <= set(value)


def _coerce_muhurta(value: Any) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(value, dict):
        return {}, []
    candidates = _coerce_candidates(value)
    top_candidate = _coerce_top_candidate(value, candidates)
    payload: dict[str, Any] = {}
    purpose = _normalized_text(_first_present(value, ("purpose", "task_type")))
    profile = _normalized_text(_first_present(value, ("purpose_profile", "profile")))
    if purpose:
        payload["purpose"] = purpose
    if profile:
        payload["purpose_profile"] = profile
    count = _safe_int(value.get("candidate_count"))
    if count is None and candidates:
        count = len(candidates)
    if count is not None:
        payload["candidate_count"] = count
    if top_candidate:
        payload["top_candidate"] = top_candidate
    order = _coerce_candidate_order(value.get("candidate_order"), candidates)
    if order:
        payload["candidate_order"] = order
    avoidance = _coerce_avoidance_flags(value, top_candidate)
    if avoidance:
        payload["avoidance_flags"] = avoidance
    skipped = [f"muhurta.{_normalized_key(key)}" for key in value if _normalized_key(key) not in KNOWN_MUHURTA_KEYS]
    return payload, skipped


def _coerce_candidates(value: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = value.get("candidates")
    if not isinstance(candidates, list):
        return []
    return [_coerce_candidate(item) for item in candidates if isinstance(item, dict)]


def _coerce_top_candidate(value: dict[str, Any], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    explicit = value.get("top_candidate") if isinstance(value.get("top_candidate"), dict) else {}
    candidate = _coerce_candidate(explicit) if explicit else (candidates[0] if candidates else {})
    if not candidate:
        return {}
    panchanga = _coerce_panchanga(candidate.get("panchanga") if isinstance(candidate.get("panchanga"), dict) else candidate)
    if panchanga:
        candidate["panchanga"] = panchanga
    return candidate


def _coerce_candidate(value: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key in ("date", "time", "window_label"):
        text = _normalized_text(value.get(key))
        if text:
            output[key] = text
    rank = _safe_int(value.get("rank"))
    if rank is not None:
        output["rank"] = rank
    score = _safe_float(value.get("score"))
    if score is not None:
        output["score"] = score
    panchanga = _coerce_panchanga(value.get("panchanga") if isinstance(value.get("panchanga"), dict) else value)
    if panchanga:
        output["panchanga"] = panchanga
    avoidance = _coerce_avoidance_flags(value, {})
    if avoidance:
        output["avoidance_flags"] = avoidance
    return output


def _coerce_panchanga(value: dict[str, Any]) -> dict[str, str]:
    output: dict[str, str] = {}
    for key in PANCHANGA_FIELDS:
        item = value.get(key)
        if isinstance(item, dict):
            item = _first_present(item, ("name", "key", "label", "number"))
        text = _normalized_text(item)
        if text:
            output[key] = text
    return output


def _coerce_avoidance_flags(value: dict[str, Any], top_candidate: dict[str, Any] | None) -> dict[str, str]:
    output: dict[str, str] = {}
    flags = value.get("avoidance_flags") if isinstance(value.get("avoidance_flags"), dict) else {}
    for key in AVOIDANCE_FLAGS:
        text = _normalized_text(flags.get(key))
        if text:
            output[key] = text
    for period in value.get("blocked_periods") or []:
        if not isinstance(period, dict):
            continue
        key = _normalized_key(period.get("key") or period.get("name"))
        if key in AVOIDANCE_FLAGS:
            output[key] = _normalized_text(period.get("status") or period.get("result") or "blocked")
    if top_candidate and isinstance(top_candidate.get("avoidance_flags"), dict):
        for key in AVOIDANCE_FLAGS:
            text = _normalized_text(top_candidate["avoidance_flags"].get(key))
            if text:
                output[key] = text
    return output


def _coerce_candidate_order(value: Any, candidates: list[dict[str, Any]]) -> list[str]:
    if isinstance(value, list):
        return [_normalized_text(item) for item in value if _normalized_text(item)]
    order = []
    for candidate in candidates:
        date = candidate.get("date")
        time = candidate.get("time")
        if date and time:
            order.append(f"{date}T{time}")
    return order


def _compare_muhurta(expected: dict[str, Any], actual: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    _compare_scalar(results, source, "muhurta_context", "muhurta_context.purpose", expected.get("purpose"), actual.get("purpose"))
    _compare_scalar(
        results,
        source,
        "purpose_profile",
        "purpose_profile.label",
        expected.get("purpose_profile"),
        actual.get("purpose_profile"),
    )
    _compare_scalar(
        results,
        source,
        "candidate_count",
        "candidate_count.total",
        expected.get("candidate_count"),
        actual.get("candidate_count"),
    )
    top_expected = expected.get("top_candidate") if isinstance(expected.get("top_candidate"), dict) else {}
    top_actual = actual.get("top_candidate") if isinstance(actual.get("top_candidate"), dict) else {}
    if top_expected and not top_actual:
        missing.append("candidate_ranking.top_candidate")
    else:
        for field in ("date", "time", "rank", "window_label"):
            _compare_scalar(
                results,
                source,
                "candidate_ranking",
                f"top_candidate.{field}",
                top_expected.get(field),
                top_actual.get(field),
            )
        if top_expected.get("score") is not None:
            passed = _numbers_equal(top_expected.get("score"), top_actual.get("score"))
            results.append(
                _result(
                    source=source,
                    layer="candidate_ranking",
                    field="top_candidate.score",
                    expected=top_expected.get("score"),
                    actual=top_actual.get("score"),
                    passed=passed,
                )
            )
            results.append(
                _result(
                    source=source,
                    layer="candidate_ranking",
                    field="candidate_ranking.top_candidate.score",
                    expected=top_expected.get("score"),
                    actual=top_actual.get("score"),
                    passed=passed,
                )
            )
        expected_panchanga = top_expected.get("panchanga") if isinstance(top_expected.get("panchanga"), dict) else {}
        actual_panchanga = top_actual.get("panchanga") if isinstance(top_actual.get("panchanga"), dict) else {}
        for key in PANCHANGA_FIELDS:
            _compare_scalar(
                results,
                source,
                "panchanga_factors",
                f"panchanga.{key}",
                expected_panchanga.get(key),
                actual_panchanga.get(key),
            )
    if expected.get("candidate_order"):
        _compare_scalar(
            results,
            source,
            "candidate_ranking",
            "candidate_ranking.order",
            expected.get("candidate_order"),
            actual.get("candidate_order"),
        )
    expected_avoidance = expected.get("avoidance_flags") if isinstance(expected.get("avoidance_flags"), dict) else {}
    actual_avoidance = actual.get("avoidance_flags") if isinstance(actual.get("avoidance_flags"), dict) else {}
    for key in AVOIDANCE_FLAGS:
        _compare_scalar(
            results,
            source,
            "avoidance_flags",
            f"avoidance_flags.{key}",
            expected_avoidance.get(key),
            actual_avoidance.get(key),
        )
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
        passed = _numbers_equal(expected, actual)
        expected_value = _safe_float(expected)
        actual_value = _safe_float(actual)
    else:
        expected_value = _normalized_value(expected)
        actual_value = _normalized_value(actual)
        passed = expected_value == actual_value
    results.append(
        _result(
            source=source,
            layer=layer,
            field=field,
            expected=expected_value,
            actual=actual_value,
            passed=passed,
        )
    )


def _result(*, source: str, layer: str, field: str, expected: Any, actual: Any, passed: bool) -> dict[str, Any]:
    return {
        "source": source,
        "layer": layer,
        "field": field,
        "expected": expected,
        "actual": actual,
        "passed": passed,
        "tolerance": NUMERIC_TOLERANCE if isinstance(expected, (int, float)) or isinstance(actual, (int, float)) else None,
    }


def _numbers_equal(expected: Any, actual: Any) -> bool:
    expected_float = _safe_float(expected)
    actual_float = _safe_float(actual)
    if expected_float is None or actual_float is None:
        return False
    return math.isclose(expected_float, actual_float, abs_tol=NUMERIC_TOLERANCE)


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
    if field.startswith("top_candidate.") or field == "candidate_ranking.order":
        return "candidate_ranking"
    if field.startswith("panchanga."):
        return "panchanga_factors"
    if field.startswith("avoidance_flags."):
        return "avoidance_flags"
    parts = field.split(".")
    return parts[0] if parts and parts[0] in LAYERS else ""


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
