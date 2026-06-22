from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_attachment_work_orders import (
    build_witness_core_evidence_attachment_work_orders_report,
)


FORBIDDEN_MARKERS = [
    "source_report",
    "field_results",
    "expected",
    "actual",
    "sources_present",
    "seal_witness_case",
    "--ack-diff-open",
    "C:\\",
    "C:/Users",
    "/Users/",
    "/home/",
    ".env",
    "evidence available",
    "ready for release",
    "release ready",
    "verified parity",
    "accepted parity",
    "parity success",
    "authoritative",
    "complete",
    "done",
]


P59_CASE_IDS = [
    "vrindavan-1990-08-15-1024",
    "delhi-india-1947-08-15-000001",
    "mayapur-2001-02-03-0910",
    "new-york-2026-03-08-0155",
    "new-york-2026-11-01-0130",
]


FAMILY_ORDER = [
    "jhora_screenshot_or_packet",
    "parashara_light_manual_values_or_packet",
]


def test_core_evidence_attachment_work_orders_expand_p59_rows_in_family_order(tmp_path):
    attachment_gate_path = tmp_path / "attachment-gate.json"
    attachment_gate_path.write_text(json.dumps(_p59_attachment_gate_payload()), encoding="utf-8")

    report = build_witness_core_evidence_attachment_work_orders_report(
        attachment_gate_report_path=attachment_gate_path,
    )

    assert report["schema_version"] == "jyotish-core-evidence-attachment-work-orders-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P61-A"
    assert report["status"] == "blocked_pending_attachments"
    assert report["summary"] == {
        "source_attachment_rows": 5,
        "source_operator_attachment_manifest_rows": 5,
        "case_work_order_rows": 5,
        "work_order_rows": 10,
        "pending_work_order_count": 10,
        "pending_jhora_work_order_count": 5,
        "pending_parashara_light_work_order_count": 5,
        "ready_to_mark_count": 0,
        "blocked_case_count": 5,
        "attached_evidence_files_count": 0,
        "attached_evidence_family_count": 0,
        "missing_attachment_slot_count": 10,
        "remaining_not_reviewed_count": 20,
        "release_gate_status": "blocked",
        "command_smoke_matrix_status": "ready",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }
    assert [row["case_id"] for row in report["case_attachment_work_order_manifest"]] == P59_CASE_IDS
    assert [row["case_id"] for row in report["work_orders"][::2]] == P59_CASE_IDS
    assert [row["evidence_family"] for row in report["work_orders"][:4]] == FAMILY_ORDER + FAMILY_ORDER
    assert [row["work_order_index"] for row in report["work_orders"]] == list(range(1, 11))
    assert all(row["work_order_status"] == "pending_not_attached" for row in report["work_orders"])
    assert all(row["ready_to_mark"] is False for row in report["work_orders"])
    assert report["work_orders"][0]["safe_action_label"] == "collect_jhora_screenshot"
    assert report["work_orders"][1]["safe_action_label"] == "attach_parashara_light_manual_values"
    assert report["work_orders"][0]["safe_validation_command_families"] == [
        "build_witness_core_evidence_attachment_work_orders_report",
        "build_witness_core_evidence_attachment_gate_report",
        "preflight_witness_review",
    ]
    first_case = report["case_attachment_work_order_manifest"][0]
    assert first_case["work_order_indices"] == [1, 2]
    assert first_case["family_statuses"] == {
        "jhora_screenshot_or_packet": "pending_not_attached",
        "parashara_light_manual_values_or_packet": "pending_not_attached",
    }
    assert first_case["case_work_order_status"] == "blocked_pending_attachments"
    assert first_case["ready_to_mark"] is False
    assert _serialized_safe(report)


def test_core_evidence_attachment_work_orders_command_writes_safe_json_without_mutating_p59(tmp_path):
    attachment_gate_path = tmp_path / "attachment-gate.json"
    output_path = tmp_path / "work-orders.json"
    attachment_gate_path.write_text(json.dumps(_p59_attachment_gate_payload()), encoding="utf-8")
    before = attachment_gate_path.read_text(encoding="utf-8")

    call_command(
        "build_witness_core_evidence_attachment_work_orders_report",
        "--attachment-gate-report",
        str(attachment_gate_path),
        "--output",
        str(output_path),
    )

    written = _read_json(output_path)
    assert written["schema_version"] == "jyotish-core-evidence-attachment-work-orders-v1"
    assert written["summary"]["work_order_rows"] == 10
    assert written["summary"]["case_work_order_rows"] == 5
    assert written["summary"]["pending_jhora_work_order_count"] == 5
    assert written["summary"]["pending_parashara_light_work_order_count"] == 5
    assert written["summary"]["ready_to_mark_count"] == 0
    assert _serialized_safe(written)
    assert attachment_gate_path.read_text(encoding="utf-8") == before


