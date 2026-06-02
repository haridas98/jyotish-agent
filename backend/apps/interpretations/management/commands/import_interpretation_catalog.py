from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.interpretations.catalog_importer import import_interpretation_catalog


class Command(BaseCommand):
    help = "Import reviewed source works, passages, and interpretation rules from a JSON catalog."

    def add_arguments(self, parser):
        parser.add_argument("catalog_path")

    def handle(self, *args, **options):
        catalog_path = Path(options["catalog_path"])
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        counts = import_interpretation_catalog(catalog)
        self.stdout.write(
            self.style.SUCCESS(
                "Imported catalog: "
                f"{counts['works']} works, {counts['passages']} passages, "
                f"{counts['rules']} rules, {counts['blocks']} blocks."
            )
        )
