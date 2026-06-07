import json
from io import StringIO

from django.core.management import call_command


def test_build_witness_review_batch_packets_writes_paired_cases_and_skips_unpaired(tmp_path):
    from apps.calculations.management.commands.build_witness_review_batch_packets import (
        build_witness_review_batch_packets,
    )

    jhora_root, pl_root = _write_batch_roots(tmp_path)
    output_root = tmp_path / "review-packets"

    payload = build_witness_review_batch_packets(
        jhora_root=jhora_root,
        pl_root=pl_root,
        output_root=output_root,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:00:00+05:00",
    )

    assert payload["schema_version"] == "jyotish-witness-review-batch-packets-v1"
    assert payload["summary"]["written_count"] == 1
    assert payload["summary"]["skipped_count"] >= 1
    assert payload["summary"]["reviewable_count"] == 1
    assert payload["summary"]["blocked_count"] == 0
    assert payload["summary"]["ack_required_count"] == 1
    assert payload["summary"]["remaining_to_target_count"] >= 19
    next_action_by_id = {row["id"]: row for row in payload["next_actions"]}
    assert "vrindavan-1990-08-15-1024" in next_action_by_id
    assert "pl_witness_packet" in next_action_by_id["vrindavan-1990-08-15-1024"]["missing_secondary_witness"]
    assert (
        "attach_pl_witness_packet_or_manual_values"
        in next_action_by_id["vrindavan-1990-08-15-1024"]["suggested_actions"]
    )
    written = payload["written"][0]
    assert written["id"] == "sterlitamak-1998-04-30-1345"
    assert written["ack_required"] is True
    assert written["blocked"] is False
    assert [item["key"] for item in written["review_checklist"]] == [
        "jhora_evidence",
        "parashara_light_evidence",
        "open_diffs",
        "review_ack",
    ]
    assert written["review_checklist"][2]["status"] == "ack_required"
    assert (
        written["review_checklist_summary"]
        == "JHora evidence=ready; Parashara Light evidence=ready; Open diffs=ack_required; Manual ACK=ack_required"
    )
    assert payload["metadata"]["reviewer"] == "Haridas"
    assert payload["metadata"]["reviewed_at"] == "2026-06-07T12:00:00+05:00"
    assert payload["metadata"]["jhora_root"] == str(jhora_root)
    assert payload["metadata"]["pl_root"] == str(pl_root)
    assert payload["metadata"]["generated_at"]
    markdown = (output_root / "sterlitamak-1998-04-30-1345.md").read_text(encoding="utf-8")
    assert "ACK required: yes" in markdown
    assert "seal_witness_case" not in markdown
    index = (output_root / "_index.md").read_text(encoding="utf-8")
    assert payload["summary"]["index_path"] == str(output_root / "_index.md")
    assert payload["summary"]["index_json_path"] == str(output_root / "_index.json")
    assert "# Witness Review Batch Index" in index
    assert "Reviewer: Haridas" in index
    assert "Reviewed at: 2026-06-07T12:00:00+05:00" in index
    assert "Written: 1" in index
    assert "Reviewable packets: 1" in index
    assert "ACK-required packets: 1" in index
    assert "Skipped:" in index
    assert "sterlitamak-1998-04-30-1345" in index
    assert "ACK: yes" in index
    assert "Checklist: JHora evidence=ready; Parashara Light evidence=ready; Open diffs=ack_required; Manual ACK=ack_required" in index
    assert "missing_jhora_or_pl_pair" in index
    assert "## Next Actions" in index
    assert "vrindavan-1990-08-15-1024" in index
    index_json = json.loads((output_root / "_index.json").read_text(encoding="utf-8"))
    assert index_json["summary"]["written_count"] == 1
    assert index_json["summary"]["reviewable_count"] == 1
    assert index_json["metadata"]["reviewer"] == "Haridas"
    assert index_json["written"][0]["ack_required"] is True
    assert index_json["written"][0]["review_checklist"][3]["key"] == "review_ack"
    assert index_json["written"][0]["review_checklist_summary"] == written["review_checklist_summary"]
    assert any(row["id"] == "vrindavan-1990-08-15-1024" for row in index_json["next_actions"])


