import json

from django.core.management import call_command


def test_build_parashara_light_visible_settings_capture_records_fingerprints_without_embedding_images(tmp_path):
    from apps.calculations.parashara_light_visible_settings_capture import build_parashara_light_visible_settings_capture

    main_state = tmp_path / "main-ui-state.json"
    main_state.write_text(
        json.dumps(
            {
                "window_title": "Parashara's Light 7.0.1 - [Haridas]",
                "control_count": 26,
                "screenshot_blank": False,
            }
        ),
        encoding="utf-8",
    )
    menu_state = tmp_path / "options-menu-ui-state.json"
    menu_state.write_text(
        json.dumps({"window_title": "", "control_count": 0, "screenshot_blank": False}),
        encoding="utf-8",
    )
    coordinate_menu_state = tmp_path / "options-coordinate-menu-ui-state.json"
    coordinate_menu_state.write_text(
        json.dumps({"window_title": "", "control_count": 0, "screenshot_blank": False}),
        encoding="utf-8",
    )
    main_screenshot = tmp_path / "main.png"
    main_screenshot.write_bytes(b"png-main")
    menu_screenshot = tmp_path / "options-menu.png"
    menu_screenshot.write_bytes(b"png-menu")

    report = build_parashara_light_visible_settings_capture(
        capture_id="pl7-haridas-visible-settings",
        ui_state_paths=[main_state, menu_state, coordinate_menu_state],
        screenshot_paths=[main_screenshot, menu_screenshot],
    )

    assert report["source"] == "parashara_light_visible_settings_capture"
    assert report["artifact_policy"] == "private_audit_only_do_not_commit"
    assert report["status"] == "menu_path_captured_settings_dialog_pending"
    assert report["settings_dialog_captured"] is False
    assert report["surfaces_count"] == 3
    assert report["screenshots_count"] == 2
    assert report["next_action"] == "capture_calculation_options_dialog_or_native_export"
    assert report["screenshots"][0]["sha256"]
    assert "image_bytes" not in report["screenshots"][0]
    assert report["ui_states"][0]["window_title"].startswith("Parashara")


def test_build_parashara_light_visible_settings_capture_detects_pl7_calculation_dialog_object_names(tmp_path):
    from apps.calculations.parashara_light_visible_settings_capture import build_parashara_light_visible_settings_capture

    calculation_dialog_state = tmp_path / "calculation-options-dialog-ui-state.json"
    calculation_dialog_state.write_text(
        json.dumps(
            {
                "window_title": "User Preferences",
                "control_count": 60,
                "screenshot_blank": False,
                "controls": [
                    {"text": "FormOptionsCalculations"},
                    {"text": "calculations_ayanamshaFrame"},
                    {"text": "calculations_lahiriRadio"},
                ],
            }
        ),
        encoding="utf-8",
    )
    screenshot = tmp_path / "calculation-options-dialog.png"
    screenshot.write_bytes(b"png-dialog")

    report = build_parashara_light_visible_settings_capture(
        capture_id="pl7-haridas-visible-settings",
        ui_state_paths=[calculation_dialog_state],
        screenshot_paths=[screenshot],
    )

    assert report["status"] == "settings_dialog_captured"
    assert report["settings_dialog_captured"] is True
    assert report["next_action"] == "review_visible_calculation_options"
    assert "formoptionscalculations" in report["ui_states"][0]["matched_terms"]


def test_build_parashara_light_visible_settings_capture_command_writes_json(monkeypatch, tmp_path):
    output_path = tmp_path / "visible-settings.json"
    ui_state = tmp_path / "ui-state.json"
    ui_state.write_text("{}", encoding="utf-8")
    screenshot = tmp_path / "screen.png"
    screenshot.write_bytes(b"png")

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_parashara_light_visible_settings_capture.build_parashara_light_visible_settings_capture",
        lambda capture_id, ui_state_paths, screenshot_paths: {
            "source": "parashara_light_visible_settings_capture",
            "capture_id": capture_id,
            "ui_states_count": len(ui_state_paths),
            "screenshots_count": len(screenshot_paths),
        },
    )

    call_command(
        "build_parashara_light_visible_settings_capture",
        "--id",
        "pl7-test",
        "--ui-state",
        str(ui_state),
        "--screenshot",
        str(screenshot),
        "--output",
        str(output_path),
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["source"] == "parashara_light_visible_settings_capture"
    assert payload["capture_id"] == "pl7-test"
    assert payload["screenshots_count"] == 1
