from __future__ import annotations

from pathlib import Path
from typing import Any

from .chart import build_birth_chart
from .dual_calculation import build_dual_calculation_report
from .ephemeris import EphemerisProvider
from .jhora_export import parse_jhora_complete_calculations
from .jhora_parity_suite import jhora_parity_suite_manifest

SCHEMA_VERSION = "jyotish-jhora-verification-packet-v1"

DEFAULT_TOLERANCES = {
    "planet_longitude_arcseconds": 1.0,
    "lagna_arcseconds": 5.0,
    "shadbala_virupas": 0.01,
    "special_point_arcseconds": 90.0,
}

CAPTURE_CHECKLIST = [
    "Birth input screen: date, local time, place, latitude, longitude, timezone and DST.",
    "Preferences: Drik/SSS, ayanamsa, true/mean nodes, house/bhava, sunrise and panchanga settings.",
    "Main chart screen: D1 plus visible D9/D10/D30/D60 and right-side special points.",
    "Basics tab: graha longitude, rashi, nakshatra, pada, retrograde flags and panchanga.",
    "Dasas tab: Vimshottari MD/AD/PD with start/end dates.",
    "Strengths tab: shadbala, vimshopaka and avastha tables.",
    "Ashtakavarga tab: BAV rows and SAV totals.",
    "Miscellany/special points: Gulika, Mandi, upagrahas and special lagnas.",
    "Copy complete calculations text and save it beside screenshots.",
]


def build_jhora_verification_packet(
    data: dict[str, Any],
    *,
    packet_id: str = "jhora-verification-packet",
    jhora_export_text: str = "",
    jhora_export_path: str = "",
    jhora_ui_table_dump: dict[str, Any] | None = None,
    jhora_ui_table_dump_path: str = "",
    screenshot_paths: list[str] | None = None,
    reviewer: str = "",
    reviewed_at: str = "",
    jhora_version: str = "8.0",
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    birth_input = dict(data)
    parsed = parse_jhora_complete_calculations(jhora_export_text) if jhora_export_text.strip() else {}
    fixture = _fixture_payload(
        birth_input,
        parsed,
        packet_id=packet_id,
        jhora_export_path=jhora_export_path,
        jhora_ui_table_dump=jhora_ui_table_dump or {},
        jhora_ui_table_dump_path=jhora_ui_table_dump_path,
        screenshot_paths=screenshot_paths or [],
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        jhora_version=jhora_version,
    )
    chart = build_birth_chart(birth_input, provider=provider)
    dual = build_dual_calculation_report(birth_input, provider=provider)
    return {
        "schema_version": SCHEMA_VERSION,
        "id": packet_id,
        "status": "jhora_export_parsed" if parsed else "capture_pending",
        "fixture": fixture,
        "jyotish_agent_chart": chart,
        "dual_calculation": dual,
        "parity_suite": jhora_parity_suite_manifest(),
        "jhora_capture_checklist": CAPTURE_CHECKLIST,
    }


def render_jhora_capture_checklist(packet: dict[str, Any]) -> str:
    fixture = packet.get("fixture") if isinstance(packet.get("fixture"), dict) else {}
    metadata = fixture.get("jhora_metadata") if isinstance(fixture.get("jhora_metadata"), dict) else {}
    lines = [
        f"# JHora Verification Packet: {packet.get('id', '')}",
        "",
        f"- status: {packet.get('status', '')}",
        f"- fixture review_status: {fixture.get('review_status', '')}",
        f"- JHora version required: {metadata.get('version_required', '')}",
        f"- timezone/DST: {metadata.get('timezone_offset', '')} / {metadata.get('timezone_source', '')}",
        "",
        "## Capture Checklist",
    ]
    for item in packet.get("jhora_capture_checklist", []):
        lines.append(f"- [ ] {item}")
    lines.extend(
        [
            "",
            "## Rule",
            "",
            "Do not mark this fixture as `jhora_verified` until the export text, screenshots, settings and reviewer are recorded.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_jhora_verification_packet(packet: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    import json

    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "packet": target / "packet.json",
        "fixture": target / "fixture.json",
        "chart": target / "jyotish-agent-chart.json",
        "dual_calculation": target / "dual-calculation.json",
        "checklist": target / "jhora-capture-checklist.md",
    }
    paths["packet"].write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["fixture"].write_text(
        json.dumps(packet["fixture"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    paths["chart"].write_text(
        json.dumps(packet["jyotish_agent_chart"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    paths["dual_calculation"].write_text(
        json.dumps(packet["dual_calculation"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    paths["checklist"].write_text(render_jhora_capture_checklist(packet), encoding="utf-8")
    return {key: str(path) for key, path in paths.items()}


def _fixture_payload(
    birth_input: dict[str, Any],
    parsed: dict[str, Any],
    *,
    packet_id: str,
    jhora_export_path: str,
    jhora_ui_table_dump: dict[str, Any],
    jhora_ui_table_dump_path: str,
    screenshot_paths: list[str],
    reviewer: str,
    reviewed_at: str,
    jhora_version: str,
) -> dict[str, Any]:
    parsed_metadata = parsed.get("metadata") if isinstance(parsed.get("metadata"), dict) else {}
    jhora_expected = dict(parsed.get("jhora_expected", {}) if parsed else {})
    if jhora_ui_table_dump:
        jhora_expected["ui_tables"] = jhora_ui_table_dump
    return {
        "id": packet_id,
        "source": "jhora_complete_calculations_clipboard" if parsed else "jhora_capture_packet",
        "review_status": "draft",
        "notes": (
            "Capture packet for JHora parity. Keep draft until export text, screenshots and "
            "all calculation preferences are reviewed."
        ),
        "input": birth_input,
        "jhora_metadata": {
            "profile_status": "unverified",
            "version_required": jhora_version,
            "siddhanta_model": birth_input.get("calculation_model") or birth_input.get("siddhanta_model") or "",
            "ayanamsa": parsed_metadata.get("ayanamsa") or birth_input.get("ayanamsa") or "",
            "ayanamsa_degrees": parsed_metadata.get("ayanamsa_degrees"),
            "node_type": birth_input.get("node_type") or "",
            "house_system": birth_input.get("house_system") or "",
            "bhava_system": birth_input.get("bhava_system") or "",
            "varga_options": birth_input.get("varga_scheme") or "",
            "sunrise_source": birth_input.get("sunrise_source") or "",
            "timezone_source": birth_input.get("timezone_source") or "user_supplied_or_jhora_ui",
            "timezone_offset": birth_input.get("timezone_offset") or "",
            "shadbala_options": birth_input.get("shadbala_profile") or "",
            "reviewer": reviewer,
            "reviewed_at": reviewed_at,
            "capture_status": "export_parsed" if parsed else "export_pending",
        },
        "capture_files": {
            "complete_calculations_text": jhora_export_path,
            "ui_table_dump": jhora_ui_table_dump_path,
            "screenshots": screenshot_paths,
        },
        "expected": parsed.get("expected", {}) if parsed else {},
        "jhora_expected": jhora_expected,
        "tolerances": DEFAULT_TOLERANCES,
    }
