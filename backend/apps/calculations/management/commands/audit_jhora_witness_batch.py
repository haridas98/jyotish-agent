from __future__ import annotations

import json

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.calculations.witness_batch import audit_jhora_pl_witness_batch


class Command(BaseCommand):
    help = "Audit the 20-chart JHora/Parashara Light witness batch status."

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
        parser.add_argument("--target-reviewed-count", type=int, default=20)
        parser.add_argument("--json", action="store_true")
        parser.add_argument("--fail-if-target-missing", action="store_true")

    def handle(self, *args, **options):
        payload = audit_jhora_pl_witness_batch(
            jhora_root=options["jhora_root"],
            pl_root=options["pl_root"],
            target_reviewed_count=options["target_reviewed_count"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(_text_summary(payload))

        if options["fail_if_target_missing"] and not payload["summary"]["target_met"]:
            raise CommandError("JHora/PL witness target is not met")


def _text_summary(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        f"suite cases: {summary['suite_case_count']}",
        f"target reviewed: {summary['target_reviewed_count']}",
        f"authoritative ready: {summary['authoritative_ready_count']}",
        f"PL reviewed: {summary['pl_reviewed_count']}",
        f"batch review ready: {summary['batch_review_ready_count']}",
        f"capture started: {summary['capture_started_count']}",
        f"PL witnesses: {summary['pl_witness_count']}",
        f"target met: {summary['target_met']}",
    ]
    if summary["next_case_ids"]:
        lines.append("next cases:")
        lines.extend(f"- {case_id}" for case_id in summary["next_case_ids"][:20])
    if payload["next_actions"]:
        lines.append("next actions:")
        for item in payload["next_actions"][:20]:
            actions = ", ".join(item["suggested_actions"]) or "none"
            lines.append(f"- {item['id']}: {actions}")
    return "\n".join(lines)
