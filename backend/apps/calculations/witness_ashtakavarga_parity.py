from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.utils import timezone

from .constants import RASHIS
from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .witness_batch import PL_REVIEW_STATUSES, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-ashtakavarga-parity-report-v1"
LAYERS = ("bhinna", "sarva")
ASHTAKAVARGA_BODIES = ("Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani")
BODY_ALIASES = {
    "Su": "Surya",
    "Sun": "Surya",
    "Surya": "Surya",
    "Mo": "Chandra",
    "Moon": "Chandra",
    "Chandra": "Chandra",
    "Ma": "Mangala",
    "Mars": "Mangala",
    "Mangala": "Mangala",
    "Me": "Budha",
    "Mercury": "Budha",
    "Budha": "Budha",
    "Ju": "Guru",
    "Jupiter": "Guru",
    "Guru": "Guru",
    "Ve": "Shukra",
    "Venus": "Shukra",
    "Shukra": "Shukra",
    "Sa": "Shani",
    "Saturn": "Shani",
    "Shani": "Shani",
}


def build_witness_ashtakavarga_parity_report(
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
            "bodies": list(ASHTAKAVARGA_BODIES),
            "normalization_notes": [
                "Body aliases are normalized to Jyotish Agent body names.",
                "Rashi labels and zero-based rashi indexes are normalized to RASHIS order.",
                "Lagna rows are ignored unless both payloads expose stable comparable cells.",
            ],
            "witness_sources": ["jhora", "parashara_light"],
        },
        "summary": _summary(rows, target_reviewed_count),
        "layer_summary": _layer_summary(rows),
        "body_summary": _body_summary(rows),
        "cases": rows,
    }


def render_ashtakavarga_parity_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Ashtakavarga Parity Report",
        "",
        "Diagnostic comparison of reviewed witness packets against Jyotish Agent Ashtakavarga payloads.",
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
                f"- Failed layers: {', '.join(row['failed_layers']) or 'none'}",
                f"- Missing layers: {', '.join(row['missing_layers']) or 'none'}",
                f"- Failed cells: {', '.join(row['failed_cells']) or 'none'}",
                f"- Missing cells: {', '.join(row['missing_cells']) or 'none'}",
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
    missing_cells: list[str] = []
    witness_missing_records = 0
    for record in reviewed_records:
        source_results, source_missing, missing_kind = _compare_record(record)
        field_results.extend(source_results)
        missing_cells.extend(source_missing)
        if missing_kind == "witness" and not source_results:
            witness_missing_records += 1

    if not field_results:
        if witness_missing_records == len(reviewed_records):
            return _empty_case(case_row, "missing", sources_present, review_statuses, sorted(set(missing_cells)))
        return _empty_case(case_row, "not_comparable", sources_present, review_statuses, sorted(set(missing_cells or ["ashtakavarga"])))

    failed_cells = sorted({str(item["cell"]) for item in field_results if not item.get("passed")})
    checked_cells = sorted({str(item["cell"]) for item in field_results})
    checked_layers = sorted({str(item["layer"]) for item in field_results})
    failed_layers = sorted({str(item["layer"]) for item in field_results if not item.get("passed")})
    missing_layers = sorted({_layer_from_cell(item) for item in missing_cells if _layer_from_cell(item)})
    comparison_status = "failed" if failed_cells else "passed"
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": comparison_status,
        "checked_layers": checked_layers,
        "failed_layers": failed_layers,
        "missing_layers": missing_layers,
        "checked_cells": checked_cells,
        "failed_cells": failed_cells,
        "missing_cells": sorted(set(missing_cells)),
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
    missing_cells: list[str],
) -> dict[str, Any]:
    return {
        "case_id": str(case_row["id"]),
        "review_status": ",".join(review_statuses),
        "sources_present": sources_present,
        "comparison_status": status,
        "checked_layers": [],
        "failed_layers": [],
        "missing_layers": sorted({_layer_from_cell(item) for item in missing_cells if _layer_from_cell(item)}),
        "checked_cells": [],
        "failed_cells": [],
        "missing_cells": missing_cells,
        "field_results": [],
    }


def _is_reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or "")
    if record["source"] == "jhora":
        return status in AUTHORITATIVE_REVIEW_STATUSES
    return status in PL_REVIEW_STATUSES


def _compare_record(record: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], str]:
    fixture, chart = _load_fixture_and_chart(Path(str(record.get("path") or "")))
    expected = _expected_ashtakavarga(fixture, str(record["source"]))
    actual = _actual_ashtakavarga(chart)
    if not expected:
        return [], [f"{record['source']}.ashtakavarga"], "witness"
    if not actual:
        return [], ["calculated.ashtakavarga"], "calculated"
    return (*_compare_ashtakavarga(expected, actual, str(record["source"])), "")


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


