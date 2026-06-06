from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .jhora_accuracy_report import load_jhora_accuracy_report
from .parashara_light_packet_report import load_parashara_light_packet_report


def build_witness_summary(
    *,
    jhora_report_path: str | Path,
    parashara_light_packet_path: str | Path,
    parashara_light_manual_values_path: str | Path = "",
    parashara_light_profile_report_path: str | Path = "",
    parashara_light_forensic_report_path: str | Path = "",
    parashara_light_settings_evidence_path: str | Path = "",
    parashara_light_visible_settings_capture_path: str | Path = "",
    parashara_light_calculation_options_report_path: str | Path = "",
    parashara_light_settings_aware_forensic_path: str | Path = "",
    parashara_light_preferences_inventory_path: str | Path = "",
    parashara_light_hidden_option_store_path: str | Path = "",
    parashara_light_option_store_diff_path: str | Path = "",
) -> dict[str, Any]:
    jhora = _jhora_summary(jhora_report_path)
    parashara_light = _parashara_light_summary(
        parashara_light_packet_path,
        manual_witness_values_path=parashara_light_manual_values_path,
        profile_report_path=parashara_light_profile_report_path,
        forensic_report_path=parashara_light_forensic_report_path,
        settings_evidence_path=parashara_light_settings_evidence_path,
        visible_settings_capture_path=parashara_light_visible_settings_capture_path,
        calculation_options_report_path=parashara_light_calculation_options_report_path,
        settings_aware_forensic_path=parashara_light_settings_aware_forensic_path,
        preferences_inventory_path=parashara_light_preferences_inventory_path,
        hidden_option_store_path=parashara_light_hidden_option_store_path,
        option_store_diff_path=parashara_light_option_store_diff_path,
    )
    open_items = _open_items(jhora, parashara_light)
    return {
        "overall_status": _overall_status(jhora, parashara_light),
        "jhora": jhora,
        "parashara_light": parashara_light,
        "open_items": open_items,
    }


def _jhora_summary(path: str | Path) -> dict[str, Any]:
    try:
        report = load_jhora_accuracy_report(path)
    except FileNotFoundError:
        return {
            "available": False,
            "status": "missing",
            "source_report": str(path),
            "fixture_id": "",
            "failed_checks": 0,
            "missing_fields_count": 0,
        }

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    longitude = summary.get("longitude") if isinstance(summary.get("longitude"), dict) else {}
    exact_groups = summary.get("exact_groups") if isinstance(summary.get("exact_groups"), list) else []
    missing_fields = summary.get("missing_fields") if isinstance(summary.get("missing_fields"), list) else []
    failed_checks = int(longitude.get("failed") or 0) + sum(
        int(group.get("failed") or 0) for group in exact_groups if isinstance(group, dict)
    )
    return {
        "available": True,
        "status": "matched" if report.get("passed") else "diff_open",
        "fixture_id": report.get("fixture_id", ""),
        "source_report": report.get("source_report", str(path)),
        "failed_checks": failed_checks,
        "missing_fields_count": len(missing_fields),
        "max_delta_arcseconds": float(longitude.get("max_delta_arcseconds") or 0.0),
        "corrected_max_delta_arcseconds": float(longitude.get("corrected_max_delta_arcseconds") or 0.0),
        "layers": summary.get("jhora_layers") or {},
    }


