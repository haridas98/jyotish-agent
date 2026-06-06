from __future__ import annotations

import hashlib
import locale
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .parashara_light_profile import build_parashara_light_profile_report


TEXT_ARTIFACTS = (
    Path("Bin") / "paths.txt",
    Path("Bin") / "langnm.txt",
    Path("Temp") / "recover.txt",
    Path("Temp") / "htpl.log",
)


def build_parashara_light_settings_evidence(
    *,
    chart_xml: str | Path,
    options_dir: str | Path,
    pl7_dir: str | Path,
    session_token_limit: int = 40,
) -> dict[str, Any]:
    chart_path = Path(chart_xml)
    options_path = Path(options_dir)
    pl7_path = Path(pl7_dir)
    _require_file(chart_path, "chart_xml")
    _require_dir(options_path, "options_dir")
    _require_dir(pl7_path, "pl7_dir")

    birth_profile = build_parashara_light_profile_report(chart_path)
    return {
        "source": "parashara_light_settings_evidence",
        "artifact_policy": "private_audit_only_do_not_commit",
        "proprietary_binary_policy": "hash_only_do_not_parse",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "next_action": "capture_visible_pl_profile_settings",
        "source_paths": {
            "chart_xml": str(chart_path),
            "options_dir": str(options_path),
            "pl7_dir": str(pl7_path),
        },
        "environment": _environment_snapshot(),
        "birth_profile": {
            "subject": birth_profile.get("subject", {}),
            "raw_birth_info": birth_profile.get("raw_birth_info", {}),
            "candidate_normalization": birth_profile.get("candidate_normalization", {}),
            "data_quality_flags": birth_profile.get("data_quality_flags", []),
        },
        "chart_manifest": _manifest_entry(
            chart_path,
            root=chart_path.parent,
            classification="birth_xml_profile_source",
        ),
        "options_manifest": [
            _manifest_entry(path, root=options_path, classification="proprietary_option_hash_only")
            for path in _iter_files(options_path)
        ],
        "text_artifacts": _text_artifacts(pl7_path),
        "session_token_manifest": [
            _manifest_entry(path, root=pl7_path, classification="opaque_session_token_hash_only")
            for path in _recent_session_tokens(pl7_path, limit=session_token_limit)
        ],
        "notes": [
            "This report deliberately avoids deserializing PL7 proprietary option/session formats.",
            "Use hashes and timestamps to prove which PL7 artifacts were present during the audit window.",
            "Visible PL profile/settings screens are still required before treating calculation settings as confirmed.",
        ],
    }


def _environment_snapshot() -> dict[str, Any]:
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "locale": locale.getlocale(),
        "timezone_name": time.tzname,
        "timezone_offset_seconds": time.timezone,
        "daylight_saving_observed": bool(time.daylight),
    }


def _text_artifacts(pl7_path: Path) -> list[dict[str, Any]]:
    artifacts = []
    for relative in TEXT_ARTIFACTS:
        path = pl7_path / relative
        if not path.exists() or not path.is_file():
            continue
        entry = _manifest_entry(path, root=pl7_path, classification="safe_text_runtime_artifact")
        entry["content_preview"] = _decode_preview(path)
        artifacts.append(entry)
    return artifacts


def _recent_session_tokens(pl7_path: Path, *, limit: int) -> list[Path]:
    temp_dir = pl7_path / "Temp"
    if not temp_dir.exists() or not temp_dir.is_dir():
        return []
    files = [path for path in temp_dir.glob("*.e31") if path.is_file()]
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return files[: max(limit, 0)]


def _iter_files(root: Path) -> list[Path]:
    return sorted((path for path in root.rglob("*") if path.is_file()), key=lambda path: _relative_path(path, root))


def _manifest_entry(path: Path, *, root: Path, classification: str) -> dict[str, Any]:
    stat = path.stat()
    return {
        "relative_path": _relative_path(path, root),
        "bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "sha256": _sha256(path),
        "classification": classification,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _decode_preview(path: Path, *, limit: int = 500) -> str:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "cp1251", "latin-1"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = ""
    text = "".join(char if char.isprintable() or char in "\r\n\t" else " " for char in text)
    return text.strip()[:limit]


def _relative_path(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _require_file(path: Path, label: str) -> None:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"{label} file not found: {path}")


def _require_dir(path: Path, label: str) -> None:
    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"{label} directory not found: {path}")
