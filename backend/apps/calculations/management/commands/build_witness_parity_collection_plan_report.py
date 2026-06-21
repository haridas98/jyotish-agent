from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.calculations.management.commands.build_witness_parity_roadmap_report import _build_summary_from_settings
from apps.calculations.witness_parity_collection_plan import build_witness_parity_collection_plan


class Command(BaseCommand):
    help = "Build the safe witness parity collection plan snapshot."

    def add_arguments(self, parser):
        parser.add_argument("--output", default="")
        parser.add_argument("--out", default="")

    def handle(self, *args, **options):
        plan = build_witness_parity_collection_plan(_build_summary_from_settings())
        encoded = json.dumps(plan, ensure_ascii=False, indent=2)
        output = str(options.get("output") or options.get("out") or "").strip()
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        else:
            self.stdout.write(encoded)
