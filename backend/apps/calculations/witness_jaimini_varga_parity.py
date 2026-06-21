from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-jaimini-varga-parity-report-v1"
DEFAULT_VARGA_CODES = ("D5", "D6", "D8", "D11")
LAYERS = (
    "jaimini_varga_context",
    "d5_rows",
    "d6_rows",
    "d8_rows",
    "d11_rows",
    "placement_rows",
    "review_gates",
)
BODY_ALIASES = {
    "ascendant": "Lagna",
    "lagna": "Lagna",
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
    "ketu": "Ketu",
}
SIGN_ALIASES = {
    "aries": "Mesha",
    "mesha": "Mesha",
    "taurus": "Vrishabha",
    "vrishabha": "Vrishabha",
    "gemini": "Mithuna",
    "mithuna": "Mithuna",
    "cancer": "Karka",
    "karka": "Karka",
    "leo": "Simha",
    "simha": "Simha",
    "virgo": "Kanya",
    "kanya": "Kanya",
    "libra": "Tula",
    "tula": "Tula",
    "scorpio": "Vrischika",
    "vrischika": "Vrischika",
    "sagittarius": "Dhanu",
    "dhanu": "Dhanu",
    "capricorn": "Makara",
    "makara": "Makara",
    "aquarius": "Kumbha",
    "kumbha": "Kumbha",
    "pisces": "Meena",
    "meena": "Meena",
}
SIGN_BY_INDEX = {
    0: "Mesha",
    1: "Vrishabha",
    2: "Mithuna",
    3: "Karka",
    4: "Simha",
    5: "Kanya",
    6: "Tula",
    7: "Vrischika",
    8: "Dhanu",
    9: "Makara",
    10: "Kumbha",
    11: "Meena",
}
KNOWN_CODE_FIELDS = {"placements", "rows", "varga_rows", "method", "calculation_preset", "status"}
PLACEMENT_FIELDS = {"body", "name", "graha", "planet", "rashi", "sign", "rashi_index", "sign_index", "method", "calculation_preset", "status", "varga", "code"}


def build_witness_jaimini_varga_parity_report(
    *,
    witness_dir: str | Path,
    pl_root: str | Path = "",
    target_reviewed_count: int = 20,
    varga_codes: tuple[str, ...] | list[str] = DEFAULT_VARGA_CODES,
) -> dict[str, Any]:
    codes = tuple(_normalize_varga_code(code) for code in varga_codes if _normalize_varga_code(code))
    audit = audit_jhora_pl_witness_batch(
        jhora_root=witness_dir,
        pl_root=pl_root,
        target_reviewed_count=target_reviewed_count,
    )
    rows = [_case_report(row, codes) for row in audit["cases"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "generated_at": timezone.now().isoformat(),
            "target_reviewed_count": target_reviewed_count,
            "varga_codes": list(codes),
            "layers": list(LAYERS),
            "diagnostic_policy": "Reviewed witness D5/D6/D8/D11 placement rows are compared only when matching Jyotish Agent payload rows already exist.",
            "readiness_policy": "Absent D5/D6/D8/D11 actual payloads are reported as readiness gaps, not calculation failures.",
            "normalization_notes": [
                "Body labels and sign labels are normalized before comparison.",
                "Rows, placement lists, and code-keyed mappings are accepted for witness and actual payloads.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "varga_summary": _varga_summary(rows, codes),
        "field_summary": _field_summary(rows),
        "readiness_summary": _readiness_summary(rows, codes),
        "cases": rows,
    }


def render_jaimini_varga_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Jaimini Varga Parity Gap Report",
        "",
        "Diagnostic comparison of reviewed witness D5/D6/D8/D11 placement rows against existing Jyotish Agent payload rows.",
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
        "## Varga summary",
    ]
    for code, row in sorted(report.get("varga_summary", {}).items()):
        lines.append(
            f"- {code}: passed {row['passed']}, failed {row['failed']}, missing {row['missing']}, "
            f"not comparable {row['not_comparable']}, skipped {row['skipped']}"
        )
    lines.append("")
    lines.append("## Readiness summary")
    for code, row in sorted(report.get("readiness_summary", {}).items()):
        lines.append(f"- {code}: compared {row['compared']}, actual missing {row['actual_missing']}")
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
                f"- Failed vargas: {', '.join(row['failed_vargas']) or 'none'}",
                f"- Missing vargas: {', '.join(row['missing_vargas']) or 'none'}",
                f"- Skipped vargas: {', '.join(row['skipped_vargas']) or 'none'}",
                f"- Failed fields: {', '.join(row['failed_fields']) or 'none'}",
                f"- Missing fields: {', '.join(row['missing_fields']) or 'none'}",
                f"- Skipped fields: {', '.join(row['skipped_fields']) or 'none'}",
            ]
        )
    return "\n".join(lines) + "\n"


