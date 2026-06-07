import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def test_promote_jhora_witness_batch_promotes_ready_and_reports_blocked(tmp_path):
    from apps.calculations.management.commands.promote_jhora_witness_batch import (
        promote_jhora_witness_batch,
    )

    ready_dir = tmp_path / "jhora" / "ready"
    blocked_dir = tmp_path / "jhora" / "blocked"
    output_dir = tmp_path / "accuracy"
    ready_dir.mkdir(parents=True)
    blocked_dir.mkdir(parents=True)
    (ready_dir / "fixture.json").write_text(json.dumps(_reviewed_fixture("ready-case")), encoding="utf-8")
    blocked = _reviewed_fixture("blocked-case")
    blocked["review_status"] = "draft"
    (blocked_dir / "fixture.json").write_text(json.dumps(blocked), encoding="utf-8")

    payload = promote_jhora_witness_batch(jhora_root=tmp_path / "jhora", output_dir=output_dir)

    assert payload["summary"]["scanned_count"] == 2
    assert payload["summary"]["promoted_count"] == 1
    assert payload["summary"]["blocked_count"] == 1
    assert (output_dir / "ready-case.json").exists()
    blocked_row = next(row for row in payload["cases"] if row["id"] == "blocked-case")
    assert blocked_row["status"] == "blocked"
    assert "authoritative_review_status" in blocked_row["blockers"]


def test_promote_jhora_witness_batch_dry_run_reports_ready_without_writing(tmp_path):
    from apps.calculations.management.commands.promote_jhora_witness_batch import (
        promote_jhora_witness_batch,
    )

    case_dir = tmp_path / "jhora" / "ready"
    output_dir = tmp_path / "accuracy"
    case_dir.mkdir(parents=True)
    (case_dir / "packet.json").write_text(
        json.dumps({"fixture": _reviewed_fixture("ready-case")}),
        encoding="utf-8",
    )

    payload = promote_jhora_witness_batch(jhora_root=tmp_path / "jhora", output_dir=output_dir, dry_run=True)

    assert payload["summary"]["ready_count"] == 1
    assert payload["summary"]["promoted_count"] == 0
    assert not (output_dir / "ready-case.json").exists()
    assert payload["cases"][0]["status"] == "ready"


def test_promote_jhora_witness_batch_command_outputs_json(tmp_path):
    case_dir = tmp_path / "jhora" / "ready"
    output_dir = tmp_path / "accuracy"
    case_dir.mkdir(parents=True)
    (case_dir / "fixture.json").write_text(json.dumps(_reviewed_fixture("ready-case")), encoding="utf-8")
    stdout = StringIO()

    call_command(
        "promote_jhora_witness_batch",
        "--jhora-root",
        str(tmp_path / "jhora"),
        "--output-dir",
        str(output_dir),
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    assert payload["summary"]["promoted_count"] == 1
    assert payload["cases"][0]["status"] == "promoted"


def test_promote_jhora_witness_batch_command_can_fail_if_blocked(tmp_path):
    case_dir = tmp_path / "jhora" / "blocked"
    case_dir.mkdir(parents=True)
    fixture = _reviewed_fixture("blocked-case")
    fixture["review_status"] = "draft"
    (case_dir / "fixture.json").write_text(json.dumps(fixture), encoding="utf-8")

    with pytest.raises(CommandError, match="blocked"):
        call_command(
            "promote_jhora_witness_batch",
            "--jhora-root",
            str(tmp_path / "jhora"),
            "--output-dir",
            str(tmp_path / "accuracy"),
            "--fail-if-blocked",
        )


def _reviewed_fixture(fixture_id: str):
    return {
        "id": fixture_id,
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
        "expected": {"ascendant": {"longitude": 115.4, "rashi": "Karka"}},
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
