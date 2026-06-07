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
    (tmp_path / "complete-calculations.txt").write_text(
        "\n".join(
            [
                "Natal Chart",
                "",
                "Date:          April 30, 1998",
                "Time:          13:45:00",
                "Time Zone:     6:00:00 (East of GMT)",
                "Place:         55 E 57' 01\", 53 N 37' 49\"",
                "               Sterlitamak, Russia",
            ]
        ),
        encoding="utf-8",
    )
    jhora_case_dir = tmp_path / "jhora-case"
    jhora_case_dir.mkdir()
    jhora_fixture = {
        "id": "sterlitamak-1998-04-30-1345",
        "review_status": "draft",
        "input": {
            "birth_date": "1998-04-30",
            "birth_time": "13:45:00",
            "place_name": "Sterlitamak",
            "timezone": "Asia/Yekaterinburg",
            "latitude": 53.6304,
            "longitude": 55.9502,
        },
        "expected": {"ascendant": {"longitude": 10.0, "rashi": "Mesha"}},
        "jhora_metadata": {
            "capture_status": "export_parsed",
            "ayanamsa": "lahiri",
            "timezone_offset": "+06:00",
        },
        "capture_files": {
            "complete_calculations_text": "jhora-complete-calculations.txt",
            "screenshots": ["screen.png"],
        },
    }
    (jhora_case_dir / "fixture.json").write_text(json.dumps(jhora_fixture), encoding="utf-8")
    pl_case_dir = tmp_path / "pl-case"
    pl_case_dir.mkdir()
    pl_packet_path = pl_case_dir / "packet.json"
    pl_packet_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-parashara-light-verification-packet-v1",
                "id": "pl7-haridas",
                "status": "pl_ui_state_captured",
                "fixture": {
                    "review_status": "draft",
                    "input": {
                        "birth_date": "1998-04-30",
                        "birth_time": "13:45:00",
                        "place_name": "Sterlitamak",
                        "timezone": "Asia/Yekaterinburg",
                        "timezone_offset": "+06:00",
                    },
                    "pl_metadata": {
                        "capture_status": "ui_state_captured",
                        "ayanamsa": "lahiri",
                        "timezone_offset": "+06:00",
                    },
                    "capture_files": {"ui_state": "pl-ui-state.json", "screenshots": ["pl.png"]},
                    "manual_witness_values": [{"source": "pl7", "body": "Surya", "rashi": "Vrishabha"}],
                },
                "pl_capture_checklist": [],
                "jyotish_agent_chart": {
                    "birth": {
                        "date": "1998-04-30",
                        "time": "13:45:00",
                        "timezone": "Asia/Yekaterinburg",
                        "utc_offset": "+06:00",
                        "local_datetime": "1998-04-30T13:45:00+06:00",
                        "utc_datetime": "1998-04-30T07:45:00+00:00",
                    },
                    "grahas": [{"body": "Surya", "rashi": "Mesha", "rashi_index": 0}],
                    "houses": [{"house": 10, "rashi": "Mesha", "rashi_index": 0}],
                },
            }
        ),
        encoding="utf-8",
    )
    settings.JHORA_ACCURACY_REPORT_PATH = jhora_path
    settings.JHORA_WITNESS_CASE_PATH = jhora_case_dir
    settings.PARASHARA_LIGHT_PACKET_PATH = pl_packet_path
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    profile_report_path = tmp_path / "pl-profile.json"
    profile_report_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_birth_xml_profile",
                "source_xml": "C:\\GeoVision\\GeoVisionCharts\\Haridas.xml",
                "raw_birth_info": {
                    "timezone": -5.0,
                    "dst": 1.0,
                    "city": "Sterlitamak",
                },
                "candidate_normalization": {
                    "longitude_east_candidate": 55.9666667,
                    "timezone_offset_hours_candidate": 6.0,
                    "timezone_formula": "-(TimeZone - DST)",
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
    preferences_inventory_path = tmp_path / "pl-preferences-inventory.json"
    preferences_inventory_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_preferences_inventory",
                "status": "internal_ephemeris_mode_not_visible",
                "tabs_count": 4,
                "visible_ayanamsha_controls": True,
                "visible_graph_ephemeris_display_option": True,
                "visible_system_paths": True,
                "internal_ephemeris_mode_visible": False,
                "next_action": "capture_native_export_or_hidden_option_store",
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_PREFERENCES_INVENTORY_PATH = preferences_inventory_path
    hidden_option_store_path = tmp_path / "pl-hidden-option-store.json"
    hidden_option_store_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_hidden_option_store",
                "status": "hidden_option_store_candidates_identified",
                "proprietary_binary_policy": "hash_only_do_not_parse",
                "primary_candidate": {"relative_path": "popts1.dat"},
                "candidate_counts": {
                    "option_store_candidates": 3,
                    "session_token_candidates": 1,
                },
                "next_action": "diff_option_store_before_after_visible_setting_change",
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_HIDDEN_OPTION_STORE_PATH = hidden_option_store_path
    option_store_diff_path = tmp_path / "pl-option-store-diff.json"
    option_store_diff_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_option_store_diff",
                "status": "option_store_diff_captured",
                "proprietary_binary_policy": "hash_only_do_not_parse",
                "visible_setting": "System.ShowStatusBar",
                "primary_candidate": "popts1.dat",
                "changed_candidates_count": 1,
                "restore_verified": True,
                "next_action": "inspect_pl_native_export_or_ephemeris_mode",
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_OPTION_STORE_DIFF_PATH = option_store_diff_path
    internal_settings_audit_path = tmp_path / "pl-internal-settings-audit.json"
    internal_settings_audit_path.write_text(
        json.dumps(
            {
                "source": "parashara_light_internal_settings_audit",
                "status": "internal_settings_unresolved_native_export_required",
                "evidence_gates": {
                    "visible_settings_status": "visible_settings_do_not_explain_pl_diff",
                    "internal_ephemeris_mode_visible": False,
                    "option_store_diff_status": "no_option_store_hash_change_detected",
                },
                "ruled_out": ["visible_calculation_options", "visible_preferences_ephemeris_mode"],
                "next_action": "capture_pl_native_export_or_internal_ephemeris_mode",
            }
        ),
        encoding="utf-8",
    )
    settings.PARASHARA_LIGHT_INTERNAL_SETTINGS_AUDIT_PATH = internal_settings_audit_path
    batch_index_path = tmp_path / "witness-review-index.json"
    batch_index_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-witness-review-batch-packets-v1",
                "metadata": {
                    "generated_at": "2026-06-07T12:05:00+05:00",
                    "reviewer": "Haridas",
                    "reviewed_at": "2026-06-07T12:00:00+05:00",
                    "jhora_root": str(tmp_path / "jhora"),
                    "pl_root": str(tmp_path / "pl7"),
                },
                "summary": {
                    "written_count": 1,
                    "skipped_count": 20,
                    "error_count": 0,
                    "output_root": str(tmp_path / "witness-review"),
                    "index_path": str(tmp_path / "witness-review" / "_index.md"),
                    "index_json_path": str(batch_index_path),
                    "target_reviewed_count": 20,
                    "batch_review_ready_count": 0,
                    "remaining_to_target_count": 20,
                    "reviewable_count": 1,
                    "blocked_count": 0,
                    "ack_required_count": 1,
                },
                "written": [
                    {
                        "id": "sterlitamak-1998-04-30-1345",
                        "output_path": str(tmp_path / "witness-review" / "sterlitamak-1998-04-30-1345.md"),
                        "reviewable": True,
                        "ack_required": True,
                        "blocked": False,
                    }
                ],
                "next_actions": [
                    {
                        "id": "vrindavan-1990-08-15-1024",
                        "group": "modern_exact_timezone",
                        "label": "Vrindavan modern baseline",
                        "status": "jhora_review_pending",
                        "missing_for_authoritative_review": ["jhora_screenshots"],
                        "missing_secondary_witness": ["pl_witness_packet"],
                        "suggested_actions": ["attach_jhora_screenshots", "attach_pl_witness_packet_or_manual_values"],
                    }
                ],
                "skipped": [{"id": "vrindavan-1990-08-15-1024", "reason": "missing_jhora_or_pl_pair"}],
                "errors": [],
                "audit_summary": {"batch_review_ready_count": 0, "target_met": False},
            }
        ),
        encoding="utf-8",
    )
    settings.WITNESS_REVIEW_BATCH_INDEX_PATH = batch_index_path
    capture_queue_path = tmp_path / "witness-capture-queue.json"
    capture_queue_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-witness-capture-queue-v1",
                "metadata": {
                    "generated_at": "2026-06-07T12:10:00+05:00",
                    "jhora_root": str(tmp_path / "jhora"),
                    "pl_root": str(tmp_path / "pl7"),
                    "target_reviewed_count": 20,
                    "limit": 20,
                },
                "summary": {
                    "queue_count": 20,
                    "remaining_to_target_count": 20,
                    "batch_review_ready_count": 0,
                    "capture_started_count": 21,
                    "pl_witness_count": 1,
                    "output": str(capture_queue_path),
                    "markdown_output": str(tmp_path / "capture-queue.md"),
                },
                "items": [
                    {
                        "priority": 1,
                        "id": "sterlitamak-1998-04-30-1345",
                        "group": "birth_verified",
                        "label": "Sterlitamak DST baseline",
                        "status": "review_pending",
                        "capture_targets": {
                            "jhora": ["authoritative_review_status", "reviewer"],
                            "parashara_light": ["pl_reviewer_note", "pl_review_status"],
                        },
                        "suggested_actions": [
                            "set_review_status_jhora_verified_after_manual_review",
                            "mark_parashara_light_witness_reviewed",
                        ],
                        "next_action_key": "set_review_status_jhora_verified_after_manual_review",
                        "next_command_kind": "manual_review",
                        "next_step_label": "Run review preflight first",
                        "next_command": "",
                        "manual_review_command": ".\\.venv\\Scripts\\python.exe manage.py preflight_witness_review --jhora ..\\.tmp\\jhora\\batch-queue\\sterlitamak-1998-04-30-1345 --parashara-light ..\\.tmp\\pl7\\batch-queue\\sterlitamak-1998-04-30-1345\\packet.json",
                        "blocker_count": 4,
                    }
                ],
                "next_item": {
                    "priority": 1,
                    "id": "sterlitamak-1998-04-30-1345",
                    "group": "birth_verified",
                    "label": "Sterlitamak DST baseline",
                    "status": "review_pending",
                    "capture_targets": {
                        "jhora": ["authoritative_review_status", "reviewer"],
                        "parashara_light": ["pl_reviewer_note", "pl_review_status"],
                    },
                    "suggested_actions": [
                        "set_review_status_jhora_verified_after_manual_review",
                        "mark_parashara_light_witness_reviewed",
                    ],
                    "next_action_key": "set_review_status_jhora_verified_after_manual_review",
                    "next_command_kind": "manual_review",
                    "next_step_label": "Run review preflight first",
                    "next_command": "",
                    "manual_review_command": ".\\.venv\\Scripts\\python.exe manage.py preflight_witness_review --jhora ..\\.tmp\\jhora\\batch-queue\\sterlitamak-1998-04-30-1345 --parashara-light ..\\.tmp\\pl7\\batch-queue\\sterlitamak-1998-04-30-1345\\packet.json",
                    "blocker_count": 4,
                },
                "next_command": "",
            }
        ),
        encoding="utf-8",
    )
    settings.WITNESS_CAPTURE_QUEUE_PATH = capture_queue_path

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    assert response.data["overall_status"] == "diff_open"
    witness_review = response.data["witness_review"]
    assert witness_review["available"] is True
    assert witness_review["overall"]["reviewable"] is True
    assert witness_review["overall"]["ack_required"] is True
    assert witness_review["overall"]["blocked"] is False
    assert witness_review["jhora"]["status"] == "diff_open"
    assert witness_review["parashara_light"]["status"] == "diff_open"
    assert witness_review["seal_command"].startswith(".\\.venv\\Scripts\\python.exe manage.py seal_witness_case")
    assert "--ack-diff-open" in witness_review["seal_command"]
    witness_review_batch = response.data["witness_review_batch"]
    assert witness_review_batch["available"] is True
    assert witness_review_batch["summary"]["written_count"] == 1
    assert witness_review_batch["summary"]["skipped_count"] == 20
    assert witness_review_batch["summary"]["remaining_to_target_count"] == 20
    assert witness_review_batch["summary"]["reviewable_count"] == 1
    assert witness_review_batch["summary"]["blocked_count"] == 0
    assert witness_review_batch["summary"]["ack_required_count"] == 1
    assert witness_review_batch["metadata"]["reviewer"] == "Haridas"
    assert witness_review_batch["metadata"]["generated_at"] == "2026-06-07T12:05:00+05:00"
    assert witness_review_batch["written"][0]["id"] == "sterlitamak-1998-04-30-1345"
    assert witness_review_batch["written"][0]["ack_required"] is True
    assert witness_review_batch["next_actions"][0]["id"] == "vrindavan-1990-08-15-1024"
    assert witness_review_batch["next_actions"][0]["missing_secondary_witness"] == ["pl_witness_packet"]
    assert "attach_pl_witness_packet_or_manual_values" in witness_review_batch["next_actions"][0]["suggested_actions"]
    assert witness_review_batch["skipped_reason_counts"] == {"missing_jhora_or_pl_pair": 1}
    witness_capture_queue = response.data["witness_capture_queue"]
    assert witness_capture_queue["available"] is True
    assert witness_capture_queue["summary"]["queue_count"] == 20
    assert witness_capture_queue["summary"]["capture_started_count"] == 21
    assert witness_capture_queue["metadata"]["target_reviewed_count"] == 20
    assert witness_capture_queue["items"][0]["id"] == "sterlitamak-1998-04-30-1345"
    assert witness_capture_queue["items"][0]["capture_targets"]["jhora"] == [
        "authoritative_review_status",
        "reviewer",
    ]
    assert witness_capture_queue["next_item"]["id"] == "sterlitamak-1998-04-30-1345"
    assert witness_capture_queue["next_command_kind"] == "manual_review"
    assert witness_capture_queue["next_step_label"] == "Run review preflight first"
    assert witness_capture_queue["next_command"] == ""
    assert "preflight_witness_review" in witness_capture_queue["manual_review_command"]
    assert witness_capture_queue["items"][0]["next_action_key"] == "set_review_status_jhora_verified_after_manual_review"
    assert witness_capture_queue["items"][0]["next_command_kind"] == "manual_review"
    assert witness_capture_queue["items"][0]["next_step_label"] == "Run review preflight first"
    assert witness_capture_queue["next_item"]["next_step_label"] == "Run review preflight first"
    assert witness_capture_queue["items"][0]["next_command"] == ""
    assert "preflight_witness_review" in witness_capture_queue["items"][0]["manual_review_command"]
    assert "mark_parashara_light_witness_reviewed" in witness_capture_queue["items"][0]["suggested_actions"]
    timezone_audit = response.data["birth_timezone_audit"]
    assert timezone_audit["available"] is True
    assert timezone_audit["status"] == "matched"
    assert timezone_audit["birth_date"] == "1998-04-30"
    assert timezone_audit["birth_time"] == "13:45:00"
    assert timezone_audit["timezone"] == "Asia/Yekaterinburg"
    assert timezone_audit["expected_utc_offset"] == "+06:00"
    assert timezone_audit["resolved_utc_offset"] == "+06:00"
    assert timezone_audit["local_datetime_utc_offset"] == "+06:00"
    assert timezone_audit["utc_datetime"] == "1998-04-30T07:45:00+00:00"
    assert timezone_audit["dst_observed"] is True
    assert response.data["jhora"]["available"] is True
    assert response.data["jhora"]["status"] == "diff_open"
    assert response.data["jhora"]["failed_checks"] == 2
    jhora_birth_export = response.data["jhora"]["birth_export"]
    assert jhora_birth_export["available"] is True
    assert jhora_birth_export["date"] == "April 30, 1998"
    assert jhora_birth_export["time"] == "13:45:00"
    assert jhora_birth_export["timezone_line"] == "Time Zone:     6:00:00 (East of GMT)"
    assert jhora_birth_export["parsed_utc_offset"] == "+06:00"
    assert response.data["parashara_light"]["available"] is True
    assert response.data["parashara_light"]["status"] == "diff_open"
    assert response.data["parashara_light"]["manual_failed_count"] == 1
    profile = response.data["parashara_light"]["profile"]
    assert profile["available"] is True
    assert profile["status"] == "loaded"
    assert profile["authoritative"] is False
    assert profile["raw_birth_info"]["timezone"] == -5.0
    assert profile["raw_birth_info"]["dst"] == 1.0
    assert profile["candidate_normalization"]["timezone_formula"] == "-(TimeZone - DST)"
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
    preferences_inventory = response.data["parashara_light"]["preferences_inventory"]
    assert preferences_inventory["available"] is True
    assert preferences_inventory["status"] == "internal_ephemeris_mode_not_visible"
    assert preferences_inventory["tabs_count"] == 4
    assert preferences_inventory["internal_ephemeris_mode_visible"] is False
    assert preferences_inventory["next_action"] == "capture_native_export_or_hidden_option_store"
    hidden_option_store = response.data["parashara_light"]["hidden_option_store"]
    assert hidden_option_store["available"] is True
    assert hidden_option_store["status"] == "hidden_option_store_candidates_identified"
    assert hidden_option_store["primary_candidate"] == "popts1.dat"
    assert hidden_option_store["option_store_candidates_count"] == 3
    assert hidden_option_store["next_action"] == "diff_option_store_before_after_visible_setting_change"
    option_store_diff = response.data["parashara_light"]["option_store_diff"]
    assert option_store_diff["available"] is True
    assert option_store_diff["status"] == "option_store_diff_captured"
    assert option_store_diff["visible_setting"] == "System.ShowStatusBar"
    assert option_store_diff["primary_candidate"] == "popts1.dat"
    assert option_store_diff["changed_candidates_count"] == 1
    assert option_store_diff["restore_verified"] is True
    assert option_store_diff["next_action"] == "inspect_pl_native_export_or_ephemeris_mode"
    internal_settings_audit = response.data["parashara_light"]["internal_settings_audit"]
    assert internal_settings_audit["available"] is True
    assert internal_settings_audit["status"] == "internal_settings_unresolved_native_export_required"
    assert internal_settings_audit["visible_settings_status"] == "visible_settings_do_not_explain_pl_diff"
    assert internal_settings_audit["internal_ephemeris_mode_visible"] is False
    assert internal_settings_audit["ruled_out_count"] == 2
    assert internal_settings_audit["next_action"] == "capture_pl_native_export_or_internal_ephemeris_mode"
    assert response.data["open_items"][0]["source"] == "jhora"
    assert response.data["open_items"][1]["source"] == "parashara_light"
    assert response.data["open_items"][1]["next_action"] == "capture_pl_native_export_or_internal_ephemeris_mode"


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
    settings.PARASHARA_LIGHT_PREFERENCES_INVENTORY_PATH = tmp_path / "missing-pl-preferences-inventory.json"
    settings.PARASHARA_LIGHT_HIDDEN_OPTION_STORE_PATH = tmp_path / "missing-pl-hidden-option-store.json"
    settings.PARASHARA_LIGHT_OPTION_STORE_DIFF_PATH = tmp_path / "missing-pl-option-store-diff.json"
    settings.PARASHARA_LIGHT_INTERNAL_SETTINGS_AUDIT_PATH = tmp_path / "missing-pl-internal-settings-audit.json"
    settings.WITNESS_REVIEW_BATCH_INDEX_PATH = tmp_path / "missing-witness-review-index.json"
    settings.WITNESS_CAPTURE_QUEUE_PATH = tmp_path / "missing-witness-capture-queue.json"

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    assert response.data["overall_status"] == "missing_witnesses"
    assert response.data["birth_timezone_audit"]["available"] is False
    assert response.data["jhora"]["available"] is False
    assert response.data["parashara_light"]["available"] is False
    assert response.data["parashara_light"]["profile"]["available"] is False
    assert response.data["parashara_light"]["forensic"]["available"] is False
    assert response.data["parashara_light"]["settings_evidence"]["available"] is False
    assert response.data["parashara_light"]["visible_settings_capture"]["available"] is False
    assert response.data["parashara_light"]["calculation_options"]["available"] is False
    assert response.data["parashara_light"]["settings_aware_forensic"]["available"] is False
    assert response.data["parashara_light"]["preferences_inventory"]["available"] is False
    assert response.data["parashara_light"]["hidden_option_store"]["available"] is False
    assert response.data["parashara_light"]["option_store_diff"]["available"] is False
    assert response.data["parashara_light"]["internal_settings_audit"]["available"] is False
    assert response.data["witness_capture_queue"]["available"] is False


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
    settings.PARASHARA_LIGHT_PREFERENCES_INVENTORY_PATH = tmp_path / "missing-pl-preferences-inventory.json"
    settings.PARASHARA_LIGHT_HIDDEN_OPTION_STORE_PATH = tmp_path / "missing-pl-hidden-option-store.json"
    settings.PARASHARA_LIGHT_OPTION_STORE_DIFF_PATH = tmp_path / "missing-pl-option-store-diff.json"
    settings.PARASHARA_LIGHT_INTERNAL_SETTINGS_AUDIT_PATH = tmp_path / "missing-pl-internal-settings-audit.json"

    response = APIClient().get(reverse("witness-summary"))

    assert response.status_code == 200
    profile = response.data["parashara_light"]["profile"]
    assert profile["available"] is False
    assert profile["status"] == "load_error"
    assert profile["authoritative"] is False
    assert profile["source_report"] == str(profile_path)


def test_birth_timezone_audit_reports_unknown_timezone_source(tmp_path):
    from apps.calculations.witness_summary import _birth_timezone_audit

    packet_path = tmp_path / "pl-packet.json"
    packet_path.write_text(
        json.dumps(
            {
                "fixture": {
                    "input": {
                        "birth_date": "1998-04-30",
                        "birth_time": "13:45:00",
                        "timezone": "Not/AZone",
                        "timezone_offset": "+0600",
                    }
                },
                "jyotish_agent_chart": {
                    "birth": {
                        "date": "1998-04-30",
                        "time": "13:45:00",
                        "timezone": "Not/AZone",
                        "utc_offset": "+06:00",
                        "local_datetime": "1998-04-30T13:45:00+06:00",
                        "utc_datetime": "1998-04-30T07:45:00+00:00",
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    audit = _birth_timezone_audit(packet_path)

    assert audit["timezone_source"] == "unknown"
    assert audit["expected_utc_offset"] == "+06:00"
    assert audit["status"] == "matched"
