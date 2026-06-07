from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_internal_settings_audit import (
    build_parashara_light_internal_settings_audit,
)


class Command(BaseCommand):
    help = "Build a private PL internal settings audit from visible and hash-only evidence."

    def add_arguments(self, parser):
        parser.add_argument("--settings-aware-forensic", required=True)
        parser.add_argument("--preferences-inventory", required=True)
        parser.add_argument("--hidden-option-store", required=True)
        parser.add_argument("--option-store-diff", required=True)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_internal_settings_audit(
                settings_aware_forensic_path=Path(options["settings_aware_forensic"]),
                preferences_inventory_path=Path(options["preferences_inventory"]),
                hidden_option_store_path=Path(options["hidden_option_store"]),
                option_store_diff_path=Path(options["option_store_diff"]),
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
