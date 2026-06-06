from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_visible_settings_capture import (
    build_parashara_light_visible_settings_capture,
)


class Command(BaseCommand):
    help = "Build a private PL7 visible settings capture packet from UI-state JSON and screenshots."

    def add_arguments(self, parser):
        parser.add_argument("--id", default="pl7-visible-settings")
        parser.add_argument("--ui-state", action="append", default=[])
        parser.add_argument("--screenshot", action="append", default=[])
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_visible_settings_capture(
                capture_id=options["id"],
                ui_state_paths=options["ui_state"],
                screenshot_paths=options["screenshot"],
            )
        except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
            raise CommandError(str(exc)) from exc

        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(
            json.dumps(
                {
                    "status": report.get("status", "written"),
                    "output": str(output_path),
                    "screenshots": report.get("screenshots_count", 0),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
