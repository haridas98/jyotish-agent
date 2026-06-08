from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.calculations.witness_action_labels import suggested_action_labels
from apps.calculations.witness_batch import audit_jhora_pl_witness_batch
from apps.calculations.witness_powershell import ps_quote


SCHEMA_VERSION = "jyotish-witness-capture-queue-v1"
AUTO_CAPTURE_ACTION_COMMANDS = {
    "build_jhora_witness_batch_packets": (
        ".\\.venv\\Scripts\\python.exe manage.py build_jhora_witness_batch_packets --case-id {case_id}"
    ),
    "capture_jhora_witness_batch_exports_or_attach_jhora_complete_calculations": (
        ".\\.venv\\Scripts\\python.exe manage.py capture_jhora_witness_batch_exports "
        "--case-id {case_id} --skip-existing"
    ),
    "attach_pl_witness_packet_or_manual_values": (
        ".\\.venv\\Scripts\\python.exe manage.py build_parashara_light_witness_batch_packets --case-id {case_id}"
    ),
}
MANUAL_REVIEW_ACTION_COMMANDS = {
    "set_review_status_jhora_verified_after_manual_review",
    "add_reviewer_and_reviewed_at",
    "mark_jhora_witness_reviewed",
    "mark_jhora_witness_reviewed_with_ack_diff_open",
    "mark_parashara_light_witness_reviewed",
}


