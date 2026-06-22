from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-backlog-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P53-A"
SAFE_COMMAND_FAMILIES = [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
]
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
NEXT_ACTIONS = [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_preflight_witness_review",
]


def build_witness_core_evidence_backlog_report(
    *,
    preflight_report_path: str | Path,
    batch_report_path: str | Path,
    core_report_path: str | Path,
) -> dict[str, Any]:
    preflight = _read_json(Path(preflight_report_path))
    batch = _read_json(Path(batch_report_path))
    core = _read_json(Path(core_report_path))
    batch_summary = batch.get("summary") if isinstance(batch.get("summary"), dict) else {}
    core_summary = core.get("summary") if isinstance(core.get("summary"), dict) else {}
    preflight_summary = preflight.get("summary") if isinstance(preflight.get("summary"), dict) else {}
    skipped_rows = [row for row in batch.get("skipped_rows", []) if isinstance(row, dict)]
    rows = [_backlog_row(row, index=index) for index, row in enumerate(skipped_rows, start=1)]
    blocked_count = len(rows)
    ready_to_mark_count = 0
    remaining_not_reviewed = _safe_int(
        batch_summary.get("after_not_reviewed_count", preflight_summary.get("not_reviewed_count"))
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": "blocked_evidence_backlog" if blocked_count else "empty",
        "safe_command_families": SAFE_COMMAND_FAMILIES,
        "summary": {
            "candidate_count": len(rows),
            "blocked_count": blocked_count,
            "ready_to_mark_count": ready_to_mark_count,
            "remaining_not_reviewed_count": remaining_not_reviewed,
            "release_gate_status": _safe_status(batch_summary.get("release_gate_status"), fallback="blocked"),
            "command_smoke_matrix_status": _safe_status(batch_summary.get("command_smoke_matrix_status"), fallback="ready"),
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "core_counts": {
            "case_count": _safe_int(core_summary.get("case_count")),
            "comparable_count": _safe_int(core_summary.get("comparable_count")),
            "failed_count": _safe_int(core_summary.get("failed_count")),
            "not_reviewed_count": _safe_int(core_summary.get("not_reviewed_count")),
        },
        "evidence_family_counts": {
            family: blocked_count for family in REQUIRED_EVIDENCE_FAMILIES
        },
        "rows": rows,
    }


def _backlog_row(row: dict[str, Any], *, index: int) -> dict[str, Any]:
    return {
        "candidate_index": _safe_int(row.get("candidate_index")) or index,
        "case_id": str(row.get("case_id") or ""),
        "source_family": _safe_source_family(row.get("source_family")),
        "required_evidence_families": REQUIRED_EVIDENCE_FAMILIES,
        "safe_blockers": _safe_blockers(row.get("safe_blockers")),
        "next_actions": NEXT_ACTIONS,
    }


def _safe_blockers(value: Any) -> list[str]:
    allowed = {"jhora_missing_or_blocked", "parashara_light_missing_or_blocked"}
    if not isinstance(value, list):
        return ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"]
    blockers = [str(item) for item in value if str(item) in allowed]
    return blockers or ["jhora_missing_or_blocked", "parashara_light_missing_or_blocked"]


def _safe_source_family(value: Any) -> str:
    text = str(value or "")
    return text if text in {"jhora", "parashara_light", "both", "none"} else "none"


def _safe_status(value: Any, *, fallback: str) -> str:
    text = str(value or "")
    return text if text in {"blocked", "ready"} else fallback


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
