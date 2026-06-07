from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.calculations.witness_batch import audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-witness-capture-queue-v1"


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
    items = [_queue_item(index + 1, row) for index, row in enumerate(audit["next_actions"][: max(limit, 0)])]
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
    return {
        "priority": priority,
        "id": str(row.get("id") or ""),
        "group": str(row.get("group") or ""),
        "label": str(row.get("label") or ""),
        "status": str(row.get("status") or ""),
        "capture_targets": {
            "jhora": missing_jhora,
            "parashara_light": missing_pl,
        },
        "suggested_actions": _string_list(row.get("suggested_actions")),
        "blocker_count": len(missing_jhora) + len(missing_pl),
    }


def _string_list(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, list) else []


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
                f"- Suggested actions: {', '.join(item['suggested_actions']) or 'review'}",
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
    for item in payload["items"][:10]:
        lines.append(f"- {item['priority']}. {item['id']}: {', '.join(item['suggested_actions']) or 'review'}")
    return "\n".join(lines)
