from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any

from .chart import build_birth_chart
from .ephemeris import EphemerisProvider

SCHEMA_VERSION = "jyotish-parashara-light-verification-packet-v1"

PL_CAPTURE_CHECKLIST = [
    "Birth input/settings: date, local time, timezone/DST, latitude, longitude and place.",
    "Calculation settings: ayanamsa, true/mean nodes, house/bhava system and varga options.",
    "Main worksheet: D1 chart, D9 Navamsa, graha table and Vimshottari table.",
    "Planet table: longitude, sign, nakshatra, pada, house and retrograde flags.",
    "Strengths/Shadbala worksheets if PL exposes copyable text or a stable screenshot.",
    "Record every screenshot path and keep UI-state JSON beside it.",
    "Keep this packet draft until PL settings and visible values are reviewed by a human.",
]


def build_parashara_light_verification_packet(
    data: dict[str, Any],
    *,
    packet_id: str = "pl7-verification-packet",
    pl_ui_state: dict[str, Any] | None = None,
    pl_ui_state_path: str = "",
    screenshot_paths: list[str] | None = None,
    reviewer: str = "",
    reviewed_at: str = "",
    pl_version: str = "7.0.1",
    provider: EphemerisProvider | None = None,
) -> dict[str, Any]:
    birth_input = dict(data)
    ui_state = pl_ui_state or {}
    fixture = _fixture_payload(
        birth_input,
        ui_state,
        packet_id=packet_id,
        pl_ui_state_path=pl_ui_state_path,
        screenshot_paths=screenshot_paths or [],
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        pl_version=pl_version,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "id": packet_id,
        "status": "pl_ui_state_captured" if ui_state else "capture_pending",
        "fixture": fixture,
        "jyotish_agent_chart": build_birth_chart(birth_input, provider=provider),
        "pl_capture_checklist": PL_CAPTURE_CHECKLIST,
    }


def write_parashara_light_verification_packet(packet: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    paths = {
        "packet": target / "packet.json",
        "fixture": target / "fixture.json",
        "chart": target / "jyotish-agent-chart.json",
        "checklist": target / "pl-capture-checklist.md",
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
    paths["checklist"].write_text(render_parashara_light_capture_checklist(packet), encoding="utf-8")
    return {key: str(path) for key, path in paths.items()}


def render_parashara_light_capture_checklist(packet: dict[str, Any]) -> str:
    fixture = packet.get("fixture") if isinstance(packet.get("fixture"), dict) else {}
    metadata = fixture.get("pl_metadata") if isinstance(fixture.get("pl_metadata"), dict) else {}
    lines = [
        f"# Parashara Light Verification Packet: {packet.get('id', '')}",
        "",
        f"- status: {packet.get('status', '')}",
        f"- fixture review_status: {fixture.get('review_status', '')}",
        f"- PL version required: {metadata.get('version_required', '')}",
        f"- window title: {metadata.get('window_title', '')}",
        "",
        "## Capture Checklist",
    ]
    for item in packet.get("pl_capture_checklist", []):
        lines.append(f"- [ ] {item}")
    lines.extend(
        [
            "",
            "## Rule",
            "",
            "Do not mark this packet as verified until PL settings, screenshots and visible values are reviewed.",
        ]
    )
    return "\n".join(lines) + "\n"


def _fixture_payload(
    birth_input: dict[str, Any],
    pl_ui_state: dict[str, Any],
    *,
    packet_id: str,
    pl_ui_state_path: str,
    screenshot_paths: list[str],
    reviewer: str,
    reviewed_at: str,
    pl_version: str,
) -> dict[str, Any]:
    return {
        "id": packet_id,
        "source": "parashara_light_ui_state" if pl_ui_state else "parashara_light_capture_packet",
        "review_status": "draft",
        "notes": (
            "Capture packet for Parashara's Light black-box comparison. Keep draft until "
            "birth input, calculation settings, screenshots and visible values are reviewed."
        ),
        "input": birth_input,
        "pl_metadata": {
            "profile_status": "unverified",
            "version_required": pl_version,
            "window_title": str(pl_ui_state.get("window_title") or ""),
            "ui_state_source": pl_ui_state_path,
            "captured_at": str(pl_ui_state.get("captured_at") or ""),
            "control_count": pl_ui_state.get("control_count"),
            "screenshot_blank": pl_ui_state.get("screenshot_blank"),
            "screenshot_error": pl_ui_state.get("screenshot_error"),
            "siddhanta_model": birth_input.get("calculation_model") or "",
            "ayanamsa": birth_input.get("ayanamsa") or "",
            "node_type": birth_input.get("node_type") or "",
            "house_system": birth_input.get("house_system") or "",
            "bhava_system": birth_input.get("bhava_system") or "",
            "varga_options": birth_input.get("varga_scheme") or "",
            "timezone_source": birth_input.get("timezone_source") or "user_supplied_or_pl_ui",
            "timezone_offset": birth_input.get("timezone_offset") or "",
            "reviewer": reviewer,
            "reviewed_at": reviewed_at,
            "capture_status": "ui_state_captured" if pl_ui_state else "ui_state_pending",
        },
        "capture_files": {
            "ui_state": pl_ui_state_path,
            "screenshots": screenshot_paths,
            "fingerprints": {
                "ui_state": _file_fingerprint(pl_ui_state_path),
                "screenshots": [_file_fingerprint(path) for path in screenshot_paths],
            },
        },
        "pl_expected": _pl_expected_payload(pl_ui_state),
    }


def _pl_expected_payload(pl_ui_state: dict[str, Any]) -> dict[str, Any]:
    if not pl_ui_state:
        return {}
    return {
        "ui_state": {
            "source": pl_ui_state.get("source"),
            "backend": pl_ui_state.get("backend"),
            "window_title": pl_ui_state.get("window_title"),
            "control_count": pl_ui_state.get("control_count"),
            "class_summary": pl_ui_state.get("class_summary") or [],
            "artifact_policy": pl_ui_state.get("artifact_policy"),
            "screenshot": pl_ui_state.get("screenshot"),
            "screenshot_blank": pl_ui_state.get("screenshot_blank"),
            "screenshot_error": pl_ui_state.get("screenshot_error"),
        }
    }


def _file_fingerprint(path: str) -> dict[str, Any]:
    if not path:
        return {}
    source = Path(path)
    if not source.exists():
        return {"path": path, "missing": True}
    digest = hashlib.sha256()
    size = 0
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return {"path": path, "bytes": size, "sha256": digest.hexdigest()}
