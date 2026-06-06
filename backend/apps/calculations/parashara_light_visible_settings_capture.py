from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


SETTINGS_DIALOG_TERMS = (
    "calculation options",
    "formoptionscalculations",
    "calculations_ayanamsha",
    "calculations_lahiri",
    "ayanamsha",
    "system options",
    "ayanamsa",
    "lahiri",
    "node",
    "house system",
)


def build_parashara_light_visible_settings_capture(
    *,
    capture_id: str,
    ui_state_paths: list[str | Path],
    screenshot_paths: list[str | Path],
) -> dict[str, Any]:
    ui_states = [_ui_state_summary(Path(path)) for path in ui_state_paths]
    screenshots = [
        _file_fingerprint(Path(path), classification="visible_settings_screenshot")
        for path in screenshot_paths
    ]
    settings_dialog_captured = any(_looks_like_settings_dialog(state) for state in ui_states)
    options_menu_captured = any(_looks_like_options_menu(path, state) for path, state in zip(ui_state_paths, ui_states))
    status = (
        "settings_dialog_captured"
        if settings_dialog_captured
        else "menu_path_captured_settings_dialog_pending"
        if options_menu_captured
        else "visible_settings_capture_pending"
    )
    return {
        "source": "parashara_light_visible_settings_capture",
        "capture_id": capture_id,
        "artifact_policy": "private_audit_only_do_not_commit",
        "captured_at": datetime.now(UTC).isoformat(),
        "status": status,
        "settings_dialog_captured": settings_dialog_captured,
        "options_menu_captured": options_menu_captured,
        "surfaces_count": len(ui_states),
        "screenshots_count": len(screenshots),
        "ui_states": ui_states,
        "screenshots": screenshots,
        "next_action": (
            "review_visible_calculation_options"
            if settings_dialog_captured
            else "capture_calculation_options_dialog_or_native_export"
        ),
        "notes": [
            "Screenshots are referenced by path and hash only; image bytes are not embedded in this JSON.",
            "This packet records visible PL7 navigation evidence and does not assert settings until a settings dialog or native export is captured.",
        ],
    }


def _ui_state_summary(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    controls = data.get("controls") if isinstance(data.get("controls"), list) else []
    return {
        **_file_fingerprint(path, classification="visible_settings_ui_state"),
        "window_title": str(data.get("window_title") or ""),
        "control_count": int(data.get("control_count") or len(controls)),
        "screenshot_blank": data.get("screenshot_blank"),
        "surface": _surface_from_path(path),
        "matched_terms": _matched_terms(data),
    }


def _looks_like_settings_dialog(state: dict[str, Any]) -> bool:
    return bool(state.get("matched_terms")) and state.get("surface") not in {"options_menu", "main_window"}


def _looks_like_options_menu(path: str | Path, state: dict[str, Any]) -> bool:
    return state.get("surface") == "options_menu" or "options-menu" in Path(path).name


def _matched_terms(data: dict[str, Any]) -> list[str]:
    haystack_parts = [str(data.get("window_title") or "")]
    controls = data.get("controls") if isinstance(data.get("controls"), list) else []
    for control in controls:
        if isinstance(control, dict):
            haystack_parts.append(str(control.get("text") or ""))
    haystack = "\n".join(haystack_parts).lower()
    return [term for term in SETTINGS_DIALOG_TERMS if term in haystack]


def _surface_from_path(path: Path) -> str:
    name = path.name.lower()
    if "options-menu" in name or ("options" in name and "menu" in name):
        return "options_menu"
    if "calculation-options-dialog" in name:
        return "calculation_options_dialog"
    if "calculation-options" in name:
        return "calculation_options_attempt"
    if "visible-settings" in name:
        return "main_window"
    return "pl_window"


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