def _case_report(case_row: dict[str, Any], codes: tuple[str, ...]) -> dict[str, Any]:
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
        source_results, source_missing, source_skipped, missing_kind = _compare_record(record, codes)
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
                sorted(set(missing_fields or [f"calculated.vargas.{code}" for code in codes])),
            )
        row["skipped_fields"] = sorted(set(skipped_fields))
        row["skipped_vargas"] = _vargas_from_fields(skipped_fields)
        return row

    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "checked_vargas": _sort_vargas({str(item["varga"]) for item in field_results}),
        "failed_vargas": _sort_vargas({str(item["varga"]) for item in field_results if not item.get("passed")}),
        "missing_vargas": _vargas_from_fields(missing_fields),
        "skipped_vargas": _vargas_from_fields(skipped_fields),
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
        "checked_vargas": [],
        "failed_vargas": [],
        "missing_vargas": _vargas_from_fields(missing_fields),
        "skipped_vargas": [],
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


def _compare_record(record: dict[str, Any], codes: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[str], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected, expected_skipped = _expected_vargas(fixture, str(record["source"]), codes)
    actual, actual_skipped = _actual_vargas(chart, fixture, codes)
    skipped = [*expected_skipped, *actual_skipped]
    if not expected:
        return [], [f"{record['source']}.jaimini_vargas.{code}" for code in codes], skipped, "witness"
    if not actual:
        return [], [f"calculated.vargas.{code}" for code in codes], skipped, "calculated"
    results, missing = _compare_vargas(expected, actual, str(record["source"]), codes)
    missing_kind = "none" if results else "calculated"
    return results, missing, skipped, missing_kind


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


def _expected_vargas(fixture: dict[str, Any], source: str, codes: tuple[str, ...]) -> tuple[dict[str, dict[str, dict[str, Any]]], list[str]]:
    containers: list[dict[str, Any]] = []
    for key in ("expected", "jhora_expected", "pl_expected", "manual_witness_values"):
        value = fixture.get(key)
        if isinstance(value, dict) and (key != "manual_witness_values" or source == "parashara_light"):
            containers.append(value)
    for container in containers:
        payload = _find_varga_payload(container, codes)
        if payload is not None:
            return _normalize_varga_payload(payload, codes)
    return {}, []


def _actual_vargas(
    chart: dict[str, Any],
    fixture: dict[str, Any],
    codes: tuple[str, ...],
) -> tuple[dict[str, dict[str, dict[str, Any]]], list[str]]:
    containers = [chart, fixture]
    nested = chart.get("jyotish_agent_chart") if isinstance(chart.get("jyotish_agent_chart"), dict) else None
    if nested:
        containers.insert(0, nested)
    for container in containers:
        payload = _find_varga_payload(container, codes)
        if payload is not None:
            return _normalize_varga_payload(payload, codes)
    return {}, []


def _find_varga_payload(container: dict[str, Any], codes: tuple[str, ...]) -> Any:
    for key in ("jaimini_vargas", "vargas", "varga_rows", "divisional_charts"):
        value = container.get(key)
        if value is not None:
            return value
    jaimini = container.get("jaimini")
    if isinstance(jaimini, dict):
        for key in ("vargas", "varga_rows", "divisional_charts"):
            value = jaimini.get(key)
            if value is not None:
                return value
    if any(_normalize_varga_code(key) in codes for key in container):
        return container
    return None


def _normalize_varga_payload(value: Any, codes: tuple[str, ...]) -> tuple[dict[str, dict[str, dict[str, Any]]], list[str]]:
    out: dict[str, dict[str, dict[str, Any]]] = {}
    skipped: list[str] = []
    if isinstance(value, list):
        _merge_rows(out, value, codes)
        return out, skipped
    if not isinstance(value, dict):
        return out, skipped
    for key, row in value.items():
        code = _normalize_varga_code(key)
        if code in codes:
            index, code_skipped = _placement_index(row, code)
            if index:
                out[code] = {**out.get(code, {}), **index}
            skipped.extend(code_skipped)
    for row_key in ("rows", "varga_rows", "placements"):
        if isinstance(value.get(row_key), list):
            _merge_rows(out, value[row_key], codes)
    return out, skipped


def _placement_index(value: Any, code: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    if isinstance(value, list):
        out: dict[str, dict[str, dict[str, Any]]] = {}
        _merge_rows(out, value, (code,))
        return out.get(code, {}), []
    if not isinstance(value, dict):
        return {}, []
    if isinstance(value.get("placements"), list):
        out: dict[str, dict[str, dict[str, Any]]] = {}
        _merge_rows(out, value["placements"], (code,))
        skipped = [f"{code}.{key}" for key in value if key not in KNOWN_CODE_FIELDS]
        return out.get(code, {}), skipped

    out: dict[str, dict[str, Any]] = {}
    skipped: list[str] = []
    for key, row in value.items():
        body = _normalize_body(key)
        if body:
            placement = _placement_from_value(row)
            if placement:
                out[body] = placement
        elif key not in KNOWN_CODE_FIELDS:
            skipped.append(f"{code}.{key}")
    return out, skipped


def _merge_rows(out: dict[str, dict[str, dict[str, Any]]], rows: list[Any], codes: tuple[str, ...]) -> None:
    for row in rows:
        if not isinstance(row, dict):
            continue
        code = _normalize_varga_code(row.get("varga") or row.get("code") or (codes[0] if len(codes) == 1 else ""))
        if code not in codes:
            continue
        body = _normalize_body(row.get("body") or row.get("name") or row.get("graha") or row.get("planet"))
        if not body:
            continue
        placement = _placement_from_value(row)
        if placement:
            out.setdefault(code, {})[body] = placement


def _placement_from_value(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        sign = _normalize_sign(value)
        return {"rashi": sign} if sign else {}
    if not isinstance(value, dict):
        return {}
    placement: dict[str, Any] = {}
    sign = _normalize_sign(value.get("rashi") or value.get("sign"))
    if sign:
        placement["rashi"] = sign
    index = _safe_int(value.get("rashi_index", value.get("sign_index")))
    if index is not None:
        placement["rashi_index"] = index
        placement.setdefault("rashi", SIGN_BY_INDEX.get(index, str(index)))
    for field in ("method", "calculation_preset", "status"):
        if value.get(field) is not None:
            placement[field] = str(value.get(field))
    return placement


def _compare_vargas(
    expected: dict[str, dict[str, dict[str, Any]]],
    actual: dict[str, dict[str, dict[str, Any]]],
    source: str,
    codes: tuple[str, ...],
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    for code in codes:
        expected_index = expected.get(code, {})
        actual_index = actual.get(code, {})
        if not expected_index:
            missing.append(f"{source}.jaimini_vargas.{code}")
            continue
        if not actual_index:
            missing.append(f"calculated.vargas.{code}")
            continue
        for body, expected_placement in expected_index.items():
            actual_placement = actual_index.get(body)
            if not actual_placement:
                missing.append(f"calculated.vargas.{code}.{body}")
                continue
            _append_result(results, source, code, body, "rashi", expected_placement, actual_placement)
            for field in ("method", "calculation_preset", "status"):
                if field in expected_placement and field in actual_placement:
                    _append_result(results, source, code, body, field, expected_placement, actual_placement)
    return results, missing


def _append_result(
    results: list[dict[str, Any]],
    source: str,
    code: str,
    body: str,
    field: str,
    expected_placement: dict[str, Any],
    actual_placement: dict[str, Any],
) -> None:
    expected_value = expected_placement.get(field)
    actual_value = actual_placement.get(field)
    if expected_value is None:
        return
    if actual_value is None:
        return
    results.append(
        {
            "source": source,
            "varga": code,
            "body": body,
            "field": f"{code}.{body}.{field}",
            "expected": expected_value,
            "actual": actual_value,
            "passed": str(expected_value) == str(actual_value),
        }
    )


def _summary(rows: list[dict[str, Any]], target_reviewed_count: int) -> dict[str, Any]:
    comparable = [row for row in rows if row["comparison_status"] in {"passed", "failed"}]
    passed_count = sum(1 for row in rows if row["comparison_status"] == "passed")
    return {
        "case_count": len(rows),
        "comparable_count": len(comparable),
        "passed_count": passed_count,
        "failed_count": sum(1 for row in rows if row["comparison_status"] == "failed"),
        "missing_witness_count": sum(1 for row in rows if row["comparison_status"] == "missing_witness"),
        "not_reviewed_count": sum(1 for row in rows if row["comparison_status"] == "not_reviewed"),
        "not_comparable_count": sum(1 for row in rows if row["comparison_status"] == "not_comparable"),
        "target_reviewed_count": target_reviewed_count,
        "target_met": passed_count >= target_reviewed_count,
    }


def _varga_summary(rows: list[dict[str, Any]], codes: tuple[str, ...]) -> dict[str, dict[str, int]]:
    summary = {
        code: {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0, "skipped": 0}
        for code in codes
    }
    for row in rows:
        for code in codes:
            if code in row["failed_vargas"]:
                summary[code]["failed"] += 1
            elif code in row["checked_vargas"]:
                summary[code]["passed"] += 1
            elif code in row["missing_vargas"]:
                summary[code]["missing"] += 1
            elif code in row["skipped_vargas"]:
                summary[code]["skipped"] += 1
            elif row["comparison_status"] in {"not_comparable", "not_reviewed", "missing_witness"}:
                summary[code]["not_comparable"] += 1
    return summary


def _field_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for row in rows:
        for item in row["field_results"]:
            field = str(item["field"])
            _field_row(summary, field)["failed" if not item.get("passed") else "passed"] += 1
        for field in row["missing_fields"]:
            _field_row(summary, str(field))["missing"] += 1
        for field in row["skipped_fields"]:
            _field_row(summary, str(field).split(".")[-1])["skipped"] += 1
    return summary


def _readiness_summary(rows: list[dict[str, Any]], codes: tuple[str, ...]) -> dict[str, dict[str, int]]:
    summary = {code: {"compared": 0, "actual_missing": 0} for code in codes}
    for row in rows:
        for code in codes:
            if code in row["checked_vargas"]:
                summary[code]["compared"] += 1
            if any(str(field).startswith(f"calculated.vargas.{code}") for field in row["missing_fields"]):
                summary[code]["actual_missing"] += 1
    return summary


def _field_row(summary: dict[str, dict[str, int]], key: str) -> dict[str, int]:
    if key not in summary:
        summary[key] = {"passed": 0, "failed": 0, "missing": 0, "skipped": 0}
    return summary[key]


def _vargas_from_fields(fields: list[str]) -> list[str]:
    out = []
    for field in fields:
        for part in str(field).split("."):
            code = _normalize_varga_code(part)
            if code.startswith("D") and code[1:].isdigit() and code not in out:
                out.append(code)
    return _sort_vargas(out)


def _sort_vargas(values: Any) -> list[str]:
    return sorted(set(values), key=lambda code: int(str(code)[1:]) if str(code).startswith("D") and str(code)[1:].isdigit() else 999)


def _normalize_body(value: Any) -> str:
    key = str(value or "").strip().lower().replace(" ", "_").replace("-", "_")
    return BODY_ALIASES.get(key, "")


def _normalize_sign(value: Any) -> str:
    key = str(value or "").strip().lower().replace(" ", "_").replace("-", "_")
    return SIGN_ALIASES.get(key, "")


def _normalize_varga_code(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text and text[0].isdigit():
        text = f"D{text}"
    return text


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
