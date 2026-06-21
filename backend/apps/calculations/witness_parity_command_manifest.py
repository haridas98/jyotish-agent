from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from apps.calculations.witness_parity_roadmap import PARITY_ROADMAP_DOMAINS


SCHEMA_VERSION = "witness-parity-command-manifest.v1"

_TRANSIT_COORDINATE_KEY = "witness_transit_coordinate_parity"


def build_witness_parity_command_manifest() -> dict[str, Any]:
    domains = [_domain_row(key, label) for key, label in PARITY_ROADMAP_DOMAINS]
    missing_count = sum(len(row["missing"]) for row in domains)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "ready" if missing_count == 0 else "blocked",
        "totals": {
            "integrated_count": len(domains),
            "backend_module_count": sum(1 for row in domains if row["backend_module_exists"]),
            "backend_command_count": sum(1 for row in domains if row["backend_command_exists"]),
            "backend_test_count": sum(1 for row in domains if row["backend_test_exists"]),
            "frontend_gate_count": sum(1 for row in domains if row["frontend_gate_exists"]),
            "missing_count": missing_count,
        },
        "domains": domains,
    }


def _domain_row(key: str, label: str) -> dict[str, Any]:
    stem = _backend_stem(key)
    frontend_stem = _frontend_stem(key)
    backend_module = f"witness_{stem}_parity"
    backend_command = f"build_witness_{stem}_parity_report"
    backend_test_module = f"test_witness_{stem}_parity"
    frontend_gate_script = f"check-accuracy-{frontend_stem}-parity-ui.mjs"
    exists = {
        "backend_module": _module_exists(f"apps.calculations.{backend_module}"),
        "backend_command": _module_exists(f"apps.calculations.management.commands.{backend_command}"),
        "backend_test": _module_exists(f"apps.calculations.{backend_test_module}"),
        "frontend_gate": _frontend_gate_exists(frontend_gate_script),
    }
    return {
        "key": key,
        "label": label,
        "backend_module": backend_module,
        "backend_command": backend_command,
        "backend_test_module": backend_test_module,
        "frontend_gate_script": frontend_gate_script,
        "backend_module_exists": exists["backend_module"],
        "backend_command_exists": exists["backend_command"],
        "backend_test_exists": exists["backend_test"],
        "frontend_gate_exists": exists["frontend_gate"],
        "missing": [name for name, present in exists.items() if not present],
    }


def _backend_stem(key: str) -> str:
    if key == _TRANSIT_COORDINATE_KEY:
        return "transit_coordinates"
    stem = key
    if stem.startswith("witness_"):
        stem = stem[len("witness_") :]
    if stem.endswith("_parity"):
        stem = stem[: -len("_parity")]
    return stem


def _frontend_stem(key: str) -> str:
    stem = key
    if stem.startswith("witness_"):
        stem = stem[len("witness_") :]
    if stem.endswith("_parity"):
        stem = stem[: -len("_parity")]
    return stem.replace("_", "-")


def _module_exists(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _frontend_gate_exists(script_name: str) -> bool:
    repo_root = Path(__file__).resolve().parents[3]
    return (repo_root / "frontend" / "scripts" / script_name).is_file()
