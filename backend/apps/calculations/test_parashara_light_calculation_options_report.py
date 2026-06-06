import json


def test_build_parashara_light_calculation_options_report_reads_checked_radios_by_pixels(tmp_path):
    from PIL import Image, ImageDraw

    from apps.calculations.parashara_light_calculation_options_report import (
        build_parashara_light_calculation_options_report,
    )

    window_rect = {"left": 20, "top": 7, "right": 780, "bottom": 582}
    controls = [{"text": "User Preferences", "control_type": "Window", "rect": window_rect}]
    y_by_name = {
        "calculations_lahiriRadio": 122,
        "calculations_noneRadio": 148,
        "calculations_yukteshwarRadio": 174,
        "calculations_ramanRadio": 200,
        "calculations_bhasinRadio": 226,
        "calculations_faganRadio": 252,
        "calculations_krishnamurtiNewRadio": 278,
        "calculations_krishnamurtiRadio": 304,
        "calculations_option1Radio": 327,
        "calculations_option2Radio": 353,
    }
    for name, top in y_by_name.items():
        left = 78 if name.startswith("calculations_") and "option" not in name else 430
        controls.append({"text": name, "control_type": "Pane", "rect": {"left": left, "top": top, "right": left + 293, "bottom": top + 21}})
    controls.append(
        {
            "text": "calculations_offsetEdit",
            "control_type": "Pane",
            "rect": {"left": 78, "top": 351, "right": 371, "bottom": 374},
        }
    )
    controls.append(
        {
            "text": "calculations_miscListBox",
            "control_type": "Pane",
            "rect": {"left": 419, "top": 111, "right": 733, "bottom": 311},
        }
    )

    ui_state_path = tmp_path / "calculation-options-dialog-ui-state.json"
    ui_state_path.write_text(
        json.dumps({"window_title": "User Preferences", "controls": controls}),
        encoding="utf-8",
    )

    screenshot_path = tmp_path / "calculation-options-dialog.png"
    image = Image.new("RGB", (760, 575), (255, 255, 210))
    draw = ImageDraw.Draw(image)
    for control in controls[1:]:
        if "Radio" not in control["text"]:
            continue
        rect = control["rect"]
        cx = rect["left"] - window_rect["left"] + 6
        cy = (rect["top"] + rect["bottom"]) // 2 - window_rect["top"]
        draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), outline=(110, 110, 110), fill=(250, 250, 250))
        if control["text"] in {"calculations_lahiriRadio", "calculations_option2Radio"}:
            draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(0, 0, 0))
    offset_rect = {"left": 78, "top": 351, "right": 371, "bottom": 374}
    offset_x = offset_rect["left"] - window_rect["left"] + 5
    offset_y = offset_rect["top"] - window_rect["top"] + 7
    for glyph_start in (0, 6, 15, 21, 30, 36):
        x = offset_x + glyph_start
        draw.line((x, offset_y + 1, x, offset_y + 3), fill=(0, 0, 0))
        draw.line((x + 1, offset_y, x + 2, offset_y), fill=(0, 0, 0))
        draw.line((x + 3, offset_y + 1, x + 3, offset_y + 7), fill=(0, 0, 0))
        draw.line((x + 1, offset_y + 8, x + 2, offset_y + 8), fill=(0, 0, 0))
        draw.line((x, offset_y + 5, x, offset_y + 7), fill=(0, 0, 0))
    for colon_x in (12, 27):
        x = offset_x + colon_x
        draw.point((x, offset_y + 2), fill=(0, 0, 0))
        draw.point((x, offset_y + 6), fill=(0, 0, 0))
    misc_left = 419 - window_rect["left"]
    misc_top = 111 - window_rect["top"]
    draw.rectangle((misc_left + 1, misc_top + 180, misc_left + 292, misc_top + 198), fill=(202, 202, 202))
    image.save(screenshot_path)

    report = build_parashara_light_calculation_options_report(
        capture_id="pl7-haridas-calculation-options",
        ui_state_path=ui_state_path,
        screenshot_path=screenshot_path,
    )

    assert report["source"] == "parashara_light_calculation_options_report"
    assert report["status"] == "calculation_options_reviewed"
    assert report["selected_ayanamsha"]["key"] == "lahiri"
    assert report["selected_ayanamsha"]["label"] == "Lahiri"
    assert report["selected_calculation_method"]["key"] == "parashara_male_neuter_female"
    assert report["selected_calculation_method"]["label"] == "Parashara (male/neuter/female)"
    assert report["offset_value"]["value"] == "00:00:00"
    assert report["selected_miscellaneous_item"]["label"] == "Drekkana Bala method"
    assert report["pixel_probe"]["method"] == "radio_inner_dark_pixel_count"
    assert all("image_bytes" not in option for option in report["ayanamsha_options"])
