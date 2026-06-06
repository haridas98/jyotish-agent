from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


AYANAMSHA_RADIOS = (
    ("lahiri", "Lahiri", "calculations_lahiriRadio"),
    ("none_sayana", "None (Sayana)", "calculations_noneRadio"),
    ("yukteshwar", "Yukteshwar", "calculations_yukteshwarRadio"),
    ("raman", "Raman", "calculations_ramanRadio"),
    ("bhasin", "Bhasin", "calculations_bhasinRadio"),
    ("fagan", "Fagan", "calculations_faganRadio"),
    ("krishnamurti", "Krishnamurti", "calculations_krishnamurtiRadio"),
    ("krishnamurti_new", "Krishnamurti New", "calculations_krishnamurtiNewRadio"),
)

CALCULATION_METHOD_RADIOS = (
    ("hora_ratnam_male_female_neuter", "Hora Ratnam (male/female/neuter)", "calculations_option1Radio"),
    ("parashara_male_neuter_female", "Parashara (male/neuter/female)", "calculations_option2Radio"),
)

VISIBLE_MISCELLANEOUS_ROWS = (
    ("ekadhipatya_reductions", "Ekadhipatya reductions"),
    ("varshaphala", "Varshaphala"),
    ("rashi_multiplier_for_virgo", "Rashi multiplier for Virgo"),
    ("gulik_method", "Gulik method"),
    ("ashtakavarga", "Ashtakavarga"),
    ("sunrise", "Sunrise"),
    ("karakas", "Karakas"),
    ("rahu_and_ketu", "Rahu & Ketu"),
    ("muhurta_dates", "Muhurta dates"),
    ("drekkana_bala_method", "Drekkana Bala method"),
)

DARK_PIXEL_THRESHOLD = 6