def _parashara_light_summary(
    path: str | Path,
    *,
    manual_witness_values_path: str | Path = "",
    profile_report_path: str | Path = "",
    forensic_report_path: str | Path = "",
    settings_evidence_path: str | Path = "",
    visible_settings_capture_path: str | Path = "",
    calculation_options_report_path: str | Path = "",
    settings_aware_forensic_path: str | Path = "",
    preferences_inventory_path: str | Path = "",
    hidden_option_store_path: str | Path = "",
    option_store_diff_path: str | Path = "",
) -> dict[str, Any]:
    profile = _parashara_light_profile_summary(profile_report_path)
    forensic = _parashara_light_forensic_summary(forensic_report_path)
    settings_evidence = _parashara_light_settings_evidence_summary(settings_evidence_path)
    visible_settings_capture = _parashara_light_visible_settings_capture_summary(visible_settings_capture_path)
    calculation_options = _parashara_light_calculation_options_summary(calculation_options_report_path)
    settings_aware_forensic = _parashara_light_settings_aware_forensic_summary(settings_aware_forensic_path)
    preferences_inventory = _parashara_light_preferences_inventory_summary(preferences_inventory_path)
    hidden_option_store = _parashara_light_hidden_option_store_summary(hidden_option_store_path)
    option_store_diff = _parashara_light_option_store_diff_summary(option_store_diff_path)
    try:
        report = load_parashara_light_packet_report(
            path,
            manual_witness_values_path=manual_witness_values_path,
        )
    except FileNotFoundError:
        return {
            "available": False,
            "status": "missing",
            "source_packet": str(path),
            "id": "",
            "manual_values_count": 0,
            "manual_failed_count": 0,
            "manual_completion_percent": 0,
            "profile": profile,
            "forensic": forensic,
            "settings_evidence": settings_evidence,
            "visible_settings_capture": visible_settings_capture,
            "calculation_options": calculation_options,
            "settings_aware_forensic": settings_aware_forensic,
            "preferences_inventory": preferences_inventory,
            "hidden_option_store": hidden_option_store,
            "option_store_diff": option_store_diff,
        }

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    comparison = report.get("manual_witness_comparison") if isinstance(report.get("manual_witness_comparison"), dict) else {}
    return {
        "available": True,
        "status": comparison.get("status") or "no_manual_values",
        "id": report.get("id", ""),
        "source_packet": report.get("source_packet", str(path)),
        "manual_witness_source": report.get("manual_witness_source", ""),
        "manual_values_count": int(summary.get("manual_values_count") or 0),
        "manual_failed_count": int(summary.get("manual_failed_count") or 0),
        "manual_completion_percent": int(summary.get("manual_completion_percent") or 0),
        "capture_status": summary.get("capture_status", ""),
        "review_status": summary.get("review_status", ""),
        "profile": profile,
        "forensic": forensic,
        "settings_evidence": settings_evidence,
        "visible_settings_capture": visible_settings_capture,
        "calculation_options": calculation_options,
        "settings_aware_forensic": settings_aware_forensic,
        "preferences_inventory": preferences_inventory,
        "hidden_option_store": hidden_option_store,
        "option_store_diff": option_store_diff,
    }


def _parashara_light_profile_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_profile("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_profile(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "authoritative": False,
            "error": str(exc),
            "data_quality_flags": [],
            "packet_comparison": {},
            "candidate_normalization": {},
        }

    return {
        "available": True,
        "status": "loaded",
        "source_report": str(source),
        "source_xml": report.get("source_xml", ""),
        "authoritative": False,
        "data_quality_flags": report.get("data_quality_flags") if isinstance(report.get("data_quality_flags"), list) else [],
        "packet_comparison": (
            report.get("packet_comparison") if isinstance(report.get("packet_comparison"), dict) else {}
        ),
        "candidate_normalization": (
            report.get("candidate_normalization") if isinstance(report.get("candidate_normalization"), dict) else {}
        ),
    }


def _missing_parashara_light_profile(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "authoritative": False,
        "data_quality_flags": [],
        "packet_comparison": {},
        "candidate_normalization": {},
    }


def _parashara_light_forensic_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_forensic("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_forensic(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "error": str(exc),
            "conclusion": "",
            "next_action": "",
            "engine_swiss_diff_count": 0,
            "pl_diff_count": 0,
            "pl_swiss_max_abs_arcsec": 0.0,
            "uniform_offset_status": "",
            "time_shift_status": "",
            "row_health": {"total": 0, "matched": 0, "diff_open": 0},
        }

    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    diagnostics = report.get("diagnostics") if isinstance(report.get("diagnostics"), dict) else {}
    uniform_offset = diagnostics.get("uniform_offset") if isinstance(diagnostics.get("uniform_offset"), dict) else {}
    time_shift = diagnostics.get("time_shift") if isinstance(diagnostics.get("time_shift"), dict) else {}
    rows = report.get("rows") if isinstance(report.get("rows"), list) else []
    matched_count = sum(1 for row in rows if isinstance(row, dict) and row.get("status") == "matched")
    diff_open_count = sum(1 for row in rows if isinstance(row, dict) and row.get("status") == "diff_open")
    return {
        "available": True,
        "status": "loaded",
        "source_report": str(source),
        "conclusion": summary.get("conclusion", ""),
        "next_action": diagnostics.get("next_action", ""),
        "engine_swiss_diff_count": int(summary.get("engine_swiss_diff_count") or 0),
        "pl_diff_count": int(summary.get("pl_diff_count") or 0),
        "pl_swiss_max_abs_arcsec": float(summary.get("pl_swiss_max_abs_arcsec") or 0.0),
        "uniform_offset_status": uniform_offset.get("status", ""),
        "time_shift_status": time_shift.get("status", ""),
        "row_health": {
            "total": len([row for row in rows if isinstance(row, dict)]),
            "matched": matched_count,
            "diff_open": diff_open_count,
        },
    }


