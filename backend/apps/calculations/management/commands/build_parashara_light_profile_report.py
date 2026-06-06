from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_profile import build_parashara_light_profile_report


class Command(BaseCommand):
    help = "Build a PL7 birth XML profile/settings report."

    def add_arguments(self, parser):
        parser.add_argument("--birth-xml", required=True)
        parser.add_argument("--packet", default="")
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_profile_report(
                options["birth_xml"],
                packet_path=options["packet"] or None,
            )
        except (FileNotFoundError, ValueError, json.JSONDecodeError, ET.ParseError) as exc:
            raise CommandError(str(exc)) from exc

        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(
            json.dumps(
                {
                    "status": "written",
                    "output": str(output_path),
                    "flags": report.get("data_quality_flags", []),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
