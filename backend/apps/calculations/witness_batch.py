from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from .jhora_parity_suite import jhora_parity_suite_manifest
from .witness_action_labels import suggested_action_labels
from .witness_contract import build_witness_contract, summarize_witness_contracts

SCHEMA_VERSION = "jyotish-witness-batch-audit-v1"
DEFAULT_TARGET_REVIEWED_COUNT = 20
PL_REVIEW_STATUSES = {"approved", "reviewed"}
ACTION_BY_MISSING_ARTIFACT = {
    "jhora_packet": "build_jhora_witness_batch_packets",
    "jhora_complete_calculations_text": "capture_jhora_witness_batch_exports_or_attach_jhora_complete_calculations",
    "jhora_settings_evidence": "record_jhora_settings_and_timezone_dst_evidence",
    "jhora_screenshots": "attach_jhora_screenshots",
    "reviewer_note": "add_reviewer_and_reviewed_at",
    "reviewer": "add_reviewer_and_reviewed_at",
    "reviewed_at": "add_reviewer_and_reviewed_at",
    "authoritative_review_status": "set_review_status_jhora_verified_after_manual_review",
    "expected_or_jhora_expected": "capture_jhora_expected_values_or_complete_calculations",
    "accuracy_status_checked": "mark_jhora_witness_reviewed",
    "accuracy_diff_acknowledgement": "mark_jhora_witness_reviewed_with_ack_diff_open",
    "pl_witness_packet": "attach_pl_witness_packet_or_manual_values",
    "pl_ui_state": "capture_parashara_light_ui_state_or_attach_ui_state",
    "pl_settings_evidence": "record_pl_settings_and_timezone_dst_evidence",
    "pl_screenshots": "attach_pl_screenshots",
    "manual_witness_values": "fill_pl_manual_witness_values",
    "pl_reviewer_note": "mark_parashara_light_witness_reviewed",
    "pl_review_status": "mark_parashara_light_witness_reviewed",
}


def audit_jhora_pl_witness_batch(
    *,
    jhora_root: str | Path,
    pl_root: str | Path = "",
    target_reviewed_count: int = DEFAULT_TARGET_REVIEWED_COUNT,
    include_review_preflight: bool = False,
) -> dict[str, Any]:
    manifest = jhora_parity_suite_manifest()
    load_errors: list[dict[str, str]] = []
    jhora_records = _scan_fixture_records(Path(jhora_root), "jhora", load_errors)
    pl_records = _scan_fixture_records(Path(pl_root), "parashara_light", load_errors) if pl_root else []

    jhora_by_id, jhora_by_birth = _record_indexes(jhora_records)
    pl_by_id, pl_by_birth = _record_indexes(pl_records)
    case_rows = []

    for case in manifest["cases"]:
        case_id = str(case["id"])
        birth_key = _birth_key(case.get("input", {}))
        case_jhora_records = _unique_records([*jhora_by_id.get(case_id, []), *jhora_by_birth.get(birth_key, [])])
        case_pl_records = _unique_records([*pl_by_id.get(case_id, []), *pl_by_birth.get(birth_key, [])])
        case_rows.append(_case_row(case, case_jhora_records, case_pl_records))

    summary = _summary(case_rows, target_reviewed_count, manifest["case_count"], load_errors)
    return {
        "schema_version": SCHEMA_VERSION,
        "target_reviewed_count": target_reviewed_count,
        "suite_case_count": manifest["case_count"],
        "summary": summary,
        "groups": _group_summary(case_rows),
        "next_actions": _next_actions(
            case_rows,
            max(target_reviewed_count - summary["batch_review_ready_count"], 0),
            include_review_preflight=include_review_preflight,
        ),
        "cases": case_rows,
        "load_errors": load_errors,
    }


def _scan_fixture_records(root: Path, source: str, load_errors: list[dict[str, str]]) -> list[dict[str, Any]]:
    if not root or not root.exists():
        return []

    records: list[dict[str, Any]] = []
    seen_dirs: set[Path] = set()
    candidate_paths = [*sorted(root.rglob("packet.json")), *sorted(root.rglob("fixture.json"))]
    for path in candidate_paths:
        if path.name == "fixture.json" and path.parent in seen_dirs:
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            load_errors.append({"path": str(path), "error": str(exc)})
            continue

        fixture = raw.get("fixture") if isinstance(raw, dict) and isinstance(raw.get("fixture"), dict) else raw
        if not isinstance(fixture, dict):
            load_errors.append({"path": str(path), "error": "fixture JSON must be an object"})
            continue
        record = _fixture_record(fixture, source, path)
        if not record["id"] and not record["birth_key"]:
            continue
        records.append(record)
        seen_dirs.add(path.parent)
    return records


