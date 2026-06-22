from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript import (
    build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report,
)


class Command(BaseCommand):
    help = "Build safe non-mutating core witness decision audit operator handoff validation transcript report."

    def add_arguments(self, parser):
        parser.add_argument(
            "--external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-report",
            default=(
                ".tmp/witness-review/"
                "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-smoke-matrix-p89-report.json"
            ),
        )
        parser.add_argument(
            "--output",
            default=(
                ".tmp/witness-review/"
                "core-evidence-external-receipt-manifest-decision-audit-operator-handoff-"
                "safe-validation-transcript-p91-report.json"
            ),
        )

    def handle(self, *args, **options):
        root = Path(settings.ROOT_DIR)
        report = build_witness_core_evidence_external_receipt_manifest_decision_audit_operator_handoff_safe_validation_transcript_report(
            external_receipt_manifest_decision_audit_operator_handoff_smoke_matrix_report_path=_resolve(
                root,
                options["external_receipt_manifest_decision_audit_operator_handoff_smoke_matrix_report"],
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
                    "safe_validation_transcript_case_rows": report["summary"][
                        "safe_validation_transcript_case_rows"
                    ],
                    "safe_validation_transcript_attachment_rows": report["summary"][
                        "safe_validation_transcript_attachment_rows"
                    ],
                    "safe_validation_transcript_command_rows": report["summary"][
                        "safe_validation_transcript_command_rows"
                    ],
                    "safe_validation_command_family_count": report["summary"][
                        "safe_validation_command_family_count"
                    ],
                    "safe_validation_command_execution_performed_count": report["summary"][
                        "safe_validation_command_execution_performed_count"
                    ],
                    "safe_validation_command_ready_count": report["summary"][
                        "safe_validation_command_ready_count"
                    ],
                    "safe_validation_command_blocked_count": report["summary"][
                        "safe_validation_command_blocked_count"
                    ],
                    "operator_handoff_case_packet_rows": report["summary"][
                        "operator_handoff_case_packet_rows"
                    ],
                    "operator_handoff_attachment_packet_rows": report["summary"][
                        "operator_handoff_attachment_packet_rows"
                    ],
                    "operator_handoff_smoke_case_rows": report["summary"][
                        "operator_handoff_smoke_case_rows"
                    ],
                    "operator_handoff_smoke_attachment_rows": report["summary"][
                        "operator_handoff_smoke_attachment_rows"
                    ],
                    "unsafe_external_action_command_count": report["summary"][
                        "unsafe_external_action_command_count"
                    ],
                    "command_execution_performed_count": report["summary"][
                        "command_execution_performed_count"
                    ],
                    "command_smoke_matrix_ready_count": report["summary"][
                        "command_smoke_matrix_ready_count"
                    ],
                    "command_smoke_matrix_blocked_count": report["summary"][
                        "command_smoke_matrix_blocked_count"
                    ],
                    "operator_handoff_ready_count": report["summary"]["operator_handoff_ready_count"],
                    "operator_handoff_blocked_count": report["summary"]["operator_handoff_blocked_count"],
                    "work_order_delivery_ready_count": report["summary"]["work_order_delivery_ready_count"],
                    "work_order_delivery_blocked_count": report["summary"]["work_order_delivery_blocked_count"],
                    "pending_external_evidence_decision_audit_work_order_count": report["summary"][
                        "pending_external_evidence_decision_audit_work_order_count"
                    ],
                    "pending_jhora_decision_audit_work_order_count": report["summary"][
                        "pending_jhora_decision_audit_work_order_count"
                    ],
                    "pending_parashara_light_decision_audit_work_order_count": report["summary"][
                        "pending_parashara_light_decision_audit_work_order_count"
                    ],
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
