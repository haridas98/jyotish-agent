import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def test_promote_jhora_witness_fixture_writes_authoritative_accuracy_fixture(tmp_path):
    from apps.calculations.management.commands.promote_jhora_witness_fixture import (
        promote_jhora_witness_fixture,
    )

    case_dir = tmp_path / "case"
    output_dir = tmp_path / "accuracy"
    case_dir.mkdir()
    fixture = _reviewed_fixture()
    (case_dir / "packet.json").write_text(json.dumps({"fixture": fixture}), encoding="utf-8")
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")

    result = promote_jhora_witness_fixture(case_dir, output_dir=output_dir)

    output_path = output_dir / "sterlitamak-1998-04-30-1345.json"
    promoted = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["status"] == "promoted"
    assert result["output_path"] == str(output_path)
    assert promoted["review_status"] == "jhora_verified"
    assert promoted["promotion_metadata"]["gate"] == "reviewed_jhora_witness"
    assert promoted["promotion_metadata"]["accuracy_status"] == "matched"


def test_promote_jhora_witness_fixture_refuses_draft_review_status(tmp_path):
    from apps.calculations.management.commands.promote_jhora_witness_fixture import (
        promote_jhora_witness_fixture,
    )

    case_dir = tmp_path / "case"
    case_dir.mkdir()
    fixture = _reviewed_fixture()
    fixture["review_status"] = "draft"
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")

    with pytest.raises(CommandError, match="authoritative_review_status"):
        promote_jhora_witness_fixture(case_dir, output_dir=tmp_path / "accuracy")


def test_promote_jhora_witness_fixture_requires_diff_ack(tmp_path):
    from apps.calculations.management.commands.promote_jhora_witness_fixture import (
        promote_jhora_witness_fixture,
    )

    case_dir = tmp_path / "case"
    case_dir.mkdir()
    fixture = _reviewed_fixture()
    fixture["jhora_metadata"]["accuracy_status"] = "diff_open"
    fixture["jhora_metadata"]["accuracy_diff_acknowledged"] = False
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")

    with pytest.raises(CommandError, match="accuracy_diff_acknowledgement"):
        promote_jhora_witness_fixture(case_dir, output_dir=tmp_path / "accuracy")


def test_promote_jhora_witness_fixture_command_outputs_json(tmp_path):
    case_dir = tmp_path / "case"
    output_dir = tmp_path / "accuracy"
    case_dir.mkdir()
    (case_dir / "fixture.json").write_text(json.dumps(_reviewed_fixture()), encoding="utf-8")
    stdout = StringIO()

    call_command(
        "promote_jhora_witness_fixture",
        str(case_dir),
        "--output-dir",
        str(output_dir),
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    assert payload["status"] == "promoted"
    assert payload["id"] == "sterlitamak-1998-04-30-1345"


def _reviewed_fixture():
    return {
        "id": "sterlitamak-1998-04-30-1345",
        "source": "jhora_complete_calculations_clipboard",
        "review_status": "jhora_verified",
        "input": {
            "birth_date": "1998-04-30",
            "birth_time": "13:45:00",
            "place_name": "Sterlitamak",
            "timezone": "Asia/Yekaterinburg",
            "latitude": 53.6304,
            "longitude": 55.9502,
        },
        "expected": {
            "ascendant": {"longitude": 115.4, "rashi": "Karka"},
            "grahas": {
                "Surya": {
                    "longitude": 15.9,
                    "rashi": "Mesha",
                    "nakshatra": "Bharani",
                    "pada": 1,
                }
            },
        },
        "jhora_metadata": {
            "capture_status": "export_parsed",
            "ayanamsa": "lahiri",
            "timezone_offset": "+06:00",
            "reviewer": "Haridas",
            "reviewed_at": "2026-06-07T12:00:00+05:00",
            "accuracy_status": "matched",
            "accuracy_diff_acknowledged": False,
        },
        "capture_files": {
            "complete_calculations_text": "jhora-complete-calculations.txt",
            "screenshots": ["main.png"],
        },
    }
