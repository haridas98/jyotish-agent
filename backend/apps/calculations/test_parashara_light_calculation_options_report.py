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

    ui_state_path = tmp_path / "calculation-options-dialog-ui-state.json"
    ui_state_path.write_text(
        json.dumps({"window_title": "User Preferences", "controls": controls}),
        encoding="utf-8",
    )

    screenshot_path = tmp_path / "calculation-options-dialog.png"
    image = Image.new("RGB", (760, 575), (255, 255, 210))
    draw = ImageDraw.Draw(image)
    for control in controls[1:]:
        rect = control["rect"]
        cx = rect["left"] - window_rect["left"] + 6
        cy = (rect["top"] + rect["bottom"]) // 2 - window_rect["top"]
        draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), outline=(110, 110, 110), fill=(250, 250, 250))
        if control["text"] in {"calculations_lahiriRadio", "calculations_option2Radio"}:
            draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(0, 0, 0))
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
    assert report["pixel_probe"]["method"] == "radio_inner_dark_pixel_count"
    assert all("image_bytes" not in option for option in report["ayanamsha_options"])
