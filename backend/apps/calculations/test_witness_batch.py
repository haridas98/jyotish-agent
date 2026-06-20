import io
import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def test_audit_jhora_pl_witness_batch_reports_missing_queue(tmp_path):
    from apps.calculations.witness_batch import audit_jhora_pl_witness_batch

    payload = audit_jhora_pl_witness_batch(
        jhora_root=tmp_path / "missing-jhora",
        pl_root=tmp_path / "missing-pl",
        target_reviewed_count=20,
    )

    assert payload["schema_version"] == "jyotish-witness-batch-audit-v1"
    assert payload["summary"]["suite_case_count"] >= 20
    assert payload["summary"]["review_batch_contract"]["coverage_target_met"] is True
    assert payload["summary"]["review_batch_contract"]["target_reviewed_count"] == 20
    assert payload["summary"]["review_batch_contract"]["missing_required_groups"] == []
    assert payload["summary"]["review_batch_contract"]["missing_required_focus"] == []
    assert payload["review_batch_contract"] == payload["summary"]["review_batch_contract"]
    assert payload["summary"]["authoritative_ready_count"] == 0
    assert payload["summary"]["target_met"] is False
    assert "sterlitamak-1998-04-30-1345" in payload["summary"]["next_case_ids"]
    first_action = payload["next_actions"][0]
    assert first_action["id"] == "sterlitamak-1998-04-30-1345"
    assert first_action["missing_for_authoritative_review"] == [
        "jhora_packet",
        "jhora_complete_calculations_text",
        "jhora_settings_evidence",
        "jhora_screenshots",
        "reviewer_note",
    ]
    assert first_action["missing_secondary_witness"] == ["pl_witness_packet"]
    assert first_action["suggested_actions"] == [
        "build_jhora_witness_batch_packets",
        "capture_jhora_witness_batch_exports_or_attach_jhora_complete_calculations",
        "record_jhora_settings_and_timezone_dst_evidence",
        "attach_jhora_screenshots",
        "add_reviewer_and_reviewed_at",
        "attach_pl_witness_packet_or_manual_values",
    ]
    assert first_action["suggested_action_labels"] == [
        "Build JHora witness packet",
        "Capture JHora complete export",
        "Record JHora settings and DST evidence",
        "Attach JHora screenshots",
        "Add reviewer after manual review",
        "Attach PL witness values",
    ]


def test_witness_batch_action_labels_cover_all_missing_artifact_actions():
    from apps.calculations.witness_action_labels import ACTION_LABELS
    from apps.calculations.witness_batch import ACTION_BY_MISSING_ARTIFACT

    missing_labels = sorted(set(ACTION_BY_MISSING_ARTIFACT.values()) - set(ACTION_LABELS))

    assert missing_labels == []


