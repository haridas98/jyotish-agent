from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def build_parashara_light_settings_aware_forensic(
    *,
    forensic_report_path: str | Path,
    calculation_options_report_path: str | Path,
    profile_report_path: str | Path,
) -> dict[str, Any]:
    forensic_path = Path(forensic_report_path)
    calculation_options_path = Path(calculation_options_report_path)
    profile_path = Path(profile_report_path)
    forensic = _read_json(forensic_path)
    calculation_options = _read_json(calculation_options_path)
    profile = _read_json(profile_path)

    diagnostic_gates = _diagnostic_gates(forensic)
    visible_settings = _visible_settings(calculation_options)
    profile_gates = _profile_gates(profile)
    status = _status(diagnostic_gates, visible_settings, profile_gates)
    return {
        "source": "parashara_light_settings_aware_forensic",
        "artifact_policy": "private_audit_only_do_not_commit",
        "captured_at": datetime.now(UTC).isoformat(),
        "status": status,
        "source_reports": {
            "forensic": _file_fingerprint(forensic_path, classification="pl_forensic_report"),
            "calculation_options": _file_fingerprint(
                calculation_options_path,
                classification="pl_calculation_options_report",
            ),
            "profile": _file_fingerprint(profile_path, classification="pl_profile_report"),
        },
        "diagnostic_gates": diagnostic_gates,
        "visible_settings": visible_settings,
        "profile_gates": profile_gates,
        "conclusion": _conclusion(status),
        "next_action": _next_action(status),
        "notes": [
            "Do not change the calculation engine while direct Swiss/Lahiri matches the engine.",
            "The captured visible PL settings are evidence only for the visible Calculation tab, not hidden ephemeris constants.",
        ],
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _diagnostic_gates(forensic: dict[str, Any]) -> dict[str, Any]:
    summary = forensic.get("summary") if isinstance(forensic.get("summary"), dict) else {}
    diagnostics = forensic.get("diagnostics") if isinstance(forensic.get("diagnostics"), dict) else {}
    uniform = diagnostics.get("uniform_offset") if isinstance(diagnostics.get("uniform_offset"), dict) else {}
    time_shift = diagnostics.get("time_shift") if isinstance(diagnostics.get("time_shift"), dict) else {}
    engine_swiss_diff_count = int(summary.get("engine_swiss_diff_count") or 0)
    pl_diff_count = int(summary.get("pl_diff_count") or 0)
    return {
        "engine_swiss_status": "matched" if engine_swiss_diff_count == 0 else "diff_open",
        "engine_swiss_diff_count": engine_swiss_diff_count,
        "pl_diff_count": pl_diff_count,
        "pl_swiss_max_abs_arcsec": float(summary.get("pl_swiss_max_abs_arcsec") or 0.0),
        "uniform_offset_status": uniform.get("status", ""),
        "time_shift_status": time_shift.get("status", ""),
        "forensic_conclusion": summary.get("conclusion", ""),
    }


def _visible_settings(calculation_options: dict[str, Any]) -> dict[str, Any]:
    ayanamsha = (
        calculation_options.get("selected_ayanamsha")
        if isinstance(calculation_options.get("selected_ayanamsha"), dict)
        else {}
    )
    offset = (
        calculation_options.get("offset_value")
        if isinstance(calculation_options.get("offset_value"), dict)
        else {}
    )
    method = (
        calculation_options.get("selected_calculation_method")
        if isinstance(calculation_options.get("selected_calculation_method"), dict)
        else {}
    )
    ayanamsha_key = str(ayanamsha.get("key") or "")
    offset_value = str(offset.get("value") or "")
    return {
        "calculation_options_status": calculation_options.get("status", ""),
        "ayanamsha_key": ayanamsha_key,
        "ayanamsha_label": ayanamsha.get("label", ""),
        "ayanamsha_status": "matches_engine_lahiri" if ayanamsha_key == "lahiri" else "differs_or_unknown",
        "offset_value": offset_value,
        "offset_status": "zero_offset" if offset_value == "00:00:00" else "nonzero_or_unknown",
        "calculation_method_key": method.get("key", ""),
        "calculation_method_label": method.get("label", ""),
    }


def _profile_gates(profile: dict[str, Any]) -> dict[str, Any]:
    comparison = profile.get("packet_comparison") if isinstance(profile.get("packet_comparison"), dict) else {}
    timezone_delta = _float_or_none(comparison.get("timezone_delta_hours"))
    longitude_delta = _float_or_none(comparison.get("longitude_delta_degrees"))
    latitude_delta = _float_or_none(comparison.get("latitude_delta_degrees"))
    return {
        "timezone_delta_hours": timezone_delta,
        "timezone_status": "matches_packet" if timezone_delta == 0 else "differs_or_unknown",
        "longitude_delta_degrees": longitude_delta,
        "latitude_delta_degrees": latitude_delta,
        "coordinate_status": "minor_variance_not_geocentric_longitude_driver"
        if longitude_delta is not None and latitude_delta is not None
        else "unknown",
        "data_quality_flags": profile.get("data_quality_flags") if isinstance(profile.get("data_quality_flags"), list) else [],
    }


def _status(
    diagnostic_gates: dict[str, Any],
    visible_settings: dict[str, Any],
    profile_gates: dict[str, Any],
) -> str:
    if (
        diagnostic_gates.get("engine_swiss_status") == "matched"
        and int(diagnostic_gates.get("pl_diff_count") or 0) > 0
        and diagnostic_gates.get("uniform_offset_status") == "rejected"
        and diagnostic_gates.get("time_shift_status") == "rejected"
        and visible_settings.get("ayanamsha_status") == "matches_engine_lahiri"
        and visible_settings.get("offset_status") == "zero_offset"
        and profile_gates.get("timezone_status") == "matches_packet"
    ):
        return "visible_settings_do_not_explain_pl_diff"
    return "settings_forensic_incomplete"


def _conclusion(status: str) -> str:
    if status == "visible_settings_do_not_explain_pl_diff":
        return "Visible PL Calculation settings match the engine assumptions, but PL manual witness longitudes still differ."
    return "Settings evidence is incomplete or contradictory; keep forensic diff open."


def _next_action(status: str) -> str:
    if status == "visible_settings_do_not_explain_pl_diff":
        return "capture_pl_internal_ayanamsha_value_or_ephemeris_mode"
    return "complete_visible_pl_settings_capture"


def _float_or_none(value: object) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _file_fingerprint(path: Path, *, classification: str) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path),
        "relative_path": path.name,
        "bytes": stat.st_size,
        "sha256": _sha256(path),
        "classification": classification,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
