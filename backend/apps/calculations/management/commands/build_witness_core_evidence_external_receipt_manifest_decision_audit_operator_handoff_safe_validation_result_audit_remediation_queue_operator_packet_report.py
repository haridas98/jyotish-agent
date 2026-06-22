from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet import (
    build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_report,
)


class Command(BaseCommand):
    help = "Build safe non-mutating core witness validation audit remediation operator packet report."

    def add_arguments(self, parser):
        parser.add_argument(
            "--external-receipt-manifest-decision-audit-operator-handoff-safe-validation-result-audit-remediation-queue-report",
            default=(
                ".tmp/witness-review/"
                "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
                "safe-validation-result-audit-remediation-queue-p97-report.json"
            ),
        )
        parser.add_argument(
            "--output",
            default=(
                ".tmp/witness-review/"
                "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
                "safe-validation-result-audit-remediation-queue-operator-packet-p99-report.json"
            ),
        )

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_operator_packet_report(
            external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_report_path=_resolve(
                root,
                options[
                    "external_receipt_manifest_decision_audit_operator_handoff_safe_validation_result_audit_remediation_queue_report"
                ],
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
                    "safe_validation_result_audit_remediation_queue_rows": report["summary"][
                        "safe_validation_result_audit_remediation_queue_rows"
                    ],
                    "safe_validation_result_audit_remediation_queue_operator_packet_rows": report["summary"][
                        "safe_validation_result_audit_remediation_queue_operator_packet_rows"
                    ],
                    "safe_validation_result_audit_remediation_queue_operator_packet_family_count": report["summary"][
                        "safe_validation_result_audit_remediation_queue_operator_packet_family_count"
                    ],
                    "safe_validation_result_audit_remediation_queue_operator_packet_ready_count": report["summary"][
                        "safe_validation_result_audit_remediation_queue_operator_packet_ready_count"
                    ],
                    "safe_validation_result_audit_remediation_queue_operator_packet_blocked_count": report["summary"][
                        "safe_validation_result_audit_remediation_queue_operator_packet_blocked_count"
                    ],
                    "safe_validation_result_audit_remediation_queue_operator_packet_delivered_count": report[
                        "summary"
                    ][
                        "safe_validation_result_audit_remediation_queue_operator_packet_delivered_count"
                    ],
                    "safe_validation_result_audit_remediation_queue_operator_packet_acknowledged_count": report[
                        "summary"
                    ][
                        "safe_validation_result_audit_remediation_queue_operator_packet_acknowledged_count"
                    ],
                    "safe_validation_result_audit_remediation_queue_operator_packet_closed_count": report["summary"][
                        "safe_validation_result_audit_remediation_queue_operator_packet_closed_count"
                    ],
                    "safe_validation_result_audit_remediation_queue_operator_packet_executed_count": report[
                        "summary"
                    ][
                        "safe_validation_result_audit_remediation_queue_operator_packet_executed_count"
                    ],
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
