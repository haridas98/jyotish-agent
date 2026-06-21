from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.witness_parity_command_manifest import build_witness_parity_command_manifest


class Command(BaseCommand):
    help = "Build a safe witness parity command manifest report."

    def add_arguments(self, parser):
        parser.add_argument("--out", default="")
        parser.add_argument("--fail-if-missing", action="store_true")

    def handle(self, *args, **options):
        manifest = build_witness_parity_command_manifest()
        encoded = json.dumps(manifest, ensure_ascii=False, indent=2)
        out = str(options.get("out") or "").strip()
        if out:
            output_path = Path(out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        else:
            self.stdout.write(encoded)

        if options.get("fail_if_missing") and manifest["status"] == "blocked":
            raise CommandError("witness parity command manifest has missing mappings")
