from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-jaimini-karaka-parity-report-v1"
NUMERIC_TOLERANCE = 0.01
LAYERS = (
    "karaka_context",
    "karaka_scheme",
    "karaka_assignments",
    "ranking_inputs",
    "graha_rows",
    "review_gates",
)
ROLE_ORDER_7 = ("AK", "AmK", "BK", "MK", "PiK", "GK", "DK")
ROLE_ORDER_8 = ("AK", "AmK", "BK", "MK", "PiK", "GK", "DK", "RahuK")
PAYLOAD_KEYS = ("jaimini", "jaimini_karakas", "chara_karakas", "karakas", "karaka_rows")
KNOWN_KEYS = {
    "scheme",
    "profile",
    "karaka_scheme",
    "assignments",
    "rows",
    "karaka_rows",
    "graha_rows",
    "review_gates",
    "required_factors",
    "public_interpretation_status",
}
ROLE_ALIASES = {
    "ak": "AK",
    "atma_karaka": "AK",
    "atmakaraka": "AK",
    "amk": "AmK",
    "amatya_karaka": "AmK",
    "amatyakaraka": "AmK",
    "bk": "BK",
    "bhratri_karaka": "BK",
    "bhratrikaraka": "BK",
    "mk": "MK",
    "matri_karaka": "MK",
    "matrikaraka": "MK",
    "pik": "PiK",
    "pk": "PiK",
    "putra_karaka": "PiK",
    "putrakaraka": "PiK",
    "gk": "GK",
    "gnati_karaka": "GK",
    "gnatikaraka": "GK",
    "dk": "DK",
    "dara_karaka": "DK",
    "darakaraka": "DK",
    "rahuk": "RahuK",
    "rahu_karaka": "RahuK",
}
BODY_ALIASES = {
    "sun": "Surya",
    "surya": "Surya",
    "moon": "Chandra",
    "chandra": "Chandra",
    "mars": "Mangala",
    "mangala": "Mangala",
    "kuja": "Mangala",
    "mercury": "Budha",
    "budha": "Budha",
    "jupiter": "Guru",
    "guru": "Guru",
    "venus": "Shukra",
    "shukra": "Shukra",
    "saturn": "Shani",
    "shani": "Shani",
    "rahu": "Rahu",
}


def build_witness_jaimini_karaka_parity_report(
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
            "diagnostic_policy": "Reviewed witness Jaimini karaka rows are compared with Jyotish Agent karaka payloads.",
            "normalization_notes": [
                "Seven-karaka assignments are the diagnostic default when a witness packet does not state a scheme.",
                "Body names and karaka labels are normalized before comparison.",
                "Actual rows may be derived from existing graha longitudes when explicit karaka rows are absent.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "field_summary": _field_summary(rows),
        "cases": rows,
    }


def render_jaimini_karaka_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Jaimini Karaka Parity Report",
        "",
        "Diagnostic comparison of reviewed witness Jaimini karaka rows against Jyotish Agent karaka payloads.",
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
                sorted(set(missing_fields or ["calculated.jaimini_karakas"])),
            )
        row["skipped_fields"] = sorted(set(skipped_fields))
        return row

    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "checked_layers": sorted({str(item["layer"]) for item in field_results}),
        "failed_layers": sorted({str(item["layer"]) for item in field_results if not item.get("passed")}),
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
    expected, skipped_fields = _expected_karakas(fixture, str(record["source"]))
    actual = _actual_karakas(chart, fixture)
    if not expected and not skipped_fields:
        return [], [f"{record['source']}.jaimini_karakas"], [], "witness"
    if not actual:
        return [], ["calculated.jaimini_karakas"], skipped_fields, "calculated"
    results, missing = _compare_karakas(expected, actual, str(record["source"]))
    if not results and skipped_fields:
        return [], ["jaimini_karakas.comparable_fields"], skipped_fields, "unsupported"
    if not results:
        return [], missing or ["calculated.jaimini_karakas"], skipped_fields, "calculated"
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


def _expected_karakas(fixture: dict[str, Any], source: str) -> tuple[dict[str, Any], list[str]]:
    candidates: list[Any] = []
    for container_name in ("expected", "jhora_expected", "pl_expected"):
        container = fixture.get(container_name) if isinstance(fixture.get(container_name), dict) else {}
        candidates.extend(_payload_candidates(container))
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values") if isinstance(fixture.get("manual_witness_values"), dict) else {}
        candidates.extend(_payload_candidates(manual))
    for value in candidates:
        payload, skipped_fields = _coerce_karakas(value)
        if payload or skipped_fields:
            return payload, skipped_fields
    return {}, []


