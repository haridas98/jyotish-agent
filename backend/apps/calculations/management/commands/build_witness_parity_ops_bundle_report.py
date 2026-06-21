from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.management.commands.build_witness_parity_roadmap_report import _build_summary_from_settings
from apps.calculations.witness_parity_ops_bundle import build_witness_parity_ops_bundle


class Command(BaseCommand):
    help = "Build a safe witness parity operations bundle from roadmap and gap queue aggregates."

    def add_arguments(self, parser):
        parser.add_argument("--out", default="")
        parser.add_argument("--limit", type=int, default=10)
        parser.add_argument("--state", action="append", default=[])
        parser.add_argument("--fail-if-review", action="store_true")
        parser.add_argument("--fail-if-waiting", action="store_true")
        parser.add_argument("--fail-if-high-priority", action="store_true")

    def handle(self, *args, **options):
        states = _state_filter(options.get("state") or [])
        limit = int(options.get("limit") or 0)
        summary = _build_summary_from_settings()
        full_bundle = build_witness_parity_ops_bundle(summary, limit=0)
        output_bundle = build_witness_parity_ops_bundle(summary, limit=limit, states=states)
        encoded = json.dumps(output_bundle, ensure_ascii=False, indent=2)
        out = str(options.get("out") or "").strip()
        if out:
            output_path = Path(out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        else:
            self.stdout.write(encoded)

        state_totals = full_bundle["state_totals"]
        priority_totals = full_bundle["priority_totals"]
        if options.get("fail_if_review") and state_totals["review"]:
            raise CommandError(f"parity ops bundle has {state_totals['review']} review domains")
        if options.get("fail_if_waiting") and state_totals["waiting"]:
            raise CommandError(f"parity ops bundle has {state_totals['waiting']} waiting domains")
        if options.get("fail_if_high_priority") and priority_totals["high"]:
            raise CommandError(f"parity ops bundle has {priority_totals['high']} high priority domains")


def _state_filter(values) -> set[str]:
    states: set[str] = set()
    for value in values:
        for item in str(value).split(","):
            normalized = item.strip().lower()
            if normalized in {"review", "waiting", "ready"}:
                states.add(normalized)
    return states
