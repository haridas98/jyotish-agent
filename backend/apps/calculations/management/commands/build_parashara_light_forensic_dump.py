from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_forensic import build_parashara_light_forensic_dump


class Command(BaseCommand):
    help = "Build a PL screenshot witness vs direct Swiss Lahiri forensic dump."

    def add_arguments(self, parser):
        parser.add_argument("--packet", required=True)
        parser.add_argument("--manual-witness-values", required=True)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_forensic_dump(
                options["packet"],
                options["manual_witness_values"],
            )
        except (FileNotFoundError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
            raise CommandError(str(exc)) from exc

        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(
            json.dumps(
                {
                    "status": "written",
                    "output": str(output_path),
                    "conclusion": report["summary"]["conclusion"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
