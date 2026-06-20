from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONTRACT_SCHEMA_VERSION = "jyotish-witness-contract-v1"
SUMMARY_SCHEMA_VERSION = "jyotish-witness-contract-summary-v1"
ALLOWED_UNIFIED_STATUSES = {"draft", "reviewed", "promoted", "diff_open"}
SOURCE_TYPES = {"jhora", "parashara_light"}


def build_witness_contract(
    fixture: dict[str, Any],
    *,
    source_type: str,
    diff_status: str = "",
) -> dict[str, Any]:
    source = normalize_source_type(source_type)
    metadata = _metadata(fixture, source)
    input_data = fixture.get("input") if isinstance(fixture.get("input"), dict) else {}
    capture_files = fixture.get("capture_files") if isinstance(fixture.get("capture_files"), dict) else {}
    raw_status = str(fixture.get("review_status") or metadata.get("review_status") or "draft")
    effective_diff_status = str(diff_status or metadata.get("accuracy_status") or metadata.get("manual_diff_status") or "")
    has_open_diffs = effective_diff_status == "diff_open"
    evidence = {
        "birth_data": _has_birth_data(input_data, metadata),
        "timezone_dst_evidence": _has_timezone_dst_evidence(input_data, metadata),
        "settings_evidence": _has_settings_evidence(input_data, metadata),
        "artifacts": _has_artifacts(fixture, metadata, capture_files, source),
        "review": _has_review(metadata),
        "diffs": effective_diff_status in {"matched", "diff_open"},
    }
    missing = [group for group, present in evidence.items() if not present]
    return {
        "schema_version": CONTRACT_SCHEMA_VERSION,
        "source_type": source,
        "raw_status": raw_status,
        "unified_status": normalize_witness_status(source, raw_status, diff_status=effective_diff_status),
        "has_open_diffs": has_open_diffs,
        "evidence_groups": evidence,
        "missing_evidence_groups": missing,
    }


def witness_contract_from_path(path: str | Path, *, source_type: str, diff_status: str = "") -> dict[str, Any] | None:
    source = Path(path)
    if not str(path or "").strip():
        return None
    try:
        packet_path, fixture_path = _resolve_paths(source)
        packet = _read_json(packet_path) if packet_path.exists() else {}
        fixture = _read_json(fixture_path) if fixture_path.exists() else _packet_fixture(packet)
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(fixture, dict) or not fixture:
        return None
    return build_witness_contract(fixture, source_type=source_type, diff_status=diff_status)


def normalize_source_type(value: str) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    if normalized in {"pl", "pl7", "parashara_light"}:
        return "parashara_light"
    if normalized == "jhora":
        return "jhora"
    return normalized


def normalize_witness_status(source_type: str, raw_status: str, *, diff_status: str = "") -> str:
    if str(diff_status or "").strip().lower() == "diff_open":
        return "diff_open"
    source = normalize_source_type(source_type)
    raw = str(raw_status or "draft").strip().lower()
    if raw == "diff_open":
        return "diff_open"
    if source == "jhora" and raw in {"jhora_verified", "approved", "promoted"}:
        return "promoted"
    if raw in {"reviewed", "approved"}:
        return "reviewed"
    return "draft"


def summarize_witness_contracts(contracts: list[dict[str, Any]]) -> dict[str, Any]:
    valid_contracts = [contract for contract in contracts if isinstance(contract, dict)]
    source_counts = {source: 0 for source in sorted(SOURCE_TYPES)}
    status_counts = {status: 0 for status in sorted(ALLOWED_UNIFIED_STATUSES)}
    sources: dict[str, dict[str, Any]] = {}
    missing_groups: list[str] = []
    for contract in valid_contracts:
        source = normalize_source_type(str(contract.get("source_type") or ""))
        status = str(contract.get("unified_status") or "draft")
        if source in source_counts:
            source_counts[source] += 1
        if status in status_counts:
            status_counts[status] += 1
        missing = [str(group) for group in contract.get("missing_evidence_groups", [])]
        for group in missing:
            if group not in missing_groups:
                missing_groups.append(group)
        sources[source] = {
            "source_type": source,
            "unified_status": status,
            "has_open_diffs": bool(contract.get("has_open_diffs")),
            "missing_evidence_groups": missing,
        }
    if not valid_contracts:
        missing_groups = ["birth_data"]
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "source_counts": source_counts,
        "status_counts": status_counts,
        "next_missing_evidence_groups": missing_groups,
        "sources": sources,
    }


def _metadata(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    key = "jhora_metadata" if source == "jhora" else "pl_metadata"
    value = fixture.get(key)
    return value if isinstance(value, dict) else {}


def _has_birth_data(input_data: dict[str, Any], metadata: dict[str, Any]) -> bool:
    return all(str(input_data.get(key) or "").strip() for key in ("birth_date", "birth_time", "place_name")) and bool(
        str(input_data.get("timezone") or input_data.get("timezone_offset") or metadata.get("timezone_offset") or "").strip()
    )


def _has_timezone_dst_evidence(input_data: dict[str, Any], metadata: dict[str, Any]) -> bool:
    return bool(
        str(
            input_data.get("timezone")
            or input_data.get("timezone_offset")
            or metadata.get("timezone")
            or metadata.get("timezone_offset")
            or metadata.get("timezone_source")
            or metadata.get("dst_note")
            or metadata.get("dst_source_note")
            or ""
        ).strip()
    )


def _has_settings_evidence(input_data: dict[str, Any], metadata: dict[str, Any]) -> bool:
    keys = (
        "ayanamsa",
        "node_type",
        "house_system",
        "siddhanta_model",
        "calculation_model",
        "varga_scheme",
        "ephemeris",
    )
    return any(str(metadata.get(key) or input_data.get(key) or "").strip() for key in keys)


def _has_artifacts(
    fixture: dict[str, Any],
    metadata: dict[str, Any],
    capture_files: dict[str, Any],
    source: str,
) -> bool:
    screenshots = capture_files.get("screenshots")
    has_screenshot = isinstance(screenshots, list) and any(str(item).strip() for item in screenshots)
    if source == "jhora":
        has_export = bool(
            str(capture_files.get("complete_calculations_text") or "").strip()
            or str(capture_files.get("copied_text") or "").strip()
            or metadata.get("capture_status") == "export_parsed"
            or fixture.get("jhora_expected")
            or fixture.get("expected")
        )
        return has_export and has_screenshot
    has_ui_state = bool(str(capture_files.get("ui_state") or "").strip() or metadata.get("capture_status"))
    has_values = bool(
        str(capture_files.get("manual_witness_values") or "").strip()
        or str(fixture.get("manual_witness_source") or "").strip()
        or (isinstance(fixture.get("manual_witness_values"), list) and bool(fixture.get("manual_witness_values")))
    )
    return has_ui_state and has_screenshot and has_values


def _has_review(metadata: dict[str, Any]) -> bool:
    return bool(str(metadata.get("reviewer") or "").strip() and str(metadata.get("reviewed_at") or "").strip())


def _resolve_paths(path: Path) -> tuple[Path, Path]:
    if path.name == "packet.json":
        return path, path.with_name("fixture.json")
    if path.name == "fixture.json":
        return path.with_name("packet.json"), path
    return path / "packet.json", path / "fixture.json"


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    return data if isinstance(data, dict) else {}


def _packet_fixture(packet: dict[str, Any]) -> dict[str, Any]:
    fixture = packet.get("fixture") if isinstance(packet.get("fixture"), dict) else {}
    return fixture
