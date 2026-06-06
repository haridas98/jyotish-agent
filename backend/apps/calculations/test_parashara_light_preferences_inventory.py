import json


def test_preferences_inventory_reports_no_visible_internal_ephemeris_mode(tmp_path):
    from apps.calculations.parashara_light_preferences_inventory import (
        build_parashara_light_preferences_inventory,
    )

    calculation_state = tmp_path / "calculation-ui-state.json"
    calculation_state.write_text(
        json.dumps(
            {
                "tab": "calculation",
                "controls": [
                    {"text": "FormOptionsCalculations", "is_visible": True},
                    {"text": "calculations_ayanamshaFrame", "is_visible": True},
                    {"text": "calculations_lahiriRadio", "is_visible": True},
                ],
            }
        ),
        encoding="utf-8",
    )
    color_state = tmp_path / "color-ui-state.json"
    color_state.write_text(
        json.dumps(
            {
                "tab": "color-coding",
                "controls": [
                    {"text": "FormOptionsColorCoding", "is_visible": True},
                    {"text": "colorcod_graphEphemCheckBox", "is_visible": True},
                ],
            }
        ),
        encoding="utf-8",
    )
    system_state = tmp_path / "system-ui-state.json"
    system_state.write_text(
        json.dumps(
            {
                "tab": "system",
                "controls": [
                    {"text": "FormOptionsSystem", "is_visible": True},
                    {"text": "general_optionsPathEdit", "is_visible": True},
                    {"text": "general_chartsPathEdit", "is_visible": True},
                ],
            }
        ),
        encoding="utf-8",
    )
    screenshot = tmp_path / "system.png"
    screenshot.write_bytes(b"png")

    report = build_parashara_light_preferences_inventory(
        capture_id="pl7-preferences-inventory",
        ui_state_paths=[calculation_state, color_state, system_state],
        screenshot_paths=[screenshot],
    )

    assert report["source"] == "parashara_light_preferences_inventory"
    assert report["status"] == "internal_ephemeris_mode_not_visible"
    assert report["visible_ayanamsha_controls"] is True
    assert report["visible_graph_ephemeris_display_option"] is True
    assert report["visible_system_paths"] is True
    assert report["internal_ephemeris_mode_visible"] is False
    assert report["next_action"] == "capture_native_export_or_hidden_option_store"
