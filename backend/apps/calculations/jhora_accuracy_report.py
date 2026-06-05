from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_jhora_accuracy_report(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    report = json.loads(source.read_text(encoding="utf-8-sig"))
    return summarize_jhora_accuracy_report(report, source)


def summarize_jhora_accuracy_report(report: dict[str, Any], source: Path) -> dict[str, Any]:
    comparisons = report.get("longitude_comparisons") if isinstance(report.get("longitude_comparisons"), list) else []
    exact_matches = report.get("exact_matches") if isinstance(report.get("exact_matches"), dict) else {}
    diagnostics = report.get("diagnostics") if isinstance(report.get("diagnostics"), dict) else {}
    failed_longitudes = [
        {
            "body": str(row.get("body") or ""),
            "delta_arcseconds": float(row.get("delta_arcseconds") or 0.0),
            "signed_delta_arcseconds": float(row.get("signed_delta_arcseconds") or 0.0),
        }
        for row in comparisons
        if isinstance(row, dict) and not row.get("passed")
    ]
    failed_longitudes.sort(key=lambda row: abs(row["delta_arcseconds"]), reverse=True)
    return {
        "fixture_id": str(report.get("fixture_id") or ""),
        "passed": bool(report.get("passed")),
        "generated_at": _mtime_iso(source),
        "source_report": str(source),
        "source_export": str(source.parent / "complete-calculations.txt"),
        "summary": {
            "longitude": {
                "checked": len(comparisons),
                "failed": len(failed_longitudes),
                "max_delta_arcseconds": float(diagnostics.get("max_abs_delta_arcseconds") or 0.0),
                "median_delta_arcseconds": float(diagnostics.get("median_abs_delta_arcseconds") or 0.0),
                "ayanamsa_delta_arcseconds": float(
                    (diagnostics.get("ayanamsa") or {}).get("delta_arcseconds") or 0.0
                ),
                "corrected_max_delta_arcseconds": float(
                    (diagnostics.get("ayanamsa") or {}).get("corrected_max_abs_delta_arcseconds") or 0.0
                ),
                "failed_samples": failed_longitudes[:8],
            },
            "exact_groups": _exact_groups(exact_matches),
            "jhora_layers": _jhora_layer_summary(diagnostics.get("jhora_layers")),
            "missing_fields": report.get("missing_fields") or [],
        },
        "diagnostics": diagnostics,
    }


def _exact_groups(exact_matches: dict[str, Any]) -> list[dict[str, Any]]:
    groups: dict[str, dict[str, Any]] = {}
    for raw_key, raw_value in exact_matches.items():
        key = str(raw_key)
        group = _group_key(key)
        item = groups.setdefault(group, {"key": group, "total": 0, "passed": 0, "failed": 0, "failed_samples": []})
        item["total"] += 1
        if bool(raw_value):
            item["passed"] += 1
        else:
            item["failed"] += 1
            if len(item["failed_samples"]) < 8:
                item["failed_samples"].append(key)
    return sorted(groups.values(), key=lambda row: row["key"])


def _group_key(key: str) -> str:
    parts = key.split(".")
    if parts[0] == "jhora" and len(parts) > 1:
        return parts[1]
    if parts[0].startswith("D") and len(parts[0]) <= 4:
        return "vargas"
    return parts[0]


def _jhora_layer_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    summary = {}
    for key, layer in value.items():
        if not isinstance(layer, dict):
            continue
        summary[str(key)] = {
            field: layer.get(field)
            for field in ("checked", "matched", "failed", "missing", "skipped", "max_abs_delta")
            if field in layer
        }
    return summary


def _mtime_iso(path: Path) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
