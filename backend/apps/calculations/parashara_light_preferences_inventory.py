from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


INTERNAL_EPHEMERIS_TERMS = (
    "ephemeris",
    "swiss",
    "jpl",
    "moshier",
    "drik",
    "siddhanta",
    "true_node",
    "mean_node",
    "node_model",
)


def build_parashara_light_preferences_inventory(
    *,
    capture_id: str,
    ui_state_paths: list[str | Path],
    screenshot_paths: list[str | Path],
) -> dict[str, Any]:
    tab_summaries = [_tab_summary(Path(path)) for path in ui_state_paths]
    visible_names = {
        name
        for summary in tab_summaries
        for name in summary.get("visible_control_names", [])
    }
    visible_ayanamsha_controls = any(name.startswith("calculations_") and "ayanamsha" in name for name in visible_names)
    visible_graph_ephemeris_display_option = "colorcod_graphEphemCheckBox" in visible_names
    visible_system_paths = {"general_optionsPathEdit", "general_chartsPathEdit"}.issubset(visible_names)
    internal_ephemeris_mode_visible = any(
        _looks_like_internal_ephemeris_control(name) for name in visible_names
    )
    status = (
        "internal_ephemeris_mode_visible"
        if internal_ephemeris_mode_visible
        else "internal_ephemeris_mode_not_visible"
    )
    return {
        "source": "parashara_light_preferences_inventory",
        "capture_id": capture_id,
        "artifact_policy": "private_audit_only_do_not_commit",
        "captured_at": datetime.now(UTC).isoformat(),
        "status": status,
        "tabs_count": len(tab_summaries),
        "tab_summaries": tab_summaries,
        "screenshots": [
            _file_fingerprint(Path(path), classification="pl_preferences_screenshot")
            for path in screenshot_paths
        ],
        "visible_ayanamsha_controls": visible_ayanamsha_controls,
        "visible_graph_ephemeris_display_option": visible_graph_ephemeris_display_option,
        "visible_system_paths": visible_system_paths,
        "internal_ephemeris_mode_visible": internal_ephemeris_mode_visible,
        "next_action": (
            "review_visible_internal_ephemeris_mode"
            if internal_ephemeris_mode_visible
            else "capture_native_export_or_hidden_option_store"
        ),
        "notes": [
            "Qt object names expose visible Preference controls; hidden controls are ignored through is_visible.",
            "colorcod_graphEphemCheckBox is treated as a display/color option, not as the astronomical ephemeris engine mode.",
        ],
    }


def _tab_summary(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    controls = data.get("controls") if isinstance(data.get("controls"), list) else []
    visible_names = [
        str(control.get("text"))
        for control in controls
        if isinstance(control, dict) and control.get("is_visible") and control.get("text")
    ]
    form_names = [name for name in visible_names if name.startswith("FormOptions")]
    return {
        **_file_fingerprint(path, classification="pl_preferences_ui_state"),
        "tab": data.get("tab", _tab_from_path(path)),
        "visible_controls_count": len(visible_names),
        "visible_form_names": form_names,
        "visible_control_names": visible_names,
        "matched_internal_ephemeris_terms": [
            name for name in visible_names if _looks_like_internal_ephemeris_control(name)
        ],
    }


def _looks_like_internal_ephemeris_control(name: str) -> bool:
    lower = name.lower()
    if lower == "colorcod_graphephemcheckbox":
        return False
    return any(term in lower for term in INTERNAL_EPHEMERIS_TERMS)


def _tab_from_path(path: Path) -> str:
    return path.name.split("-", 1)[0]


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
