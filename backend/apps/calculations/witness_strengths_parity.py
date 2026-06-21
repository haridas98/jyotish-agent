from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.utils import timezone

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-strengths-parity-report-v1"
LAYERS = ("vimshopaka", "shadbala")
PROFILE_SENSITIVE_LAYERS = ("shadbala",)
TOLERANCE_PROFILE = {"vimshopaka_points": 0.01, "shadbala_virupas": 0.01}
VIMSHOPAKA_SCHEME_MAP = {
    "shad_varga": "shadvarga",
    "sapta_varga": "saptavarga",
    "dasa_varga": "dashavarga",
    "shodasa_varga": "shodasha",
    "shadvarga": "shadvarga",
    "saptavarga": "saptavarga",
    "dashavarga": "dashavarga",
    "shodasha": "shodasha",
}
BODY_ALIASES = {
    "Sun": "Surya",
    "Su": "Surya",
    "Surya": "Surya",
    "Moon": "Chandra",
    "Mo": "Chandra",
    "Chandra": "Chandra",
    "Mars": "Mangala",
    "Ma": "Mangala",
    "Mangala": "Mangala",
    "Mercury": "Budha",
    "Me": "Budha",
    "Budha": "Budha",
    "Jupiter": "Guru",
    "Ju": "Guru",
    "Guru": "Guru",
    "Venus": "Shukra",
    "Ve": "Shukra",
    "Shukra": "Shukra",
    "Saturn": "Shani",
    "Sa": "Shani",
    "Shani": "Shani",
    "Rahu": "Rahu",
    "Ketu": "Ketu",
}
STRENGTH_BODIES = ("Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu")


def build_witness_strengths_parity_report(
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
            "tolerance_profile": dict(TOLERANCE_PROFILE),
            "profile_sensitive_layers": list(PROFILE_SENSITIVE_LAYERS),
            "normalization_notes": [
                "Body aliases are normalized to Jyotish Agent body names.",
                "Vimshopaka scheme labels are normalized to shadvarga, saptavarga, dashavarga and shodasha.",
                "Shadbala witness rupas are converted to virupas for comparison.",
                "Shadbala totals are profile-sensitive until settings and component audit closes.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "body_summary": _body_summary(rows),
        "cases": rows,
    }


def render_strengths_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Strengths Parity Report",
        "",
        "Diagnostic comparison of reviewed witness packets against Jyotish Agent strengths payloads.",
        "JHora and Parashara Light are used only as witness sources for comparison.",
        "Shadbala totals are profile-sensitive until settings and component audit closes.",
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
                f"- Failed layers: {', '.join(row['failed_layers']) or 'none'}",
                f"- Missing layers: {', '.join(row['missing_layers']) or 'none'}",
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
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, missing_kind = _compare_record(record)
        field_results.extend(source_results)
        missing_fields.extend(source_missing)
        if missing_kind == "witness" and not source_results:
            witness_missing_records += 1

    if not field_results:
        if witness_missing_records == len(reviewed_records):
            return _empty_case(case_row, "missing", sources_present, review_statuses, sorted(set(missing_fields)))
        return _empty_case(case_row, "not_comparable", sources_present, review_statuses, sorted(set(missing_fields or ["strengths"])))

    failed_fields = sorted({str(item["field"]) for item in field_results if not item.get("passed")})
    checked_fields = sorted({str(item["field"]) for item in field_results})
    checked_layers = sorted({str(item["layer"]) for item in field_results})
    failed_layers = sorted({str(item["layer"]) for item in field_results if not item.get("passed")})
    missing_layers = sorted({_layer_from_field(item) for item in missing_fields if _layer_from_field(item)})
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": "failed" if failed_fields else "passed",
        "checked_layers": checked_layers,
        "failed_layers": failed_layers,
        "missing_layers": missing_layers,
        "checked_fields": checked_fields,
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
        "missing_layers": sorted({_layer_from_field(item) for item in missing_fields if _layer_from_field(item)}),
        "checked_fields": [],
        "failed_fields": [],
        "missing_fields": missing_fields,
        "field_results": [],
    }


