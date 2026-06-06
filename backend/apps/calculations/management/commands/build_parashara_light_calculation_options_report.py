from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_calculation_options_report import (
    build_parashara_light_calculation_options_report,
)


class Command(BaseCommand):
    help = "Build a private PL7 calculation options report from UI-state JSON and screenshot."

    def add_arguments(self, parser):
        parser.add_argument("--id", default="pl7-calculation-options")
        parser.add_argument("--ui-state", required=True)
        parser.add_argument("--screenshot", required=True)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_calculation_options_report(
                capture_id=options["id"],
                ui_state_path=options["ui_state"],
                screenshot_path=options["screenshot"],
            )
        except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
            raise CommandError(str(exc)) from exc

        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(
            json.dumps(
                {
                    "status": report.get("status", "written"),
                    "output": str(output_path),
                    "selected_ayanamsha": report.get("selected_ayanamsha", {}).get("label", ""),
                    "selected_calculation_method": report.get("selected_calculation_method", {}).get("label", ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
