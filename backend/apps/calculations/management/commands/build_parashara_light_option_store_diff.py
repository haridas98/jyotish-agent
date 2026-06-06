from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_option_store_diff import (
    build_parashara_light_option_store_diff_report,
)


class Command(BaseCommand):
    help = "Build a private PL7 option-store diff report from hash-only snapshots."

    def add_arguments(self, parser):
        parser.add_argument("--before-snapshot", required=True)
        parser.add_argument("--changed-snapshot", required=True)
        parser.add_argument("--restored-snapshot", required=True)
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            report = build_parashara_light_option_store_diff_report(
                before_snapshot_path=Path(options["before_snapshot"]),
                changed_snapshot_path=Path(options["changed_snapshot"]),
                restored_snapshot_path=Path(options["restored_snapshot"]),
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
                    "primary_candidate": report.get("primary_candidate", ""),
                    "restore_verified": report.get("restore_verified", False),
                    "next_action": report.get("next_action", ""),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
