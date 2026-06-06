from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_hidden_option_store import (
    build_parashara_light_hidden_option_store_report,
)


class Command(BaseCommand):
    help = "Build a private PL7 hidden option-store candidate report from settings evidence."

    def add_arguments(self, parser):
        parser.add_argument("--settings-evidence", required=True)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_hidden_option_store_report(
                settings_evidence_path=options["settings_evidence"],
            )
        except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
            raise CommandError(str(exc)) from exc

        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(
            json.dumps(
                {
                    "status": report.get("status", ""),
                    "output": str(output_path),
                    "primary_candidate": report.get("primary_candidate", {}).get("relative_path", ""),
                    "next_action": report.get("next_action", ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
