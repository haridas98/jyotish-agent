import json


def test_witness_review_preflight_reports_ack_required_commands(tmp_path):
    from apps.calculations.management.commands.preflight_witness_review import (
        build_witness_review_preflight,
    )

    jhora_dir = tmp_path / "jhora"
    pl_dir = tmp_path / "pl"
    jhora_dir.mkdir()
    pl_dir.mkdir()
    jhora_fixture = {
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
    pl_fixture = {
        "id": "pl-diff-open",
        "review_status": "draft",
        "pl_metadata": {
            "capture_status": "ui_state_captured",
            "ayanamsa": "lahiri",
            "timezone_offset": "+06:00",
        },
        "capture_files": {"ui_state": "pl-ui-state.json", "screenshots": ["screen.png"]},
        "manual_witness_values": [
            {"source": "pl7", "body": "Lagna", "witness": {"rashi": "Simha"}},
        ],
    }
    pl_packet = {
        "fixture": pl_fixture,
        "jyotish_agent_chart": {
            "ascendant": {"body": "Lagna", "rashi": "Karka", "rashi_index": 3},
            "grahas": [],
            "houses": [{"house": 1, "rashi": "Karka", "rashi_index": 3}],
        },
    }
    (jhora_dir / "fixture.json").write_text(json.dumps(jhora_fixture), encoding="utf-8")
    (pl_dir / "packet.json").write_text(json.dumps(pl_packet), encoding="utf-8")
    (pl_dir / "fixture.json").write_text(json.dumps(pl_fixture), encoding="utf-8")

    payload = build_witness_review_preflight(
        jhora_path=jhora_dir,
        parashara_light_path=pl_dir,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:00:00+05:00",
    )

    assert payload["overall"] == {
        "reviewable": True,
        "ack_required": True,
        "blocked": False,
    }
    assert payload["jhora"]["status"] == "diff_open"
    assert payload["jhora"]["ack_required"] is True
    assert payload["jhora"]["review_command"].startswith(".\\.venv\\Scripts\\python.exe manage.py")
    assert "--ack-diff-open" in payload["jhora"]["review_command"]
    assert payload["parashara_light"]["status"] == "diff_open"
    assert payload["parashara_light"]["ack_required"] is True
    assert payload["parashara_light"]["review_command"].startswith(".\\.venv\\Scripts\\python.exe manage.py")
    assert "--ack-diff-open" in payload["parashara_light"]["review_command"]
