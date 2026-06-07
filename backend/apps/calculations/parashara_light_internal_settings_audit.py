from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def build_parashara_light_internal_settings_audit(
    *,
    settings_aware_forensic_path: str | Path,
    preferences_inventory_path: str | Path,
    hidden_option_store_path: str | Path,
    option_store_diff_path: str | Path,
) -> dict[str, Any]:
    settings_aware_source = Path(settings_aware_forensic_path)
    preferences_source = Path(preferences_inventory_path)
    hidden_store_source = Path(hidden_option_store_path)
    option_diff_source = Path(option_store_diff_path)

    settings_aware = _read_json(settings_aware_source)
    preferences = _read_json(preferences_source)
    hidden_store = _read_json(hidden_store_source)
    option_diff = _read_json(option_diff_source)
    evidence_gates = _evidence_gates(settings_aware, preferences, hidden_store, option_diff)
    ruled_out = _ruled_out(evidence_gates)
    status = _status(evidence_gates)

    return {
        "source": "parashara_light_internal_settings_audit",
        "artifact_policy": "private_audit_only_do_not_commit",
        "proprietary_binary_policy": "hash_only_do_not_parse",
        "captured_at": datetime.now(UTC).isoformat(),
        "status": status,
        "source_reports": {
            "settings_aware_forensic": _file_fingerprint(
                settings_aware_source,
                classification="pl_settings_aware_forensic_report",
            ),
            "preferences_inventory": _file_fingerprint(
                preferences_source,
                classification="pl_preferences_inventory_report",
            ),
            "hidden_option_store": _file_fingerprint(
                hidden_store_source,
                classification="pl_hidden_option_store_report",
            ),
            "option_store_diff": _file_fingerprint(
                option_diff_source,
                classification="pl_option_store_diff_report",
            ),
        },
        "evidence_gates": evidence_gates,
        "ruled_out": ruled_out,
        "next_action": _next_action(status),
        "notes": [
            "This report does not parse proprietary PL option bytes.",
            "It only links visible UI evidence, hash-only option-store evidence, and forensic mismatch gates.",
        ],
    }


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _evidence_gates(
    settings_aware: dict[str, Any],
    preferences: dict[str, Any],
    hidden_store: dict[str, Any],
    option_diff: dict[str, Any],
) -> dict[str, Any]:
    diagnostic_gates = settings_aware.get("diagnostic_gates") if isinstance(settings_aware.get("diagnostic_gates"), dict) else {}
    visible_settings = settings_aware.get("visible_settings") if isinstance(settings_aware.get("visible_settings"), dict) else {}
    primary_candidate = hidden_store.get("primary_candidate") if isinstance(hidden_store.get("primary_candidate"), dict) else {}
    hidden_counts = hidden_store.get("candidate_counts") if isinstance(hidden_store.get("candidate_counts"), dict) else {}
    return {
        "visible_settings_status": str(settings_aware.get("status") or ""),
        "engine_swiss_status": str(diagnostic_gates.get("engine_swiss_status") or ""),
        "pl_diff_count": int(diagnostic_gates.get("pl_diff_count") or 0),
        "uniform_offset_status": str(diagnostic_gates.get("uniform_offset_status") or ""),
        "time_shift_status": str(diagnostic_gates.get("time_shift_status") or ""),
        "ayanamsha_status": str(visible_settings.get("ayanamsha_status") or ""),
        "offset_status": str(visible_settings.get("offset_status") or ""),
        "preferences_status": str(preferences.get("status") or ""),
        "preferences_tabs_count": int(preferences.get("tabs_count") or 0),
        "internal_ephemeris_mode_visible": bool(preferences.get("internal_ephemeris_mode_visible")),
        "hidden_option_store_status": str(hidden_store.get("status") or ""),
        "hidden_option_store_primary_candidate": str(primary_candidate.get("relative_path") or ""),
        "option_store_candidates_count": int(hidden_counts.get("option_store_candidates") or 0),
        "option_store_diff_status": str(option_diff.get("status") or ""),
        "option_store_changed_candidates_count": int(option_diff.get("changed_candidates_count") or 0),
        "option_store_restore_verified": bool(option_diff.get("restore_verified")),
    }


def _ruled_out(evidence_gates: dict[str, Any]) -> list[str]:
    ruled_out = []
    if evidence_gates.get("visible_settings_status") == "visible_settings_do_not_explain_pl_diff":
        ruled_out.append("visible_calculation_options")
    if not evidence_gates.get("internal_ephemeris_mode_visible"):
        ruled_out.append("visible_preferences_ephemeris_mode")
    if evidence_gates.get("uniform_offset_status") == "rejected":
        ruled_out.append("simple_global_offset")
    if evidence_gates.get("time_shift_status") == "rejected":
        ruled_out.append("birth_time_timezone_shift")
    if evidence_gates.get("option_store_diff_status") == "no_option_store_hash_change_detected":
        ruled_out.append("show_status_bar_option_store_probe")
    return ruled_out


def _status(evidence_gates: dict[str, Any]) -> str:
    if evidence_gates.get("internal_ephemeris_mode_visible"):
        return "visible_internal_ephemeris_review_required"
    if (
        evidence_gates.get("visible_settings_status") == "visible_settings_do_not_explain_pl_diff"
        and evidence_gates.get("engine_swiss_status") == "matched"
        and int(evidence_gates.get("pl_diff_count") or 0) > 0
        and evidence_gates.get("hidden_option_store_status") == "hidden_option_store_candidates_identified"
        and evidence_gates.get("option_store_diff_status") == "no_option_store_hash_change_detected"
    ):
        return "internal_settings_unresolved_native_export_required"
    return "internal_settings_audit_incomplete"


def _next_action(status: str) -> str:
    if status == "visible_internal_ephemeris_review_required":
        return "review_visible_internal_ephemeris_mode"
    if status == "internal_settings_unresolved_native_export_required":
        return "capture_pl_native_export_or_internal_ephemeris_mode"
    return "complete_pl_internal_settings_evidence"


def _file_fingerprint(path: Path, *, classification: str) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path),
        "relative_path": path.name,
        "bytes": stat.st_size,
        "sha256": _sha256(path),
        "classification": classification,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
