import json
from io import StringIO

from django.core.management import call_command


def test_build_witness_review_packet_renders_safe_markdown_by_default(tmp_path):
    from apps.calculations.management.commands.build_witness_review_packet import (
        build_witness_review_packet,
    )

    jhora_dir, pl_dir = _write_diff_open_case(tmp_path)

    payload = build_witness_review_packet(
        jhora_path=jhora_dir,
        parashara_light_path=pl_dir,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:00:00+05:00",
    )

    markdown = payload["markdown"]
    assert payload["schema_version"] == "jyotish-witness-review-packet-v1"
    assert payload["output_path"] == ""
    assert payload["preflight"]["overall"]["ack_required"] is True
    assert "# Witness Review Packet" in markdown
    assert "Reviewable: yes" in markdown
    assert "ACK required: yes" in markdown
    assert "jhora-diff-open" in markdown
    assert "pl-diff-open" in markdown
    assert "status: diff_open" in markdown
    assert "safe next step: human ACK required before mark/seal" in markdown
    assert "mark_jhora_witness_reviewed" not in markdown
    assert "mark_parashara_light_witness_reviewed" not in markdown
    assert "seal_witness_case" not in markdown
    assert "--ack-diff-open" not in markdown
    assert "Do not run seal until manual evidence review and diff ACK are complete." in markdown


def test_build_witness_review_packet_can_render_review_commands_explicitly(tmp_path):
    from apps.calculations.management.commands.build_witness_review_packet import (
        build_witness_review_packet,
    )

    jhora_dir, pl_dir = _write_diff_open_case(tmp_path)

    payload = build_witness_review_packet(
        jhora_path=jhora_dir,
        parashara_light_path=pl_dir,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:00:00+05:00",
        include_review_commands=True,
    )

    markdown = payload["markdown"]

    assert "mark_jhora_witness_reviewed" in markdown
    assert "mark_parashara_light_witness_reviewed" in markdown
    assert "seal_witness_case" in markdown
    assert "--ack-diff-open" in markdown
    assert markdown.index("mark_jhora_witness_reviewed") < markdown.index("## Parashara Light")
    assert markdown.index("## Parashara Light") < markdown.index("mark_parashara_light_witness_reviewed")


def test_build_witness_review_packet_command_writes_output_and_json(tmp_path):
    jhora_dir, pl_dir = _write_diff_open_case(tmp_path)
    output_path = tmp_path / "packet.md"
    stdout = StringIO()

    call_command(
        "build_witness_review_packet",
        "--jhora",
        str(jhora_dir),
        "--parashara-light",
        str(pl_dir),
        "--reviewer",
        "Haridas",
        "--reviewed-at",
        "2026-06-07T12:00:00+05:00",
        "--output",
        str(output_path),
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    markdown = output_path.read_text(encoding="utf-8")
    assert payload["status"] == "written"
    assert payload["output_path"] == str(output_path)
    assert "# Witness Review Packet" in markdown
    assert "ACK required: yes" in markdown


def _write_diff_open_case(tmp_path):
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
    return jhora_dir, pl_dir
