from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_operator_packet_qa import (
    build_witness_core_evidence_operator_packet_qa_report,
)


class Command(BaseCommand):
    help = "Build safe non-mutating core witness evidence operator packet QA preflight."

    def add_arguments(self, parser):
        parser.add_argument(
            "--operator-packets-report",
            default=".tmp/witness-review/core-evidence-operator-packets-p65-report.json",
        )
        parser.add_argument(
            "--output",
            default=".tmp/witness-review/core-evidence-operator-packet-qa-p67-report.json",
        )

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_operator_packet_qa_report(
            operator_packets_report_path=_resolve(root, options["operator_packets_report"]),
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
                    "operator_packet_qa_rows": report["summary"]["operator_packet_qa_rows"],
                    "attachment_slot_qa_rows": report["summary"]["attachment_slot_qa_rows"],
                    "blocked_packet_qa_count": report["summary"]["blocked_packet_qa_count"],
                    "pending_attachment_slot_qa_count": report["summary"][
                        "pending_attachment_slot_qa_count"
                    ],
                    "pending_jhora_attachment_slot_qa_count": report["summary"][
                        "pending_jhora_attachment_slot_qa_count"
                    ],
                    "pending_parashara_light_attachment_slot_qa_count": report["summary"][
                        "pending_parashara_light_attachment_slot_qa_count"
                    ],
                    "ready_to_mark_count": report["summary"]["ready_to_mark_count"],
                    "remaining_not_reviewed_count": report["summary"]["remaining_not_reviewed_count"],
                },
                ensure_ascii=False,
            )
        )


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
