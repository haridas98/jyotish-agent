from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.calculations.management.commands.build_witness_review_packet import (
    build_witness_review_packet,
)
from apps.calculations.witness_batch import audit_jhora_pl_witness_batch


SCHEMA_VERSION = "jyotish-witness-review-batch-packets-v1"


class Command(BaseCommand):
    help = "Build markdown review packets for JHora/Parashara Light batch cases that have both witnesses."

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
            "--output-root",
            default=str(settings.ROOT_DIR / ".tmp" / "witness-review"),
            help="Directory where markdown review packets will be written.",
        )
        parser.add_argument("--reviewer", default="Haridas")
        parser.add_argument("--reviewed-at", default="")
        parser.add_argument("--target-reviewed-count", type=int, default=20)
        parser.add_argument("--only-reviewable", action="store_true")
        parser.add_argument("--fail-if-none", action="store_true")
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        payload = build_witness_review_batch_packets(
            jhora_root=options["jhora_root"],
            pl_root=options["pl_root"],
            output_root=options["output_root"],
            reviewer=options["reviewer"],
            reviewed_at=options["reviewed_at"],
            target_reviewed_count=options["target_reviewed_count"],
            only_reviewable=options["only_reviewable"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(_text_summary(payload))

        if options["fail_if_none"] and payload["summary"]["written_count"] == 0:
            raise CommandError("No JHora/PL witness review packets were written")


def build_witness_review_batch_packets(
    *,
    jhora_root: str | Path,
    pl_root: str | Path,
    output_root: str | Path,
    reviewer: str = "Haridas",
    reviewed_at: str = "",
    target_reviewed_count: int = 20,
    only_reviewable: bool = False,
) -> dict[str, Any]:
    audit = audit_jhora_pl_witness_batch(
        jhora_root=jhora_root,
        pl_root=pl_root,
        target_reviewed_count=target_reviewed_count,
    )
    output_dir = Path(output_root)
    written: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    for row in audit["cases"]:
        case_id = str(row["id"])
        jhora_path = _first_record_path(row["jhora_records"])
        pl_path = _first_record_path(row["pl_records"])
        if not (jhora_path and pl_path):
            skipped.append({"id": case_id, "reason": "missing_jhora_or_pl_pair"})
            continue

        output_path = output_dir / f"{_safe_filename(case_id)}.md"
        try:
            packet = build_witness_review_packet(
                jhora_path=jhora_path,
                parashara_light_path=pl_path,
                reviewer=reviewer,
                reviewed_at=reviewed_at,
                output=output_path,
            )
        except Exception as exc:  # noqa: BLE001 - batch command should report bad packet inputs and continue.
            errors.append({"id": case_id, "error": str(exc)})
            continue

        overall = packet["preflight"]["overall"]
        if only_reviewable and not overall["reviewable"]:
            output_path.unlink(missing_ok=True)
            skipped.append({"id": case_id, "reason": "not_reviewable"})
            continue

        written.append(
            {
                "id": case_id,
                "output_path": str(output_path),
                "reviewable": bool(overall["reviewable"]),
                "ack_required": bool(overall["ack_required"]),
                "blocked": bool(overall["blocked"]),
            }
        )

    index_path = output_dir / "_index.md"
    index_json_path = output_dir / "_index.json"
    metadata = {
        "generated_at": timezone.now().isoformat(),
        "reviewer": reviewer,
        "reviewed_at": reviewed_at,
        "jhora_root": str(jhora_root),
        "pl_root": str(pl_root),
    }
    index_markdown = _index_markdown(
        metadata=metadata,
        written=written,
        skipped=skipped,
        errors=errors,
        audit_summary=audit["summary"],
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path.write_text(index_markdown, encoding="utf-8")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "metadata": metadata,
        "summary": {
            "written_count": len(written),
            "skipped_count": len(skipped),
            "error_count": len(errors),
            "output_root": str(output_dir),
            "index_path": str(index_path),
            "index_json_path": str(index_json_path),
        },
        "written": written,
        "skipped": skipped,
        "errors": errors,
        "audit_summary": audit["summary"],
    }
    index_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _first_record_path(records: list[dict[str, Any]]) -> str:
    if not records:
        return ""
    return str(records[0].get("path") or "")


def _safe_filename(value: str) -> str:
    safe = []
    for char in value:
        if char.isalnum() or char in "-_.":
            safe.append(char)
        else:
            safe.append("-")
    return "".join(safe).strip(".-") or "witness-review"


def _index_markdown(
    *,
    metadata: dict[str, str],
    written: list[dict[str, Any]],
    skipped: list[dict[str, str]],
    errors: list[dict[str, str]],
    audit_summary: dict[str, Any],
) -> str:
    lines = [
        "# Witness Review Batch Index",
        "",
        f"- Generated at: {metadata.get('generated_at') or ''}",
        f"- Reviewer: {metadata.get('reviewer') or ''}",
        f"- Reviewed at: {metadata.get('reviewed_at') or ''}",
        f"- JHora root: `{metadata.get('jhora_root') or ''}`",
        f"- PL root: `{metadata.get('pl_root') or ''}`",
        f"- Written: {len(written)}",
        f"- Skipped: {len(skipped)}",
        f"- Errors: {len(errors)}",
        f"- Batch review ready: {audit_summary.get('batch_review_ready_count', 0)}",
        f"- Target reviewed: {audit_summary.get('target_reviewed_count', 0)}",
        f"- Target met: {_yes_no(audit_summary.get('target_met'))}",
        "",
        "## Written Packets",
        "",
    ]
    if written:
        for row in written:
            lines.append(
                f"- `{row['id']}` - Reviewable: {_yes_no(row['reviewable'])}; "
                f"ACK: {_yes_no(row['ack_required'])}; Blocked: {_yes_no(row['blocked'])}; "
                f"File: `{row['output_path']}`"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Skipped Cases", ""])
    if skipped:
        for reason, count in _reason_counts(skipped).items():
            lines.append(f"- {reason}: {count}")
    else:
        lines.append("- none")

    if errors:
        lines.extend(["", "## Errors", ""])
        for row in errors:
            lines.append(f"- `{row['id']}`: {row['error']}")

    lines.append("")
    return "\n".join(lines)


def _reason_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        reason = row.get("reason") or "unknown"
        counts[reason] = counts.get(reason, 0) + 1
    return counts


def _yes_no(value: object) -> str:
    return "yes" if bool(value) else "no"


def _text_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"written: {summary['written_count']}",
        f"skipped: {summary['skipped_count']}",
        f"errors: {summary['error_count']}",
        f"output: {summary['output_root']}",
        f"index: {summary['index_path']}",
    ]
    for row in payload["written"]:
        lines.append(
            f"- {row['id']}: {row['output_path']} "
            f"(reviewable={row['reviewable']} ack_required={row['ack_required']} blocked={row['blocked']})"
        )
    return "\n".join(lines)