def _fixture_record(fixture: dict[str, Any], source: str, path: Path) -> dict[str, Any]:
    input_data = fixture.get("input") if isinstance(fixture.get("input"), dict) else {}
    metadata = _metadata(fixture, source)
    capture_files = fixture.get("capture_files") if isinstance(fixture.get("capture_files"), dict) else {}
    artifacts = _artifact_flags(fixture, metadata, capture_files, source)
    promotion_blockers = _promotion_blockers(fixture, source)
    diff_status = _diff_status(fixture, metadata, promotion_blockers)
    return {
        "id": str(fixture.get("id") or ""),
        "source": source,
        "path": str(path),
        "review_status": str(fixture.get("review_status") or "draft"),
        "birth_key": _birth_key(input_data),
        "capture_status": str(metadata.get("capture_status") or ""),
        "reviewer": str(metadata.get("reviewer") or ""),
        "reviewed_at": str(metadata.get("reviewed_at") or ""),
        "artifacts": artifacts,
        "promotion_blockers": promotion_blockers,
        "witness_contract": build_witness_contract(fixture, source_type=source, diff_status=diff_status),
    }


def _metadata(fixture: dict[str, Any], source: str) -> dict[str, Any]:
    if source == "jhora":
        value = fixture.get("jhora_metadata")
    else:
        value = fixture.get("pl_metadata")
    return value if isinstance(value, dict) else {}


def _artifact_flags(
    fixture: dict[str, Any],
    metadata: dict[str, Any],
    capture_files: dict[str, Any],
    source: str,
) -> dict[str, bool]:
    screenshots = capture_files.get("screenshots")
    screenshot_declared = isinstance(screenshots, list) and any(str(item).strip() for item in screenshots)
    reviewer_note = bool(str(metadata.get("reviewer") or "").strip() and str(metadata.get("reviewed_at") or "").strip())

    if source == "jhora":
        return {
            "complete_calculations_text": bool(
                str(capture_files.get("complete_calculations_text") or "").strip()
                or metadata.get("capture_status") == "export_parsed"
                or fixture.get("jhora_expected")
            ),
            "settings_evidence": any(
                str(metadata.get(key) or "").strip()
                for key in ("siddhanta_model", "ayanamsa", "timezone_offset", "house_system", "node_type")
            ),
            "screenshots": screenshot_declared,
            "reviewer_note": reviewer_note,
        }

    return {
        "ui_state": bool(str(capture_files.get("ui_state") or "").strip() or metadata.get("capture_status")),
        "settings_evidence": any(
            str(metadata.get(key) or "").strip()
            for key in ("siddhanta_model", "ayanamsa", "timezone_offset", "house_system", "node_type")
        ),
        "screenshots": screenshot_declared,
        "manual_witness_values": bool(
            str(capture_files.get("manual_witness_values") or "").strip()
            or str(fixture.get("manual_witness_source") or "").strip()
            or (
                isinstance(fixture.get("manual_witness_values"), list)
                and any(isinstance(item, dict) for item in fixture["manual_witness_values"])
            )
        ),
        "reviewer_note": reviewer_note,
    }


def _case_row(case: dict[str, Any], jhora_records: list[dict[str, Any]], pl_records: list[dict[str, Any]]) -> dict[str, Any]:
    missing_for_review = _missing_for_authoritative_review(jhora_records)
    authoritative_ready = any(not record["promotion_blockers"] for record in jhora_records)
    missing_secondary_witness = _missing_for_secondary_review(pl_records)
    secondary_witness_ready = bool(pl_records) and not missing_secondary_witness
    batch_review_ready = authoritative_ready and secondary_witness_ready
    capture_started = bool(jhora_records or pl_records)
    if batch_review_ready:
        status = "batch_review_ready"
    elif authoritative_ready:
        status = "authoritative_ready"
    elif jhora_records:
        status = "jhora_review_pending"
    elif pl_records:
        status = "pl_only"
    else:
        status = "missing"

    return {
        "id": str(case["id"]),
        "group": str(case["group"]),
        "label": str(case["label"]),
        "focus": list(case.get("focus", [])),
        "status": status,
        "capture_started": capture_started,
        "authoritative_ready": authoritative_ready,
        "secondary_witness_ready": secondary_witness_ready,
        "batch_review_ready": batch_review_ready,
        "missing_for_authoritative_review": missing_for_review,
        "missing_secondary_witness": missing_secondary_witness,
        "jhora_records": [_public_record(record) for record in jhora_records],
        "pl_records": [_public_record(record) for record in pl_records],
        "witness_contract": summarize_witness_contracts(
            [record["witness_contract"] for record in [*jhora_records, *pl_records]]
        ),
    }