def _missing_parashara_light_forensic(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "conclusion": "",
        "next_action": "",
        "engine_swiss_diff_count": 0,
        "pl_diff_count": 0,
        "pl_swiss_max_abs_arcsec": 0.0,
        "uniform_offset_status": "",
        "time_shift_status": "",
        "row_health": {"total": 0, "matched": 0, "diff_open": 0},
    }


def _parashara_light_settings_evidence_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_settings_evidence("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_settings_evidence(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "error": str(exc),
            "proprietary_binary_policy": "",
            "artifact_policy": "",
            "options_files_count": 0,
            "text_artifacts_count": 0,
            "session_tokens_count": 0,
            "runtime_build": "",
            "next_action": "",
        }

    text_artifacts = report.get("text_artifacts") if isinstance(report.get("text_artifacts"), list) else []
    return {
        "available": True,
        "status": "loaded",
        "source_report": str(source),
        "proprietary_binary_policy": report.get("proprietary_binary_policy", ""),
        "artifact_policy": report.get("artifact_policy", ""),
        "options_files_count": _count_list(report.get("options_manifest")),
        "text_artifacts_count": len(text_artifacts),
        "session_tokens_count": _count_list(report.get("session_token_manifest")),
        "runtime_build": _runtime_build_from_text_artifacts(text_artifacts),
        "next_action": report.get("next_action", ""),
    }


def _runtime_build_from_text_artifacts(text_artifacts: list[Any]) -> str:
    for item in text_artifacts:
        if not isinstance(item, dict):
            continue
        if item.get("relative_path") == "Temp/htpl.log":
            return str(item.get("content_preview") or "")
    return ""


def _count_list(value: object) -> int:
    return len(value) if isinstance(value, list) else 0


def _missing_parashara_light_settings_evidence(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "proprietary_binary_policy": "",
        "artifact_policy": "",
        "options_files_count": 0,
        "text_artifacts_count": 0,
        "session_tokens_count": 0,
        "runtime_build": "",
        "next_action": "",
    }


def _parashara_light_visible_settings_capture_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_visible_settings_capture("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_visible_settings_capture(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "error": str(exc),
            "settings_dialog_captured": False,
            "options_menu_captured": False,
            "surfaces_count": 0,
            "screenshots_count": 0,
            "next_action": "",
        }

    return {
        "available": True,
        "status": report.get("status", ""),
        "source_report": str(source),
        "settings_dialog_captured": bool(report.get("settings_dialog_captured")),
        "options_menu_captured": bool(report.get("options_menu_captured")),
        "surfaces_count": int(report.get("surfaces_count") or 0),
        "screenshots_count": int(report.get("screenshots_count") or 0),
        "next_action": report.get("next_action", ""),
    }


def _missing_parashara_light_visible_settings_capture(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "settings_dialog_captured": False,
        "options_menu_captured": False,
        "surfaces_count": 0,
        "screenshots_count": 0,
        "next_action": "",
    }