def build_parashara_light_calculation_options_report(
    *,
    capture_id: str,
    ui_state_path: str | Path,
    screenshot_path: str | Path,
) -> dict[str, Any]:
    ui_state = _read_json(Path(ui_state_path))
    screenshot = Path(screenshot_path)
    controls = _controls_by_text(ui_state)
    window_rect = _window_rect(ui_state)

    ayanamsha_options = [
        _radio_option_payload(key, label, object_name, controls, window_rect, screenshot)
        for key, label, object_name in AYANAMSHA_RADIOS
    ]
    method_options = [
        _radio_option_payload(key, label, object_name, controls, window_rect, screenshot)
        for key, label, object_name in CALCULATION_METHOD_RADIOS
    ]
    selected_ayanamsha = _selected_option(ayanamsha_options)
    selected_method = _selected_option(method_options)
    offset_value = _offset_value_payload(controls, window_rect, screenshot)
    selected_miscellaneous_item = _selected_miscellaneous_item_payload(controls, window_rect, screenshot)
    status = (
        "calculation_options_reviewed"
        if selected_ayanamsha and selected_method and offset_value.get("value") and selected_miscellaneous_item.get("label")
        else "calculation_options_partial"
    )
    return {
        "source": "parashara_light_calculation_options_report",
        "capture_id": capture_id,
        "artifact_policy": "private_audit_only_do_not_commit",
        "captured_at": datetime.now(UTC).isoformat(),
        "status": status,
        "source_ui_state": _file_fingerprint(Path(ui_state_path), classification="pl_calculation_options_ui_state"),
        "source_screenshot": _file_fingerprint(screenshot, classification="pl_calculation_options_screenshot"),
        "selected_ayanamsha": selected_ayanamsha or {},
        "selected_calculation_method": selected_method or {},
        "offset_value": offset_value,
        "selected_miscellaneous_item": selected_miscellaneous_item,
        "ayanamsha_options": ayanamsha_options,
        "calculation_method_options": method_options,
        "offset_control_visible": "calculations_offsetEdit" in controls,
        "miscellaneous_list_visible": "calculations_miscListBox" in controls,
        "pixel_probe": {
            "method": "radio_inner_dark_pixel_count",
            "checked_threshold": DARK_PIXEL_THRESHOLD,
            "coordinate_basis": "control_rect_relative_to_User_Preferences_window",
        },
        "notes": [
            "Qt exposes PL7 radio controls as QWidget object names, not standard TogglePattern controls.",
            "Checked state is inferred from visible radio-dot pixels in the captured User Preferences screenshot.",
        ],
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _controls_by_text(ui_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    controls = ui_state.get("controls") if isinstance(ui_state.get("controls"), list) else []
    return {
        str(control.get("text")): control
        for control in controls
        if isinstance(control, dict) and control.get("text") and isinstance(control.get("rect"), dict)
    }


def _window_rect(ui_state: dict[str, Any]) -> dict[str, int]:
    controls = ui_state.get("controls") if isinstance(ui_state.get("controls"), list) else []
    for control in controls:
        if (
            isinstance(control, dict)
            and control.get("text") == "User Preferences"
            and control.get("control_type") == "Window"
            and isinstance(control.get("rect"), dict)
        ):
            return _rect(control["rect"])
    raise ValueError("User Preferences root window rect is missing from UI state")


def _radio_option_payload(
    key: str,
    label: str,
    object_name: str,
    controls: dict[str, dict[str, Any]],
    window_rect: dict[str, int],
    screenshot_path: Path,
) -> dict[str, Any]:
    control = controls.get(object_name)
    if not control:
        return {
            "key": key,
            "label": label,
            "object_name": object_name,
            "visible": False,
            "checked": False,
            "dark_pixel_count": 0,
            "confidence": "missing_control",
        }

    rect = _rect(control["rect"])
    probe = _radio_pixel_probe(screenshot_path, rect=rect, window_rect=window_rect)
    checked = probe["dark_pixel_count"] >= DARK_PIXEL_THRESHOLD
    return {
        "key": key,
        "label": label,
        "object_name": object_name,
        "visible": True,
        "checked": checked,
        "dark_pixel_count": probe["dark_pixel_count"],
        "probe_center": probe["center"],
        "confidence": "visual_pixel_probe" if checked else "visual_pixel_probe_unchecked",
    }


def _radio_pixel_probe(screenshot_path: Path, *, rect: dict[str, int], window_rect: dict[str, int]) -> dict[str, Any]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for PL7 radio pixel probing") from exc

    cx = rect["left"] - window_rect["left"] + 6
    cy = (rect["top"] + rect["bottom"]) // 2 - window_rect["top"]
    with Image.open(screenshot_path) as image:
        rgb = image.convert("RGB")
        crop = rgb.crop((cx - 6, cy - 6, cx + 7, cy + 7))
        pixels = crop.getdata()
        dark_pixel_count = sum(1 for pixel in pixels if max(pixel) < 80)
    return {"center": {"x": cx, "y": cy}, "dark_pixel_count": dark_pixel_count}


def _offset_value_payload(
    controls: dict[str, dict[str, Any]],
    window_rect: dict[str, int],
    screenshot_path: Path,
) -> dict[str, Any]:
    control = controls.get("calculations_offsetEdit")
    if not control:
        return {"value": "", "confidence": "missing_control", "pattern": []}
    rect = _rect(control["rect"])
    pattern = _offset_dark_column_pattern(screenshot_path, rect=rect, window_rect=window_rect)
    value = "00:00:00" if _looks_like_zero_offset_pattern(pattern) else ""
    return {
        "value": value,
        "confidence": "visual_digit_template" if value else "unrecognized_visual_pattern",
        "pattern": pattern,
    }


def _offset_dark_column_pattern(screenshot_path: Path, *, rect: dict[str, int], window_rect: dict[str, int]) -> list[int]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for PL7 offset pixel probing") from exc

    left = rect["left"] - window_rect["left"]
    top = rect["top"] - window_rect["top"]
    right = rect["right"] - window_rect["left"]
    bottom = rect["bottom"] - window_rect["top"]
    with Image.open(screenshot_path) as image:
        gray = image.convert("L").crop((left, top, right, bottom))
        width, height = gray.size
        rows = range(4, max(4, height - 4))
        column_counts = [
            sum(1 for y in rows if gray.getpixel((x, y)) < 120)
            for x in range(min(width, 80))
        ]

    groups: list[list[int]] = []
    for x, count in enumerate(column_counts):
        if x <= 2 or count == 0:
            continue
        if not groups or x > groups[-1][-1] + 1:
            groups.append([x])
        else:
            groups[-1].append(x)
    return [len(group) for group in groups]


def _looks_like_zero_offset_pattern(pattern: list[int]) -> bool:
    return pattern == [4, 4, 1, 4, 4, 1, 4, 4]


def _selected_miscellaneous_item_payload(
    controls: dict[str, dict[str, Any]],
    window_rect: dict[str, int],
    screenshot_path: Path,
) -> dict[str, Any]:
    control = controls.get("calculations_miscListBox")
    if not control:
        return {"key": "", "label": "", "confidence": "missing_control"}
    rect = _rect(control["rect"])
    selected_row = _selected_miscellaneous_row(screenshot_path, rect=rect, window_rect=window_rect)
    row_index = selected_row.get("visible_row_index", -1)
    if 0 <= row_index < len(VISIBLE_MISCELLANEOUS_ROWS):
        key, label = VISIBLE_MISCELLANEOUS_ROWS[row_index]
        return {
            "key": key,
            "label": label,
            "visible_row_index": row_index,
            "highlight_center_y": selected_row.get("highlight_center_y"),
            "confidence": "visual_highlight_row_probe",
        }
    return {
        "key": "",
        "label": "",
        "visible_row_index": row_index,
        "highlight_center_y": selected_row.get("highlight_center_y"),
        "confidence": "unrecognized_highlight_row",
    }


def _selected_miscellaneous_row(
    screenshot_path: Path,
    *,
    rect: dict[str, int],
    window_rect: dict[str, int],
) -> dict[str, Any]:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for PL7 miscellaneous list pixel probing") from exc

    left = rect["left"] - window_rect["left"]
    top = rect["top"] - window_rect["top"]
    right = rect["right"] - window_rect["left"]
    bottom = rect["bottom"] - window_rect["top"]
    with Image.open(screenshot_path) as image:
        rgb = image.convert("RGB").crop((left, top, right, bottom))
        width, height = rgb.size
        scores = []
        for y in range(height):
            sample_width = max(1, min(width - 25, 292))
            pixels = [rgb.getpixel((x, y)) for x in range(5, sample_width)]
            average = sum(sum(pixel) / 3 for pixel in pixels) / len(pixels)
            scores.append(average)

    selected_rows = [y for y, average in enumerate(scores) if average < 240]
    groups: list[list[int]] = []
    for y in selected_rows:
        if not groups or y > groups[-1][-1] + 1:
            groups.append([y])
        else:
            groups[-1].append(y)
    candidates = [group for group in groups if len(group) >= 8]
    if not candidates:
        return {"visible_row_index": -1, "highlight_center_y": None}
    best = max(candidates, key=len)
    center_y = round((best[0] + best[-1]) / 2)
    visible_row_index = round((center_y - 18) / 19)
    return {"visible_row_index": visible_row_index, "highlight_center_y": center_y}


def _selected_option(options: list[dict[str, Any]]) -> dict[str, Any] | None:
    checked = [option for option in options if option.get("checked")]
    if len(checked) != 1:
        return None
    option = checked[0]
    return {
        "key": option["key"],
        "label": option["label"],
        "object_name": option["object_name"],
        "confidence": option["confidence"],
    }


def _rect(rect: dict[str, Any]) -> dict[str, int]:
    return {
        "left": int(rect["left"]),
        "top": int(rect["top"]),
        "right": int(rect["right"]),
        "bottom": int(rect["bottom"]),
    }


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
