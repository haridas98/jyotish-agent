from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-intake-plan-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P55-A"
DEFAULT_BATCH_SIZE = 5
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_NEXT_ACTIONS = [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_preflight_witness_review",
]
SAFE_VALIDATION_COMMANDS = [
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
]
OPERATOR_NOTE = "Evidence must be collected/attached before mark commands are attempted."


def build_witness_core_evidence_intake_plan_report(
    *,
    backlog_report_path: str | Path,
    preflight_report_path: str | Path,
    batch_report_path: str | Path,
    intake_batch_size: int = DEFAULT_BATCH_SIZE,
) -> dict[str, Any]:
    backlog = _read_json(Path(backlog_report_path))
    preflight = _read_json(Path(preflight_report_path))
    batch = _read_json(Path(batch_report_path))
    backlog_summary = backlog.get("summary") if isinstance(backlog.get("summary"), dict) else {}
    preflight_summary = preflight.get("summary") if isinstance(preflight.get("summary"), dict) else {}
    rows = [row for row in backlog.get("rows", []) if isinstance(row, dict)]
    size = max(_safe_int(intake_batch_size), 0)
    intake_rows = [_intake_row(row, intake_index=index) for index, row in enumerate(rows[:size], start=1)]
    remaining_not_reviewed = _safe_int(
        backlog_summary.get("remaining_not_reviewed_count", preflight_summary.get("not_reviewed_count"))
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": "blocked_evidence_intake",
        "operator_note": OPERATOR_NOTE,
        "summary": {
            "backlog_rows": _safe_int(backlog_summary.get("candidate_count", len(rows))),
            "intake_batch_size": size,
            "intake_rows": len(intake_rows),
            "blocked_rows": _safe_int(backlog_summary.get("blocked_count", len(rows))),
            "ready_to_mark_count": 0,
            "evidence_files_committed_count": 0,
            "remaining_not_reviewed_count": remaining_not_reviewed,
            "release_gate_status": _safe_status(backlog_summary.get("release_gate_status"), fallback="blocked"),
            "command_smoke_matrix_status": _safe_status(backlog_summary.get("command_smoke_matrix_status"), fallback="ready"),
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "batch_counts": {
            "closed_count": _safe_int(_summary(batch).get("closed_count")),
            "skipped_count": _safe_int(_summary(batch).get("skipped_count")),
        },
        "rows": intake_rows,
    }


def _intake_row(row: dict[str, Any], *, intake_index: int) -> dict[str, Any]:
    return {
        "intake_index": intake_index,
        "candidate_index": _safe_int(row.get("candidate_index")),
        "case_id": str(row.get("case_id") or ""),
        "source_family": _safe_source_family(row.get("source_family")),
        "required_evidence_families": _safe_evidence_families(row.get("required_evidence_families")),
        "evidence_slot_status": {
            "jhora_screenshot_or_packet": "missing",
            "parashara_light_manual_values_or_packet": "missing",
        },
        "safe_next_actions": SAFE_NEXT_ACTIONS,
        "safe_validation_commands": SAFE_VALIDATION_COMMANDS,
        "safe_blockers": _safe_blockers(row.get("safe_blockers")),
    }


def _safe_evidence_families(value: Any) -> list[str]:
    if not isinstance(value, list):
        return REQUIRED_EVIDENCE_FAMILIES
    allowed = set(REQUIRED_EVIDENCE_FAMILIES)
    families = [str(item) for item in value if str(item) in allowed]
    return families or REQUIRED_EVIDENCE_FAMILIES


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


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return summary if isinstance(summary, dict) else {}


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
