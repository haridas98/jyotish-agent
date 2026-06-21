import json

from django.urls import reverse
from rest_framework.test import APIClient

from apps.calculations.witness_summary import build_witness_summary


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
    assert witness_review["open_diffs"]["jhora"]["failed_count"] > 0
    assert witness_review["open_diffs"]["parashara_light"]["failed_count"] == 1
    assert witness_review["open_diffs"]["parashara_light"]["sample"][0]["field"] == "Surya.rashi"
    assert witness_review["safe_next_step"] == "human ACK required before mark/seal"
    assert witness_review["seal_command"] == ""
    assert witness_review["jhora"]["review_command"] == ""
    assert witness_review["parashara_light"]["review_command"] == ""
    checklist = witness_review["review_checklist"]
    assert [item["key"] for item in checklist] == [
        "jhora_evidence",
        "parashara_light_evidence",
        "open_diffs",
        "review_ack",
    ]
    assert checklist[2]["status"] == "ack_required"
    assert "PL 1" in checklist[2]["detail"]
    assert checklist[2]["next_step"] == "review and ACK open JHora/PL diffs"
    assert checklist[3]["next_step"] == "human ACK required before mark/seal"
    witness_review_batch = response.data["witness_review_batch"]
    assert witness_review_batch["available"] is True
    assert witness_review_batch["summary"]["written_count"] == 1
    assert witness_review_batch["summary"]["skipped_count"] == 20
    assert witness_review_batch["summary"]["remaining_to_target_count"] == 20
    assert witness_review_batch["summary"]["reviewable_count"] == 1
    assert witness_review_batch["summary"]["blocked_count"] == 0
    assert witness_review_batch["summary"]["ack_required_count"] == 1
    assert witness_review_batch["summary"]["next_review_case_id"] == "sterlitamak-1998-04-30-1345"
    assert witness_review_batch["summary"]["next_review_step"] == "human ACK required before mark/seal"
    assert witness_review_batch["metadata"]["reviewer"] == "Haridas"
    assert witness_review_batch["metadata"]["generated_at"] == "2026-06-07T12:05:00+05:00"
    assert witness_review_batch["written"][0]["id"] == "sterlitamak-1998-04-30-1345"
    assert witness_review_batch["written"][0]["ack_required"] is True
    assert witness_review_batch["written"][0]["safe_next_step"] == "human ACK required before mark/seal"
    assert witness_review_batch["written"][0]["review_checklist"] == []
    assert witness_review_batch["written"][0]["review_checklist_summary"] == "none"
    assert witness_review_batch["written"][0]["review_checklist_next_steps_summary"] == "none"
    assert witness_review_batch["next_actions"][0]["id"] == "vrindavan-1990-08-15-1024"
    assert witness_review_batch["next_actions"][0]["missing_secondary_witness"] == ["pl_witness_packet"]
    assert "attach_pl_witness_packet_or_manual_values" in witness_review_batch["next_actions"][0]["suggested_actions"]
    assert "Attach PL witness values" in witness_review_batch["next_actions"][0]["suggested_action_labels"]
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
    assert witness_capture_queue["next_action_key"] == "set_review_status_jhora_verified_after_manual_review"
    assert witness_capture_queue["next_action_label"] == "Run review preflight"
    assert witness_capture_queue["next_command_kind"] == "manual_review"
    assert witness_capture_queue["next_step_label"] == "Run review preflight first"
    assert witness_capture_queue["next_command"] == ""
    assert "preflight_witness_review" in witness_capture_queue["manual_review_command"]
    assert witness_capture_queue["items"][0]["next_action_key"] == "set_review_status_jhora_verified_after_manual_review"
    assert witness_capture_queue["items"][0]["next_action_label"] == "Run review preflight"
    assert witness_capture_queue["items"][0]["next_command_kind"] == "manual_review"
    assert witness_capture_queue["items"][0]["next_step_label"] == "Run review preflight first"
    assert witness_capture_queue["next_item"]["next_step_label"] == "Run review preflight first"
    assert witness_capture_queue["items"][0]["next_command"] == ""
    assert "preflight_witness_review" in witness_capture_queue["items"][0]["manual_review_command"]
    assert "mark_parashara_light_witness_reviewed" in witness_capture_queue["items"][0]["suggested_actions"]
    assert witness_capture_queue["items"][0]["suggested_action_labels"] == [
        "Run review preflight",
        "Mark PL reviewed after ACK",
    ]
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
    contract = response.data["witness_contract"]
    assert contract["schema_version"] == "jyotish-witness-contract-summary-v1"
    assert contract["source_counts"] == {"jhora": 1, "parashara_light": 1}
    assert contract["status_counts"]["diff_open"] == 2
    assert contract["sources"]["jhora"]["unified_status"] == "diff_open"
    assert contract["sources"]["parashara_light"]["unified_status"] == "diff_open"
    assert contract["sources"]["jhora"]["has_open_diffs"] is True
    assert contract["sources"]["parashara_light"]["has_open_diffs"] is True
    assert "diffs" not in contract["sources"]["jhora"]["missing_evidence_groups"]
    assert "next_missing_evidence_groups" in contract
    assert "next_command" not in contract
    assert "manual_review_command" not in contract


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
    assert response.data["witness_contract"]["source_counts"] == {"jhora": 0, "parashara_light": 0}
    assert response.data["witness_contract"]["next_missing_evidence_groups"] == ["birth_data"]


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


