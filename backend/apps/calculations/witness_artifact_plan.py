from __future__ import annotations

from pathlib import Path
from typing import Any


SCHEMA_VERSION = "jyotish-witness-artifact-plan-v1"


def build_witness_artifact_plan(
    *,
    case_id: str,
    jhora_root: str | Path,
    pl_root: str | Path,
    review_output_root: str | Path | None = None,
) -> dict[str, Any]:
    normalized_case_id = str(case_id)
    jhora_dir = _case_dir(Path(jhora_root), normalized_case_id)
    pl_dir = _case_dir(Path(pl_root), normalized_case_id)
    review_path = Path(review_output_root) / f"{normalized_case_id}.md" if review_output_root else None
    jhora_checks = _jhora_checks(jhora_dir)
    pl_checks = _pl_checks(pl_dir)
    jhora_missing = _missing_required_groups(jhora_checks)
    pl_missing = _missing_required_groups(pl_checks)
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": normalized_case_id,
        "missing_required_evidence_groups": sorted(set(jhora_missing) | set(pl_missing)),
        "jhora": {
            "packet_dir": str(jhora_dir),
            "checks": jhora_checks,
            "missing_required_evidence_groups": jhora_missing,
        },
        "parashara_light": {
            "packet_dir": str(pl_dir),
            "checks": pl_checks,
            "missing_required_evidence_groups": pl_missing,
        },
        "review": {
            "packet_path": str(review_path or ""),
            "exists": bool(review_path and review_path.exists()),
        },
    }


def _case_dir(root: Path, case_id: str) -> Path:
    base = root if root.name == "batch-queue" else root / "batch-queue"
    return base / case_id


def _jhora_checks(packet_dir: Path) -> list[dict[str, Any]]:
    return [
        _check(packet_dir / "packet.json", "packet_json", "jhora_packet", "build_jhora_witness_batch_packets"),
        _check(packet_dir / "fixture.json", "fixture_json", "jhora_packet", "build_jhora_witness_batch_packets"),
        _check(
            packet_dir / "jhora-complete-calculations.txt",
            "complete_calculations_text",
            "jhora_complete_calculations_text",
            "capture_jhora_witness_batch_exports_or_attach_jhora_complete_calculations",
        ),
        _check(
            packet_dir / "jhora-settings-evidence.json",
            "settings_evidence",
            "jhora_settings_evidence",
            "record_jhora_settings_and_timezone_dst_evidence",
        ),
        _screenshot_check(packet_dir / "screenshots", "jhora_screenshots", "attach_jhora_screenshots"),
    ]


def _pl_checks(packet_dir: Path) -> list[dict[str, Any]]:
    return [
        _check(packet_dir / "packet.json", "packet_json", "pl_witness_packet", "attach_pl_witness_packet_or_manual_values"),
        _check(packet_dir / "fixture.json", "fixture_json", "pl_witness_packet", "attach_pl_witness_packet_or_manual_values"),
        _check(
            packet_dir / "manual-values-template.json",
            "manual_values_template",
            "manual_values_template",
            "attach_pl_witness_packet_or_manual_values",
            required_for_review=False,
        ),
        _check(
            packet_dir / "manual-witness-values.json",
            "manual_witness_values",
            "manual_witness_values",
            "attach_pl_witness_packet_or_manual_values",
        ),
        _check(
            packet_dir / "pl-ui-state.json",
            "ui_state",
            "pl_ui_state",
            "capture_parashara_light_ui_state_or_attach_ui_state",
        ),
        _check(
            packet_dir / "pl-settings-evidence.json",
            "settings_evidence",
            "pl_settings_evidence",
            "record_pl_settings_and_timezone_dst_evidence",
        ),
        _screenshot_check(packet_dir / "screenshots", "pl_screenshots", "attach_pl_screenshots"),
    ]


def _check(
    path: Path,
    name: str,
    evidence_group: str,
    next_action_key: str,
    *,
    required_for_review: bool = True,
) -> dict[str, Any]:
    return {
        "name": name,
        "path": str(path),
        "exists": path.exists(),
        "required_for_review": required_for_review,
        "evidence_group": evidence_group,
        "next_action_key": next_action_key,
    }


def _screenshot_check(path: Path, evidence_group: str, next_action_key: str) -> dict[str, Any]:
    files = _screenshot_files(path)
    return {
        "name": "screenshots",
        "path": str(path),
        "exists": bool(files),
        "files": files,
        "required_for_review": True,
        "evidence_group": evidence_group,
        "next_action_key": next_action_key,
    }


def _screenshot_files(path: Path) -> list[str]:
    if not path.is_dir():
        return []
    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    return [
        str(item)
        for item in sorted(path.iterdir(), key=lambda candidate: candidate.name.lower())
        if item.is_file() and item.suffix.lower() in allowed
    ]


def _missing_required_groups(checks: list[dict[str, Any]]) -> list[str]:
    groups = {
        str(item["evidence_group"])
        for item in checks
        if item.get("required_for_review") and not item.get("exists")
    }
    return sorted(groups)
