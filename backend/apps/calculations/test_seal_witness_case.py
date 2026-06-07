import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.calculations.chart import build_birth_chart


def test_seal_witness_case_marks_both_witnesses_and_promotes_jhora(tmp_path):
    from apps.calculations.management.commands.seal_witness_case import seal_witness_case

    jhora_dir, pl_dir, output_dir = _case_dirs(tmp_path)
    chart = _write_ready_case(jhora_dir, pl_dir)

    payload = seal_witness_case(
        jhora_path=jhora_dir,
        parashara_light_path=pl_dir,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:00:00+05:00",
        promotion_output_dir=output_dir,
    )

    jhora_fixture = json.loads((jhora_dir / "fixture.json").read_text(encoding="utf-8"))
    pl_fixture = json.loads((pl_dir / "fixture.json").read_text(encoding="utf-8"))
    promoted = json.loads((output_dir / "sterlitamak-1998-04-30-1345.json").read_text(encoding="utf-8"))
    assert payload["status"] == "sealed"
    assert jhora_fixture["review_status"] == "jhora_verified"
    assert jhora_fixture["jhora_metadata"]["accuracy_status"] == "matched"
    assert pl_fixture["review_status"] == "reviewed"
    assert pl_fixture["pl_metadata"]["manual_witness_status"] == "matched"
    assert promoted["promotion_metadata"]["gate"] == "reviewed_jhora_witness"
    assert promoted["expected"]["ascendant"]["rashi"] == chart["ascendant"]["rashi"]


def test_seal_witness_case_dry_run_does_not_write(tmp_path):
    from apps.calculations.management.commands.seal_witness_case import seal_witness_case

    jhora_dir, pl_dir, output_dir = _case_dirs(tmp_path)
    _write_ready_case(jhora_dir, pl_dir)

    payload = seal_witness_case(
        jhora_path=jhora_dir,
        parashara_light_path=pl_dir,
        reviewer="Haridas",
        reviewed_at="2026-06-07T12:00:00+05:00",
        promotion_output_dir=output_dir,
        dry_run=True,
    )

    jhora_fixture = json.loads((jhora_dir / "fixture.json").read_text(encoding="utf-8"))
    pl_fixture = json.loads((pl_dir / "fixture.json").read_text(encoding="utf-8"))
    assert payload["status"] == "ready"
    assert jhora_fixture["review_status"] == "draft"
    assert pl_fixture["review_status"] == "draft"
    assert not (output_dir / "sterlitamak-1998-04-30-1345.json").exists()


def test_seal_witness_case_requires_ack_for_open_diffs(tmp_path):
    from apps.calculations.management.commands.seal_witness_case import seal_witness_case

    jhora_dir, pl_dir, output_dir = _case_dirs(tmp_path)
    _write_ready_case(jhora_dir, pl_dir, diff_open=True)

    with pytest.raises(CommandError, match="ack-diff-open"):
        seal_witness_case(
            jhora_path=jhora_dir,
            parashara_light_path=pl_dir,
            reviewer="Haridas",
            reviewed_at="2026-06-07T12:00:00+05:00",
            promotion_output_dir=output_dir,
        )


def test_seal_witness_case_command_outputs_json(tmp_path):
    jhora_dir, pl_dir, output_dir = _case_dirs(tmp_path)
    _write_ready_case(jhora_dir, pl_dir)
    stdout = StringIO()

    call_command(
        "seal_witness_case",
        "--jhora",
        str(jhora_dir),
        "--parashara-light",
        str(pl_dir),
        "--reviewer",
        "Haridas",
        "--reviewed-at",
        "2026-06-07T12:00:00+05:00",
        "--promotion-output-dir",
        str(output_dir),
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    assert payload["status"] == "sealed"
    assert payload["promotion"]["status"] == "promoted"


def _case_dirs(tmp_path):
    jhora_dir = tmp_path / "jhora" / "sterlitamak"
    pl_dir = tmp_path / "pl7" / "sterlitamak"
    output_dir = tmp_path / "accuracy"
    jhora_dir.mkdir(parents=True)
    pl_dir.mkdir(parents=True)
    return jhora_dir, pl_dir, output_dir


def _write_ready_case(jhora_dir, pl_dir, *, diff_open: bool = False):
    input_data = {
        "birth_date": "1998-04-30",
        "birth_time": "13:45:00",
        "place_name": "Sterlitamak",
        "timezone": "Asia/Yekaterinburg",
        "latitude": 53.6304,
        "longitude": 55.9502,
    }
    chart = build_birth_chart(input_data)
    expected_longitude = float(chart["ascendant"]["longitude"]) + (10.0 if diff_open else 0.0)
    jhora_fixture = {
        "id": "sterlitamak-1998-04-30-1345",
        "source": "jhora_complete_calculations_clipboard",
        "review_status": "draft",
        "input": input_data,
        "expected": {
            "ascendant": {
                "longitude": expected_longitude,
                "rashi": chart["ascendant"]["rashi"],
            }
        },
        "jhora_metadata": {
            "capture_status": "export_parsed",
            "ayanamsa": "lahiri",
            "timezone_offset": "+06:00",
        },
        "capture_files": {
            "complete_calculations_text": "jhora-complete-calculations.txt",
            "screenshots": ["main.png"],
        },
    }
    pl_fixture = {
        "id": "pl7-sterlitamak-1998",
        "source": "parashara_light_manual_witness",
        "review_status": "draft",
        "input": input_data,
        "pl_metadata": {
            "capture_status": "ui_state_captured",
            "ayanamsa": "lahiri",
            "timezone_offset": "+06:00",
        },
        "capture_files": {"ui_state": "state.json", "screenshots": ["pl.png"]},
        "manual_witness_values": [
            {
                "source": "pl7",
                "body": "Lagna",
                "witness": {"rashi": "Simha" if diff_open else chart["ascendant"]["rashi"]},
            }
        ],
    }
    (jhora_dir / "packet.json").write_text(json.dumps({"fixture": jhora_fixture}), encoding="utf-8")
    (jhora_dir / "fixture.json").write_text(json.dumps(jhora_fixture), encoding="utf-8")
    (pl_dir / "packet.json").write_text(
        json.dumps({"fixture": pl_fixture, "jyotish_agent_chart": chart}),
        encoding="utf-8",
    )
    (pl_dir / "fixture.json").write_text(json.dumps(pl_fixture), encoding="utf-8")
    return chart
