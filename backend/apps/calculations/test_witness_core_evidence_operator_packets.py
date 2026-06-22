from __future__ import annotations

import json
import subprocess
from pathlib import Path

from django.core.management import call_command

from apps.calculations.witness_core_evidence_operator_packets import (
    build_witness_core_evidence_operator_packets_report,
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


P63_CASE_IDS = [
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


def test_core_evidence_operator_packets_preserve_p63_case_and_family_order(tmp_path):
    handoff_path = tmp_path / "handoff.json"
    handoff_path.write_text(json.dumps(_p63_handoff_payload()), encoding="utf-8")

    report = build_witness_core_evidence_operator_packets_report(
        handoff_report_path=handoff_path,
    )

    assert report["schema_version"] == "jyotish-core-evidence-operator-packets-v1"
    assert report["domain"] == "witness_core_parity"
    assert report["stage"] == "P65-A"
    assert report["status"] == "blocked_pending_operator_packet_evidence"
    assert report["summary"] == {
        "source_case_handoff_rows": 5,
        "source_handoff_work_order_rows": 10,
        "operator_packet_rows": 5,
        "operator_attachment_slot_rows": 10,
        "pending_operator_packet_count": 5,
        "pending_operator_attachment_slot_count": 10,
        "pending_jhora_attachment_slot_count": 5,
        "pending_parashara_light_attachment_slot_count": 5,
        "blocked_packet_count": 5,
        "ready_to_mark_count": 0,
        "attached_evidence_files_count": 0,
        "attached_evidence_family_count": 0,
        "missing_attachment_slot_count": 10,
        "remaining_not_reviewed_count": 20,
        "release_gate_status": "blocked",
        "command_smoke_matrix_status": "ready",
        "parity_success_claimed": False,
        "release_ready_claimed": False,
    }
    assert [row["case_id"] for row in report["operator_packet_rows"]] == P63_CASE_IDS
    assert [row["case_id"] for row in report["operator_attachment_slot_rows"][::2]] == P63_CASE_IDS
    assert [row["evidence_family"] for row in report["operator_attachment_slot_rows"][:4]] == (
        FAMILY_ORDER + FAMILY_ORDER
    )
    assert [row["operator_packet_index"] for row in report["operator_packet_rows"]] == list(range(1, 6))
    assert [row["operator_attachment_slot_index"] for row in report["operator_attachment_slot_rows"]] == list(range(1, 11))
    assert report["operator_packet_rows"][0]["source_handoff_work_order_indices"] == [1, 2]
    assert report["operator_packet_rows"][0]["attachment_slot_indices"] == [1, 2]
    assert report["operator_packet_rows"][-1]["source_handoff_work_order_indices"] == [9, 10]
    assert report["operator_packet_rows"][-1]["attachment_slot_indices"] == [9, 10]
    assert all(row["packet_status"] == "blocked_pending_operator_packet_evidence" for row in report["operator_packet_rows"])
    assert all(row["case_handoff_status"] == "blocked_pending_operator_evidence" for row in report["operator_packet_rows"])
    assert all(row["case_work_order_status"] == "blocked_pending_attachments" for row in report["operator_packet_rows"])
    assert all(row["ready_to_mark"] is False for row in report["operator_packet_rows"])
    assert all(row["p65_packet_status"] == "blocked_pending_operator_packet_evidence" for row in report["operator_attachment_slot_rows"])
    assert all(row["evidence_file_status"] == "not_attached" for row in report["operator_attachment_slot_rows"])
    assert all(row["ready_to_mark"] is False for row in report["operator_attachment_slot_rows"])
    assert report["operator_attachment_slot_rows"][0]["safe_action_label"] == "collect_jhora_screenshot"
    assert report["operator_attachment_slot_rows"][1]["safe_action_label"] == "attach_parashara_light_manual_values"
    assert report["operator_packet_rows"][0]["safe_validation_command_families"] == [
        "build_witness_core_evidence_operator_packets_report",
        "build_witness_core_evidence_attachment_handoff_report",
        "build_witness_core_evidence_attachment_work_orders_report",
        "build_witness_core_evidence_attachment_gate_report",
        "preflight_witness_review",
    ]
    assert _serialized_safe(report)


def test_core_evidence_operator_packets_command_writes_safe_json_without_mutating_p63(tmp_path, monkeypatch):
    handoff_path = tmp_path / "handoff.json"
    output_path = tmp_path / "operator-packets.json"
    handoff_path.write_text(json.dumps(_p63_handoff_payload()), encoding="utf-8")
    before = handoff_path.read_text(encoding="utf-8")

    def fail_external_execution(*args, **kwargs):
        raise AssertionError("P65 command must not run external tools")

    monkeypatch.setattr(subprocess, "Popen", fail_external_execution)

    call_command(
        "build_witness_core_evidence_operator_packets_report",
        "--handoff-report",
        str(handoff_path),
        "--output",
        str(output_path),
    )

    written = _read_json(output_path)
    assert written["schema_version"] == "jyotish-core-evidence-operator-packets-v1"
    assert written["summary"]["operator_packet_rows"] == 5
    assert written["summary"]["operator_attachment_slot_rows"] == 10
    assert written["summary"]["pending_jhora_attachment_slot_count"] == 5
    assert written["summary"]["pending_parashara_light_attachment_slot_count"] == 5
    assert written["summary"]["ready_to_mark_count"] == 0
    assert _serialized_safe(written)
    assert handoff_path.read_text(encoding="utf-8") == before


def test_p65_committed_core_evidence_operator_packets_artifact_is_safe_and_current():
    repo_root = Path(__file__).resolve().parents[3]
    report = _read_json(
        repo_root / ".tmp" / "witness-review" / "core-evidence-operator-packets-p65-report.json"
    )
    handoff = _read_json(
        repo_root / ".tmp" / "witness-review" / "core-evidence-attachment-handoff-p63-report.json"
    )

    assert report["schema_version"] == "jyotish-core-evidence-operator-packets-v1"
    assert report["stage"] == "P65-A"
    assert report["summary"]["source_case_handoff_rows"] == 5
    assert report["summary"]["source_handoff_work_order_rows"] == 10
    assert report["summary"]["operator_packet_rows"] == 5
    assert report["summary"]["operator_attachment_slot_rows"] == 10
    assert report["summary"]["pending_operator_packet_count"] == 5
    assert report["summary"]["pending_operator_attachment_slot_count"] == 10
    assert report["summary"]["pending_jhora_attachment_slot_count"] == 5
    assert report["summary"]["pending_parashara_light_attachment_slot_count"] == 5
    assert report["summary"]["blocked_packet_count"] == 5
    assert report["summary"]["ready_to_mark_count"] == 0
    assert report["summary"]["remaining_not_reviewed_count"] == 20
    assert [row["case_id"] for row in report["operator_packet_rows"]] == P63_CASE_IDS
    assert [row["case_id"] for row in report["operator_attachment_slot_rows"][::2]] == P63_CASE_IDS
    assert [row["case_id"] for row in handoff["case_handoff_rows"]] == P63_CASE_IDS
    assert all(row["p65_packet_status"] == "blocked_pending_operator_packet_evidence" for row in report["operator_attachment_slot_rows"])
    assert all(row["ready_to_mark"] is False for row in report["operator_attachment_slot_rows"])
    assert _serialized_safe(report)


def test_core_evidence_operator_packets_stage_does_not_change_forbidden_files():
    changed = subprocess.check_output(["git", "diff", "--name-only"], text=True).splitlines()
    allowed = {
        ".tmp/witness-review/core-evidence-operator-packets-p65-report.json",
        "backend/apps/calculations/witness_core_evidence_operator_packets.py",
        "backend/apps/calculations/management/commands/build_witness_core_evidence_operator_packets_report.py",
        "backend/apps/calculations/test_witness_core_evidence_operator_packets.py",
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


def _p63_handoff_payload():
    handoff_orders = []
    case_rows = []
    for case_index, case_id in enumerate(P63_CASE_IDS, start=1):
        indices = []
        for family in FAMILY_ORDER:
            index = len(handoff_orders) + 1
            indices.append(index)
            handoff_orders.append(
                {
                    "handoff_work_order_index": index,
                    "source_work_order_index": index,
                    "case_handoff_index": case_index,
                    "case_id": case_id,
                    "evidence_family": family,
                    "p57_evidence_slot_status": "missing",
                    "p59_attachment_slot_status": "not_attached",
                    "p61_work_order_status": "pending_not_attached",
                    "p63_handoff_status": "blocked_pending_operator_evidence",
                    "ready_to_mark": False,
                    "safe_action_label": (
                        "collect_jhora_screenshot"
                        if family == "jhora_screenshot_or_packet"
                        else "attach_parashara_light_manual_values"
                    ),
                }
            )
        case_rows.append(
            {
                "case_handoff_index": case_index,
                "case_id": case_id,
                "source_work_order_indices": indices,
                "required_evidence_families": FAMILY_ORDER,
                "work_order_statuses": {
                    "jhora_screenshot_or_packet": "pending_not_attached",
                    "parashara_light_manual_values_or_packet": "pending_not_attached",
                },
                "case_handoff_status": "blocked_pending_operator_evidence",
                "case_work_order_status": "blocked_pending_attachments",
                "ready_to_mark": False,
            }
        )
    return {
        "schema_version": "jyotish-core-evidence-attachment-handoff-v1",
        "domain": "witness_core_parity",
        "stage": "P63-A",
        "status": "blocked_pending_operator_evidence",
        "operator_note": "External evidence has not been attached; handoff rows are labels only and do not collect evidence.",
        "summary": {
            "case_handoff_rows": 5,
            "handoff_work_order_rows": 10,
            "pending_handoff_count": 10,
            "pending_jhora_handoff_count": 5,
            "pending_parashara_light_handoff_count": 5,
            "blocked_case_count": 5,
            "ready_to_mark_count": 0,
            "attached_evidence_files_count": 0,
            "attached_evidence_family_count": 0,
            "missing_attachment_slot_count": 10,
            "remaining_not_reviewed_count": 20,
            "release_gate_status": "blocked",
            "command_smoke_matrix_status": "ready",
        },
        "case_handoff_rows": case_rows,
        "handoff_work_order_rows": handoff_orders,
    }


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _serialized_safe(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False).lower()
    return all(marker.lower() not in text for marker in FORBIDDEN_MARKERS)
