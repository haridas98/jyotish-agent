from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def build_parashara_light_option_store_diff_report(
    *,
    before_snapshot_path: str | Path,
    changed_snapshot_path: str | Path,
    restored_snapshot_path: str | Path,
) -> dict[str, Any]:
    before_source = Path(before_snapshot_path)
    changed_source = Path(changed_snapshot_path)
    restored_source = Path(restored_snapshot_path)
    before = _load_snapshot(before_source)
    changed = _load_snapshot(changed_source)
    restored = _load_snapshot(restored_source)

    before_files = _files_by_path(before)
    changed_files = _files_by_path(changed)
    restored_files = _files_by_path(restored)
    candidate_paths = sorted(set(before_files) | set(changed_files) | set(restored_files))
    changed_candidates = [
        _diff_payload(relative_path, before_files, changed_files, restored_files)
        for relative_path in candidate_paths
        if _hash_for(before_files, relative_path) != _hash_for(changed_files, relative_path)
    ]
    restore_verified = all(
        _hash_for(before_files, relative_path) == _hash_for(restored_files, relative_path)
        for relative_path in candidate_paths
    )

    status = _status(changed_candidates, restore_verified)
    return {
        "source": "parashara_light_option_store_diff",
        "artifact_policy": "private_audit_only_do_not_commit",
        "proprietary_binary_policy": "hash_only_do_not_parse",
        "captured_at": datetime.now(UTC).isoformat(),
        "status": status,
        "visible_setting": _visible_setting(before, changed, restored),
        "source_snapshots": {
            "before": _file_fingerprint(before_source, classification="before_hash_snapshot"),
            "changed": _file_fingerprint(changed_source, classification="changed_hash_snapshot"),
            "restored": _file_fingerprint(restored_source, classification="restored_hash_snapshot"),
        },
        "snapshot_labels": {
            "before": before.get("label", ""),
            "changed": changed.get("label", ""),
            "restored": restored.get("label", ""),
        },
        "candidate_counts": {
            "before": len(before_files),
            "changed": len(changed_files),
            "restored": len(restored_files),
        },
        "changed_candidates_count": len(changed_candidates),
        "changed_candidates": changed_candidates,
        "primary_candidate": changed_candidates[0]["relative_path"] if changed_candidates else "",
        "restore_verified": restore_verified,
        "next_action": _next_action(status),
        "notes": [
            "Only file metadata and SHA-256 hashes are compared; proprietary option bytes are not parsed.",
            "A restored hash matching the before snapshot means the visible setting was returned to its baseline state.",
        ],
    }


def _load_snapshot(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _files_by_path(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = snapshot.get("files") if isinstance(snapshot.get("files"), list) else []
    result = {}
    for item in files:
        if not isinstance(item, dict):
            continue
        relative_path = str(item.get("relative_path") or "")
        if relative_path:
            result[relative_path] = item
    return result


def _diff_payload(
    relative_path: str,
    before_files: dict[str, dict[str, Any]],
    changed_files: dict[str, dict[str, Any]],
    restored_files: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    before = before_files.get(relative_path, {})
    changed = changed_files.get(relative_path, {})
    restored = restored_files.get(relative_path, {})
    before_hash = str(before.get("sha256") or "")
    changed_hash = str(changed.get("sha256") or "")
    restored_hash = str(restored.get("sha256") or "")
    return {
        "relative_path": relative_path,
        "before_sha256": before_hash,
        "changed_sha256": changed_hash,
        "restored_sha256": restored_hash,
        "before_bytes": int(before.get("bytes") or 0),
        "changed_bytes": int(changed.get("bytes") or 0),
        "restored_bytes": int(restored.get("bytes") or 0),
        "changed_from_before": before_hash != changed_hash,
        "restored_to_before": before_hash == restored_hash,
    }


def _hash_for(files: dict[str, dict[str, Any]], relative_path: str) -> str:
    return str(files.get(relative_path, {}).get("sha256") or "")


def _visible_setting(*snapshots: dict[str, Any]) -> str:
    for snapshot in snapshots:
        value = snapshot.get("visible_setting")
        if value:
            return str(value)
        action = snapshot.get("action")
        if isinstance(action, dict) and action.get("visible_setting"):
            return str(action["visible_setting"])
    return ""


def _status(changed_candidates: list[dict[str, Any]], restore_verified: bool) -> str:
    if not changed_candidates:
        return "no_option_store_hash_change_detected"
    if restore_verified:
        return "option_store_diff_captured"
    return "option_store_restore_mismatch"


def _next_action(status: str) -> str:
    if status == "option_store_diff_captured":
        return "inspect_pl_native_export_or_ephemeris_mode"
    if status == "no_option_store_hash_change_detected":
        return "try_another_visible_setting_or_capture_native_export"
    return "restore_visible_setting_manually_before_continuing"


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
