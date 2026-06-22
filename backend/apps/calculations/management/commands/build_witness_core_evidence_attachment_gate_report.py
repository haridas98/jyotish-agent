from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_attachment_gate import (
    build_witness_core_evidence_attachment_gate_report,
)


class Command(BaseCommand):
    help = "Build a safe non-mutating core witness evidence attachment gate."

    def add_arguments(self, parser):
        parser.add_argument("--readiness-report", default=".tmp/witness-review/core-evidence-readiness-p57-report.json")
        parser.add_argument("--output", default=".tmp/witness-review/core-evidence-attachment-gate-p59-report.json")

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_attachment_gate_report(
            readiness_report_path=_resolve(root, options["readiness_report"]),
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
                    "attachment_rows": report["summary"]["attachment_rows"],
                    "ready_to_mark_count": report["summary"]["ready_to_mark_count"],
                    "blocked_no_attached_evidence_count": report["summary"][
                        "blocked_no_attached_evidence_count"
                    ],
                    "missing_attachment_slot_count": report["summary"]["missing_attachment_slot_count"],
                    "attached_evidence_files_count": report["summary"]["attached_evidence_files_count"],
                    "remaining_not_reviewed_count": report["summary"]["remaining_not_reviewed_count"],
                },
                ensure_ascii=False,
            )
        )


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
