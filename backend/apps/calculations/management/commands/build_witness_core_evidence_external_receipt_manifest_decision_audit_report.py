from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_external_receipt_manifest_decision_audit import (
    build_witness_core_evidence_external_receipt_manifest_decision_audit_report,
)


class Command(BaseCommand):
    help = "Build safe non-mutating core witness external evidence receipt manifest decision audit report."

    def add_arguments(self, parser):
        parser.add_argument(
            "--external-receipt-manifest-decision-queue-report",
            default=".tmp/witness-review/core-evidence-external-receipt-manifest-decision-queue-p81-report.json",
        )
        parser.add_argument(
            "--output",
            default=".tmp/witness-review/core-evidence-external-receipt-manifest-decision-audit-p83-report.json",
        )

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_external_receipt_manifest_decision_audit_report(
            external_receipt_manifest_decision_queue_report_path=_resolve(
                root,
                options["external_receipt_manifest_decision_queue_report"],
            ),
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
                    "case_receipt_manifest_decision_audit_rows": report["summary"][
                        "case_receipt_manifest_decision_audit_rows"
                    ],
                    "attachment_receipt_manifest_decision_audit_rows": report["summary"][
                        "attachment_receipt_manifest_decision_audit_rows"
                    ],
                    "pending_external_evidence_receipt_manifest_decision_audit_count": report["summary"][
                        "pending_external_evidence_receipt_manifest_decision_audit_count"
                    ],
                    "pending_jhora_receipt_manifest_decision_audit_count": report["summary"][
                        "pending_jhora_receipt_manifest_decision_audit_count"
                    ],
                    "pending_parashara_light_receipt_manifest_decision_audit_count": report["summary"][
                        "pending_parashara_light_receipt_manifest_decision_audit_count"
                    ],
                    "decision_queue_rows": report["summary"]["decision_queue_rows"],
                    "decision_audit_ready_count": report["summary"]["decision_audit_ready_count"],
                    "decision_audit_blocked_count": report["summary"]["decision_audit_blocked_count"],
                    "decision_recorded_count": report["summary"]["decision_recorded_count"],
                    "decision_audited_count": report["summary"]["decision_audited_count"],
                    "decision_audit_passed_count": report["summary"]["decision_audit_passed_count"],
                    "decision_audit_failed_count": report["summary"]["decision_audit_failed_count"],
                    "ready_to_attach_count": report["summary"]["ready_to_attach_count"],
                    "ready_to_mark_count": report["summary"]["ready_to_mark_count"],
                    "remaining_not_reviewed_count": report["summary"]["remaining_not_reviewed_count"],
                },
                ensure_ascii=False,
            )
        )


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path