def _parashara_light_calculation_options_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_calculation_options("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_calculation_options(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "error": str(exc),
            "selected_ayanamsha_key": "",
            "selected_ayanamsha_label": "",
            "selected_calculation_method_key": "",
            "selected_calculation_method_label": "",
            "offset_value": "",
            "selected_miscellaneous_item_key": "",
            "selected_miscellaneous_item_label": "",
            "offset_control_visible": False,
            "miscellaneous_list_visible": False,
        }

    ayanamsha = report.get("selected_ayanamsha") if isinstance(report.get("selected_ayanamsha"), dict) else {}
    method = (
        report.get("selected_calculation_method")
        if isinstance(report.get("selected_calculation_method"), dict)
        else {}
    )
    offset = report.get("offset_value") if isinstance(report.get("offset_value"), dict) else {}
    miscellaneous_item = (
        report.get("selected_miscellaneous_item")
        if isinstance(report.get("selected_miscellaneous_item"), dict)
        else {}
    )
    return {
        "available": True,
        "status": report.get("status", ""),
        "source_report": str(source),
        "selected_ayanamsha_key": ayanamsha.get("key", ""),
        "selected_ayanamsha_label": ayanamsha.get("label", ""),
        "selected_calculation_method_key": method.get("key", ""),
        "selected_calculation_method_label": method.get("label", ""),
        "offset_value": offset.get("value", ""),
        "selected_miscellaneous_item_key": miscellaneous_item.get("key", ""),
        "selected_miscellaneous_item_label": miscellaneous_item.get("label", ""),
        "offset_control_visible": bool(report.get("offset_control_visible")),
        "miscellaneous_list_visible": bool(report.get("miscellaneous_list_visible")),
    }


def _missing_parashara_light_calculation_options(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "selected_ayanamsha_key": "",
        "selected_ayanamsha_label": "",
        "selected_calculation_method_key": "",
        "selected_calculation_method_label": "",
        "offset_value": "",
        "selected_miscellaneous_item_key": "",
        "selected_miscellaneous_item_label": "",
        "offset_control_visible": False,
        "miscellaneous_list_visible": False,
    }


def _parashara_light_settings_aware_forensic_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_settings_aware_forensic("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_settings_aware_forensic(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "error": str(exc),
            "ayanamsha_status": "",
            "offset_status": "",
            "engine_swiss_status": "",
            "uniform_offset_status": "",
            "time_shift_status": "",
            "next_action": "",
        }

    visible_settings = report.get("visible_settings") if isinstance(report.get("visible_settings"), dict) else {}
    diagnostic_gates = report.get("diagnostic_gates") if isinstance(report.get("diagnostic_gates"), dict) else {}
    return {
        "available": True,
        "status": report.get("status", ""),
        "source_report": str(source),
        "ayanamsha_status": visible_settings.get("ayanamsha_status", ""),
        "offset_status": visible_settings.get("offset_status", ""),
        "engine_swiss_status": diagnostic_gates.get("engine_swiss_status", ""),
        "uniform_offset_status": diagnostic_gates.get("uniform_offset_status", ""),
        "time_shift_status": diagnostic_gates.get("time_shift_status", ""),
        "next_action": report.get("next_action", ""),
    }


def _missing_parashara_light_settings_aware_forensic(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "ayanamsha_status": "",
        "offset_status": "",
        "engine_swiss_status": "",
        "uniform_offset_status": "",
        "time_shift_status": "",
        "next_action": "",
    }


def _parashara_light_preferences_inventory_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_preferences_inventory("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_preferences_inventory(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "error": str(exc),
            "tabs_count": 0,
            "visible_ayanamsha_controls": False,
            "visible_graph_ephemeris_display_option": False,
            "visible_system_paths": False,
            "internal_ephemeris_mode_visible": False,
            "next_action": "",
        }

    return {
        "available": True,
        "status": report.get("status", ""),
        "source_report": str(source),
        "tabs_count": int(report.get("tabs_count") or 0),
        "visible_ayanamsha_controls": bool(report.get("visible_ayanamsha_controls")),
        "visible_graph_ephemeris_display_option": bool(report.get("visible_graph_ephemeris_display_option")),
        "visible_system_paths": bool(report.get("visible_system_paths")),
        "internal_ephemeris_mode_visible": bool(report.get("internal_ephemeris_mode_visible")),
        "next_action": report.get("next_action", ""),
    }