def _expected_ashtakavarga(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    expected = fixture.get("expected")
    if isinstance(expected, dict) and isinstance(expected.get("ashtakavarga"), dict):
        return expected["ashtakavarga"]
    if source == "parashara_light":
        manual = fixture.get("manual_witness_values")
        if isinstance(manual, dict) and isinstance(manual.get("ashtakavarga"), dict):
            return manual["ashtakavarga"]
    return {}


def _actual_ashtakavarga(chart: dict[str, Any]) -> dict[str, Any]:
    classical = chart.get("classical") if isinstance(chart.get("classical"), dict) else {}
    value = classical.get("ashtakavarga") if isinstance(classical.get("ashtakavarga"), dict) else {}
    return value if isinstance(value, dict) else {}


def _compare_ashtakavarga(
    expected: dict[str, Any],
    actual: dict[str, Any],
    source: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    results: list[dict[str, Any]] = []
    missing: list[str] = []
    expected_bhinna = _expected_bhinna(expected)
    actual_bhinna = actual.get("bhinna") if isinstance(actual.get("bhinna"), dict) else {}
    if expected_bhinna:
        if not actual_bhinna:
            missing.append("calculated.bhinna")
        else:
            _compare_bhinna(results, missing, expected_bhinna, actual_bhinna, source)
    else:
        missing.append(f"{source}.bhinna")

    expected_sarva = _score_cells(expected.get("sarva"))
    actual_sarva = _score_cells(actual.get("sarva"))
    if expected_sarva:
        if not actual_sarva:
            missing.append("calculated.sarva")
        else:
            _compare_cells(results, missing, "sarva", "", expected_sarva, actual_sarva, source)
    return results, missing


def _compare_bhinna(
    results: list[dict[str, Any]],
    missing: list[str],
    expected_bhinna: dict[str, dict[str, int]],
    actual_bhinna: dict[str, Any],
    source: str,
) -> None:
    for body, expected_cells in expected_bhinna.items():
        actual_cells = _score_cells(actual_bhinna.get(body))
        if not actual_cells:
            missing.append(f"calculated.bhinna.{body}")
            continue
        _compare_cells(results, missing, "bhinna", body, expected_cells, actual_cells, source)


def _compare_cells(
    results: list[dict[str, Any]],
    missing: list[str],
    layer: str,
    body: str,
    expected_cells: dict[str, int],
    actual_cells: dict[str, int],
    source: str,
) -> None:
    prefix = f"{layer}.{body}" if body else layer
    for cell, expected_value in expected_cells.items():
        if cell not in actual_cells:
            missing.append(f"calculated.{prefix}.{cell}")
            continue
        actual_value = actual_cells[cell]
        results.append(
            {
                "source": source,
                "layer": layer,
                "body": body,
                "cell": f"{prefix}.{cell}",
                "expected": expected_value,
                "actual": actual_value,
                "passed": int(expected_value) == int(actual_value),
            }
        )


def _expected_bhinna(value: dict[str, Any]) -> dict[str, dict[str, int]]:
    if isinstance(value.get("bhinna"), dict):
        source = value["bhinna"]
    else:
        source = {key: row for key, row in value.items() if _body_name(key)}
    result: dict[str, dict[str, int]] = {}
    for body_key, row in source.items():
        body = _body_name(body_key)
        if not body or body not in ASHTAKAVARGA_BODIES:
            continue
        cells = _score_cells(row)
        if cells:
            result[body] = cells
    return result


def _score_cells(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    scores = value.get("scores")
    if isinstance(scores, list):
        result = {
            RASHIS[index]: int(raw)
            for index, raw in enumerate(scores[: len(RASHIS)])
            if _int_or_none(raw) is not None
        }
        total = _int_or_none(value.get("total"))
        if total is not None:
            result["total"] = total
        return result
    result: dict[str, int] = {}
    for key, raw in value.items():
        if key in {"scores"}:
            continue
        if key == "total":
            converted = _int_or_none(raw)
            if converted is not None:
                result["total"] = converted
            continue
        rashi = _rashi_name(key)
        converted = _int_or_none(raw)
        if rashi and converted is not None:
            result[rashi] = converted
    return result


def _body_name(value: Any) -> str:
    return BODY_ALIASES.get(str(value), "")


def _rashi_name(value: Any) -> str:
    text = str(value)
    if text in RASHIS:
        return text
    converted = _int_or_none(value)
    if converted is not None and 0 <= converted < len(RASHIS):
        return RASHIS[converted]
    return ""


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
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
                if row["comparison_status"] == "missing" or _has_witness_missing(row.get("missing_cells"), layer):
                    summary[layer]["missing"] += 1
                else:
                    summary[layer]["not_comparable"] += 1
            elif layer in row["checked_layers"]:
                summary[layer]["passed"] += 1
            elif row["comparison_status"] in {"missing", "not_comparable", "not_reviewed", "missing_witness"}:
                summary[layer]["not_comparable"] += 1
    return summary


def _body_summary(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary = {body: {"passed": 0, "failed": 0, "missing": 0, "not_comparable": 0} for body in ASHTAKAVARGA_BODIES}
    for row in rows:
        checked = {_body_from_cell(cell) for cell in row["checked_cells"]}
        failed = {_body_from_cell(cell) for cell in row["failed_cells"]}
        missing = {_body_from_cell(cell) for cell in row["missing_cells"]}
        for body in ASHTAKAVARGA_BODIES:
            if body in failed:
                summary[body]["failed"] += 1
            elif body in missing and body not in checked:
                summary[body]["missing"] += 1
            elif body in checked:
                summary[body]["passed"] += 1
            elif row["comparison_status"] in {"missing", "not_comparable", "not_reviewed", "missing_witness"}:
                summary[body]["not_comparable"] += 1
    return summary


def _has_witness_missing(missing_cells: Any, layer: str) -> bool:
    if not isinstance(missing_cells, list):
        return False
    return any(str(item).startswith(("jhora.", "parashara_light.")) and layer in str(item) for item in missing_cells)


def _layer_from_cell(value: str) -> str:
    text = str(value)
    if "bhinna" in text:
        return "bhinna"
    if "sarva" in text:
        return "sarva"
    if "ashtakavarga" in text:
        return ""
    return ""


def _body_from_cell(value: str) -> str:
    parts = str(value).split(".")
    if len(parts) >= 3 and parts[0] == "bhinna":
        return parts[1]
    if len(parts) >= 4 and parts[1] == "bhinna":
        return parts[2]
    return ""
