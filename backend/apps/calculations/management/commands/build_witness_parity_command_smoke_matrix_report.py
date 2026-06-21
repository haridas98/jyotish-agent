from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.witness_parity_command_smoke_matrix import build_witness_parity_command_smoke_matrix


class Command(BaseCommand):
    help = "Build a safe witness parity command smoke matrix report."

    def add_arguments(self, parser):
        parser.add_argument("--out", default="")
        parser.add_argument("--fail-if-blocked", action="store_true")

    def handle(self, *args, **options):
        matrix = build_witness_parity_command_smoke_matrix()
        encoded = json.dumps(matrix, ensure_ascii=False, indent=2)
        out = str(options.get("out") or "").strip()
        if out:
            output_path = Path(out)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        else:
            self.stdout.write(encoded)

        if options.get("fail_if_blocked") and matrix["status"] == "blocked":
            raise CommandError("witness parity command smoke matrix is blocked")
