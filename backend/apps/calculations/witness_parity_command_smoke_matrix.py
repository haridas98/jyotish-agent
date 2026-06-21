from __future__ import annotations

from typing import Any

from apps.calculations.witness_parity_command_manifest import (
    SCHEMA_VERSION as MANIFEST_SCHEMA_VERSION,
    build_witness_parity_command_manifest,
)


SCHEMA_VERSION = "witness-parity-command-smoke-matrix.v1"


def build_witness_parity_command_smoke_matrix() -> dict[str, Any]:
    manifest = build_witness_parity_command_manifest()
    domains = [_domain_row(row) for row in manifest.get("domains", []) if isinstance(row, dict)]
    blocked_count = sum(1 for row in domains if not row["smoke_ready"])
    missing_count = sum(len(row["missing"]) for row in domains)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_from_schema_version": MANIFEST_SCHEMA_VERSION,
        "status": "ready" if blocked_count == 0 else "blocked",
        "totals": {
            "domain_count": len(domains),
            "smoke_ready_count": sum(1 for row in domains if row["smoke_ready"]),
            "blocked_count": blocked_count,
            "missing_count": missing_count,
        },
        "domains": domains,
    }


def _domain_row(manifest_row: dict[str, Any]) -> dict[str, Any]:
    backend_command_exists = bool(manifest_row.get("backend_command_exists"))
    backend_test_exists = bool(manifest_row.get("backend_test_exists"))
    frontend_gate_exists = bool(manifest_row.get("frontend_gate_exists"))
    smoke_ready = bool(manifest_row.get("backend_module_exists")) and backend_command_exists and backend_test_exists and frontend_gate_exists
    backend_command = str(manifest_row.get("backend_command") or "")
    return {
        "key": str(manifest_row.get("key") or ""),
        "label": str(manifest_row.get("label") or ""),
        "backend_command": backend_command,
        "frontend_gate_script": str(manifest_row.get("frontend_gate_script") or ""),
        "smoke_ready": smoke_ready,
        "missing": _safe_missing(manifest_row.get("missing")),
        "contract": {
            "has_backend_command": backend_command_exists,
            "has_backend_test": backend_test_exists,
            "has_frontend_gate": frontend_gate_exists,
            "command_invocation_hint": f"manage.py {backend_command} --out <file>" if backend_command else "manage.py <command> --out <file>",
        },
    }


def _safe_missing(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    allowed = {"backend_module", "backend_command", "backend_test", "frontend_gate"}
    return [str(item) for item in value if str(item) in allowed]