def test_witness_capture_queue_hides_mutating_commands(tmp_path):
    capture_queue_path = tmp_path / "witness-capture-queue.json"
    capture_queue_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-witness-capture-queue-v1",
                "summary": {"queue_count": 2},
                "next_command": ".\\.venv\\Scripts\\python.exe manage.py seal_witness_case --case one",
                "manual_review_command": (
                    ".\\.venv\\Scripts\\python.exe manage.py mark_jhora_witness_reviewed --case one"
                ),
                "items": [
                    {
                        "priority": 1,
                        "id": "one",
                        "next_command": (
                            ".\\.venv\\Scripts\\python.exe manage.py capture_jhora_complete_export --case one"
                        ),
                        "manual_review_command": (
                            ".\\.venv\\Scripts\\python.exe manage.py "
                            "mark_parashara_light_witness_reviewed --case one"
                        ),
                    },
                    {
                        "priority": 2,
                        "id": "two",
                        "next_command": (
                            ".\\.venv\\Scripts\\python.exe manage.py promote_jhora_witness_batch --case two"
                        ),
                        "manual_review_command": (
                            ".\\.venv\\Scripts\\python.exe manage.py preflight_witness_review "
                            "--jhora two --parashara-light two\\packet.json"
                        ),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        witness_capture_queue_path=capture_queue_path,
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
    )

    queue = summary["witness_capture_queue"]
    assert "capture_jhora_complete_export" in queue["next_command"]
    assert queue["manual_review_command"] == ""
    assert "capture_jhora_complete_export" in queue["items"][0]["next_command"]
    assert queue["items"][0]["manual_review_command"] == ""
    assert queue["items"][1]["next_command"] == ""
    assert "preflight_witness_review" in queue["items"][1]["manual_review_command"]


def test_witness_capture_queue_rejects_commands_that_only_contain_safe_tokens(tmp_path):
    capture_queue_path = tmp_path / "witness-capture-queue.json"
    capture_queue_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-witness-capture-queue-v1",
                "summary": {"queue_count": 2},
                "next_command": "Remove-Item C:\\tmp\\x # build_jhora_witness_batch_packets",
                "manual_review_command": "Write-Host preflight_witness_review; Remove-Item x",
                "items": [
                    {
                        "priority": 1,
                        "id": "one",
                        "next_command": (
                            ".\\.venv\\Scripts\\python.exe manage.py capture_jhora_complete_export "
                            "--case one; Remove-Item x"
                        ),
                        "manual_review_command": (
                            ".\\.venv\\Scripts\\python.exe manage.py preflight_witness_review; Remove-Item x"
                        ),
                    },
                    {
                        "priority": 2,
                        "id": "two",
                        "next_command": (
                            ".\\.venv\\Scripts\\python.exe manage.py build_jhora_witness_batch_packets "
                            "--case-id 'case; still quoted'"
                        ),
                        "manual_review_command": (
                            ".\\.venv\\Scripts\\python.exe manage.py preflight_witness_review "
                            "--jhora 'case''; still quoted' --safe-next-only"
                        ),
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        witness_capture_queue_path=capture_queue_path,
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
    )

    queue = summary["witness_capture_queue"]
    assert queue["next_command"] == ""
    assert queue["manual_review_command"] == ""
    assert queue["items"][0]["next_command"] == ""
    assert queue["items"][0]["manual_review_command"] == ""
    assert "case; still quoted" in queue["items"][1]["next_command"]
    assert "case''; still quoted" in queue["items"][1]["manual_review_command"]


def test_witness_review_batch_legacy_summary_case_id_uses_written_next_step(tmp_path):
    batch_index_path = tmp_path / "witness-review-index.json"
    batch_index_path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-witness-review-batch-packets-v1",
                "summary": {
                    "written_count": 1,
                    "next_review_case_id": "sterlitamak-1998-04-30-1345",
                },
                "written": [
                    {
                        "id": "sterlitamak-1998-04-30-1345",
                        "reviewable": False,
                        "ack_required": True,
                        "blocked": True,
                        "safe_next_step": "resolve missing evidence before review",
                        "review_checklist_next_steps_summary": (
                            "Parashara Light evidence: capture missing evidence: pl_ui_state"
                        ),
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        witness_review_batch_index_path=batch_index_path,
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
    )

    batch = summary["witness_review_batch"]
    assert batch["summary"]["next_review_case_id"] == "sterlitamak-1998-04-30-1345"
    assert (
        batch["summary"]["next_review_step"]
        == "Parashara Light evidence: capture missing evidence: pl_ui_state"
    )


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


def _write_core_parity_report(path, *, status: str = "failed", case_id: str = "case-a"):
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-core-parity-report-v1",
                "metadata": {
                    "generated_at": "2026-06-20T12:00:00+00:00",
                    "target_reviewed_count": 20,
                    "tolerance_profile": {"planet_longitude_arcseconds": 1.0, "lagna_arcseconds": 5.0},
                    "witness_sources": ["jhora", "parashara_light"],
                },
                "summary": {
                    "case_count": 2,
                    "comparable_count": 1,
                    "passed_count": 0 if status == "failed" else 20,
                    "failed_count": 1 if status == "failed" else 0,
                    "missing_witness_count": 1,
                    "not_reviewed_count": 0,
                    "not_comparable_count": 0,
                    "target_reviewed_count": 20,
                    "target_met": status != "failed",
                },
                "cases": [
                    {
                        "case_id": case_id,
                        "review_status": "jhora_verified",
                        "sources_present": ["jhora"],
                        "comparison_status": status,
                        "field_results": [
                            {
                                "source": "jhora",
                                "field": "grahas.Surya.longitude",
                                "expected": 10.0,
                                "actual": 10.1,
                                "delta_arcseconds": 360.0,
                                "passed": False,
                            }
                        ],
                        "missing_fields": ["jhora.grahas.Chandra.longitude"],
                        "failed_fields": ["grahas.Surya.longitude"],
                        "max_abs_delta_arcseconds": 360.0,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_witness_summary_exposes_safe_core_parity_diagnostic(tmp_path):
    report_path = tmp_path / "core-parity-report.json"
    _write_core_parity_report(report_path)

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_core_parity_report_path=report_path,
    )

    parity = summary["witness_core_parity"]
    assert parity["available"] is True
    assert parity["status"] == "diff_open"
    assert parity["schema_version"] == "jyotish-core-parity-report-v1"
    assert parity["source_report"] == str(report_path)
    assert parity["summary"]["failed_count"] == 1
    assert parity["target_met"] is False
    assert parity["tolerance_profile"]["planet_longitude_arcseconds"] == 1.0
    assert parity["next_actions"] == [
        {
            "case_id": "case-a",
            "status": "failed",
            "sources_present": ["jhora"],
            "missing_fields": ["jhora.grahas.Chandra.longitude"],
            "failed_fields": ["grahas.Surya.longitude"],
        }
    ]
    serialized = json.dumps(parity, ensure_ascii=False)
    for forbidden in ["field_results", '"expected"', '"actual"', "mark_", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    for forbidden in ["source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in serialized


def test_witness_summary_core_parity_missing_and_invalid_are_safe(tmp_path):
    missing_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_core_parity_report_path=tmp_path / "missing-core-parity.json",
    )
    assert missing_summary["witness_core_parity"]["available"] is False
    assert missing_summary["witness_core_parity"]["status"] == "missing"

    invalid_path = tmp_path / "invalid-core-parity.json"
    invalid_path.write_text("{broken", encoding="utf-8")
    invalid_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_core_parity_report_path=invalid_path,
    )
    parity = invalid_summary["witness_core_parity"]
    assert parity["available"] is False
    assert parity["status"] == "invalid"
    assert "traceback" not in json.dumps(parity, ensure_ascii=False).lower()


def test_witness_summary_api_cache_fingerprint_includes_core_parity_path(settings, tmp_path):
    first_path = tmp_path / "first-core-parity.json"
    second_path = tmp_path / "second-core-parity.json"
    _write_core_parity_report(first_path, case_id="first-case")
    _write_core_parity_report(second_path, case_id="second-case")
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    settings.WITNESS_CORE_PARITY_REPORT_PATH = first_path

    first_response = APIClient().get(reverse("witness-summary"))
    settings.WITNESS_CORE_PARITY_REPORT_PATH = second_path
    second_response = APIClient().get(reverse("witness-summary"))

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.data["witness_core_parity"]["next_actions"][0]["case_id"] == "first-case"
    assert second_response.data["witness_core_parity"]["next_actions"][0]["case_id"] == "second-case"


def test_witness_core_parity_default_path_matches_command_output(settings):
    normalized = str(settings.WITNESS_CORE_PARITY_REPORT_PATH).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/core-parity-report.json")


def _write_varga_parity_report(path, *, status: str = "failed", case_id: str = "case-varga-a"):
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-varga-parity-report-v1",
                "metadata": {
                    "generated_at": "2026-06-20T12:00:00+00:00",
                    "target_reviewed_count": 20,
                    "varga_codes": ["D7", "D9", "D10"],
                    "witness_sources": ["jhora", "parashara_light"],
                },
                "summary": {
                    "case_count": 2,
                    "comparable_count": 1,
                    "passed_count": 0 if status == "failed" else 20,
                    "failed_count": 1 if status == "failed" else 0,
                    "missing_witness_count": 0,
                    "not_reviewed_count": 0,
                    "not_comparable_count": 1,
                    "target_reviewed_count": 20,
                    "target_met": status != "failed",
                },
                "varga_summary": {
                    "D7": {"passed": 1, "failed": 0, "missing": 0, "not_comparable": 1},
                    "D9": {"passed": 0, "failed": 1 if status == "failed" else 0, "missing": 0, "not_comparable": 1},
                    "D10": {"passed": 1, "failed": 0, "missing": 1, "not_comparable": 0},
                },
                "cases": [
                    {
                        "case_id": case_id,
                        "review_status": "jhora_verified",
                        "sources_present": ["jhora"],
                        "comparison_status": status,
                        "checked_vargas": ["D7", "D9"],
                        "failed_vargas": ["D9"] if status == "failed" else [],
                        "missing_vargas": ["D10"],
                        "field_results": [
                            {
                                "source": "jhora",
                                "varga": "D9",
                                "field": "D9.Surya.rashi",
                                "body": "Surya",
                                "expected": "Mesha",
                                "actual": "Vrishabha",
                                "passed": False,
                            }
                        ],
                        "missing_fields": ["calculated.vargas.D10"],
                        "failed_fields": ["D9.Surya.rashi"] if status == "failed" else [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_witness_summary_exposes_safe_varga_parity_diagnostic(tmp_path):
    report_path = tmp_path / "varga-parity-report.json"
    _write_varga_parity_report(report_path)

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_varga_parity_report_path=report_path,
    )

    parity = summary["witness_varga_parity"]
    assert parity["available"] is True
    assert parity["status"] == "diff_open"
    assert parity["schema_version"] == "jyotish-varga-parity-report-v1"
    assert parity["source_report"] == str(report_path)
    assert parity["summary"]["failed_count"] == 1
    assert parity["varga_summary"]["D9"]["failed"] == 1
    assert parity["target_met"] is False
    assert parity["next_actions"] == [
        {
            "case_id": "case-varga-a",
            "status": "failed",
            "checked_vargas": ["D7", "D9"],
            "failed_vargas": ["D9"],
            "missing_vargas": ["D10"],
            "missing_fields": ["calculated.vargas.D10"],
            "failed_fields": ["D9.Surya.rashi"],
        }
    ]
    serialized = json.dumps(parity, ensure_ascii=False)
    for forbidden in ["field_results", '"expected"', '"actual"', "mark_", "seal_witness_case", "--ack-diff-open"]:
        assert forbidden not in serialized
    for forbidden in ["source_anchor", "method_authority", "scriptural_authority"]:
        assert forbidden not in serialized


def test_witness_summary_varga_parity_missing_and_invalid_are_safe(tmp_path):
    missing_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_varga_parity_report_path=tmp_path / "missing-varga-parity.json",
    )
    assert missing_summary["witness_varga_parity"]["available"] is False
    assert missing_summary["witness_varga_parity"]["status"] == "missing"

    invalid_path = tmp_path / "invalid-varga-parity.json"
    invalid_path.write_text("{broken", encoding="utf-8")
    invalid_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_varga_parity_report_path=invalid_path,
    )
    parity = invalid_summary["witness_varga_parity"]
    assert parity["available"] is False
    assert parity["status"] == "invalid"
    assert "traceback" not in json.dumps(parity, ensure_ascii=False).lower()


def test_witness_summary_api_cache_fingerprint_includes_varga_parity_path(settings, tmp_path):
    first_path = tmp_path / "first-varga-parity.json"
    second_path = tmp_path / "second-varga-parity.json"
    _write_varga_parity_report(first_path, case_id="first-varga-case")
    _write_varga_parity_report(second_path, case_id="second-varga-case")
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    settings.WITNESS_VARGA_PARITY_REPORT_PATH = first_path

    first_response = APIClient().get(reverse("witness-summary"))
    settings.WITNESS_VARGA_PARITY_REPORT_PATH = second_path
    second_response = APIClient().get(reverse("witness-summary"))

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.data["witness_varga_parity"]["next_actions"][0]["case_id"] == "first-varga-case"
    assert second_response.data["witness_varga_parity"]["next_actions"][0]["case_id"] == "second-varga-case"


def test_witness_varga_parity_default_path_matches_command_output(settings):
    normalized = str(settings.WITNESS_VARGA_PARITY_REPORT_PATH).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/varga-parity-report.json")


def _write_dasha_parity_report(path, *, status: str = "failed", case_id: str = "case-dasha-a"):
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-dasha-parity-report-v1",
                "metadata": {
                    "generated_at": "2026-06-20T12:00:00+00:00",
                    "target_reviewed_count": 20,
                    "dasha_system": "vimshottari",
                    "levels": ["mahadasha", "antardasha"],
                    "witness_sources": ["jhora", "parashara_light"],
                },
                "summary": {
                    "case_count": 2,
                    "comparable_count": 1,
                    "passed_count": 0 if status == "failed" else 20,
                    "failed_count": 1 if status == "failed" else 0,
                    "missing_witness_count": 0,
                    "not_reviewed_count": 0,
                    "not_comparable_count": 1,
                    "target_reviewed_count": 20,
                    "target_met": status != "failed",
                },
                "level_summary": {
                    "mahadasha": {"passed": 0, "failed": 1 if status == "failed" else 0, "missing": 0, "not_comparable": 1},
                    "antardasha": {"passed": 1, "failed": 0, "missing": 1, "not_comparable": 0},
                },
                "cases": [
                    {
                        "case_id": case_id,
                        "review_status": "jhora_verified",
                        "sources_present": ["jhora"],
                        "comparison_status": status,
                        "checked_levels": ["mahadasha", "antardasha"],
                        "failed_levels": ["mahadasha"] if status == "failed" else [],
                        "missing_levels": ["antardasha"],
                        "field_results": [
                            {
                                "source": "jhora",
                                "level": "mahadasha",
                                "field": "current_mahadasha_lord",
                                "expected": "Rahu",
                                "actual": "Guru",
                                "passed": False,
                            }
                        ],
                        "missing_fields": ["witness.vimshottari.antardasha"],
                        "failed_fields": ["vimshottari.current_mahadasha_lord"] if status == "failed" else [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_witness_summary_exposes_safe_dasha_parity_diagnostic(tmp_path):
    report_path = tmp_path / "dasha-parity-report.json"
    _write_dasha_parity_report(report_path)

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_dasha_parity_report_path=report_path,
    )

    parity = summary["witness_dasha_parity"]
    assert parity["available"] is True
    assert parity["status"] == "diff_open"
    assert parity["schema_version"] == "jyotish-dasha-parity-report-v1"
    assert parity["source_report"] == str(report_path)
    assert parity["summary"]["failed_count"] == 1
    assert parity["level_summary"]["mahadasha"]["failed"] == 1
    assert parity["target_met"] is False
    assert parity["next_actions"] == [
        {
            "case_id": "case-dasha-a",
            "status": "failed",
            "checked_levels": ["mahadasha", "antardasha"],
            "failed_levels": ["mahadasha"],
            "missing_levels": ["antardasha"],
            "missing_fields": ["witness.vimshottari.antardasha"],
            "failed_fields": ["vimshottari.current_mahadasha_lord"],
        }
    ]
    serialized = json.dumps(parity, ensure_ascii=False).lower()
    for forbidden in [
        "field_results",
        '"expected"',
        '"actual"',
        "sources_present",
        "mark_",
        "seal_witness_case",
        "--ack-diff-open",
        "authority",
        "authoritative",
    ]:
        assert forbidden not in serialized


def test_witness_summary_dasha_parity_missing_and_invalid_are_safe(tmp_path):
    missing_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_dasha_parity_report_path=tmp_path / "missing-dasha-parity.json",
    )
    assert missing_summary["witness_dasha_parity"]["available"] is False
    assert missing_summary["witness_dasha_parity"]["status"] == "missing"

    invalid_path = tmp_path / "invalid-dasha-parity.json"
    invalid_path.write_text("{broken", encoding="utf-8")
    invalid_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_dasha_parity_report_path=invalid_path,
    )
    parity = invalid_summary["witness_dasha_parity"]
    assert parity["available"] is False
    assert parity["status"] == "invalid"
    assert "traceback" not in json.dumps(parity, ensure_ascii=False).lower()


def test_witness_summary_api_cache_fingerprint_includes_dasha_parity_path(settings, tmp_path):
    first_path = tmp_path / "first-dasha-parity.json"
    second_path = tmp_path / "second-dasha-parity.json"
    _write_dasha_parity_report(first_path, case_id="first-dasha-case")
    _write_dasha_parity_report(second_path, case_id="second-dasha-case")
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    settings.WITNESS_DASHA_PARITY_REPORT_PATH = first_path

    first_response = APIClient().get(reverse("witness-summary"))
    settings.WITNESS_DASHA_PARITY_REPORT_PATH = second_path
    second_response = APIClient().get(reverse("witness-summary"))

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.data["witness_dasha_parity"]["next_actions"][0]["case_id"] == "first-dasha-case"
    assert second_response.data["witness_dasha_parity"]["next_actions"][0]["case_id"] == "second-dasha-case"


def test_witness_dasha_parity_default_path_matches_command_output(settings):
    normalized = str(settings.WITNESS_DASHA_PARITY_REPORT_PATH).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/dasha-parity-report.json")


def _write_panchanga_parity_report(path, *, status: str = "failed", case_id: str = "case-panchanga-a"):
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-panchanga-parity-report-v1",
                "metadata": {
                    "generated_at": "2026-06-20T12:00:00+00:00",
                    "target_reviewed_count": 20,
                    "fields": ["tithi", "vara", "yoga", "karana", "nakshatra"],
                    "witness_sources": ["jhora", "parashara_light"],
                },
                "summary": {
                    "case_count": 2,
                    "comparable_count": 1,
                    "passed_count": 0 if status == "failed" else 20,
                    "failed_count": 1 if status == "failed" else 0,
                    "missing_witness_count": 0,
                    "not_reviewed_count": 0,
                    "not_comparable_count": 1,
                    "target_reviewed_count": 20,
                    "target_met": status != "failed",
                },
                "field_summary": {
                    "tithi": {"passed": 0, "failed": 1 if status == "failed" else 0, "missing": 0, "not_comparable": 1},
                    "vara": {"passed": 1, "failed": 0, "missing": 1, "not_comparable": 0},
                    "yoga": {"passed": 1, "failed": 0, "missing": 0, "not_comparable": 0},
                },
                "cases": [
                    {
                        "case_id": case_id,
                        "review_status": "jhora_verified",
                        "sources_present": ["jhora"],
                        "comparison_status": status,
                        "checked_fields": ["tithi", "vara"],
                        "failed_panchanga_fields": ["tithi"] if status == "failed" else [],
                        "missing_panchanga_fields": ["vara"],
                        "field_results": [
                            {
                                "source": "jhora",
                                "panchanga_field": "tithi",
                                "field": "panchanga.tithi",
                                "expected": ["krishna_shashthi"],
                                "actual": ["shukla_panchami"],
                                "passed": False,
                            }
                        ],
                        "missing_fields": ["jhora.panchanga.vara"],
                        "failed_fields": ["panchanga.tithi"] if status == "failed" else [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_witness_summary_exposes_safe_panchanga_parity_diagnostic(tmp_path):
    report_path = tmp_path / "panchanga-parity-report.json"
    _write_panchanga_parity_report(report_path)

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_panchanga_parity_report_path=report_path,
    )

    parity = summary["witness_panchanga_parity"]
    assert parity["available"] is True
    assert parity["status"] == "diff_open"
    assert parity["schema_version"] == "jyotish-panchanga-parity-report-v1"
    assert parity["source_report"] == str(report_path)
    assert parity["summary"]["failed_count"] == 1
    assert parity["field_summary"]["tithi"]["failed"] == 1
    assert parity["target_met"] is False
    assert parity["next_actions"] == [
        {
            "case_id": "case-panchanga-a",
            "status": "failed",
            "checked_fields": ["tithi", "vara"],
            "missing_fields": ["jhora.panchanga.vara"],
            "failed_fields": ["panchanga.tithi"],
        }
    ]
    serialized = json.dumps(parity, ensure_ascii=False).lower()
    for forbidden in [
        "field_results",
        '"expected"',
        '"actual"',
        "sources_present",
        "mark_",
        "seal_witness_case",
        "--ack-diff-open",
        "authority",
        "authoritative",
    ]:
        assert forbidden not in serialized


def test_witness_summary_panchanga_parity_missing_and_invalid_are_safe(tmp_path):
    missing_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_panchanga_parity_report_path=tmp_path / "missing-panchanga-parity.json",
    )
    assert missing_summary["witness_panchanga_parity"]["available"] is False
    assert missing_summary["witness_panchanga_parity"]["status"] == "missing"

    invalid_path = tmp_path / "invalid-panchanga-parity.json"
    invalid_path.write_text("{broken", encoding="utf-8")
    invalid_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_panchanga_parity_report_path=invalid_path,
    )
    parity = invalid_summary["witness_panchanga_parity"]
    assert parity["available"] is False
    assert parity["status"] == "invalid"
    assert "traceback" not in json.dumps(parity, ensure_ascii=False).lower()


def test_witness_summary_api_cache_fingerprint_includes_panchanga_parity_path(settings, tmp_path):
    first_path = tmp_path / "first-panchanga-parity.json"
    second_path = tmp_path / "second-panchanga-parity.json"
    _write_panchanga_parity_report(first_path, case_id="first-panchanga-case")
    _write_panchanga_parity_report(second_path, case_id="second-panchanga-case")
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    settings.WITNESS_PANCHANGA_PARITY_REPORT_PATH = first_path

    first_response = APIClient().get(reverse("witness-summary"))
    settings.WITNESS_PANCHANGA_PARITY_REPORT_PATH = second_path
    second_response = APIClient().get(reverse("witness-summary"))

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.data["witness_panchanga_parity"]["next_actions"][0]["case_id"] == "first-panchanga-case"
    assert second_response.data["witness_panchanga_parity"]["next_actions"][0]["case_id"] == "second-panchanga-case"


def test_witness_panchanga_parity_default_path_matches_command_output(settings):
    normalized = str(settings.WITNESS_PANCHANGA_PARITY_REPORT_PATH).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/panchanga-parity-report.json")


def _write_ashtakavarga_parity_report(path, *, status: str = "failed", case_id: str = "case-ashtakavarga-a"):
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-ashtakavarga-parity-report-v1",
                "metadata": {
                    "generated_at": "2026-06-21T00:00:00+00:00",
                    "target_reviewed_count": 20,
                    "layers": ["bhinna", "sarva"],
                    "witness_sources": ["jhora", "parashara_light"],
                },
                "summary": {
                    "case_count": 2,
                    "comparable_count": 1,
                    "passed_count": 0 if status == "failed" else 20,
                    "failed_count": 1 if status == "failed" else 0,
                    "missing_witness_count": 0,
                    "not_reviewed_count": 0,
                    "not_comparable_count": 1,
                    "target_reviewed_count": 20,
                    "target_met": status != "failed",
                },
                "layer_summary": {
                    "bhinna": {"passed": 0, "failed": 1 if status == "failed" else 0, "missing": 0, "not_comparable": 1},
                    "sarva": {"passed": 1, "failed": 0, "missing": 1, "not_comparable": 0},
                },
                "body_summary": {
                    "Surya": {"passed": 0, "failed": 1 if status == "failed" else 0, "missing": 0, "not_comparable": 1},
                    "Chandra": {"passed": 1, "failed": 0, "missing": 0, "not_comparable": 0},
                },
                "cases": [
                    {
                        "case_id": case_id,
                        "review_status": "jhora_verified",
                        "sources_present": ["jhora"],
                        "comparison_status": status,
                        "checked_layers": ["bhinna", "sarva"],
                        "failed_layers": ["bhinna"] if status == "failed" else [],
                        "missing_layers": ["sarva"] if status != "failed" else [],
                        "checked_cells": ["bhinna.Surya.Mesha", "sarva.total"],
                        "failed_cells": ["bhinna.Surya.Mesha"] if status == "failed" else [],
                        "missing_cells": ["calculated.sarva.total"] if status != "failed" else [],
                        "field_results": [
                            {
                                "source": "jhora",
                                "layer": "bhinna",
                                "body": "Surya",
                                "cell": "bhinna.Surya.Mesha",
                                "expected": 4,
                                "actual": 3,
                                "passed": False,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_witness_summary_exposes_safe_ashtakavarga_parity_diagnostic(tmp_path):
    report_path = tmp_path / "ashtakavarga-parity-report.json"
    _write_ashtakavarga_parity_report(report_path)

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_ashtakavarga_parity_report_path=report_path,
    )

    parity = summary["witness_ashtakavarga_parity"]
    assert parity["available"] is True
    assert parity["status"] == "diff_open"
    assert parity["schema_version"] == "jyotish-ashtakavarga-parity-report-v1"
    assert parity["source_report"] == str(report_path)
    assert parity["summary"]["failed_count"] == 1
    assert parity["layer_summary"]["bhinna"]["failed"] == 1
    assert parity["body_summary"]["Surya"]["failed"] == 1
    assert parity["target_met"] is False
    assert parity["next_actions"] == [
        {
            "case_id": "case-ashtakavarga-a",
            "status": "failed",
            "checked_layers": ["bhinna", "sarva"],
            "failed_layers": ["bhinna"],
            "missing_layers": [],
            "missing_cells": [],
            "failed_cells": ["bhinna.Surya.Mesha"],
        }
    ]
    serialized = json.dumps(parity, ensure_ascii=False).lower()
    for forbidden in [
        "field_results",
        '"expected"',
        '"actual"',
        "sources_present",
        "checked_cells",
        "mark_",
        "seal_witness_case",
        "--ack-diff-open",
        "authority",
        "authoritative",
    ]:
        assert forbidden not in serialized


def test_witness_summary_ashtakavarga_parity_missing_and_invalid_are_safe(tmp_path):
    missing_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_ashtakavarga_parity_report_path=tmp_path / "missing-ashtakavarga-parity.json",
    )
    assert missing_summary["witness_ashtakavarga_parity"]["available"] is False
    assert missing_summary["witness_ashtakavarga_parity"]["status"] == "missing"

    invalid_path = tmp_path / "invalid-ashtakavarga-parity.json"
    invalid_path.write_text("{broken", encoding="utf-8")
    invalid_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_ashtakavarga_parity_report_path=invalid_path,
    )
    parity = invalid_summary["witness_ashtakavarga_parity"]
    assert parity["available"] is False
    assert parity["status"] == "invalid"
    assert "traceback" not in json.dumps(parity, ensure_ascii=False).lower()


def test_witness_summary_api_cache_fingerprint_includes_ashtakavarga_parity_path(settings, tmp_path):
    first_path = tmp_path / "first-ashtakavarga-parity.json"
    second_path = tmp_path / "second-ashtakavarga-parity.json"
    _write_ashtakavarga_parity_report(first_path, case_id="first-ashtakavarga-case")
    _write_ashtakavarga_parity_report(second_path, case_id="second-ashtakavarga-case")
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    settings.WITNESS_ASHTAKAVARGA_PARITY_REPORT_PATH = first_path

    first_response = APIClient().get(reverse("witness-summary"))
    settings.WITNESS_ASHTAKAVARGA_PARITY_REPORT_PATH = second_path
    second_response = APIClient().get(reverse("witness-summary"))

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.data["witness_ashtakavarga_parity"]["next_actions"][0]["case_id"] == "first-ashtakavarga-case"
    assert second_response.data["witness_ashtakavarga_parity"]["next_actions"][0]["case_id"] == "second-ashtakavarga-case"


def test_witness_ashtakavarga_parity_default_path_matches_command_output(settings):
    normalized = str(settings.WITNESS_ASHTAKAVARGA_PARITY_REPORT_PATH).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/ashtakavarga-parity-report.json")


def _write_strengths_parity_report(path, *, status: str = "failed", case_id: str = "case-strengths-a"):
    path.write_text(
        json.dumps(
            {
                "schema_version": "jyotish-strengths-parity-report-v1",
                "metadata": {
                    "generated_at": "2026-06-21T00:00:00+00:00",
                    "target_reviewed_count": 20,
                    "layers": ["vimshopaka", "shadbala"],
                    "profile_sensitive_layers": ["shadbala"],
                    "witness_sources": ["jhora", "parashara_light"],
                },
                "summary": {
                    "case_count": 2,
                    "comparable_count": 1,
                    "passed_count": 0 if status == "failed" else 20,
                    "failed_count": 1 if status == "failed" else 0,
                    "missing_witness_count": 0,
                    "not_reviewed_count": 0,
                    "not_comparable_count": 1,
                    "target_reviewed_count": 20,
                    "target_met": status != "failed",
                },
                "layer_summary": {
                    "vimshopaka": {"passed": 0, "failed": 1 if status == "failed" else 0, "missing": 0, "not_comparable": 1},
                    "shadbala": {"passed": 1, "failed": 0, "missing": 1, "not_comparable": 0},
                },
                "body_summary": {
                    "Surya": {"passed": 0, "failed": 1 if status == "failed" else 0, "missing": 0, "not_comparable": 1},
                    "Chandra": {"passed": 1, "failed": 0, "missing": 0, "not_comparable": 0},
                },
                "cases": [
                    {
                        "case_id": case_id,
                        "review_status": "jhora_verified",
                        "sources_present": ["jhora"],
                        "comparison_status": status,
                        "checked_layers": ["vimshopaka", "shadbala"],
                        "failed_layers": ["vimshopaka"] if status == "failed" else [],
                        "missing_layers": ["shadbala"] if status != "failed" else [],
                        "checked_fields": ["vimshopaka.Surya.shadvarga", "shadbala.Surya.total_virupas"],
                        "failed_fields": ["vimshopaka.Surya.shadvarga"] if status == "failed" else [],
                        "missing_fields": ["calculated.shadbala.Surya.total_virupas"] if status != "failed" else [],
                        "field_results": [
                            {
                                "source": "jhora",
                                "layer": "vimshopaka",
                                "body": "Surya",
                                "field": "vimshopaka.Surya.shadvarga",
                                "expected": 12.52,
                                "actual": 12.5,
                                "passed": False,
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_witness_summary_exposes_safe_strengths_parity_diagnostic(tmp_path):
    report_path = tmp_path / "strengths-parity-report.json"
    _write_strengths_parity_report(report_path)

    summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_strengths_parity_report_path=report_path,
    )

    parity = summary["witness_strengths_parity"]
    assert parity["available"] is True
    assert parity["status"] == "diff_open"
    assert parity["schema_version"] == "jyotish-strengths-parity-report-v1"
    assert parity["source_report"] == str(report_path)
    assert parity["summary"]["failed_count"] == 1
    assert parity["layer_summary"]["vimshopaka"]["failed"] == 1
    assert parity["body_summary"]["Surya"]["failed"] == 1
    assert parity["target_met"] is False
    assert parity["profile_sensitive_layers"] == ["shadbala"]
    assert parity["next_actions"] == [
        {
            "case_id": "case-strengths-a",
            "status": "failed",
            "checked_layers": ["vimshopaka", "shadbala"],
            "failed_layers": ["vimshopaka"],
            "missing_layers": [],
            "checked_fields": ["vimshopaka.Surya.shadvarga", "shadbala.Surya.total_virupas"],
            "missing_fields": [],
            "failed_fields": ["vimshopaka.Surya.shadvarga"],
        }
    ]
    serialized = json.dumps(parity, ensure_ascii=False).lower()
    for forbidden in [
        "field_results",
        '"expected"',
        '"actual"',
        "sources_present",
        '"source"',
        "mark_",
        "seal_witness_case",
        "--ack-diff-open",
        "authority",
        "authoritative",
    ]:
        assert forbidden not in serialized


def test_witness_summary_strengths_parity_missing_and_invalid_are_safe(tmp_path):
    missing_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_strengths_parity_report_path=tmp_path / "missing-strengths-parity.json",
    )
    assert missing_summary["witness_strengths_parity"]["available"] is False
    assert missing_summary["witness_strengths_parity"]["status"] == "missing"

    invalid_path = tmp_path / "invalid-strengths-parity.json"
    invalid_path.write_text("{broken", encoding="utf-8")
    invalid_summary = build_witness_summary(
        jhora_report_path=tmp_path / "missing-jhora-report.json",
        parashara_light_packet_path=tmp_path / "missing-pl-packet.json",
        witness_strengths_parity_report_path=invalid_path,
    )
    parity = invalid_summary["witness_strengths_parity"]
    assert parity["available"] is False
    assert parity["status"] == "invalid"
    assert "traceback" not in json.dumps(parity, ensure_ascii=False).lower()


def test_witness_summary_api_cache_fingerprint_includes_strengths_parity_path(settings, tmp_path):
    first_path = tmp_path / "first-strengths-parity.json"
    second_path = tmp_path / "second-strengths-parity.json"
    _write_strengths_parity_report(first_path, case_id="first-strengths-case")
    _write_strengths_parity_report(second_path, case_id="second-strengths-case")
    settings.JHORA_ACCURACY_REPORT_PATH = tmp_path / "missing-jhora.json"
    settings.PARASHARA_LIGHT_PACKET_PATH = tmp_path / "missing-pl.json"
    settings.PARASHARA_LIGHT_MANUAL_WITNESS_VALUES_PATH = ""
    settings.WITNESS_STRENGTHS_PARITY_REPORT_PATH = first_path

    first_response = APIClient().get(reverse("witness-summary"))
    settings.WITNESS_STRENGTHS_PARITY_REPORT_PATH = second_path
    second_response = APIClient().get(reverse("witness-summary"))

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.data["witness_strengths_parity"]["next_actions"][0]["case_id"] == "first-strengths-case"
    assert second_response.data["witness_strengths_parity"]["next_actions"][0]["case_id"] == "second-strengths-case"


def test_witness_strengths_parity_default_path_matches_command_output(settings):
    normalized = str(settings.WITNESS_STRENGTHS_PARITY_REPORT_PATH).replace("\\", "/")

    assert normalized.endswith("/.tmp/witness-review/strengths-parity-report.json")
