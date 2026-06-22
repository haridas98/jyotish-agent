from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_attachment_work_orders import (
    build_witness_core_evidence_attachment_work_orders_report,
)


class Command(BaseCommand):
    help = "Build safe non-mutating core witness evidence attachment work orders."

    def add_arguments(self, parser):
        parser.add_argument(
            "--attachment-gate-report",
            default=".tmp/witness-review/core-evidence-attachment-gate-p59-report.json",
        )
        parser.add_argument(
            "--output",
            default=".tmp/witness-review/core-evidence-attachment-work-orders-p61-report.json",
        )

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_attachment_work_orders_report(
            attachment_gate_report_path=_resolve(root, options["attachment_gate_report"]),
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
                    "work_order_rows": report["summary"]["work_order_rows"],
                    "pending_work_order_count": report["summary"]["pending_work_order_count"],
                    "pending_jhora_work_order_count": report["summary"]["pending_jhora_work_order_count"],
                    "pending_parashara_light_work_order_count": report["summary"][
                        "pending_parashara_light_work_order_count"
                    ],
                    "blocked_case_count": report["summary"]["blocked_case_count"],
                    "ready_to_mark_count": report["summary"]["ready_to_mark_count"],
                    "remaining_not_reviewed_count": report["summary"]["remaining_not_reviewed_count"],
                },
                ensure_ascii=False,
            )
        )


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
