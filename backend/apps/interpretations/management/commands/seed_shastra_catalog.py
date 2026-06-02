from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.interpretations.catalog_importer import import_interpretation_catalog
from apps.interpretations.shastra_catalog import shastra_authority_catalog


class Command(BaseCommand):
    help = "Seed the research-only shastra authority catalog and explanation source anchors."

    def handle(self, *args, **options):
        counts = import_interpretation_catalog(shastra_authority_catalog())
        self.stdout.write(
            self.style.SUCCESS(
                "Seeded shastra catalog: "
                f"{counts['works']} works, {counts['passages']} passages, "
                f"{counts['rules']} rules, {counts['blocks']} blocks."
            )
        )
