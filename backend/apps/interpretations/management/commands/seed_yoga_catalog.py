from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.interpretations.catalog_importer import import_interpretation_catalog
from apps.interpretations.yoga_catalog import yoga_catalog_import_payload, yoga_registry


class Command(BaseCommand):
    help = "Seed the research-only classical yoga catalog."

    def handle(self, *args, **options):
        counts = import_interpretation_catalog(yoga_catalog_import_payload())
        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded yoga catalog: {len(yoga_registry())} yogas, {counts['passages']} passages."
            )
        )