def test_audit_jhora_pl_witness_batch_matches_draft_jhora_and_pl_by_birth_key(tmp_path):
    from apps.calculations.witness_batch import audit_jhora_pl_witness_batch

    jhora_dir = tmp_path / "jhora" / "sterlitamak"
    pl_dir = tmp_path / "pl7" / "haridas"
    jhora_dir.mkdir(parents=True)
    pl_dir.mkdir(parents=True)
    input_data = {
        "birth_date": "1998-04-30",
        "birth_time": "13:45:00",
        "place_name": "Sterlitamak",
        "timezone": "Asia/Yekaterinburg",
    }
    (jhora_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "sterlitamak-1998-04-30-1345",
                "review_status": "draft",
                "input": input_data,
                "jhora_metadata": {
                    "capture_status": "export_parsed",
                    "ayanamsa": "Lahiri",
                    "timezone_offset": "+06:00",
                },
                "capture_files": {
                    "complete_calculations_text": "complete-calculations.txt",
                    "screenshots": ["main.png"],
                },
            }
        ),
        encoding="utf-8",
    )
    (pl_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "pl7-haridas-1998",
                "review_status": "draft",
                "input": input_data,
                "pl_metadata": {"capture_status": "ui_state_captured"},
                "capture_files": {"ui_state": "state.json", "screenshots": ["pl.png"]},
            }
        ),
        encoding="utf-8",
    )

    payload = audit_jhora_pl_witness_batch(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    case = next(row for row in payload["cases"] if row["id"] == "sterlitamak-1998-04-30-1345")

    assert case["status"] == "jhora_review_pending"
    assert case["capture_started"] is True
    assert case["pl_records"]
    assert case["secondary_witness_ready"] is False
    assert case["missing_secondary_witness"] == [
        "pl_settings_evidence",
        "manual_witness_values",
        "pl_reviewer_note",
        "pl_review_status",
    ]
    assert case["missing_for_authoritative_review"] == [
        "authoritative_review_status",
        "reviewer",
        "reviewed_at",
        "expected_or_jhora_expected",
    ]
    jhora_contract = case["jhora_records"][0]["witness_contract"]
    pl_contract = case["pl_records"][0]["witness_contract"]
    assert jhora_contract["source_type"] == "jhora"
    assert jhora_contract["unified_status"] == "draft"
    assert "review" in jhora_contract["missing_evidence_groups"]
    assert "diffs" in jhora_contract["missing_evidence_groups"]
    assert pl_contract["source_type"] == "parashara_light"
    assert pl_contract["unified_status"] == "draft"
    assert "settings_evidence" in pl_contract["missing_evidence_groups"]
    assert payload["summary"]["capture_started_count"] == 1
    assert payload["summary"]["pl_witness_count"] == 1
    assert payload["summary"]["pl_reviewed_count"] == 0
    assert payload["summary"]["batch_review_ready_count"] == 0


def test_audit_jhora_pl_witness_batch_counts_authoritative_reviewed_case(tmp_path):
    from apps.calculations.witness_batch import audit_jhora_pl_witness_batch

    jhora_dir = tmp_path / "jhora" / "sterlitamak"
    jhora_dir.mkdir(parents=True)
    (jhora_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "sterlitamak-1998-04-30-1345",
                "review_status": "jhora_verified",
                "input": {
                    "birth_date": "1998-04-30",
                    "birth_time": "13:45:00",
                    "place_name": "Sterlitamak",
                },
                "jhora_metadata": {
                    "capture_status": "export_parsed",
                    "ayanamsa": "Lahiri",
                    "timezone_offset": "+06:00",
                    "reviewer": "Haridas",
                    "reviewed_at": "2026-06-07T00:00:00+00:00",
                    "accuracy_status": "matched",
                },
                "capture_files": {
                    "complete_calculations_text": "complete-calculations.txt",
                    "screenshots": ["main.png"],
                },
                "expected": {"ascendant": {"longitude": 115.4, "rashi": "Karka"}},
            }
        ),
        encoding="utf-8",
    )

    payload = audit_jhora_pl_witness_batch(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    case = next(row for row in payload["cases"] if row["id"] == "sterlitamak-1998-04-30-1345")

    assert case["status"] == "authoritative_ready"
    assert case["authoritative_ready"] is True
    assert case["batch_review_ready"] is False
    assert case["jhora_records"][0]["witness_contract"]["unified_status"] == "promoted"
    assert case["missing_for_authoritative_review"] == []
    assert payload["summary"]["authoritative_ready_count"] == 1


def test_audit_jhora_pl_witness_batch_does_not_count_reviewed_case_without_expected_data(tmp_path):
    from apps.calculations.witness_batch import audit_jhora_pl_witness_batch

    jhora_dir = tmp_path / "jhora" / "sterlitamak"
    jhora_dir.mkdir(parents=True)
    (jhora_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "sterlitamak-1998-04-30-1345",
                "review_status": "jhora_verified",
                "input": {
                    "birth_date": "1998-04-30",
                    "birth_time": "13:45:00",
                    "place_name": "Sterlitamak",
                },
                "jhora_metadata": {
                    "capture_status": "export_parsed",
                    "ayanamsa": "Lahiri",
                    "timezone_offset": "+06:00",
                    "reviewer": "Haridas",
                    "reviewed_at": "2026-06-07T00:00:00+00:00",
                    "accuracy_status": "matched",
                },
                "capture_files": {
                    "complete_calculations_text": "complete-calculations.txt",
                    "screenshots": ["main.png"],
                },
            }
        ),
        encoding="utf-8",
    )

    payload = audit_jhora_pl_witness_batch(jhora_root=tmp_path / "jhora", pl_root=tmp_path / "pl7")
    case = next(row for row in payload["cases"] if row["id"] == "sterlitamak-1998-04-30-1345")

    assert case["status"] == "jhora_review_pending"
    assert case["authoritative_ready"] is False
    assert case["missing_for_authoritative_review"] == ["expected_or_jhora_expected"]