class Command(BaseCommand):
    help = "Build a compact JHora/Parashara Light capture queue from witness batch audit blockers."

    def add_arguments(self, parser):
        parser.add_argument(
            "--jhora-root",
            default=str(settings.ROOT_DIR / ".tmp" / "jhora"),
            help="Directory containing JHora packet/fixture artifacts.",
        )
        parser.add_argument(
            "--pl-root",
            default=str(settings.ROOT_DIR / ".tmp" / "pl7"),
            help="Directory containing Parashara Light packet/fixture artifacts.",
        )
        parser.add_argument(
            "--output",
            default=str(settings.ROOT_DIR / ".tmp" / "witness-review" / "capture-queue.json"),
            help="JSON queue output path.",
        )
        parser.add_argument(
            "--markdown-output",
            default=str(settings.ROOT_DIR / ".tmp" / "witness-review" / "capture-queue.md"),
            help="Markdown queue output path.",
        )
        parser.add_argument("--target-reviewed-count", type=int, default=20)
        parser.add_argument("--limit", type=int, default=20)
        parser.add_argument("--json", action="store_true")
        parser.add_argument("--next-only", action="store_true")

    def handle(self, *args, **options):
        payload = build_witness_capture_queue(
            jhora_root=options["jhora_root"],
            pl_root=options["pl_root"],
            output=options["output"],
            markdown_output=options["markdown_output"],
            target_reviewed_count=options["target_reviewed_count"],
            limit=options["limit"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        elif options["next_only"]:
            self.stdout.write(_next_only_summary(payload))
        else:
            self.stdout.write(_text_summary(payload))


def build_witness_capture_queue(
    *,
    jhora_root: str | Path,
    pl_root: str | Path,
    output: str | Path,
    markdown_output: str | Path = "",
    target_reviewed_count: int = 20,
    limit: int = 20,
) -> dict[str, Any]:
    audit = audit_jhora_pl_witness_batch(
        jhora_root=jhora_root,
        pl_root=pl_root,
        target_reviewed_count=target_reviewed_count,
    )
    case_rows = {str(row.get("id") or ""): row for row in audit.get("cases", []) if isinstance(row, dict)}
    items = [
        _queue_item(index + 1, _with_case_records(row, case_rows))
        for index, row in enumerate(audit["next_actions"][: max(limit, 0)])
    ]
    next_item = items[0] if items else None
    output_path = Path(output)
    markdown_path = Path(markdown_output) if str(markdown_output or "").strip() else None
    payload = {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "generated_at": timezone.now().isoformat(),
            "jhora_root": str(jhora_root),
            "pl_root": str(pl_root),
            "target_reviewed_count": target_reviewed_count,
            "limit": limit,
        },
        "summary": {
            "queue_count": len(items),
            "remaining_to_target_count": max(
                int(audit["summary"].get("target_reviewed_count") or 0)
                - int(audit["summary"].get("batch_review_ready_count") or 0),
                0,
            ),
            "batch_review_ready_count": int(audit["summary"].get("batch_review_ready_count") or 0),
            "capture_started_count": int(audit["summary"].get("capture_started_count") or 0),
            "pl_witness_count": int(audit["summary"].get("pl_witness_count") or 0),
            "output": str(output_path),
            "markdown_output": str(markdown_path or ""),
        },
        "items": items,
        "next_item": next_item,
        "next_action_key": next_item["next_action_key"] if next_item else "",
        "next_action_label": next_item["next_action_label"] if next_item else "",
        "next_command_kind": next_item["next_command_kind"] if next_item else "",
        "next_step_label": next_item["next_step_label"] if next_item else "",
        "next_command": next_item["next_command"] if next_item else "",
        "manual_review_command": next_item["manual_review_command"] if next_item else "",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    if markdown_path is not None:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(_markdown_queue(payload), encoding="utf-8")
    return payload


def _queue_item(priority: int, row: dict[str, Any]) -> dict[str, Any]:
    missing_jhora = _string_list(row.get("missing_for_authoritative_review"))
    missing_pl = _string_list(row.get("missing_secondary_witness"))
    suggested_actions = _string_list(row.get("suggested_actions"))
    action_labels = suggested_action_labels(suggested_actions)
    case_id = str(row.get("id") or "")
    next_action = suggested_actions[0] if suggested_actions else ""
    next_action_label = action_labels[0] if action_labels else ""
    auto_command = _next_auto_command(case_id, next_action)
    manual_command = _next_manual_review_command(row, next_action)
    command_kind = "auto_capture" if auto_command else "manual_review" if manual_command else "manual"
    return {
        "priority": priority,
        "id": case_id,
        "group": str(row.get("group") or ""),
        "label": str(row.get("label") or ""),
        "status": str(row.get("status") or ""),
        "capture_targets": {
            "jhora": missing_jhora,
            "parashara_light": missing_pl,
        },
        "suggested_actions": suggested_actions,
        "suggested_action_labels": action_labels,
        "next_action_key": next_action,
        "next_action_label": next_action_label,
        "next_command_kind": command_kind,
        "next_step_label": _next_step_label(command_kind),
        "next_command": auto_command,
        "manual_review_command": manual_command,
        "blocker_count": len(missing_jhora) + len(missing_pl),
    }


def _with_case_records(action: dict[str, Any], case_rows: dict[str, dict[str, Any]]) -> dict[str, Any]:
    case_row = case_rows.get(str(action.get("id") or ""), {})
    return {
        **action,
        "jhora_records": case_row.get("jhora_records", []),
        "pl_records": case_row.get("pl_records", []),
    }


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


def _next_auto_command(case_id: str, action: str) -> str:
    template = AUTO_CAPTURE_ACTION_COMMANDS.get(action)
    return template.format(case_id=ps_quote(case_id)) if template else ""


def _next_step_label(kind: str) -> str:
    if kind == "auto_capture":
        return "Run capture command"
    if kind == "manual_review":
        return "Run review preflight first"
    return "Manual capture/review"


def _next_manual_review_command(row: dict[str, Any], action: str) -> str:
    if action not in MANUAL_REVIEW_ACTION_COMMANDS:
        return ""
    jhora_path = _preferred_jhora_path(row.get("jhora_records"))
    pl_path = _preferred_pl_path(row.get("pl_records"))
    if not jhora_path and not pl_path:
        return ""
    parts = [".\\.venv\\Scripts\\python.exe", "manage.py", "preflight_witness_review"]
    if jhora_path:
        parts.extend(["--jhora", ps_quote(jhora_path)])
    if pl_path:
        parts.extend(["--parashara-light", ps_quote(pl_path)])
    parts.append("--safe-next-only")
    return " ".join(parts)


def _preferred_jhora_path(value: Any) -> str:
    return _preferred_record_path(value, required_artifacts=("complete_calculations_text", "settings_evidence", "screenshots"))


def _preferred_pl_path(value: Any) -> str:
    return _preferred_record_path(value, required_artifacts=("ui_state", "settings_evidence", "screenshots", "manual_witness_values"))


def _preferred_record_path(value: Any, *, required_artifacts: tuple[str, ...]) -> str:
    if not isinstance(value, list):
        return ""
    fallback = ""
    for row in value:
        if not isinstance(row, dict):
            continue
        path = str(row.get("path") or "").strip()
        if path:
            fallback = fallback or path
        artifacts = row.get("artifacts") if isinstance(row.get("artifacts"), dict) else {}
        if path and all(bool(artifacts.get(key)) for key in required_artifacts):
            return path
    return fallback


def _markdown_queue(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Witness Capture Queue",
        "",
        f"- Queue count: {summary['queue_count']}",
        f"- Batch review ready: {summary['batch_review_ready_count']}",
        f"- Remaining to target: {summary['remaining_to_target_count']}",
        f"- Capture started: {summary['capture_started_count']}",
        f"- PL witnesses: {summary['pl_witness_count']}",
        "",
    ]
    for item in payload["items"]:
        lines.extend(
            [
                f"## {item['priority']}. {item['id']}",
                "",
                f"- Label: {item['label']}",
                f"- Status: {item['status']}",
                f"- JHora blockers: {', '.join(item['capture_targets']['jhora']) or 'none'}",
                f"- PL blockers: {', '.join(item['capture_targets']['parashara_light']) or 'none'}",
                f"- Suggested actions: {', '.join(item.get('suggested_action_labels') or item['suggested_actions']) or 'review'}",
                f"- Next step: {item['next_step_label']}",
                f"- Next command: {item['next_command'] or 'manual review required'}",
                f"- Manual review command: {item['manual_review_command'] or 'n/a'}",
                "",
            ]
        )
    return "\n".join(lines)


def _text_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"queue: {summary['queue_count']}",
        f"remaining: {summary['remaining_to_target_count']}",
        f"json: {summary['output']}",
    ]
    if summary["markdown_output"]:
        lines.append(f"markdown: {summary['markdown_output']}")
    next_item = payload.get("next_item") if isinstance(payload.get("next_item"), dict) else {}
    if next_item.get("next_step_label"):
        lines.append(f"next step: {next_item['next_step_label']}")
    if payload["next_command"]:
        lines.append(f"next command: {payload['next_command']}")
    elif next_item.get("manual_review_command"):
        lines.append(f"manual review command: {next_item['manual_review_command']}")
    for item in payload["items"][:10]:
        actions = ", ".join(item.get("suggested_action_labels") or item["suggested_actions"]) or "review"
        lines.append(f"- {item['priority']}. {item['id']}: {actions}")
    return "\n".join(lines)


def _next_only_summary(payload: dict[str, Any]) -> str:
    next_item = payload.get("next_item") if isinstance(payload.get("next_item"), dict) else {}
    next_action = str(
        payload.get("next_action_label")
        or next_item.get("next_action_label")
        or payload.get("next_action_key")
        or next_item.get("next_action_key")
        or "review"
    )
    next_step = str(payload.get("next_step_label") or next_item.get("next_step_label") or "Manual capture/review")
    next_command = str(payload.get("next_command") or next_item.get("next_command") or "")
    manual_review_command = str(
        payload.get("manual_review_command") or next_item.get("manual_review_command") or ""
    )
    lines = [
        f"next action: {next_action}",
        f"next step: {next_step}",
    ]
    if next_command:
        lines.append(f"next command: {next_command}")
    elif manual_review_command:
        lines.append(f"manual review command: {manual_review_command}")
    else:
        lines.append("next command: manual capture/review")
    return "\n".join(lines)
