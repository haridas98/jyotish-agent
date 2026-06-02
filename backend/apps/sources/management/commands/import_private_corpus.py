from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand

from apps.sources.private_corpus import DEFAULT_CHUNK_CHARS, import_private_corpus_manifest


class Command(BaseCommand):
    help = "Import local private full-text books as research-only SourcePassage chunks."

    def add_arguments(self, parser):
        parser.add_argument("manifest_path")
        parser.add_argument("--chunk-chars", type=int, default=DEFAULT_CHUNK_CHARS)

    def handle(self, *args, **options):
        counts = import_private_corpus_manifest(
            Path(options["manifest_path"]),
            chunk_chars=int(options["chunk_chars"]),
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Imported private corpus: {counts['works']} works, {counts['passages']} research-only passages."
            )
        )
