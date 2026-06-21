from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.management.commands.build_witness_parity_roadmap_report import _build_summary_from_settings
from apps.calculations.witness_parity_release_gate import build_witness_parity_release_gate


class Command(BaseCommand):
    help = "Build a safe witness parity release gate report from parity operations aggregates."

    def add_arguments(self, parser):
        parser.add_argument("--out", default="")
        parser.add_argument("--limit", type=int, default=10)
        parser.add_argument("--fail-if-blocked", action="store_true")

    def handle(self, *args, **options):
        limit = int(options.get("limit") or 0)
        summary = _build_summary_from_settings()
        full_gate = build_witness_parity_release_gate(summary, limit=0)
        output_gate = build_witness_parity_release_gate(summary, limit=limit)
        encoded = json.dumps(output_gate, ensure_ascii=False, indent=2)
        out = str(options.get("out") or "").strip()
        if out:
            output_path = Path(out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        else:
            self.stdout.write(encoded)

        if options.get("fail_if_blocked") and full_gate["status"] == "blocked":
            raise CommandError("parity release gate is blocked")
