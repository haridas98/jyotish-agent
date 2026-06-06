from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .manual_witness_comparison import compare_manual_witness_values


def load_parashara_light_packet_report(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    packet = json.loads(source.read_text(encoding="utf-8-sig"))
    fixture = packet.get("fixture") if isinstance(packet.get("fixture"), dict) else {}
    metadata = fixture.get("pl_metadata") if isinstance(fixture.get("pl_metadata"), dict) else {}
    capture_files = fixture.get("capture_files") if isinstance(fixture.get("capture_files"), dict) else {}
    chart = packet.get("jyotish_agent_chart") if isinstance(packet.get("jyotish_agent_chart"), dict) else {}
    ascendant = chart.get("ascendant") if isinstance(chart.get("ascendant"), dict) else {}
    manual_values = fixture.get("manual_witness_values")
    if not isinstance(manual_values, list):
        manual_values = []
    manual_witness_comparison = compare_manual_witness_values(chart, manual_values)

    summary = {
        "review_status": fixture.get("review_status", ""),
        "capture_status": metadata.get("capture_status", ""),
        "version_required": metadata.get("version_required", ""),
        "window_title": metadata.get("window_title", ""),
        "control_count": metadata.get("control_count"),
        "screenshot_blank": metadata.get("screenshot_blank"),
        "screenshot_error": metadata.get("screenshot_error"),
        "screenshots_count": len(capture_files.get("screenshots") or []),
        "fingerprints": capture_files.get("fingerprints") or {},
        "jyotish_agent_lagna": ascendant.get("rashi", ""),
        "manual_values_count": manual_witness_comparison["summary"]["manual_values_count"],
        "manual_failed_count": manual_witness_comparison["summary"]["failed_count"],
    }
    return {
        "schema_version": packet.get("schema_version", ""),
        "id": packet.get("id", ""),
        "status": packet.get("status", ""),
        "summary": summary,
        "manual_witness_comparison": manual_witness_comparison,
        "checklist_count": len(packet.get("pl_capture_checklist") or []),
        "source_packet": str(source),
    }
