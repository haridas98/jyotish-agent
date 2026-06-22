from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_intake_plan import build_witness_core_evidence_intake_plan_report


class Command(BaseCommand):
    help = "Build a safe non-mutating core witness evidence intake plan."

    def add_arguments(self, parser):
        parser.add_argument("--backlog-report", default=".tmp/witness-review/core-evidence-backlog-p53-report.json")
        parser.add_argument("--preflight-report", default=".tmp/witness-review/core-review-preflight-report.json")
        parser.add_argument("--batch-report", default=".tmp/witness-review/core-review-batch-p51-report.json")
        parser.add_argument("--output", default=".tmp/witness-review/core-evidence-intake-p55-report.json")
        parser.add_argument("--intake-batch-size", type=int, default=5)

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_intake_plan_report(
            backlog_report_path=_resolve(root, options["backlog_report"]),
            preflight_report_path=_resolve(root, options["preflight_report"]),
            batch_report_path=_resolve(root, options["batch_report"]),
            intake_batch_size=options["intake_batch_size"],
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
                    "intake_rows": report["summary"]["intake_rows"],
                    "ready_to_mark_count": report["summary"]["ready_to_mark_count"],
                    "evidence_files_committed_count": report["summary"]["evidence_files_committed_count"],
                    "remaining_not_reviewed_count": report["summary"]["remaining_not_reviewed_count"],
                },
                ensure_ascii=False,
            )
        )


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
