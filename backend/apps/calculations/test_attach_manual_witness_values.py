import json

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


def test_attach_manual_witness_values_updates_packet_and_sibling_fixture(tmp_path):
    from apps.calculations.management.commands.attach_manual_witness_values import (
        attach_manual_witness_values,
    )

    case_dir = tmp_path / "packet"
    case_dir.mkdir()
    fixture = {
        "id": "pl7-sterlitamak",
        "review_status": "draft",
        "capture_files": {"ui_state": "ui-state.json"},
        "manual_witness_values": [],
    }
    packet = {"schema_version": "test", "fixture": fixture}
    manual_values = [{"source": "pl7", "body": "Lagna", "witness": {"rashi": "Karka"}}]
    packet_path = case_dir / "packet.json"
    fixture_path = case_dir / "fixture.json"
    values_path = tmp_path / "manual-values.json"
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
    values_path.write_text(json.dumps(manual_values), encoding="utf-8")

    result = attach_manual_witness_values(packet_path, values_path)

    saved_packet = json.loads(packet_path.read_text(encoding="utf-8"))
    saved_fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert result["status"] == "updated"
    assert result["count"] == 1
    assert saved_packet["fixture"] == saved_fixture
    assert saved_fixture["manual_witness_values"] == manual_values
    assert saved_fixture["manual_witness_source"] == str(values_path)
    assert saved_fixture["capture_files"]["manual_witness_values"] == str(values_path)


def test_attach_manual_witness_values_rejects_non_array_file(tmp_path):
    from apps.calculations.management.commands.attach_manual_witness_values import (
        attach_manual_witness_values,
    )

    packet_path = tmp_path / "packet.json"
    values_path = tmp_path / "manual-values.json"
    packet_path.write_text(json.dumps({"fixture": {"id": "pl7"}}), encoding="utf-8")
    values_path.write_text(json.dumps({"body": "Lagna"}), encoding="utf-8")

    with pytest.raises(CommandError, match="JSON array"):
        attach_manual_witness_values(packet_path, values_path)


def test_attach_manual_witness_values_command_requires_one_target(tmp_path):
    values_path = tmp_path / "manual-values.json"
    values_path.write_text(json.dumps([]), encoding="utf-8")

    with pytest.raises(CommandError, match="Pass exactly one"):
        call_command("attach_manual_witness_values", "--manual-witness-values", str(values_path))
