import json

import pytest
from django.core.management.base import CommandError


def test_mark_jhora_witness_reviewed_updates_packet_and_fixture(tmp_path):
    from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
        mark_jhora_witness_reviewed,
    )

    case_dir = tmp_path / "sterlitamak"
    case_dir.mkdir()
    fixture = {
        "id": "sterlitamak-1998-04-30-1345",
        "review_status": "draft",
        "jhora_metadata": {
            "siddhanta_model": "drik_siddhanta",
            "ayanamsa": "lahiri",
            "timezone_offset": "+06:00",
            "reviewer": "",
            "reviewed_at": "",
        },
        "capture_files": {
            "complete_calculations_text": "jhora-complete-calculations.txt",
            "screenshots": ["screenshots/main.png"],
        },
        "jhora_expected": {"graha_positions": []},
    }
    packet = {"schema_version": "jyotish-jhora-verification-packet-v1", "fixture": fixture}
    (case_dir / "packet.json").write_text(json.dumps(packet), encoding="utf-8")
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")

    result = mark_jhora_witness_reviewed(
        case_dir,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:00:00+05:00",
    )

    assert result["status"] == "updated"
    saved_packet = json.loads((case_dir / "packet.json").read_text(encoding="utf-8"))
    saved_fixture = json.loads((case_dir / "fixture.json").read_text(encoding="utf-8"))
    assert saved_fixture["review_status"] == "jhora_verified"
    assert saved_packet["fixture"]["review_status"] == "jhora_verified"
    assert saved_fixture["jhora_metadata"]["reviewer"] == "Haridas"
    assert saved_fixture["jhora_metadata"]["reviewed_at"] == "2026-06-07T12:00:00+05:00"
    assert saved_packet["fixture"] == saved_fixture


def test_mark_jhora_witness_reviewed_refuses_incomplete_packet(tmp_path):
    from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
        mark_jhora_witness_reviewed,
    )

    case_dir = tmp_path / "missing-screenshots"
    case_dir.mkdir()
    (case_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "missing-screenshots",
                "review_status": "draft",
                "jhora_metadata": {"ayanamsa": "lahiri", "timezone_offset": "+06:00"},
                "capture_files": {"complete_calculations_text": "jhora-complete-calculations.txt"},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CommandError, match="jhora_screenshots"):
        mark_jhora_witness_reviewed(
            case_dir,
            reviewer="Haridas",
            reviewed_at="2026-06-07T12:00:00+05:00",
        )


def test_mark_jhora_witness_reviewed_requires_ack_for_open_accuracy_diff(tmp_path):
    from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
        mark_jhora_witness_reviewed,
    )

    case_dir = tmp_path / "jhora-diff-open"
    case_dir.mkdir()
    fixture = {
        "id": "jhora-diff-open",
        "review_status": "draft",
        "input": {
            "birth_date": "1998-04-30",
            "birth_time": "13:45:00",
            "place_name": "Sterlitamak",
            "timezone": "Asia/Yekaterinburg",
            "latitude": 53.6304,
            "longitude": 55.9502,
        },
        "expected": {"ascendant": {"longitude": 10.0, "rashi": "Mesha"}},
        "jhora_metadata": {
            "capture_status": "export_parsed",
            "ayanamsa": "lahiri",
            "timezone_offset": "+06:00",
        },
        "capture_files": {
            "complete_calculations_text": "jhora-complete-calculations.txt",
            "screenshots": ["screen.png"],
        },
        "jhora_expected": {"special_points": {}},
    }
    packet = {"schema_version": "jyotish-jhora-verification-packet-v1", "fixture": fixture}
    (case_dir / "packet.json").write_text(json.dumps(packet), encoding="utf-8")
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")

    with pytest.raises(CommandError, match="accuracy diff_open"):
        mark_jhora_witness_reviewed(
            case_dir,
            reviewer="Haridas",
            reviewed_at="2026-06-07T12:00:00+05:00",
        )

    result = mark_jhora_witness_reviewed(
        case_dir,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:00:00+05:00",
        ack_diff_open=True,
    )

    saved_fixture = json.loads((case_dir / "fixture.json").read_text(encoding="utf-8"))
    assert result["accuracy_status"] == "diff_open"
    assert saved_fixture["jhora_metadata"]["accuracy_diff_acknowledged"] is True
