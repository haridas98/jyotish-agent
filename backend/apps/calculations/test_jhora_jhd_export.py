import json

from django.core.management import call_command


def test_jhd_text_from_birth_input_matches_sterlitamak_compact_format():
    from apps.calculations.jhora_import import parse_jhd_text
    from apps.calculations.jhora_jhd_export import jhd_text_from_birth_input

    text = jhd_text_from_birth_input(
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45:00",
            "place_name": "Sterlitamak",
            "timezone": "Asia/Yekaterinburg",
            "timezone_offset": "+06:00",
            "latitude": 53.6304,
            "longitude": 55.9502,
        }
    )
    lines = text.splitlines()

    assert lines[:7] == [
        "4",
        "30",
        "1998",
        "13.450000",
        "-6.000000",
        "-55.570120",
        "53.378240",
    ]
    parsed = parse_jhd_text(text, source_name="sterlitamak-1998.jhd")
    assert parsed["birth_time"] == "13:45:00"
    assert parsed["jhora_timezone_offset_hours"] == 6.0
    assert parsed["latitude"] == 53.6304
    assert parsed["longitude"] == 55.9502


def test_build_jhora_witness_batch_jhd_files_command_writes_selected_case(tmp_path):
    output_root = tmp_path / "jhora"
    call_command(
        "build_jhora_witness_batch_jhd_files",
        "--case-id",
        "sterlitamak-1998-04-30-1345",
        "--output-root",
        str(output_root),
    )

    output_path = output_root / "sterlitamak-1998-04-30-1345" / "sterlitamak-1998-04-30-1345.jhd"
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").splitlines()[3] == "13.450000"


def test_build_jhora_witness_batch_jhd_files_command_outputs_json(tmp_path):
    stdout = __import__("io").StringIO()
    call_command(
        "build_jhora_witness_batch_jhd_files",
        "--case-id",
        "vrindavan-1990-08-15-1024",
        "--output-root",
        str(tmp_path),
        "--json",
        stdout=stdout,
    )

    payload = json.loads(stdout.getvalue())
    assert payload["summary"] == {"selected": 1, "written": 1}
    assert payload["results"][0]["case_id"] == "vrindavan-1990-08-15-1024"
