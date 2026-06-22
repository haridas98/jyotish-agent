from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-core-evidence-attachment-gate-v1"
DOMAIN_KEY = "witness_core_parity"
STAGE = "P59-A"
ATTACHMENT_GATE_STATUS = "blocked_no_attached_evidence"
REQUIRED_EVIDENCE_FAMILIES = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]
SAFE_NEXT_ACTIONS = [
    "collect_jhora_screenshot",
    "attach_parashara_light_manual_values",
    "rerun_evidence_attachment_gate",
    "rerun_preflight_witness_review",
]
SAFE_VALIDATION_COMMANDS = [
    "build_witness_core_evidence_attachment_gate_report",
    "preflight_witness_review",
    "mark_jhora_witness_reviewed",
    "mark_parashara_light_witness_reviewed",
]
OPERATOR_NOTE = "Evidence must be attached before mark commands are attempted."


def build_witness_core_evidence_attachment_gate_report(*, readiness_report_path: str | Path) -> dict[str, Any]:
    readiness = _read_json(Path(readiness_report_path))
    readiness_summary = readiness.get("summary") if isinstance(readiness.get("summary"), dict) else {}
    readiness_rows = [row for row in readiness.get("rows", []) if isinstance(row, dict)]
    rows = [_attachment_row(row, attachment_index=index) for index, row in enumerate(readiness_rows, start=1)]
    operator_attachment_manifest = [_operator_attachment(row) for row in rows]
    missing_attachment_slot_count = sum(len(row["missing_attachment_families"]) for row in rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "domain": DOMAIN_KEY,
        "stage": STAGE,
        "status": ATTACHMENT_GATE_STATUS if rows else "empty",
        "operator_note": OPERATOR_NOTE,
        "summary": {
            "readiness_rows": _safe_int(readiness_summary.get("readiness_rows", len(readiness_rows))),
            "attachment_rows": len(rows),
            "operator_attachment_manifest_rows": len(operator_attachment_manifest),
            "attached_evidence_files_count": 0,
            "attached_evidence_family_count": 0,
            "missing_attachment_slot_count": missing_attachment_slot_count,
            "jhora_attached_count": 0,
            "parashara_light_attached_count": 0,
            "jhora_missing_count": sum(
                1 for row in rows if "jhora_screenshot_or_packet" in row["missing_attachment_families"]
            ),
            "parashara_light_missing_count": sum(
                1
                for row in rows
                if "parashara_light_manual_values_or_packet" in row["missing_attachment_families"]
            ),
            "ready_to_mark_count": 0,
            "blocked_no_attached_evidence_count": len(rows),
            "remaining_not_reviewed_count": _safe_int(readiness_summary.get("remaining_not_reviewed_count")),
            "release_gate_status": _safe_status(readiness_summary.get("release_gate_status"), fallback="blocked"),
            "command_smoke_matrix_status": _safe_status(
                readiness_summary.get("command_smoke_matrix_status"),
                fallback="ready",
            ),
            "parity_success_claimed": False,
            "release_ready_claimed": False,
        },
        "rows": rows,
        "operator_attachment_manifest": operator_attachment_manifest,
    }


def _attachment_row(row: dict[str, Any], *, attachment_index: int) -> dict[str, Any]:
    attachment_slot_status = {
        family: "not_attached"
        for family in REQUIRED_EVIDENCE_FAMILIES
    }
    missing_attachment_families = [
        family for family in REQUIRED_EVIDENCE_FAMILIES if attachment_slot_status.get(family) == "not_attached"
    ]
    return {
        "attachment_index": attachment_index,
        "readiness_index": _safe_int(row.get("readiness_index")) or attachment_index,
        "intake_index": _safe_int(row.get("intake_index")) or attachment_index,
        "candidate_index": _safe_int(row.get("candidate_index")),
        "case_id": str(row.get("case_id") or ""),
        "source_family": _safe_source_family(row.get("source_family")),
        "required_evidence_families": _safe_evidence_families(row.get("required_evidence_families")),
        "p57_evidence_slot_status": _safe_p57_slot_status(row.get("evidence_slot_status")),
        "attachment_slot_status": attachment_slot_status,
        "attached_evidence_family_count": 0,
        "ready_to_mark": False,
        "attachment_gate_status": ATTACHMENT_GATE_STATUS,
        "missing_attachment_families": missing_attachment_families,
        "safe_next_actions": SAFE_NEXT_ACTIONS,
        "safe_validation_commands": SAFE_VALIDATION_COMMANDS,
    }


def _operator_attachment(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "attachment_index": row["attachment_index"],
        "readiness_index": row["readiness_index"],
        "intake_index": row["intake_index"],
        "candidate_index": row["candidate_index"],
        "case_id": row["case_id"],
        "source_family": row["source_family"],
        "evidence_families_to_attach": row["required_evidence_families"],
        "attachment_slot_status": row["attachment_slot_status"],
        "safe_action_labels": SAFE_NEXT_ACTIONS,
        "validation_command_families": SAFE_VALIDATION_COMMANDS,
        "blocked_note": OPERATOR_NOTE,
    }


def _safe_p57_slot_status(value: Any) -> dict[str, str]:
    if not isinstance(value, dict):
        return {family: "missing" for family in REQUIRED_EVIDENCE_FAMILIES}
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