def test_audit_jhora_pl_witness_batch_counts_fully_reviewed_jhora_and_pl_case(tmp_path):
    from apps.calculations.witness_batch import audit_jhora_pl_witness_batch

    input_data = {
        "birth_date": "1998-04-30",
        "birth_time": "13:45:00",
        "place_name": "Sterlitamak",
    }
    jhora_dir = tmp_path / "jhora" / "sterlitamak"
    pl_dir = tmp_path / "pl7" / "haridas"
    jhora_dir.mkdir(parents=True)
    pl_dir.mkdir(parents=True)
    (jhora_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "sterlitamak-1998-04-30-1345",
                "review_status": "jhora_verified",
                "input": input_data,
                "jhora_metadata": {
                    "capture_status": "export_parsed",
                    "ayanamsa": "Lahiri",
                    "timezone_offset": "+06:00",
                    "reviewer": "Haridas",
                    "reviewed_at": "2026-06-07T00:00:00+00:00",
                    "accuracy_status": "matched",
                },
                "capture_files": {
                    "complete_calculations_text": "complete-calculations.txt",
                    "screenshots": ["main.png"],
                },
                "expected": {"ascendant": {"longitude": 115.4, "rashi": "Karka"}},
            }
        ),
        encoding="utf-8",
    )
    (pl_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "pl7-haridas-1998",
                "review_status": "reviewed",
                "input": input_data,
                "pl_metadata": {
                    "capture_status": "ui_state_captured",
                    "ayanamsa": "Lahiri",
                    "timezone_offset": "+06:00",
                    "reviewer": "Haridas",
                    "reviewed_at": "2026-06-07T00:30:00+00:00",
                },
                "capture_files": {"ui_state": "state.json", "screenshots": ["pl.png"]},
                "manual_witness_values": [{"body": "Lagna", "rashi": "Karka"}],
            }
        ),
        encoding="utf-8",
    )

    payload = audit_jhora_pl_witness_batch(
        jhora_root=tmp_path / "jhora",
        pl_root=tmp_path / "pl7",
        target_reviewed_count=1,
    )
    case = next(row for row in payload["cases"] if row["id"] == "sterlitamak-1998-04-30-1345")

    assert case["authoritative_ready"] is True
    assert case["secondary_witness_ready"] is True
    assert case["batch_review_ready"] is True
    assert case["jhora_records"][0]["witness_contract"]["unified_status"] == "promoted"
    assert case["pl_records"][0]["witness_contract"]["unified_status"] == "reviewed"
    assert case["witness_contract"]["status_counts"]["promoted"] == 1
    assert case["witness_contract"]["status_counts"]["reviewed"] == 1
    assert case["missing_secondary_witness"] == []
    assert payload["summary"]["pl_reviewed_count"] == 1
    assert payload["summary"]["batch_review_ready_count"] == 1
    assert payload["summary"]["target_met"] is True


