from __future__ import annotations

from django.core.management.base import BaseCommand

from apps.interpretations.evidence_matcher import build_shastra_evidence


class Command(BaseCommand):
    help = "Match shastra condition matrix rows to imported source passages."

    def add_arguments(self, parser):
        parser.add_argument("--condition-key", action="append", dest="condition_keys")
        parser.add_argument("--limit-per-condition", type=int, default=5)
        parser.add_argument("--min-score", type=int, default=10)

    def handle(self, *args, **options):
        result = build_shastra_evidence(
            condition_keys=options.get("condition_keys"),
            limit_per_condition=int(options["limit_per_condition"]),
            min_score=int(options["min_score"]),
        )
        summary = result["summary"]
        self.stdout.write(
            self.style.SUCCESS(
                "Built shastra evidence: "
                f"{summary['conditions_processed']} conditions, "
                f"{summary['evidence_created_or_updated']} evidence links."
            )
        )
