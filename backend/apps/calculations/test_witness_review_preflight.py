import json
from io import StringIO

from django.core.management import call_command


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
    assert payload["seal_command"].startswith(".\\.venv\\Scripts\\python.exe manage.py seal_witness_case")
    assert "--jhora" in payload["seal_command"]
    assert "--parashara-light" in payload["seal_command"]
    assert "--ack-diff-open" in payload["seal_command"]


def test_witness_review_preflight_safe_next_only_hides_mutating_commands(tmp_path):
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
    stdout = StringIO()

    call_command(
        "preflight_witness_review",
        "--jhora",
        str(jhora_dir),
        "--parashara-light",
        str(pl_dir),
        "--safe-next-only",
        stdout=stdout,
    )

    text = stdout.getvalue()

    assert "reviewable: true" in text
    assert "ack required: true" in text
    assert "jhora status: diff_open" in text
    assert "parashara light status: diff_open" in text
    assert "safe next step: human ACK required before mark/seal" in text
    assert "seal_witness_case" not in text
    assert "mark_jhora_witness_reviewed" not in text
    assert "mark_parashara_light_witness_reviewed" not in text


def test_witness_review_preflight_quotes_powershell_metacharacters():
    from apps.calculations.management.commands.preflight_witness_review import (
        _review_command,
        _seal_command,
    )

    review_command = _review_command(
        "mark_jhora_witness_reviewed",
        "C:\\cases\\jhora'; Write-Error nope",
        reviewer="O'Brien; Stop-Process",
        reviewed_at="2026-06-07T12:00:00+05:00",
        ack_required=True,
    )
    seal_command = _seal_command(
        "C:\\cases\\jh&bad",
        "C:\\cases\\pl|bad",
        reviewer="O'Brien",
        reviewed_at="",
        ack_required=False,
    )

    assert "'C:\\cases\\jhora''; Write-Error nope'" in review_command
    assert "--reviewer 'O''Brien; Stop-Process'" in review_command
    assert "--reviewed-at '2026-06-07T12:00:00+05:00'" in review_command
    assert "--ack-diff-open" in review_command
    assert "--jhora 'C:\\cases\\jh&bad'" in seal_command
    assert "--parashara-light 'C:\\cases\\pl|bad'" in seal_command
    assert "--reviewer 'O''Brien'" in seal_command
