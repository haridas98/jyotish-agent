from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_settings_evidence import build_parashara_light_settings_evidence


class Command(BaseCommand):
    help = "Build a private PL7 settings evidence manifest without parsing proprietary binaries."

    def add_arguments(self, parser):
        parser.add_argument("--chart-xml", required=True)
        parser.add_argument("--options-dir", required=True)
        parser.add_argument("--pl7-dir", required=True)
        parser.add_argument("--session-token-limit", type=int, default=40)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_settings_evidence(
                chart_xml=options["chart_xml"],
                options_dir=options["options_dir"],
                pl7_dir=options["pl7_dir"],
                session_token_limit=options["session_token_limit"],
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
                    "options_files": len(report.get("options_manifest", [])),
                    "session_tokens": len(report.get("session_token_manifest", [])),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
