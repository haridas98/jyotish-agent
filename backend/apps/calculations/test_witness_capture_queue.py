import json
from io import StringIO

from django.core.management import call_command


def test_build_witness_capture_queue_writes_json_and_markdown(tmp_path):
    from apps.calculations.management.commands.build_witness_capture_queue import build_witness_capture_queue

    output = tmp_path / "capture-queue.json"
    markdown_output = tmp_path / "capture-queue.md"

    payload = build_witness_capture_queue(
        jhora_root=tmp_path / "missing-jhora",
        pl_root=tmp_path / "missing-pl",
        output=output,
        markdown_output=markdown_output,
        target_reviewed_count=20,
        limit=2,
    )

    assert payload["schema_version"] == "jyotish-witness-capture-queue-v1"
    assert payload["summary"]["queue_count"] == 2
    assert payload["summary"]["remaining_to_target_count"] == 20
    first = payload["items"][0]
    assert first["priority"] == 1
    assert first["id"] == "sterlitamak-1998-04-30-1345"
    assert first["capture_targets"]["jhora"] == [
        "jhora_packet",
        "jhora_complete_calculations_text",
        "jhora_settings_evidence",
        "jhora_screenshots",
        "reviewer_note",
    ]
    assert first["capture_targets"]["parashara_light"] == ["pl_witness_packet"]
    assert "build_jhora_witness_batch_packets" in first["suggested_actions"]
    assert json.loads(output.read_text(encoding="utf-8"))["summary"]["queue_count"] == 2
    markdown = markdown_output.read_text(encoding="utf-8")
    assert "# Witness Capture Queue" in markdown
    assert "sterlitamak-1998-04-30-1345" in markdown
    assert "PL blockers: pl_witness_packet" in markdown


def test_build_witness_capture_queue_command_outputs_json(tmp_path):
    output = tmp_path / "capture-queue.json"
    markdown_output = tmp_path / "capture-queue.md"
    stdout = StringIO()

    call_command(
        "build_witness_capture_queue",
        "--jhora-root",
        str(tmp_path / "missing-jhora"),
        "--pl-root",
        str(tmp_path / "missing-pl"),
        "--output",
        str(output),
        "--markdown-output",
        str(markdown_output),
        "--limit",
        "1",
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    assert payload["summary"]["queue_count"] == 1
    assert payload["items"][0]["priority"] == 1
    assert output.exists()
    assert markdown_output.exists()
