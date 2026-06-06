import json


def test_settings_aware_forensic_marks_visible_settings_as_not_explaining_diff(tmp_path):
    from apps.calculations.parashara_light_settings_aware_forensic import (
        build_parashara_light_settings_aware_forensic,
    )

    forensic_path = tmp_path / "forensic.json"
    forensic_path.write_text(
        json.dumps(
            {
                "summary": {
                    "engine_swiss_diff_count": 0,
                    "pl_diff_count": 5,
                    "pl_swiss_max_abs_arcsec": 649.421084,
                    "conclusion": "engine_matches_swiss_pl_profile_diff_open",
                },
                "diagnostics": {
                    "uniform_offset": {"status": "rejected"},
                    "time_shift": {"status": "rejected"},
                },
            }
        ),
        encoding="utf-8",
    )
    calculation_options_path = tmp_path / "calculation-options.json"
    calculation_options_path.write_text(
        json.dumps(
            {
                "status": "calculation_options_reviewed",
                "selected_ayanamsha": {"key": "lahiri", "label": "Lahiri"},
                "offset_value": {"value": "00:00:00"},
                "selected_calculation_method": {
                    "key": "parashara_male_neuter_female",
                    "label": "Parashara (male/neuter/female)",
                },
            }
        ),
        encoding="utf-8",
    )
    profile_path = tmp_path / "profile.json"
    profile_path.write_text(
        json.dumps(
            {
                "packet_comparison": {
                    "longitude_delta_degrees": 0.016467,
                    "latitude_delta_degrees": -0.013733,
                    "timezone_delta_hours": 0.0,
                },
                "data_quality_flags": ["PL_PACKET_COORDINATE_VARIANCE"],
            }
        ),
        encoding="utf-8",
    )

    report = build_parashara_light_settings_aware_forensic(
        forensic_report_path=forensic_path,
        calculation_options_report_path=calculation_options_path,
        profile_report_path=profile_path,
    )

    assert report["source"] == "parashara_light_settings_aware_forensic"
    assert report["status"] == "visible_settings_do_not_explain_pl_diff"
    assert report["visible_settings"]["ayanamsha_status"] == "matches_engine_lahiri"
    assert report["visible_settings"]["offset_status"] == "zero_offset"
    assert report["diagnostic_gates"]["engine_swiss_status"] == "matched"
    assert report["diagnostic_gates"]["uniform_offset_status"] == "rejected"
    assert report["diagnostic_gates"]["time_shift_status"] == "rejected"
    assert report["profile_gates"]["timezone_status"] == "matches_packet"
    assert report["next_action"] == "capture_pl_internal_ayanamsha_value_or_ephemeris_mode"
