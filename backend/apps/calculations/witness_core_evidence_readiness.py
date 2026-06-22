from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-readiness-preflight-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P57-A"
READINESS_STATUS = "blocked_missing_evidence"
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
OPERATOR_NOTE = "Evidence must be collected and attached before mark commands are attempted."


def build_witness_core_evidence_readiness_report(*, intake_report_path: str | Path) -> dict[str, Any]:
    intake = _read_json(Path(intake_report_path))
    intake_summary = intake.get("summary") if isinstance(intake.get("summary"), dict) else {}
    intake_rows = [row for row in intake.get("rows", []) if isinstance(row, dict)]
    rows = [_readiness_row(row, readiness_index=index) for index, row in enumerate(intake_rows, start=1)]
    operator_packet_manifest = [_operator_packet(row) for row in rows]
    jhora_missing_count = sum(
        1 for row in rows if "jhora_screenshot_or_packet" in row["missing_evidence_families"]
    )
    parashara_light_missing_count = sum(
        1 for row in rows if "parashara_light_manual_values_or_packet" in row["missing_evidence_families"]
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": READINESS_STATUS if rows else "empty",
        "operator_note": OPERATOR_NOTE,
        "summary": {
            "intake_rows": _safe_int(intake_summary.get("intake_rows", len(intake_rows))),
            "readiness_rows": len(rows),
            "ready_to_mark_count": 0,
            "blocked_missing_evidence_count": len(rows),
            "missing_evidence_slot_count": jhora_missing_count + parashara_light_missing_count,
            "jhora_missing_count": jhora_missing_count,
            "parashara_light_missing_count": parashara_light_missing_count,
            "evidence_files_committed_count": _safe_int(intake_summary.get("evidence_files_committed_count")),
            "remaining_not_reviewed_count": _safe_int(intake_summary.get("remaining_not_reviewed_count")),
            "release_gate_status": _safe_status(intake_summary.get("release_gate_status"), fallback="blocked"),
            "command_smoke_matrix_status": _safe_status(
                intake_summary.get("command_smoke_matrix_status"),
                fallback="ready",
            ),
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "rows": rows,
        "operator_packet_manifest": operator_packet_manifest,
    }


def _readiness_row(row: dict[str, Any], *, readiness_index: int) -> dict[str, Any]:
    evidence_slot_status = _safe_slot_status(row.get("evidence_slot_status"))
    missing_evidence_families = [
        family for family in REQUIRED_EVIDENCE_FAMILIES if evidence_slot_status.get(family) == "missing"
    ]
    return {
        "readiness_index": readiness_index,
        "intake_index": _safe_int(row.get("intake_index")) or readiness_index,
        "candidate_index": _safe_int(row.get("candidate_index")),
        "case_id": str(row.get("case_id") or ""),
        "source_family": _safe_source_family(row.get("source_family")),
        "required_evidence_families": _safe_evidence_families(row.get("required_evidence_families")),
        "evidence_slot_status": evidence_slot_status,
        "ready_to_mark": False,
        "readiness_status": READINESS_STATUS,
        "missing_evidence_families": missing_evidence_families,
        "safe_next_actions": SAFE_NEXT_ACTIONS,
        "safe_validation_commands": SAFE_VALIDATION_COMMANDS,
    }


def _operator_packet(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "readiness_index": row["readiness_index"],
        "intake_index": row["intake_index"],
        "candidate_index": row["candidate_index"],
        "case_id": row["case_id"],
        "source_family": row["source_family"],
        "evidence_families_to_collect": row["required_evidence_families"],
        "evidence_slot_status": row["evidence_slot_status"],
        "safe_action_labels": SAFE_NEXT_ACTIONS,
        "validation_command_families": SAFE_VALIDATION_COMMANDS,
        "blocked_note": OPERATOR_NOTE,
    }


def _safe_slot_status(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {
            "jhora_screenshot_or_packet": "missing",
            "parashara_light_manual_values_or_packet": "missing",
        }
    return {
        family: "missing" if str(value.get(family) or "") == "missing" else "missing"
        for family in REQUIRED_EVIDENCE_FAMILIES
    }


def _safe_evidence_families(value: Any) -> list[str]:
    if not isinstance(value, list):
        return REQUIRED_EVIDENCE_FAMILIES
    allowed = set(REQUIRED_EVIDENCE_FAMILIES)
    families = [str(item) for item in value if str(item) in allowed]
    return families or REQUIRED_EVIDENCE_FAMILIES


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
