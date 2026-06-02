import json

from django.core.management import call_command


def test_import_jhora_jhd_inputs_command_writes_draft_fixtures(tmp_path):
    input_dir = tmp_path / "jhd"
    output_dir = tmp_path / "fixtures"
    input_dir.mkdir()
    (input_dir / "India.jhd").write_text(
        "\n".join(
            [
                "8",
                "15",
                "1947",
                "0.000167",
                "-5.300000",
                "-77.130000",
                "28.400000",
                "0.000000",
                "-5.500000",
                "-5.500000",
                "0",
                "105",
                "Delhi",
                "India",
            ]
        ),
        encoding="utf-8",
    )

    call_command("import_jhora_jhd_inputs", str(input_dir), "--output-dir", str(output_dir))

    fixture_path = output_dir / "jhora-input-india.json"
    assert fixture_path.exists()
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert fixture["review_status"] == "draft"
    assert fixture["input"]["place_name"] == "Delhi"
    assert fixture["jhora_metadata"]["version_required"] == "8.0"
