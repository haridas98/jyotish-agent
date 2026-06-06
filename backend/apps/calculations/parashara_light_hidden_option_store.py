from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def build_parashara_light_hidden_option_store_report(
    *,
    settings_evidence_path: str | Path,
) -> dict[str, Any]:
    source = Path(settings_evidence_path)
    evidence = json.loads(source.read_text(encoding="utf-8-sig"))
    options = evidence.get("options_manifest") if isinstance(evidence.get("options_manifest"), list) else []
    sessions = (
        evidence.get("session_token_manifest")
        if isinstance(evidence.get("session_token_manifest"), list)
        else []
    )
    option_candidates = [_candidate_payload(item) for item in options if _is_option_store_candidate(item)]
    option_candidates.sort(key=_candidate_sort_key)
    session_candidates = [_candidate_payload(item) for item in sessions]
    session_candidates.sort(key=lambda item: str(item.get("modified_at") or ""), reverse=True)
    status = "hidden_option_store_candidates_identified" if option_candidates else "hidden_option_store_candidates_missing"
    return {
        "source": "parashara_light_hidden_option_store",
        "artifact_policy": "private_audit_only_do_not_commit",
        "proprietary_binary_policy": "hash_only_do_not_parse",
        "captured_at": datetime.now(UTC).isoformat(),
        "status": status,
        "source_settings_evidence": _file_fingerprint(source, classification="pl_settings_evidence_report"),
        "primary_candidate": option_candidates[0] if option_candidates else {},
        "candidate_counts": {
            "option_store_candidates": len(option_candidates),
            "session_token_candidates": len(session_candidates),
            "source_options_count": len(options),
        },
        "option_store_candidates": option_candidates,
        "session_token_candidates": session_candidates[:10],
        "next_action": (
            "diff_option_store_before_after_visible_setting_change"
            if option_candidates
            else "capture_native_export_or_hidden_option_store"
        ),
        "notes": [
            "Candidates are selected by filename and timestamp only; proprietary option bytes are not parsed.",
            "popts*.dat and OP*/TRANSOP* files are treated as likely option stores until proven otherwise by before/after hash diffs.",
        ],
    }


def _is_option_store_candidate(item: object) -> bool:
    if not isinstance(item, dict):
        return False
    name = str(item.get("relative_path") or "").lower()
    path = Path(name)
    return (
        name.startswith("popts")
        or name.startswith("op")
        or name.startswith("transop")
        or "option" in name
        or path.suffix.lower() in {".wsl"}
    )


def _candidate_payload(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "relative_path": item.get("relative_path", ""),
        "bytes": int(item.get("bytes") or 0),
        "modified_at": item.get("modified_at", ""),
        "sha256": item.get("sha256", ""),
        "classification": item.get("classification", ""),
        "reason": _candidate_reason(str(item.get("relative_path") or "")),
    }


def _candidate_reason(relative_path: str) -> str:
    lower = relative_path.lower()
    if lower.startswith("popts"):
        return "primary_preferences_option_store_name"
    if lower.startswith("op"):
        return "option_store_name_prefix"
    if lower.startswith("transop"):
        return "transit_option_store_name_prefix"
    if lower.endswith(".wsl"):
        return "worksheet_layout_option_store_candidate"
    if "option" in lower:
        return "contains_option_name"
    return "option_store_candidate"


def _candidate_sort_key(item: dict[str, Any]) -> tuple[int, str]:
    reason_rank = {
        "primary_preferences_option_store_name": 0,
        "option_store_name_prefix": 1,
        "transit_option_store_name_prefix": 2,
        "contains_option_name": 3,
        "worksheet_layout_option_store_candidate": 4,
    }
    return (reason_rank.get(str(item.get("reason")), 9), str(item.get("relative_path") or ""))


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