def _missing_for_authoritative_review(jhora_records: list[dict[str, Any]]) -> list[str]:
    if not jhora_records:
        return ["jhora_packet", "jhora_complete_calculations_text", "jhora_settings_evidence", "jhora_screenshots", "reviewer_note"]

    if any(not record["promotion_blockers"] for record in jhora_records):
        return []

    promotion_blockers = _dedupe(
        [blocker for record in jhora_records for blocker in record.get("promotion_blockers", [])]
    )
    if promotion_blockers:
        return promotion_blockers

    artifacts = defaultdict(bool)
    for record in jhora_records:
        for key, value in record["artifacts"].items():
            artifacts[key] = artifacts[key] or bool(value)

    missing = []
    for key, label in (
        ("complete_calculations_text", "jhora_complete_calculations_text"),
        ("settings_evidence", "jhora_settings_evidence"),
        ("screenshots", "jhora_screenshots"),
        ("reviewer_note", "reviewer_note"),
    ):
        if not artifacts[key]:
            missing.append(label)
    if not any(record["review_status"] in AUTHORITATIVE_REVIEW_STATUSES for record in jhora_records):
        missing.append("authoritative_review_status")
    return missing


def _missing_for_secondary_review(pl_records: list[dict[str, Any]]) -> list[str]:
    if not pl_records:
        return ["pl_witness_packet"]

    artifacts = defaultdict(bool)
    for record in pl_records:
        for key, value in record["artifacts"].items():
            artifacts[key] = artifacts[key] or bool(value)

    missing = []
    for key, label in (
        ("ui_state", "pl_ui_state"),
        ("settings_evidence", "pl_settings_evidence"),
        ("screenshots", "pl_screenshots"),
        ("manual_witness_values", "manual_witness_values"),
        ("reviewer_note", "pl_reviewer_note"),
    ):
        if not artifacts[key]:
            missing.append(label)
    if not any(record["review_status"] in PL_REVIEW_STATUSES for record in pl_records):
        missing.append("pl_review_status")
    return missing


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": record["source"],
        "path": record["path"],
        "review_status": record["review_status"],
        "capture_status": record["capture_status"],
        "artifacts": record["artifacts"],
        "promotion_blockers": record.get("promotion_blockers", []),
        "witness_contract": record["witness_contract"],
    }


def _promotion_blockers(fixture: dict[str, Any], source: str) -> list[str]:
    if source != "jhora":
        return []
    from apps.calculations.management.commands.promote_jhora_witness_fixture import promotion_blockers

    try:
        blockers, _status = promotion_blockers(fixture)
    except Exception as exc:  # noqa: BLE001 - batch audit should expose bad captures instead of crashing.
        return [f"promotion_gate_error:{exc}"]
    return blockers


def _diff_status(fixture: dict[str, Any], metadata: dict[str, Any], promotion_blockers: list[str]) -> str:
    status = str(metadata.get("accuracy_status") or metadata.get("manual_diff_status") or "")
    if status:
        return status
    if "accuracy_diff_acknowledgement" in promotion_blockers:
        return "diff_open"
    return ""


def _summary(
    case_rows: list[dict[str, Any]],
    target_reviewed_count: int,
    suite_case_count: int,
    load_errors: list[dict[str, str]],
) -> dict[str, Any]:
    authoritative_ready_count = sum(1 for row in case_rows if row["authoritative_ready"])
    batch_review_ready_count = sum(1 for row in case_rows if row["batch_review_ready"])
    capture_started_count = sum(1 for row in case_rows if row["capture_started"])
    return {
        "suite_case_count": suite_case_count,
        "target_reviewed_count": target_reviewed_count,
        "authoritative_ready_count": authoritative_ready_count,
        "secondary_witness_ready_count": sum(1 for row in case_rows if row["secondary_witness_ready"]),
        "batch_review_ready_count": batch_review_ready_count,
        "capture_started_count": capture_started_count,
        "missing_count": sum(1 for row in case_rows if row["status"] == "missing"),
        "pl_witness_count": sum(1 for row in case_rows if row["pl_records"]),
        "pl_reviewed_count": sum(
            1
            for row in case_rows
            if any(record["review_status"] in PL_REVIEW_STATUSES for record in row["pl_records"])
        ),
        "load_error_count": len(load_errors),
        "target_met": batch_review_ready_count >= target_reviewed_count,
        "next_case_ids": [
            row["id"]
            for row in case_rows
            if not row["batch_review_ready"]
        ][: max(target_reviewed_count - batch_review_ready_count, 0)],
    }


