from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .witness_batch import _case_row, _scan_fixture_records, audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-core-review-preflight-v1"
DOMAIN_KEY = "witness_core_parity"
DOMAIN_LABEL = "Core parity"
SAFE_COMMAND_FAMILIES = [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
]
BLOCKER_LABELS = {
    "authoritative_review_status": "jhora_review_status",
    "expected_or_jhora_expected": "jhora_values",
}


def build_witness_core_review_preflight(
    *,
    jhora_root: str | Path,
    pl_root: str | Path,
    core_report_path: str | Path,
    collection_plan: dict[str, Any],
    repo_root: str | Path,
) -> dict[str, Any]:
    core_report = _read_json(Path(core_report_path))
    audit = audit_jhora_pl_witness_batch(jhora_root=jhora_root, pl_root=pl_root, target_reviewed_count=20)
    audit_cases = _direct_case_rows(jhora_root=jhora_root, pl_root=pl_root)
    audit_cases.update({str(row.get("id") or ""): row for row in audit.get("cases", []) if isinstance(row, dict)})
    core_cases = [row for row in core_report.get("cases", []) if isinstance(row, dict)]
    rows = [
        _row(core_case, audit_cases.get(str(core_case.get("case_id") or ""), {}), repo_root=Path(repo_root))
        for core_case in core_cases
        if str(core_case.get("comparison_status") or "") == "not_reviewed"
    ]
    summary = core_report.get("summary") if isinstance(core_report.get("summary"), dict) else {}
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "label": DOMAIN_LABEL,
        "artifact_availability": _artifact_availability(collection_plan),
        "release_gate_status": str(collection_plan.get("release_gate_status") or ""),
        "command_smoke_matrix_status": str(collection_plan.get("command_smoke_matrix_status") or ""),
        "status": "blocked",
        "blocked_reason": "witness_core_parity is blocked by not-reviewed witness rows",
        "availability_note": "artifact availability is aligned at 19/19/0",
        "release_note": "release gate remains blocked",
        "claim_policy": "no parity success or release readiness is claimed",
        "safe_command_families": SAFE_COMMAND_FAMILIES,
        "summary": {
            "case_count": _safe_int(summary.get("case_count")),
            "not_reviewed_count": len(rows),
            "blocked_by": "review_witness_rows",
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "rows": rows,
    }


def _row(core_case: dict[str, Any], audit_case: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    jhora_paths = _record_paths(audit_case.get("jhora_records"), repo_root=repo_root)
    pl_paths = _record_paths(audit_case.get("pl_records"), repo_root=repo_root)
    return {
        "case_id": str(core_case.get("case_id") or audit_case.get("id") or ""),
        "review_status": str(core_case.get("review_status") or ""),
        "comparison_status": "not_reviewed",
        "source_family": _source_family(jhora_paths, pl_paths),
        "jhora_evidence_paths": jhora_paths,
        "parashara_light_evidence_paths": pl_paths,
        "review_blockers": {
            "jhora": _safe_blockers(audit_case.get("missing_for_authoritative_review")),
            "parashara_light": _safe_blockers(audit_case.get("missing_secondary_witness")),
        },
        "next_command_families": SAFE_COMMAND_FAMILIES,
    }


def _artifact_availability(collection_plan: dict[str, Any]) -> dict[str, int]:
    value = collection_plan.get("report_availability") if isinstance(collection_plan.get("report_availability"), dict) else {}
    return {
        "domain_count": _safe_int(value.get("domain_count")),
        "present_count": _safe_int(value.get("present_count")),
        "missing_count": _safe_int(value.get("missing_count")),
    }


def _direct_case_rows(*, jhora_root: str | Path, pl_root: str | Path) -> dict[str, dict[str, Any]]:
    load_errors: list[dict[str, str]] = []
    jhora_records = _scan_fixture_records(Path(jhora_root), "jhora", load_errors)
    pl_records = _scan_fixture_records(Path(pl_root), "parashara_light", load_errors)
    case_ids = sorted({record["id"] for record in [*jhora_records, *pl_records] if record.get("id")})
    result: dict[str, dict[str, Any]] = {}
    for case_id in case_ids:
        result[case_id] = _case_row(
            {"id": case_id, "group": "review_backlog", "label": case_id, "focus": []},
            [record for record in jhora_records if record.get("id") == case_id],
            [record for record in pl_records if record.get("id") == case_id],
        )
    return result


def _record_paths(value: Any, *, repo_root: Path) -> list[str]:
    if not isinstance(value, list):
        return []
    paths = []
    for row in value:
        if not isinstance(row, dict):
            continue
        path = str(row.get("path") or "").strip()
        if path:
            paths.append(_repo_relative_path(Path(path), repo_root=repo_root))
    return sorted(dict.fromkeys(paths))


def _repo_relative_path(path: Path, *, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.name


def _source_family(jhora_paths: list[str], pl_paths: list[str]) -> str:
    if jhora_paths and pl_paths:
        return "both"
    if jhora_paths:
        return "jhora"
    if pl_paths:
        return "parashara_light"
    return "none"


def _safe_blockers(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [BLOCKER_LABELS.get(str(item), str(item)) for item in value]


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