def test_build_witness_review_batch_packets_command_outputs_json(tmp_path):
    jhora_root, pl_root = _write_batch_roots(tmp_path)
    output_root = tmp_path / "review-packets"
    stdout = StringIO()

    call_command(
        "build_witness_review_batch_packets",
        "--jhora-root",
        str(jhora_root),
        "--pl-root",
        str(pl_root),
        "--output-root",
        str(output_root),
        "--reviewer",
        "Haridas",
        "--reviewed-at",
        "2026-06-07T12:00:00+05:00",
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    assert payload["summary"]["written_count"] == 1
    assert payload["metadata"]["reviewer"] == "Haridas"
    assert payload["written"][0]["output_path"].endswith("sterlitamak-1998-04-30-1345.md")
    assert payload["summary"]["index_path"].endswith("_index.md")
    assert payload["summary"]["index_json_path"].endswith("_index.json")
    assert payload["next_actions"]
    assert (output_root / "_index.md").exists()
    assert (output_root / "_index.json").exists()


def test_build_witness_review_batch_packets_command_text_shows_checklist(tmp_path):
    jhora_root, pl_root = _write_batch_roots(tmp_path)
    output_root = tmp_path / "review-packets"
    stdout = StringIO()

    call_command(
        "build_witness_review_batch_packets",
        "--jhora-root",
        str(jhora_root),
        "--pl-root",
        str(pl_root),
        "--output-root",
        str(output_root),
        "--reviewer",
        "Haridas",
        "--reviewed-at",
        "2026-06-07T12:00:00+05:00",
        stdout=stdout,
    )

    text = stdout.getvalue()
    assert "sterlitamak-1998-04-30-1345" in text
    assert "checklist=JHora evidence=ready; Parashara Light evidence=ready; Open diffs=ack_required; Manual ACK=ack_required" in text
    assert "seal_witness_case" not in text


def _write_batch_roots(tmp_path):
    jhora_root = tmp_path / "jhora"
    pl_root = tmp_path / "pl7"
    jhora_dir = jhora_root / "sterlitamak"
    pl_dir = pl_root / "haridas"
    vrindavan_dir = jhora_root / "vrindavan"
    jhora_dir.mkdir(parents=True)
    pl_dir.mkdir(parents=True)
    vrindavan_dir.mkdir(parents=True)
    input_data = {
        "birth_date": "1998-04-30",
        "birth_time": "13:45:00",
        "place_name": "Sterlitamak",
        "timezone": "Asia/Yekaterinburg",
        "latitude": 53.6304,
        "longitude": 55.9502,
    }
    jhora_fixture = {
        "id": "sterlitamak-1998-04-30-1345",
        "review_status": "draft",
        "input": input_data,
        "expected": {"ascendant": {"longitude": 10.0, "rashi": "Mesha"}},
        "jhora_metadata": {
            "capture_status": "export_parsed",
            "ayanamsa": "Lahiri",
            "timezone_offset": "+06:00",
        },
        "capture_files": {
            "complete_calculations_text": "complete-calculations.txt",
            "screenshots": ["main.png"],
        },
        "jhora_expected": {"special_points": {}},
    }
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
    (jhora_dir / "fixture.json").write_text(json.dumps(jhora_fixture), encoding="utf-8")
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
    (vrindavan_dir / "fixture.json").write_text(
        json.dumps(
            {
                "id": "vrindavan-1990-08-15-1024",
                "review_status": "draft",
                "input": {
                    "birth_date": "1990-08-15",
                    "birth_time": "10:24:00",
                    "place_name": "Vrindavan",
                },
                "jhora_metadata": {"capture_status": "export_parsed", "ayanamsa": "Lahiri"},
                "capture_files": {"complete_calculations_text": "complete.txt"},
            }
        ),
        encoding="utf-8",
    )
    return jhora_root, pl_root
