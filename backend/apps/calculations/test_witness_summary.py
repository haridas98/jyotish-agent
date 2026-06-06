import json

from django.urls import reverse
from rest_framework.test import APIClient


def test_witness_summary_api_combines_jhora_and_parashara_light(settings, tmp_path):
    jhora_path = tmp_path / "jhora-accuracy.json"
    jhora_path.write_text(
        json.dumps(
            {
                "fixture_id": "sterlitamak-1998",
                "passed": False,
                "longitude_comparisons": [
                    {"body": "Surya", "delta_arcseconds": 42.0, "signed_delta_arcseconds": -42.0, "passed": False}
                ],
                "exact_matches": {"jhora.vimshopaka.Sun": True, "jhora.shadbala.Sun": False},
                "missing_fields": [],
                "diagnostics": {"jhora_layers": {"shadbala": {"checked": 1, "matched": 0, "failed": 1}}},
            }
        ),
        encoding="utf-8",
    )
    pl_packet_path = tmp_path / "pl-packet.json"
    pl_packet_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-parashara-light-verification-packet-v1",
                "id": "pl7-haridas",
                "status": "pl_ui_state_captured",
                "fixture": {
                    "review_status": "draft",
                    "pl_metadata": {"capture_status": "ui_state_captured"},
                    "capture_files": {"screenshots": []},
                    "manual_witness_values": [{"source": "pl7", "body": "Surya", "rashi": "Vrishabha"}],
                },
                "pl_capture_checklist": [],
                "jyotish_agent_chart": {
                    "grahas": [{"body": "Surya", "rashi": "Mesha", "rashi_index": 0}],
                    "houses": [{"house": 10, "rashi": "Mesha", "rashi_index": 0}],
                },
            }
        ),
        encoding="utf-8",
    )
    settings.JHORA_ACCURACY_REPORT_PATH = jhora_path
    settings.PARASHARA_LIGHT_PACKET_PATH = pl_packet_path
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    profile_report_path = tmp_path / "pl-profile.json"
    profile_report_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_birth_xml_profile",
                "source_xml": "C:\\GeoVision\\GeoVisionCharts\\Haridas.xml",
                "candidate_normalization": {
                    "longitude_east_candidate": 55.9666667,
                    "timezone_offset_hours_candidate": 6.0,
                },
                "packet_comparison": {
                    "longitude_delta_degrees": 0.016467,
                    "latitude_delta_degrees": -0.013733,
                    "timezone_delta_hours": 0.0,
                },
                "data_quality_flags": [
                    "PL_LONGITUDE_EAST_NEGATIVE_CONVENTION",
                    "PL_PACKET_COORDINATE_VARIANCE",
                ],
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_PROFILE_REPORT_PATH = profile_report_path
    forensic_report_path = tmp_path / "pl-forensic.json"
    forensic_report_path.write_text(
        json.dumps(
            {
                "summary": {
                    "conclusion": "engine_matches_swiss_pl_profile_diff_open",
                    "engine_swiss_diff_count": 0,
                    "pl_diff_count": 5,
                    "pl_swiss_max_abs_arcsec": 649.421084,
                },
                "diagnostics": {
                    "uniform_offset": {"status": "rejected"},
                    "time_shift": {"status": "rejected"},
                    "next_action": "capture_parashara_light_profile_settings",
                },
                "rows": [
                    {"body": "Surya", "status": "diff_open"},
                    {"body": "Chandra", "status": "matched"},
                    {"body": "Budha", "status": "diff_open"},
                ],
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_FORENSIC_REPORT_PATH = forensic_report_path
    settings_evidence_path = tmp_path / "pl-settings-evidence.json"
    settings_evidence_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_settings_evidence",
                "artifact_policy": "private_audit_only_do_not_commit",
                "proprietary_binary_policy": "hash_only_do_not_parse",
                "next_action": "capture_visible_pl_profile_settings",
                "text_artifacts": [
                    {"relative_path": "Temp/htpl.log", "content_preview": "PL7.0, build B.08.01.06"}
                ],
                "options_manifest": [{"relative_path": "popts1.dat"}],
                "session_token_manifest": [{"relative_path": "Temp/20501.e31"}],
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_SETTINGS_EVIDENCE_PATH = settings_evidence_path
    visible_capture_path = tmp_path / "pl-visible-settings.json"
    visible_capture_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_visible_settings_capture",
                "status": "menu_path_captured_settings_dialog_pending",
                "settings_dialog_captured": False,
                "options_menu_captured": True,
                "surfaces_count": 3,
                "screenshots_count": 3,
                "next_action": "capture_calculation_options_dialog_or_native_export",
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_VISIBLE_SETTINGS_CAPTURE_PATH = visible_capture_path
    calculation_options_path = tmp_path / "pl-calculation-options.json"
    calculation_options_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_calculation_options_report",
                "status": "calculation_options_reviewed",
                "selected_ayanamsha": {"key": "lahiri", "label": "Lahiri"},
                "selected_calculation_method": {
                    "key": "parashara_male_neuter_female",
                    "label": "Parashara (male/neuter/female)",
                },
                "offset_value": {"value": "00:00:00", "confidence": "visual_digit_template"},
                "selected_miscellaneous_item": {
                    "key": "drekkana_bala_method",
                    "label": "Drekkana Bala method",
                },
                "offset_control_visible": True,
                "miscellaneous_list_visible": True,
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_CALCULATION_OPTIONS_REPORT_PATH = calculation_options_path
    settings_aware_forensic_path = tmp_path / "pl-settings-aware-forensic.json"
    settings_aware_forensic_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_settings_aware_forensic",
                "status": "visible_settings_do_not_explain_pl_diff",
                "visible_settings": {
                    "ayanamsha_status": "matches_engine_lahiri",
                    "offset_status": "zero_offset",
                },
                "diagnostic_gates": {
                    "engine_swiss_status": "matched",
                    "uniform_offset_status": "rejected",
                    "time_shift_status": "rejected",
                },
                "next_action": "capture_pl_internal_ayanamsha_value_or_ephemeris_mode",
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_SETTINGS_AWARE_FORENSIC_PATH = settings_aware_forensic_path

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    assert response.data["overall_status"] == "diff_open"
    assert response.data["jhora"]["available"] is True
    assert response.data["jhora"]["status"] == "diff_open"
    assert response.data["jhora"]["failed_checks"] == 2
    assert response.data["parashara_light"]["available"] is True
    assert response.data["parashara_light"]["status"] == "diff_open"
    assert response.data["parashara_light"]["manual_failed_count"] == 1
    profile = response.data["parashara_light"]["profile"]
    assert profile["available"] is True
    assert profile["status"] == "loaded"
    assert profile["authoritative"] is False
    assert profile["packet_comparison"]["longitude_delta_degrees"] == 0.016467
    assert "PL_PACKET_COORDINATE_VARIANCE" in profile["data_quality_flags"]
    forensic = response.data["parashara_light"]["forensic"]
    assert forensic["available"] is True
    assert forensic["status"] == "loaded"
    assert forensic["conclusion"] == "engine_matches_swiss_pl_profile_diff_open"
    assert forensic["uniform_offset_status"] == "rejected"
    assert forensic["time_shift_status"] == "rejected"
    assert forensic["next_action"] == "capture_parashara_light_profile_settings"
    assert forensic["row_health"] == {"total": 3, "matched": 1, "diff_open": 2}
    settings_evidence = response.data["parashara_light"]["settings_evidence"]
    assert settings_evidence["available"] is True
    assert settings_evidence["status"] == "loaded"
    assert settings_evidence["proprietary_binary_policy"] == "hash_only_do_not_parse"
    assert settings_evidence["options_files_count"] == 1
    assert settings_evidence["session_tokens_count"] == 1
    assert settings_evidence["runtime_build"] == "PL7.0, build B.08.01.06"
    visible_capture = response.data["parashara_light"]["visible_settings_capture"]
    assert visible_capture["available"] is True
    assert visible_capture["status"] == "menu_path_captured_settings_dialog_pending"
    assert visible_capture["settings_dialog_captured"] is False
    assert visible_capture["screenshots_count"] == 3
    assert visible_capture["next_action"] == "capture_calculation_options_dialog_or_native_export"
    calculation_options = response.data["parashara_light"]["calculation_options"]
    assert calculation_options["available"] is True
    assert calculation_options["status"] == "calculation_options_reviewed"
    assert calculation_options["selected_ayanamsha_label"] == "Lahiri"
    assert calculation_options["selected_calculation_method_label"] == "Parashara (male/neuter/female)"
    assert calculation_options["offset_value"] == "00:00:00"
    assert calculation_options["selected_miscellaneous_item_label"] == "Drekkana Bala method"
    assert calculation_options["offset_control_visible"] is True
    settings_aware_forensic = response.data["parashara_light"]["settings_aware_forensic"]
    assert settings_aware_forensic["available"] is True
    assert settings_aware_forensic["status"] == "visible_settings_do_not_explain_pl_diff"
    assert settings_aware_forensic["ayanamsha_status"] == "matches_engine_lahiri"
    assert settings_aware_forensic["offset_status"] == "zero_offset"
    assert settings_aware_forensic["next_action"] == "capture_pl_internal_ayanamsha_value_or_ephemeris_mode"
    assert response.data["open_items"][0]["source"] == "jhora"
    assert response.data["open_items"][1]["source"] == "parashara_light"


def test_witness_summary_api_reports_missing_sources(settings, tmp_path):
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    settings.PARASHARA_LIGHT_PROFILE_REPORT_PATH = tmp_path / "missing-pl-profile.json"
    settings.PARASHARA_LIGHT_FORENSIC_REPORT_PATH = tmp_path / "missing-pl-forensic.json"
    settings.PARASHARA_LIGHT_SETTINGS_EVIDENCE_PATH = tmp_path / "missing-pl-settings-evidence.json"
    settings.PARASHARA_LIGHT_VISIBLE_SETTINGS_CAPTURE_PATH = tmp_path / "missing-pl-visible-settings.json"
    settings.PARASHARA_LIGHT_CALCULATION_OPTIONS_REPORT_PATH = tmp_path / "missing-pl-calculation-options.json"
    settings.PARASHARA_LIGHT_SETTINGS_AWARE_FORENSIC_PATH = tmp_path / "missing-pl-settings-aware-forensic.json"

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    assert response.data["overall_status"] == "missing_witnesses"
    assert response.data["jhora"]["available"] is False
    assert response.data["parashara_light"]["available"] is False
    assert response.data["parashara_light"]["profile"]["available"] is False
    assert response.data["parashara_light"]["forensic"]["available"] is False
    assert response.data["parashara_light"]["settings_evidence"]["available"] is False
    assert response.data["parashara_light"]["visible_settings_capture"]["available"] is False
    assert response.data["parashara_light"]["calculation_options"]["available"] is False
    assert response.data["parashara_light"]["settings_aware_forensic"]["available"] is False


def test_witness_summary_api_reports_pl_profile_load_error(settings, tmp_path):
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    profile_path = tmp_path / "broken-pl-profile.json"
    profile_path.write_text("{broken", encoding="utf-8")
    settings.PARASHARA_LIGHT_PROFILE_REPORT_PATH = profile_path
    settings.PARASHARA_LIGHT_FORENSIC_REPORT_PATH = tmp_path / "missing-pl-forensic.json"
    settings.PARASHARA_LIGHT_SETTINGS_EVIDENCE_PATH = tmp_path / "missing-pl-settings-evidence.json"
    settings.PARASHARA_LIGHT_VISIBLE_SETTINGS_CAPTURE_PATH = tmp_path / "missing-pl-visible-settings.json"
    settings.PARASHARA_LIGHT_CALCULATION_OPTIONS_REPORT_PATH = tmp_path / "missing-pl-calculation-options.json"
    settings.PARASHARA_LIGHT_SETTINGS_AWARE_FORENSIC_PATH = tmp_path / "missing-pl-settings-aware-forensic.json"

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    profile = response.data["parashara_light"]["profile"]
    assert profile["available"] is False
    assert profile["status"] == "load_error"
    assert profile["authoritative"] is False
    assert profile["source_report"] == str(profile_path)
