from __future__ import annotations

from pathlib import Path
from typing import Any

from .jhora_accuracy_report import load_jhora_accuracy_report
from .parashara_light_packet_report import load_parashara_light_packet_report


def build_witness_summary(
    *,
    jhora_report_path: str | Path,
    parashara_light_packet_path: str | Path,
    parashara_light_manual_values_path: str | Path = "",
) -> dict[str, Any]:
    jhora = _jhora_summary(jhora_report_path)
    parashara_light = _parashara_light_summary(
        parashara_light_packet_path,
        manual_witness_values_path=parashara_light_manual_values_path,
    )
    open_items = _open_items(jhora, parashara_light)
    return {
        "overall_status": _overall_status(jhora, parashara_light),
        "jhora": jhora,
        "parashara_light": parashara_light,
        "open_items": open_items,
    }


def _jhora_summary(path: str | Path) -> dict[str, Any]:
    try:
        report = load_jhora_accuracy_report(path)
    except FileNotFoundError:
        return {
            "available": False,
            "status": "missing",
            "source_report": str(path),
            "fixture_id": "",
            "failed_checks": 0,
            "missing_fields_count": 0,
        }

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    longitude = summary.get("longitude") if isinstance(summary.get("longitude"), dict) else {}
    exact_groups = summary.get("exact_groups") if isinstance(summary.get("exact_groups"), list) else []
    missing_fields = summary.get("missing_fields") if isinstance(summary.get("missing_fields"), list) else []
    failed_checks = int(longitude.get("failed") or 0) + sum(
        int(group.get("failed") or 0) for group in exact_groups if isinstance(group, dict)
    )
    return {
        "available": True,
        "status": "matched" if report.get("passed") else "diff_open",
        "fixture_id": report.get("fixture_id", ""),
        "source_report": report.get("source_report", str(path)),
        "failed_checks": failed_checks,
        "missing_fields_count": len(missing_fields),
        "max_delta_arcseconds": float(longitude.get("max_delta_arcseconds") or 0.0),
        "corrected_max_delta_arcseconds": float(longitude.get("corrected_max_delta_arcseconds") or 0.0),
        "layers": summary.get("jhora_layers") or {},
    }


def _parashara_light_summary(
    path: str | Path,
    *,
    manual_witness_values_path: str | Path = "",
) -> dict[str, Any]:
    try:
        report = load_parashara_light_packet_report(
            path,
            manual_witness_values_path=manual_witness_values_path,
        )
    except FileNotFoundError:
        return {
            "available": False,
            "status": "missing",
            "source_packet": str(path),
            "id": "",
            "manual_values_count": 0,
            "manual_failed_count": 0,
            "manual_completion_percent": 0,
        }

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    comparison = report.get("manual_witness_comparison") if isinstance(report.get("manual_witness_comparison"), dict) else {}
    return {
        "available": True,
        "status": comparison.get("status") or "no_manual_values",
        "id": report.get("id", ""),
        "source_packet": report.get("source_packet", str(path)),
        "manual_witness_source": report.get("manual_witness_source", ""),
        "manual_values_count": int(summary.get("manual_values_count") or 0),
        "manual_failed_count": int(summary.get("manual_failed_count") or 0),
        "manual_completion_percent": int(summary.get("manual_completion_percent") or 0),
        "capture_status": summary.get("capture_status", ""),
        "review_status": summary.get("review_status", ""),
    }


def _overall_status(jhora: dict[str, Any], parashara_light: dict[str, Any]) -> str:
    if not jhora["available"] and not parashara_light["available"]:
        return "missing_witnesses"
    if jhora["status"] == "diff_open" or parashara_light["status"] == "diff_open":
        return "diff_open"
    if parashara_light["status"] in {"no_manual_values", "no_checked_fields"}:
        return "needs_manual_witness"
    if jhora["status"] == "missing" or parashara_light["status"] == "missing":
        return "partial"
    return "matched"


def _open_items(jhora: dict[str, Any], parashara_light: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    if jhora["status"] == "diff_open":
        items.append(
            {
                "source": "jhora",
                "status": "diff_open",
                "label": "JHora export diff",
                "failed_checks": jhora["failed_checks"],
            }
        )
    if parashara_light["status"] == "diff_open":
        items.append(
            {
                "source": "parashara_light",
                "status": "diff_open",
                "label": "Parashara Light manual diff",
                "failed_checks": parashara_light["manual_failed_count"],
            }
        )
    if parashara_light["status"] in {"no_manual_values", "no_checked_fields"}:
        items.append(
            {
                "source": "parashara_light",
                "status": "needs_manual_witness",
                "label": "Fill Parashara Light manual witness values",
                "completion_percent": parashara_light["manual_completion_percent"],
            }
        )
    return items