def _payload_candidates(container: Any) -> list[Any]:
    if not isinstance(container, dict):
        return []
    candidates: list[Any] = []
    if _looks_like_karaka_payload(container):
        candidates.append(container)
    for key in PAYLOAD_KEYS:
        if key in container:
            candidates.append(container.get(key))
    for key in ("jaimini", "jaimini_karakas"):
        nested = container.get(key) if isinstance(container.get(key), dict) else {}
        for payload_key in PAYLOAD_KEYS:
            if payload_key in nested:
                candidates.append(nested.get(payload_key))
    return candidates


def _actual_karakas(chart: dict[str, Any], fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    containers: list[dict[str, Any]] = [chart]
    if isinstance(fixture, dict):
        nested_chart = fixture.get("jyotish_agent_chart") if isinstance(fixture.get("jyotish_agent_chart"), dict) else {}
        containers.extend([nested_chart, fixture])
    for container in containers:
        for candidate in _payload_candidates(container):
            payload, _skipped = _coerce_karakas(candidate)
            if payload:
                return payload
        derived = _derive_from_grahas(container)
        if derived:
            return derived
    return {}


def _looks_like_karaka_payload(value: dict[str, Any]) -> bool:
    if any(_canonical_role(key) for key in value):
        return True
    return any(key in value for key in ("scheme", "profile", "assignments", "rows", "graha_rows", "karaka_rows", "review_gates"))


def _coerce_karakas(value: Any) -> tuple[dict[str, Any], list[str]]:
    if isinstance(value, list):
        value = {"rows": value}
    if not isinstance(value, dict):
        return {}, []
    if not _looks_like_karaka_payload(value):
        for key in PAYLOAD_KEYS:
            nested = value.get(key) if isinstance(value.get(key), (dict, list)) else {}
            if nested:
                return _coerce_karakas(nested)

    assignments: dict[str, str] = {}
    rows = _rows_from_value(value)
    for row in rows:
        role = _canonical_role(_first_present(row, ("karaka", "chara_karaka", "role", "key")))
        body = _canonical_body(_first_present(row, ("body", "graha", "planet", "name")))
        if role and body:
            assignments[role] = body
    assignment_source = value.get("assignments") if isinstance(value.get("assignments"), dict) else value
    if isinstance(assignment_source, dict):
        for key, item in assignment_source.items():
            role = _canonical_role(key)
            body = _canonical_body(item)
            if role and body:
                assignments[role] = body

    grahas: dict[str, dict[str, Any]] = {}
    for row in rows:
        body = _canonical_body(_first_present(row, ("body", "graha", "planet", "name")))
        if not body:
            continue
        grahas[body] = _coerce_graha_row(row)

    scheme = _normalize_scheme(value.get("scheme") or value.get("profile") or value.get("karaka_scheme"))
    if not scheme and assignments:
        scheme = "eight_karaka" if "RahuK" in assignments else "seven_karaka"

    gates = value.get("review_gates") if isinstance(value.get("review_gates"), dict) else {}
    required = _coerce_string_list(gates.get("required_factors") or value.get("required_factors"))
    public_status = _normalized_text(gates.get("public_interpretation_status") or value.get("public_interpretation_status"))

    output: dict[str, Any] = {
        "scheme": scheme,
        "assignments": assignments,
        "grahas": {body: row for body, row in grahas.items() if row},
    }
    if required:
        output["required_factors"] = required
    if public_status:
        output["public_interpretation_status"] = public_status

    skipped = [
        f"jaimini_karakas.{_normalized_key(key)}"
        for key in value
        if _normalized_key(key) and _normalized_key(key) not in KNOWN_KEYS and not _canonical_role(key)
    ]
    return _drop_empty(output), skipped


def _rows_from_value(value: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[Any] = []
    for key in ("rows", "graha_rows", "karaka_rows"):
        if isinstance(value.get(key), list):
            rows.extend(value.get(key) or [])
    if isinstance(value.get("chara_karakas"), list):
        rows.extend(value.get("chara_karakas") or [])
    return [row for row in rows if isinstance(row, dict)]


def _coerce_graha_row(row: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    role = _canonical_role(row.get("chara_karaka") or row.get("karaka"))
    if role:
        output["chara_karaka"] = role
    degree = _safe_float(
        row.get("degree_within_sign")
        if row.get("degree_within_sign") is not None
        else row.get("longitude_within_sign")
        if row.get("longitude_within_sign") is not None
        else row.get("degree")
    )
    if degree is not None:
        output["degree_within_sign"] = degree
    rashi = _normalized_text(row.get("rashi") or row.get("sign"))
    if rashi:
        output["rashi"] = rashi
    nakshatra = _normalized_text(row.get("nakshatra"))
    if nakshatra:
        output["nakshatra"] = nakshatra
    pada = _safe_int(row.get("pada"))
    if pada is not None:
        output["pada"] = pada
    return output


def _derive_from_grahas(container: dict[str, Any]) -> dict[str, Any]:
    rows = container.get("grahas") if isinstance(container.get("grahas"), list) else []
    grahas: list[tuple[float, str, dict[str, Any]]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        body = _canonical_body(row.get("body") or row.get("name") or row.get("graha"))
        if body not in {"Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani"}:
            continue
        longitude = _safe_float(row.get("longitude"))
        if longitude is None:
            continue
        degree = longitude % 30.0
        graha_row = _coerce_graha_row({**row, "degree_within_sign": degree})
        grahas.append((degree, body, graha_row))
    if len(grahas) < 7:
        return {}
    ordered = sorted(grahas, key=lambda item: item[0], reverse=True)[:7]
    assignments = {role: body for role, (_degree, body, _row) in zip(ROLE_ORDER_7, ordered)}
    return {
        "scheme": "seven_karaka",
        "assignments": assignments,
        "grahas": {body: row for _degree, body, row in ordered},
        "derived_from_existing_graha_longitudes": True,
    }


def _compare_karakas(expected: dict[str, Any], actual: dict[str, Any], source: str) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    _compare_scalar(results, missing, source, "karaka_scheme", "scheme", expected.get("scheme"), actual.get("scheme"))
    roles = ROLE_ORDER_8 if expected.get("scheme") == "eight_karaka" else ROLE_ORDER_7
    for role in roles:
        _compare_scalar(
            results,
            missing,
            source,
            "karaka_assignments",
            f"assignment.{role}",
            (expected.get("assignments") or {}).get(role),
            (actual.get("assignments") or {}).get(role),
        )
    for body, expected_row in (expected.get("grahas") or {}).items():
        actual_row = (actual.get("grahas") or {}).get(body) or {}
        for key in ("degree_within_sign", "rashi", "nakshatra", "pada"):
            _compare_scalar(
                results,
                missing,
                source,
                "ranking_inputs",
                f"graha.{body}.{key}",
                expected_row.get(key),
                actual_row.get(key),
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
    if actual.get("derived_from_existing_graha_longitudes"):
        results.append(
            {
                "source": source,
                "layer": "graha_rows",
                "field": "derived_from_existing_graha_longitudes",
                "expected": True,
                "actual": True,
                "passed": True,
                "tolerance": None,
            }
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


def _canonical_role(value: Any) -> str:
    key = _normalized_key(value)
    return ROLE_ALIASES.get(key, str(value or "").strip() if str(value or "").strip() in ROLE_ORDER_8 else "")


def _canonical_body(value: Any) -> str:
    key = _normalized_key(value)
    return BODY_ALIASES.get(key, "")


def _normalize_scheme(value: Any) -> str:
    key = _normalized_key(value)
    if not key:
        return ""
    if "8" in key or key == "eight_karaka":
        return "eight_karaka"
    return "seven_karaka"


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


def _normalized_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def _coerce_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return sorted({_normalized_key(item) for item in value if _normalized_key(item)})
    if isinstance(value, dict):
        return sorted({_normalized_key(key) for key, present in value.items() if present and _normalized_key(key)})
    text = _normalized_key(value)
    return [text] if text else []


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
    if field == "scheme":
        return "karaka_scheme"
    if field.startswith("assignment."):
        return "karaka_assignments"
    if field.startswith("graha."):
        return "ranking_inputs"
    if field in {"required_factors", "public_interpretation_status"}:
        return "review_gates"
    if field == "derived_from_existing_graha_longitudes":
        return "graha_rows"
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