def _is_reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or "")
    if record["source"] == "jhora":
        return status in AUTHORITATIVE_REVIEW_STATUSES
    return status in PL_REVIEW_STATUSES


def _compare_record(record: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected = _expected_strengths(fixture, str(record["source"]))
    actual = _actual_strengths(chart)
    if not expected:
        return [], [f"{record['source']}.strengths"], "witness"
    if not actual:
        return [], ["calculated.strengths"], "calculated"
    return (*_compare_strengths(expected, actual, str(record["source"])), "")


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


def _expected_strengths(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    expected = fixture.get("expected")
    if isinstance(expected, dict) and (isinstance(expected.get("vimsopaka"), dict) or isinstance(expected.get("shadbala"), dict)):
        return expected
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values")
        if isinstance(manual, dict) and (isinstance(manual.get("vimsopaka"), dict) or isinstance(manual.get("shadbala"), dict)):
            return manual
    return {}


def _actual_strengths(chart: dict[str, Any]) -> dict[str, Any]:
    classical = chart.get("classical") if isinstance(chart.get("classical"), dict) else {}
    if not isinstance(classical, dict):
        return {}
    result = {}
    if isinstance(classical.get("vimshopaka_bala"), dict):
        result["vimshopaka_bala"] = classical["vimshopaka_bala"]
    if isinstance(classical.get("shadbala"), dict):
        result["shadbala"] = classical["shadbala"]
    return result


def _compare_strengths(
    expected: dict[str, Any],
    actual: dict[str, Any],
    source: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    _compare_vimshopaka(results, missing, expected.get("vimsopaka"), actual.get("vimshopaka_bala"), source)
    _compare_shadbala(results, missing, expected.get("shadbala"), actual.get("shadbala"), source)
    return results, missing


def _compare_vimshopaka(results: list[dict[str, Any]], missing: list[str], expected: Any, actual: Any, source: str) -> None:
    if not isinstance(expected, dict):
        missing.append(f"{source}.vimshopaka")
        return
    actual_items = _actual_items(actual)
    if not actual_items:
        missing.append("calculated.vimshopaka")
        return
    for body_key, expected_row in expected.items():
        body = _body_name(body_key)
        if not body or not isinstance(expected_row, dict):
            continue
        actual_row = actual_items.get(body)
        actual_scores = actual_row.get("scheme_scores") if isinstance(actual_row, dict) and isinstance(actual_row.get("scheme_scores"), dict) else {}
        if not actual_scores:
            missing.append(f"calculated.vimshopaka.{body}")
            continue
        for expected_scheme, actual_scheme in VIMSHOPAKA_SCHEME_MAP.items():
            expected_value = _expected_vimshopaka_score(expected_row.get(expected_scheme))
            if expected_value is None:
                continue
            actual_value = _float_or_none(actual_scores.get(actual_scheme))
            field = f"vimshopaka.{body}.{actual_scheme}"
            if actual_value is None:
                missing.append(f"calculated.{field}")
                continue
            _append_result(
                results,
                source=source,
                layer="vimshopaka",
                body=body,
                field=field,
                expected=expected_value,
                actual=actual_value,
                tolerance=TOLERANCE_PROFILE["vimshopaka_points"],
            )


def _compare_shadbala(results: list[dict[str, Any]], missing: list[str], expected: Any, actual: Any, source: str) -> None:
    if not isinstance(expected, dict):
        missing.append(f"{source}.shadbala")
        return
    actual_items = _actual_items(actual)
    if not actual_items:
        missing.append("calculated.shadbala")
        return
    for body_key, expected_row in expected.items():
        body = _body_name(body_key)
        if not body or not isinstance(expected_row, dict):
            continue
        actual_row = actual_items.get(body)
        if not isinstance(actual_row, dict):
            missing.append(f"calculated.shadbala.{body}")
            continue
        expected_value = _expected_shadbala_virupas(expected_row)
        if expected_value is None:
            continue
        actual_value = _float_or_none(actual_row.get("known_total"))
        field = f"shadbala.{body}.total_virupas"
        if actual_value is None:
            missing.append(f"calculated.{field}")
            continue
        _append_result(
            results,
            source=source,
            layer="shadbala",
            body=body,
            field=field,
            expected=expected_value,
            actual=actual_value,
            tolerance=TOLERANCE_PROFILE["shadbala_virupas"],
            profile_sensitive=True,
        )


def _append_result(
    results: list[dict[str, Any]],
    *,
    source: str,
    layer: str,
    body: str,
    field: str,
    expected: float,
    actual: float,
    tolerance: float,
    profile_sensitive: bool = False,
) -> None:
    delta = round(actual - expected, 6)
    results.append(
        {
            "source": source,
            "layer": layer,
            "body": body,
            "field": field,
            "expected": round(expected, 6),
            "actual": round(actual, 6),
            "delta": delta,
            "tolerance": tolerance,
            "profile_sensitive": profile_sensitive,
            "passed": abs(delta) <= tolerance,
        }
    )


def _actual_items(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, dict):
        return {}
    rows = value.get("items")
    if isinstance(rows, list):
        return {
            str(row.get("body")): row
            for row in rows
            if isinstance(row, dict) and row.get("body")
        }
    return {}


def _expected_vimshopaka_score(value: Any) -> float | None:
    if isinstance(value, dict):
        return _float_or_none(value.get("score"))
    return _float_or_none(value)


def _expected_shadbala_virupas(row: dict[str, Any]) -> float | None:
    for key in ("shadbala", "virupas", "known_total"):
        value = _float_or_none(row.get(key))
        if value is not None:
            return value
    rupas = _float_or_none(row.get("rupas"))
    if rupas is not None:
        return round(rupas * 60.0, 6)
    return None


def _body_name(value: Any) -> str:
    return BODY_ALIASES.get(str(value), "")


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


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
        for layer in LAYERS:
            if layer in row["failed_layers"]:
                summary[layer]["failed"] += 1
            elif layer in row["missing_layers"]:
                if row["comparison_status"] == "missing" or _has_witness_missing(row.get("missing_fields"), layer):
                    summary[layer]["missing"] += 1
                else:
                    summary[layer]["not_comparable"] += 1
            elif layer in row["checked_layers"]:
                summary[layer]["passed"] += 1
            elif row["comparison_status"] in {"missing", "not_comparable", "not_reviewed", "missing_witness"}:
                summary[layer]["not_comparable"] += 1
    return summary


def _body_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary = {body: {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0} for body in STRENGTH_BODIES}
    for row in rows:
        checked = {_body_from_field(field) for field in row["checked_fields"]}
        failed = {_body_from_field(field) for field in row["failed_fields"]}
        missing = {_body_from_field(field) for field in row["missing_fields"]}
        for body in STRENGTH_BODIES:
            if body in failed:
                summary[body]["failed"] += 1
            elif body in missing and body not in checked:
                summary[body]["missing"] += 1
            elif body in checked:
                summary[body]["passed"] += 1
            elif row["comparison_status"] in {"missing", "not_comparable", "not_reviewed", "missing_witness"}:
                summary[body]["not_comparable"] += 1
    return summary


def _has_witness_missing(missing_fields: Any, layer: str) -> bool:
    if not isinstance(missing_fields, list):
        return False
    return any(str(item).startswith(("jhora.", "parashara_light.")) and layer in str(item) for item in missing_fields)


def _layer_from_field(value: str) -> str:
    text = str(value)
    if "vimshopaka" in text or "vimsopaka" in text:
        return "vimshopaka"
    if "shadbala" in text:
        return "shadbala"
    if "strengths" in text:
        return ""
    return ""


def _body_from_field(value: str) -> str:
    parts = str(value).split(".")
    if len(parts) >= 3 and parts[0] in LAYERS:
        return parts[1]
    if len(parts) >= 4 and parts[1] in LAYERS:
        return parts[2]
    return ""
