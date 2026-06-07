import json
from io import StringIO

from django.core.management import call_command


def test_build_parashara_light_witness_batch_packets_scaffolds_selected_cases(tmp_path):
    from apps.calculations.management.commands.build_parashara_light_witness_batch_packets import (
        build_parashara_light_witness_batch_packets,
    )

    output_root = tmp_path / "pl7-batch"

    payload = build_parashara_light_witness_batch_packets(
        output_root=output_root,
        case_ids=["sterlitamak-1998-04-30-1345", "vrindavan-1990-08-15-1024"],
        pl_version="7.0.1",
        force=True,
    )

    assert payload["schema_version"] == "jyotish-parashara-light-witness-batch-packets-v1"
    assert payload["summary"] == {
        "created_count": 2,
        "skipped_count": 0,
        "error_count": 0,
        "output_root": str(output_root),
        "index_path": str(output_root / "_index.json"),
    }
    first = payload["created"][0]
    assert first["id"] == "sterlitamak-1998-04-30-1345"
    assert first["packet_id"] == "pl7-sterlitamak-1998-04-30-1345"
    assert first["manual_template_count"] >= 10
    case_dir = output_root / "sterlitamak-1998-04-30-1345"
    packet = json.loads((case_dir / "packet.json").read_text(encoding="utf-8"))
    template = json.loads((case_dir / "manual-values-template.json").read_text(encoding="utf-8"))
    index = json.loads((output_root / "_index.json").read_text(encoding="utf-8"))
    assert packet["status"] == "capture_pending"
    assert packet["fixture"]["review_status"] == "draft"
    assert packet["fixture"]["pl_metadata"]["version_required"] == "7.0.1"
    assert packet["fixture"]["pl_metadata"]["profile_status"] == "unverified"
    assert packet["fixture"]["capture_files"]["screenshots"] == []
    assert template[0]["source"] == "pl7"
    assert template[0]["witness"]["status"] == "pending"
    assert index["summary"]["created_count"] == 2


def test_build_parashara_light_witness_batch_packets_command_outputs_json(tmp_path):
    output_root = tmp_path / "pl7-batch"
    stdout = StringIO()

    call_command(
        "build_parashara_light_witness_batch_packets",
        "--output-root",
        str(output_root),
        "--case-id",
        "sterlitamak-1998-04-30-1345",
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    assert payload["summary"]["created_count"] == 1
    assert payload["created"][0]["paths"]["packet"].endswith("packet.json")
    assert (output_root / "sterlitamak-1998-04-30-1345" / "manual-values-template.json").exists()
