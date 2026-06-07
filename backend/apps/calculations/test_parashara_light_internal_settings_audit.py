import json

from django.core.management import call_command


def test_internal_settings_audit_requires_native_export_when_visible_paths_are_exhausted(tmp_path):
    from apps.calculations.parashara_light_internal_settings_audit import (
        build_parashara_light_internal_settings_audit,
    )

    settings_aware_path = tmp_path / "settings-aware.json"
    settings_aware_path.write_text(
        json.dumps(
            {
                "status": "visible_settings_do_not_explain_pl_diff",
                "diagnostic_gates": {
                    "engine_swiss_status": "matched",
                    "pl_diff_count": 5,
                    "uniform_offset_status": "rejected",
                    "time_shift_status": "rejected",
                },
                "visible_settings": {
                    "ayanamsha_status": "matches_engine_lahiri",
                    "offset_status": "zero_offset",
                },
                "next_action": "capture_pl_internal_ayanamsha_value_or_ephemeris_mode",
            }
        ),
        encoding="utf-8",
    )
    preferences_path = tmp_path / "preferences.json"
    preferences_path.write_text(
        json.dumps(
            {
                "status": "internal_ephemeris_mode_not_visible",
                "tabs_count": 4,
                "visible_ayanamsha_controls": True,
                "internal_ephemeris_mode_visible": False,
                "next_action": "capture_native_export_or_hidden_option_store",
            }
        ),
        encoding="utf-8",
    )
    hidden_store_path = tmp_path / "hidden-store.json"
    hidden_store_path.write_text(
        json.dumps(
            {
                "status": "hidden_option_store_candidates_identified",
                "proprietary_binary_policy": "hash_only_do_not_parse",
                "primary_candidate": {"relative_path": "popts1.dat"},
                "candidate_counts": {"option_store_candidates": 30, "session_token_candidates": 40},
                "next_action": "diff_option_store_before_after_visible_setting_change",
            }
        ),
        encoding="utf-8",
    )
    option_diff_path = tmp_path / "option-diff.json"
    option_diff_path.write_text(
        json.dumps(
            {
                "status": "no_option_store_hash_change_detected",
                "visible_setting": "System.ShowStatusBar",
                "changed_candidates_count": 0,
                "restore_verified": True,
                "next_action": "try_another_visible_setting_or_capture_native_export",
            }
        ),
        encoding="utf-8",
    )

    report = build_parashara_light_internal_settings_audit(
        settings_aware_forensic_path=settings_aware_path,
        preferences_inventory_path=preferences_path,
        hidden_option_store_path=hidden_store_path,
        option_store_diff_path=option_diff_path,
    )

    assert report["source"] == "parashara_light_internal_settings_audit"
    assert report["status"] == "internal_settings_unresolved_native_export_required"
    assert report["evidence_gates"]["visible_settings_status"] == "visible_settings_do_not_explain_pl_diff"
    assert report["evidence_gates"]["internal_ephemeris_mode_visible"] is False
    assert report["evidence_gates"]["option_store_diff_status"] == "no_option_store_hash_change_detected"
    assert report["evidence_gates"]["hidden_option_store_primary_candidate"] == "popts1.dat"
    assert "visible_calculation_options" in report["ruled_out"]
    assert "visible_preferences_ephemeris_mode" in report["ruled_out"]
    assert report["next_action"] == "capture_pl_native_export_or_internal_ephemeris_mode"


def test_internal_settings_audit_command_writes_json(monkeypatch, tmp_path):
    output_path = tmp_path / "audit.json"

    def fake_build(**kwargs):
        assert kwargs["settings_aware_forensic_path"] == tmp_path / "settings-aware.json"
        assert kwargs["preferences_inventory_path"] == tmp_path / "preferences.json"
        assert kwargs["hidden_option_store_path"] == tmp_path / "hidden-store.json"
        assert kwargs["option_store_diff_path"] == tmp_path / "option-diff.json"
        return {"source": "parashara_light_internal_settings_audit", "status": "ok"}

    monkeypatch.setattr(
        "apps.calculations.management.commands.build_parashara_light_internal_settings_audit."
        "build_parashara_light_internal_settings_audit",
        fake_build,
    )

    call_command(
        "build_parashara_light_internal_settings_audit",
        "--settings-aware-forensic",
        str(tmp_path / "settings-aware.json"),
        "--preferences-inventory",
        str(tmp_path / "preferences.json"),
        "--hidden-option-store",
        str(tmp_path / "hidden-store.json"),
        "--option-store-diff",
        str(tmp_path / "option-diff.json"),
        "--output",
        str(output_path),
    )

    assert json.loads(output_path.read_text(encoding="utf-8"))["status"] == "ok"
