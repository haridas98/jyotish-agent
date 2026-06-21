from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.management.commands.build_witness_parity_roadmap_report import _build_summary_from_settings
from apps.calculations.witness_parity_gap_queue import build_witness_parity_gap_queue
from apps.calculations.witness_parity_roadmap import build_witness_parity_roadmap


class Command(BaseCommand):
    help = "Build a safe prioritized witness parity gap queue from the parity roadmap."

    def add_arguments(self, parser):
        parser.add_argument("--out", default="")
        parser.add_argument("--limit", type=int, default=0)
        parser.add_argument("--state", action="append", default=[])
        parser.add_argument("--fail-if-review", action="store_true")
        parser.add_argument("--fail-if-waiting", action="store_true")

    def handle(self, *args, **options):
        roadmap = build_witness_parity_roadmap(_build_summary_from_settings())
        report = build_witness_parity_gap_queue(roadmap)
        output_report = _filtered_report(report, options)
        encoded = json.dumps(output_report, ensure_ascii=False, indent=2)
        out = str(options.get("out") or "").strip()
        if out:
            output_path = Path(out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        else:
            self.stdout.write(encoded)

        totals = report["totals"]
        if options.get("fail_if_review") and totals["review_count"]:
            raise CommandError(f"parity gap queue has {totals['review_count']} review domains")
        if options.get("fail_if_waiting") and totals["waiting_count"]:
            raise CommandError(f"parity gap queue has {totals['waiting_count']} waiting domains")


def _filtered_report(report, options):
    states = _state_filter(options.get("state") or [])
    rows = [row for row in report["queue"] if not states or row["state"] in states]
    limit = int(options.get("limit") or 0)
    if limit > 0:
        rows = rows[:limit]
    return {
        **report,
        "queue": rows,
    }


def _state_filter(values) -> set[str]:
    states: set[str] = set()
    for value in values:
        for item in str(value).split(","):
            normalized = item.strip().lower()
            if normalized in {"review", "waiting", "ready"}:
                states.add(normalized)
    return states