def _next_actions(
    case_rows: list[dict[str, Any]],
    limit: int,
    *,
    include_review_preflight: bool = False,
) -> list[dict[str, Any]]:
    actions = []
    for row in case_rows:
        if row["batch_review_ready"]:
            continue
        suggested_actions = _suggested_actions(row)
        action = {
            "id": row["id"],
            "group": row["group"],
            "label": row["label"],
            "status": row["status"],
            "batch_review_ready": row["batch_review_ready"],
            "missing_for_authoritative_review": row["missing_for_authoritative_review"],
            "missing_secondary_witness": row["missing_secondary_witness"],
            "suggested_actions": suggested_actions,
            "suggested_action_labels": suggested_action_labels(suggested_actions),
        }
        if include_review_preflight:
            action["review_preflight"] = _review_preflight(row)
        actions.append(action)
        if len(actions) >= limit:
            break
    return actions


def _review_preflight(row: dict[str, Any]) -> dict[str, Any]:
    from apps.calculations.management.commands.preflight_witness_review import build_witness_review_preflight

    jhora_path = _first_record_path(row["jhora_records"])
    pl_path = _first_record_path(row["pl_records"])
    try:
        return build_witness_review_preflight(jhora_path=jhora_path, parashara_light_path=pl_path)
    except Exception as exc:  # noqa: BLE001 - audit must report preflight blockers without hiding the queue.
        return {
            "schema_version": "jyotish-witness-review-preflight-v1",
            "overall": {"reviewable": False, "ack_required": False, "blocked": True},
            "error": str(exc),
        }


def _first_record_path(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    return str(records[0].get("path") or "")


def _suggested_actions(row: dict[str, Any]) -> list[str]:
    actions = []
    for missing in [*row["missing_for_authoritative_review"], *row["missing_secondary_witness"]]:
        action = ACTION_BY_MISSING_ARTIFACT.get(missing)
        if action and action not in actions:
            actions.append(action)
    return actions


def _group_summary(case_rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    groups: dict[str, dict[str, int]] = {}
    for row in case_rows:
        group = row["group"]
        if group not in groups:
            groups[group] = {
                "total": 0,
                "authoritative_ready": 0,
                "secondary_witness_ready": 0,
                "batch_review_ready": 0,
                "capture_started": 0,
                "pl_witness": 0,
                "pl_reviewed": 0,
            }
        groups[group]["total"] += 1
        groups[group]["authoritative_ready"] += int(bool(row["authoritative_ready"]))
        groups[group]["secondary_witness_ready"] += int(bool(row["secondary_witness_ready"]))
        groups[group]["batch_review_ready"] += int(bool(row["batch_review_ready"]))
        groups[group]["capture_started"] += int(bool(row["capture_started"]))
        groups[group]["pl_witness"] += int(bool(row["pl_records"]))
        groups[group]["pl_reviewed"] += int(
            any(record["review_status"] in PL_REVIEW_STATUSES for record in row["pl_records"])
        )
    return groups


def _record_indexes(records: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    by_id: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_birth: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record["id"]:
            by_id[record["id"]].append(record)
        if record["birth_key"]:
            by_birth[record["birth_key"]].append(record)
    return by_id, by_birth


def _unique_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for record in records:
        key = record["path"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def _dedupe(values: list[str]) -> list[str]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def _birth_key(input_data: Any) -> str:
    if not isinstance(input_data, dict):
        return ""
    date = str(input_data.get("birth_date") or "").strip()
    time = str(input_data.get("birth_time") or "").strip()
    place = str(input_data.get("place_name") or "").strip().casefold()
    if len(time) == 5:
        time = f"{time}:00"
    if not (date and time and place):
        return ""
    return "|".join([date, time, place])
