from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_review_batch import build_witness_core_review_batch_report


class Command(BaseCommand):
    help = "Build a safe non-mutating core witness review batch report."

    def add_arguments(self, parser):
        parser.add_argument("--preflight-report", default=".tmp/witness-review/core-review-preflight-report.json")
        parser.add_argument("--core-report", default=".tmp/witness-review/core-parity-report.json")
        parser.add_argument("--output", default=".tmp/witness-review/core-review-batch-p51-report.json")
        parser.add_argument("--requested-close-count", type=int, default=5)
        parser.add_argument("--reviewer", default="Haridas")
        parser.add_argument("--reviewed-at", default="2026-06-22T00:00:00+00:00")

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_review_batch_report(
            preflight_report_path=_resolve(root, options["preflight_report"]),
            core_report_path=_resolve(root, options["core_report"]),
            repo_root=root,
            requested_close_count=options["requested_close_count"],
            reviewer=options["reviewer"],
            reviewed_at=options["reviewed_at"],
        )
        encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        output = options["output"]
        if output:
            output_path = _resolve(root, output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        self.stdout.write(
            json.dumps(
                {
                    "schema_version": report["schema_version"],
                    "domain": report["domain"],
                    "status": report["status"],
                    "requested_close_count": report["summary"]["requested_close_count"],
                    "closed_count": report["summary"]["closed_count"],
                    "skipped_count": report["summary"]["skipped_count"],
                    "after_not_reviewed_count": report["summary"]["after_not_reviewed_count"],
                },
                ensure_ascii=False,
            )
        )


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
