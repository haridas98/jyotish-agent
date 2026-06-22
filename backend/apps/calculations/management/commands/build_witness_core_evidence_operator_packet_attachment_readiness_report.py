from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_operator_packet_attachment_readiness import (
    build_witness_core_evidence_operator_packet_attachment_readiness_report,
)


class Command(BaseCommand):
    help = "Build safe non-mutating core witness evidence operator packet attachment-readiness report."

    def add_arguments(self, parser):
        parser.add_argument(
            "--operator-packet-qa-report",
            default=".tmp/witness-review/core-evidence-operator-packet-qa-p67-report.json",
        )
        parser.add_argument(
            "--output",
            default=".tmp/witness-review/core-evidence-operator-packet-attachment-readiness-p69-report.json",
        )

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_operator_packet_attachment_readiness_report(
            operator_packet_qa_report_path=_resolve(root, options["operator_packet_qa_report"]),
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
                    "case_attachment_readiness_rows": report["summary"][
                        "case_attachment_readiness_rows"
                    ],
                    "attachment_readiness_slot_rows": report["summary"][
                        "attachment_readiness_slot_rows"
                    ],
                    "blocked_case_attachment_count": report["summary"][
                        "blocked_case_attachment_count"
                    ],
                    "pending_external_evidence_attachment_count": report["summary"][
                        "pending_external_evidence_attachment_count"
                    ],
                    "pending_jhora_external_attachment_count": report["summary"][
                        "pending_jhora_external_attachment_count"
                    ],
                    "pending_parashara_light_external_attachment_count": report["summary"][
                        "pending_parashara_light_external_attachment_count"
                    ],
                    "ready_to_attach_count": report["summary"]["ready_to_attach_count"],
                    "ready_to_mark_count": report["summary"]["ready_to_mark_count"],
                    "remaining_not_reviewed_count": report["summary"][
                        "remaining_not_reviewed_count"
                    ],
                },
                ensure_ascii=False,
            )
        )


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
