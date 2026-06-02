from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.sources.segmentation import segment_private_corpus


class Command(BaseCommand):
    help = "Split imported private full-text chunks into review-only shastra passage candidates."

    def add_arguments(self, parser):
        parser.add_argument("work_slug", nargs="?")
        parser.add_argument("--max-chars", type=int, default=1800)

    def handle(self, *args, **options):
        counts = segment_private_corpus(
            work_slug=options.get("work_slug"),
            max_chars=int(options["max_chars"]),
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Segmented private corpus: "
                f"{counts['works']} works, "
                f"{counts['source_chunks']} source chunks, "
                f"{counts['candidate_passages']} candidate passages."
            )
        )