def test_p61_committed_core_evidence_attachment_work_orders_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(
        repo_root / ".tmp" / "witness-review" / "core-evidence-attachment-work-orders-p61-report.json"
    )
    attachment_gate = _read_json(
        repo_root / ".tmp" / "witness-review" / "core-evidence-attachment-gate-p59-report.json"
    )

    assert report["schema_version"] == "jyotish-core-evidence-attachment-work-orders-v1"
    assert report["stage"] == "P61-A"
    assert report["summary"]["source_attachment_rows"] == 5
    assert report["summary"]["source_operator_attachment_manifest_rows"] == 5
    assert report["summary"]["case_work_order_rows"] == 5
    assert report["summary"]["work_order_rows"] == 10
    assert report["summary"]["pending_work_order_count"] == 10
    assert report["summary"]["pending_jhora_work_order_count"] == 5
    assert report["summary"]["pending_parashara_light_work_order_count"] == 5
    assert report["summary"]["blocked_case_count"] == 5
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert [row["case_id"] for row in report["case_attachment_work_order_manifest"]] == P59_CASE_IDS
    assert [row["case_id"] for row in report["work_orders"][::2]] == P59_CASE_IDS
    assert [row["case_id"] for row in attachment_gate["rows"]] == P59_CASE_IDS
    assert all(row["work_order_status"] == "pending_not_attached" for row in report["work_orders"])
    assert all(row["ready_to_mark"] is False for row in report["work_orders"])
    assert _serialized_safe(report)


def test_core_evidence_attachment_work_orders_stage_does_not_change_forbidden_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    allowed = {
        ".tmp/witness-review/core-evidence-attachment-work-orders-p61-report.json",
        "backend/apps/calculations/witness_core_evidence_attachment_work_orders.py",
        "backend/apps/calculations/management/commands/build_witness_core_evidence_attachment_work_orders_report.py",
        "backend/apps/calculations/test_witness_core_evidence_attachment_work_orders.py",
    }
    forbidden_exact = {
        "backend/config/settings.py",
        "backend/apps/calculations/classical.py",
        "backend/apps/calculations/chart.py",
        "backend/apps/calculations/ephemeris.py",
        "backend/apps/calculations/math.py",
        "backend/apps/calculations/panchanga.py",
        "backend/apps/calculations/vimshottari.py",
        "backend/apps/calculations/dasha_systems.py",
        "backend/apps/calculations/vargas.py",
        "backend/apps/calculations/accuracy.py",
        "backend/apps/calculations/graha_drishti.py",
        "backend/apps/calculations/rashi_drishti.py",
        "backend/apps/calculations/transit_coordinates.py",
        "backend/apps/calculations/workflows.py",
    }
    for path in changed:
        normalized = path.replace("\\", "/")
        assert normalized in allowed
        assert normalized not in forbidden_exact
        assert not normalized.startswith("frontend/")
        assert not normalized.startswith("deploy/")
        assert not normalized.startswith(".github/")
        assert "/migrations/" not in normalized
        assert "/fixtures/" not in normalized


def _p59_attachment_gate_payload():
    rows = []
    manifest = []
    for index, case_id in enumerate(P59_CASE_IDS, start=1):
        row = {
            "attachment_index": index,
            "readiness_index": index,
            "intake_index": index,
            "candidate_index": index,
            "case_id": case_id,
            "source_family": "both",
            "required_evidence_families": FAMILY_ORDER,
            "p57_evidence_slot_status": {
                "jhora_screenshot_or_packet": "missing",
                "parashara_light_manual_values_or_packet": "missing",
            },
            "attachment_slot_status": {
                "jhora_screenshot_or_packet": "not_attached",
                "parashara_light_manual_values_or_packet": "not_attached",
            },
            "ready_to_mark": False,
            "attachment_gate_status": "blocked_no_attached_evidence",
        }
        rows.append(row)
        manifest.append({"case_id": case_id})
    return {
        "schema_version": "jyotish-core-evidence-attachment-gate-v1",
        "domain": "witness_core_parity",
        "stage": "P59-A",
        "status": "blocked_no_attached_evidence",
        "summary": {
            "attachment_rows": 5,
            "operator_attachment_manifest_rows": 5,
            "attached_evidence_files_count": 0,
            "attached_evidence_family_count": 0,
            "missing_attachment_slot_count": 10,
            "ready_to_mark_count": 0,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
        },
        "rows": rows,
        "operator_attachment_manifest": manifest,
    }


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
