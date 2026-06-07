import json

import pytest
from django.core.management.base import CommandError


def test_mark_parashara_light_witness_reviewed_updates_packet_and_fixture(tmp_path):
    from apps.calculations.management.commands.mark_parashara_light_witness_reviewed import (
        mark_parashara_light_witness_reviewed,
    )

    case_dir = tmp_path / "pl-sterlitamak"
    case_dir.mkdir()
    fixture = {
        "id": "pl7-sterlitamak-1998",
        "review_status": "draft",
        "pl_metadata": {
            "capture_status": "ui_state_captured",
            "ayanamsa": "lahiri",
            "timezone_offset": "+06:00",
            "reviewer": "",
            "reviewed_at": "",
        },
        "capture_files": {
            "ui_state": "pl-ui-state.json",
            "screenshots": ["screenshots/main.png"],
        },
        "manual_witness_values": [{"body": "Lagna", "rashi": "Karka"}],
    }
    packet = {"schema_version": "jyotish-parashara-light-verification-packet-v1", "fixture": fixture}
    (case_dir / "packet.json").write_text(json.dumps(packet), encoding="utf-8")
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")

    result = mark_parashara_light_witness_reviewed(
        case_dir,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:30:00+05:00",
    )

    saved_packet = json.loads((case_dir / "packet.json").read_text(encoding="utf-8"))
    saved_fixture = json.loads((case_dir / "fixture.json").read_text(encoding="utf-8"))
    assert result["status"] == "updated"
    assert saved_fixture["review_status"] == "reviewed"
    assert saved_packet["fixture"]["review_status"] == "reviewed"
    assert saved_fixture["pl_metadata"]["reviewer"] == "Haridas"
    assert saved_fixture["pl_metadata"]["reviewed_at"] == "2026-06-07T12:30:00+05:00"
    assert saved_packet["fixture"] == saved_fixture


def test_mark_parashara_light_witness_reviewed_refuses_incomplete_packet(tmp_path):
    from apps.calculations.management.commands.mark_parashara_light_witness_reviewed import (
        mark_parashara_light_witness_reviewed,
    )

    case_dir = tmp_path / "pl-incomplete"
    case_dir.mkdir()
    (case_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "pl-incomplete",
                "review_status": "draft",
                "pl_metadata": {"capture_status": "ui_state_captured", "timezone_offset": "+06:00"},
                "capture_files": {"ui_state": "pl-ui-state.json", "screenshots": []},
                "manual_witness_values": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(CommandError, match="pl_screenshots"):
        mark_parashara_light_witness_reviewed(
            case_dir,
            reviewer="Haridas",
            reviewed_at="2026-06-07T12:30:00+05:00",
        )
