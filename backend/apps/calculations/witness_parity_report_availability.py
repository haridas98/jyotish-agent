from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping

from django.conf import settings

from apps.calculations.witness_parity_command_manifest import build_witness_parity_command_manifest
from apps.calculations.witness_parity_roadmap import PARITY_ROADMAP_DOMAINS


SCHEMA_VERSION = "witness-parity-report-availability.v1"


def build_witness_parity_report_availability(
    *,
    report_paths: Mapping[str, Any] | None = None,
    path_exists: Callable[[str], bool] | None = None,
) -> dict[str, Any]:
    paths = report_paths or _report_paths_from_settings()
    exists = path_exists or (lambda path: Path(path).is_file())
    manifest_by_key = {
        row.get("key"): row
        for row in build_witness_parity_command_manifest().get("domains", [])
        if isinstance(row, dict)
    }
    domains = [
        _domain_row(key, label, paths=paths, exists=exists, manifest_row=manifest_by_key.get(key) or {})
        for key, label in PARITY_ROADMAP_DOMAINS
    ]
    present_count = sum(1 for row in domains if row["report_present"])
    missing_count = len(domains) - present_count
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready" if missing_count == 0 else "missing_reports",
        "totals": {
            "domain_count": len(domains),
            "present_count": present_count,
            "missing_count": missing_count,
        },
        "domains": domains,
    }


def _domain_row(
    key: str,
    label: str,
    *,
    paths: Mapping[str, Any],
    exists: Callable[[str], bool],
    manifest_row: dict[str, Any],
) -> dict[str, Any]:
    setting_name = _setting_name(key)
    report_path = str(paths.get(setting_name) or "")
    present = bool(report_path and exists(report_path))
    backend_command = str(manifest_row.get("backend_command") or _command_name(key))
    return {
        "key": key,
        "label": label,
        "report_present": present,
        "report_setting": setting_name,
        "report_filename": _safe_filename(report_path),
        "backend_command": backend_command,
        "collection_hint": f"manage.py {backend_command} --output <report-json>",
        "state": "present" if present else "missing",
    }


def _report_paths_from_settings() -> dict[str, Any]:
    return {setting_name: getattr(settings, setting_name, "") for setting_name in _all_setting_names()}


def _all_setting_names() -> list[str]:
    return [_setting_name(key) for key, _label in PARITY_ROADMAP_DOMAINS]


def _setting_name(key: str) -> str:
    stem = key
    if stem.startswith("witness_"):
        stem = stem[len("witness_") :]
    return f"WITNESS_{stem.upper()}_REPORT_PATH"


def _command_name(key: str) -> str:
    stem = key
    if stem.startswith("witness_"):
        stem = stem[len("witness_") :]
    if stem.endswith("_parity"):
        stem = stem[: -len("_parity")]
    if key == "witness_transit_coordinate_parity":
        stem = "transit_coordinates"
    return f"build_witness_{stem}_parity_report"


def _safe_filename(report_path: str) -> str:
    if not report_path:
        return "<report-json>"
    filename = Path(report_path).name
    return filename or "<report-json>"
