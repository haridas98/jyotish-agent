from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_backlog import build_witness_core_evidence_backlog_report


class Command(BaseCommand):
    help = "Build a safe non-mutating core witness evidence backlog report."

    def add_arguments(self, parser):
        parser.add_argument("--preflight-report", default=".tmp/witness-review/core-review-preflight-report.json")
        parser.add_argument("--batch-report", default=".tmp/witness-review/core-review-batch-p51-report.json")
        parser.add_argument("--core-report", default=".tmp/witness-review/core-parity-report.json")
        parser.add_argument("--output", default=".tmp/witness-review/core-evidence-backlog-p53-report.json")

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_backlog_report(
            preflight_report_path=_resolve(root, options["preflight_report"]),
            batch_report_path=_resolve(root, options["batch_report"]),
            core_report_path=_resolve(root, options["core_report"]),
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
                    "stage": report["stage"],
                    "status": report["status"],
                    "blocked_count": report["summary"]["blocked_count"],
                    "ready_to_mark_count": report["summary"]["ready_to_mark_count"],
                    "remaining_not_reviewed_count": report["summary"]["remaining_not_reviewed_count"],
                },
                ensure_ascii=False,
            )
        )


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
