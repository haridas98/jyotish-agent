from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .management.commands.preflight_witness_review import build_witness_review_preflight


SCHEMA_VERSION = "jyotish-core-review-batch-v1"
DOMAIN_KEY = "witness_core_parity"
SAFE_COMMAND_FAMILIES = [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
]


def build_witness_core_review_batch_report(
    *,
    preflight_report_path: str | Path,
    core_report_path: str | Path,
    repo_root: str | Path,
    requested_close_count: int = 5,
    reviewer: str = "Haridas",
    reviewed_at: str = "2026-06-22T00:00:00+00:00",
) -> dict[str, Any]:
    preflight = _read_json(Path(preflight_report_path))
    core = _read_json(Path(core_report_path))
    rows = [row for row in preflight.get("rows", []) if isinstance(row, dict)]
    core_summary = core.get("summary") if isinstance(core.get("summary"), dict) else {}
    before_not_reviewed = _safe_int(preflight.get("summary", {}).get("not_reviewed_count"))
    skipped_rows = [
        _skipped_row(
            row,
            index=index,
            repo_root=Path(repo_root),
            reviewer=reviewer,
            reviewed_at=reviewed_at,
        )
        for index, row in enumerate(rows, start=1)
    ]
    closed_rows: list[dict[str, Any]] = []
    closed_count = len(closed_rows)
    skipped_count = len(skipped_rows)
    status = "closed_batch" if closed_count else "blocked_no_reviewable_rows"
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "status": status,
        "safe_command_families": SAFE_COMMAND_FAMILIES,
        "summary": {
            "requested_close_count": _safe_int(requested_close_count),
            "candidate_count": len(rows),
            "closed_count": closed_count,
            "skipped_count": skipped_count,
            "before_not_reviewed_count": before_not_reviewed,
            "after_not_reviewed_count": before_not_reviewed - closed_count,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "core_counts": {
            "case_count": _safe_int(core_summary.get("case_count")),
            "comparable_count": _safe_int(core_summary.get("comparable_count")),
            "failed_count": _safe_int(core_summary.get("failed_count")),
            "not_reviewed_count": _safe_int(core_summary.get("not_reviewed_count")),
        },
        "closed_rows": closed_rows,
        "skipped_rows": skipped_rows,
    }


def _skipped_row(
    row: dict[str, Any],
    *,
    index: int,
    repo_root: Path,
    reviewer: str,
    reviewed_at: str,
) -> dict[str, Any]:
    blockers = _candidate_blockers(row, repo_root=repo_root, reviewer=reviewer, reviewed_at=reviewed_at)
    return {
        "candidate_index": index,
        "case_id": str(row.get("case_id") or ""),
        "source_family": _safe_source_family(row.get("source_family")),
        "status": "skipped_blocked",
        "safe_blockers": blockers,
    }


def _candidate_blockers(
    row: dict[str, Any],
    *,
    repo_root: Path,
    reviewer: str,
    reviewed_at: str,
) -> list[str]:
    jhora_paths = _safe_path_list(row.get("jhora_evidence_paths"))
    pl_paths = _safe_path_list(row.get("parashara_light_evidence_paths"))
    if not jhora_paths and not pl_paths:
        return ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"]
    if not jhora_paths:
        return ["jhora_missing_or_blocked"]
    if not pl_paths:
        return ["parashara_light_missing_or_blocked"]

    best_blockers: list[str] = []
    for jhora_path in jhora_paths:
        for pl_path in pl_paths:
            payload = build_witness_review_preflight(
                jhora_path=repo_root / jhora_path,
                parashara_light_path=repo_root / pl_path,
                reviewer=reviewer,
                reviewed_at=reviewed_at,
            )
            overall = payload.get("overall") if isinstance(payload.get("overall"), dict) else {}
            if overall.get("reviewable"):
                return ["explicit_review_command_required"]
            blockers = _safe_payload_blockers(payload)
            if not best_blockers or len(blockers) < len(best_blockers):
                best_blockers = blockers
    return best_blockers or ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"]


def _safe_payload_blockers(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    jhora = payload.get("jhora") if isinstance(payload.get("jhora"), dict) else {}
    pl = payload.get("parashara_light") if isinstance(payload.get("parashara_light"), dict) else {}
    if jhora.get("missing_evidence"):
        blockers.append("jhora_missing_or_blocked")
    if pl.get("missing_evidence"):
        blockers.append("parashara_light_missing_or_blocked")
    return blockers


def _safe_path_list(value: Any) -> list[Path]:
    if not isinstance(value, list):
        return []
    return [Path(str(item)) for item in value if str(item).strip()]


def _safe_source_family(value: Any) -> str:
    text = str(value or "")
    return text if text in {"jhora", "parashara_light", "both", "none"} else "none"


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
