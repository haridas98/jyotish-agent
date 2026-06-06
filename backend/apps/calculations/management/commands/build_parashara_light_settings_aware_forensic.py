from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_settings_aware_forensic import (
    build_parashara_light_settings_aware_forensic,
)


class Command(BaseCommand):
    help = "Build a private PL settings-aware forensic summary."

    def add_arguments(self, parser):
        parser.add_argument("--forensic-report", required=True)
        parser.add_argument("--calculation-options-report", required=True)
        parser.add_argument("--profile-report", required=True)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_settings_aware_forensic(
                forensic_report_path=options["forensic_report"],
                calculation_options_report_path=options["calculation_options_report"],
                profile_report_path=options["profile_report"],
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
                    "next_action": report.get("next_action", ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