def test_audit_jhora_pl_witness_batch_can_include_review_preflight_ack_requirement(tmp_path):
    from apps.calculations.witness_batch import audit_jhora_pl_witness_batch

    input_data = {
        "birth_date": "1998-04-30",
        "birth_time": "13:45:00",
        "place_name": "Sterlitamak",
        "timezone": "Asia/Yekaterinburg",
        "latitude": 53.6304,
        "longitude": 55.9502,
    }
    jhora_dir = tmp_path / "jhora" / "sterlitamak"
    pl_dir = tmp_path / "pl7" / "haridas"
    jhora_dir.mkdir(parents=True)
    pl_dir.mkdir(parents=True)
    (jhora_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "sterlitamak-1998-04-30-1345",
                "review_status": "draft",
                "input": input_data,
                "expected": {"ascendant": {"longitude": 10.0, "rashi": "Mesha"}},
                "jhora_metadata": {
                    "capture_status": "export_parsed",
                    "ayanamsa": "Lahiri",
                    "timezone_offset": "+06:00",
                    "accuracy_status": "diff_open",
                },
                "capture_files": {
                    "complete_calculations_text": "complete-calculations.txt",
                    "screenshots": ["main.png"],
                },
                "jhora_expected": {"special_points": {}},
            }
        ),
        encoding="utf-8",
    )
    pl_fixture = {
        "id": "pl7-haridas-1998",
        "review_status": "draft",
        "input": input_data,
        "pl_metadata": {
            "capture_status": "ui_state_captured",
            "ayanamsa": "Lahiri",
            "timezone_offset": "+06:00",
        },
        "capture_files": {"ui_state": "state.json", "screenshots": ["pl.png"]},
        "manual_witness_values": [
            {"source": "pl7", "body": "Lagna", "witness": {"rashi": "Simha"}},
        ],
    }
    (pl_dir / "packet.json").write_text(
        json.dumps(
            {
                "fixture": pl_fixture,
                "jyotish_agent_chart": {
                    "ascendant": {"body": "Lagna", "rashi": "Karka", "rashi_index": 3},
                    "grahas": [],
                    "houses": [{"house": 1, "rashi": "Karka", "rashi_index": 3}],
                },
            }
        ),
        encoding="utf-8",
    )
    (pl_dir / "fixture.json").write_text(json.dumps(pl_fixture), encoding="utf-8")

    payload = audit_jhora_pl_witness_batch(
        jhora_root=tmp_path / "jhora",
        pl_root=tmp_path / "pl7",
        target_reviewed_count=1,
        include_review_preflight=True,
    )

    first_action = payload["next_actions"][0]
    assert first_action["id"] == "sterlitamak-1998-04-30-1345"
    assert first_action["review_preflight"]["overall"]["ack_required"] is True
    assert first_action["review_preflight"]["jhora"]["status"] == "diff_open"
    assert first_action["review_preflight"]["parashara_light"]["status"] == "diff_open"
    case = next(row for row in payload["cases"] if row["id"] == "sterlitamak-1998-04-30-1345")
    assert case["jhora_records"][0]["witness_contract"]["unified_status"] == "diff_open"
    assert case["jhora_records"][0]["witness_contract"]["has_open_diffs"] is True


def test_audit_jhora_witness_batch_command_outputs_json_and_can_fail(tmp_path):
    stdout = io.StringIO()
    call_command(
        "audit_jhora_witness_batch",
        "--jhora-root",
        str(tmp_path / "jhora"),
        "--pl-root",
        str(tmp_path / "pl7"),
        "--json",
        stdout=stdout,
    )
    payload = json.loads(stdout.getvalue())
    assert payload["summary"]["target_met"] is False
    assert "suggested_action_labels" in payload["next_actions"][0]

    text_stdout = io.StringIO()
    call_command(
        "audit_jhora_witness_batch",
        "--jhora-root",
        str(tmp_path / "jhora"),
        "--pl-root",
        str(tmp_path / "pl7"),
        stdout=text_stdout,
    )
    assert "Build JHora witness packet" in text_stdout.getvalue()

    with pytest.raises(CommandError, match="witness target is not met"):
        call_command(
            "audit_jhora_witness_batch",
            "--jhora-root",
            str(tmp_path / "jhora"),
            "--pl-root",
            str(tmp_path / "pl7"),
            "--fail-if-target-missing",
        )