def _missing_parashara_light_preferences_inventory(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "tabs_count": 0,
        "visible_ayanamsha_controls": False,
        "visible_graph_ephemeris_display_option": False,
        "visible_system_paths": False,
        "internal_ephemeris_mode_visible": False,
        "next_action": "",
    }


def _parashara_light_hidden_option_store_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_hidden_option_store("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_hidden_option_store(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "error": str(exc),
            "proprietary_binary_policy": "",
            "primary_candidate": "",
            "option_store_candidates_count": 0,
            "session_token_candidates_count": 0,
            "next_action": "",
        }

    primary = report.get("primary_candidate") if isinstance(report.get("primary_candidate"), dict) else {}
    counts = report.get("candidate_counts") if isinstance(report.get("candidate_counts"), dict) else {}
    return {
        "available": True,
        "status": report.get("status", ""),
        "source_report": str(source),
        "proprietary_binary_policy": report.get("proprietary_binary_policy", ""),
        "primary_candidate": primary.get("relative_path", ""),
        "option_store_candidates_count": int(counts.get("option_store_candidates") or 0),
        "session_token_candidates_count": int(counts.get("session_token_candidates") or 0),
        "next_action": report.get("next_action", ""),
    }


def _missing_parashara_light_hidden_option_store(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "proprietary_binary_policy": "",
        "primary_candidate": "",
        "option_store_candidates_count": 0,
        "session_token_candidates_count": 0,
        "next_action": "",
    }


def _parashara_light_option_store_diff_summary(path: str | Path) -> dict[str, Any]:
    if not path:
        return _missing_parashara_light_option_store_diff("")
    source = Path(path)
    try:
        report = json.loads(source.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return _missing_parashara_light_option_store_diff(str(source))
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        return {
            "available": False,
            "status": "load_error",
            "source_report": str(source),
            "error": str(exc),
            "proprietary_binary_policy": "",
            "visible_setting": "",
            "primary_candidate": "",
            "changed_candidates_count": 0,
            "restore_verified": False,
            "next_action": "",
        }

    return {
        "available": True,
        "status": report.get("status", ""),
        "source_report": str(source),
        "proprietary_binary_policy": report.get("proprietary_binary_policy", ""),
        "visible_setting": report.get("visible_setting", ""),
        "primary_candidate": report.get("primary_candidate", ""),
        "changed_candidates_count": int(report.get("changed_candidates_count") or 0),
        "restore_verified": bool(report.get("restore_verified")),
        "next_action": report.get("next_action", ""),
    }


def _missing_parashara_light_option_store_diff(path: str) -> dict[str, Any]:
    return {
        "available": False,
        "status": "missing",
        "source_report": path,
        "proprietary_binary_policy": "",
        "visible_setting": "",
        "primary_candidate": "",
        "changed_candidates_count": 0,
        "restore_verified": False,
        "next_action": "",
    }


def _overall_status(jhora: dict[str, Any], parashara_light: dict[str, Any]) -> str:
    if not jhora["available"] and not parashara_light["available"]:
        return "missing_witnesses"
    if jhora["status"] == "diff_open" or parashara_light["status"] == "diff_open":
        return "diff_open"
    if parashara_light["status"] in {"no_manual_values", "no_checked_fields"}:
        return "needs_manual_witness"
    if jhora["status"] == "missing" or parashara_light["status"] == "missing":
        return "partial"
    return "matched"


def _open_items(jhora: dict[str, Any], parashara_light: dict[str, Any]) -> list[dict[str, Any]]:
    items = []
    if jhora["status"] == "diff_open":
        items.append(
            {
                "source": "jhora",
                "status": "diff_open",
                "label": "JHora export diff",
                "failed_checks": jhora["failed_checks"],
            }
        )
    if parashara_light["status"] == "diff_open":
        items.append(
            {
                "source": "parashara_light",
                "status": "diff_open",
                "label": "Parashara Light manual diff",
                "failed_checks": parashara_light["manual_failed_count"],
            }
        )
    if parashara_light["status"] in {"no_manual_values", "no_checked_fields"}:
        items.append(
            {
                "source": "parashara_light",
                "status": "needs_manual_witness",
                "label": "Fill Parashara Light manual witness values",
                "completion_percent": parashara_light["manual_completion_percent"],
            }
        )
    return items
