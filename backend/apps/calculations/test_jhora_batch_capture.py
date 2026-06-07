import pytest


JHORA_EXPORT_TEXT = """Natal Chart

Date:          April 30, 1998
Time:          13:45:00
Time Zone:     6:00:00 (East of GMT)
"""


def test_capture_jhora_witness_batch_exports_writes_selected_case(tmp_path):
    from apps.calculations.management.commands.capture_jhora_witness_batch_exports import (
        capture_jhora_witness_batch_exports,
    )

    launches = []
    captures = []

    def fake_launch(executable, source):
        launches.append((executable, source))

    def fake_capture(**kwargs):
        captures.append(kwargs)
        return {
            "status": "captured",
            "parsed_utc_offset": "+06:00",
            "window_title": "Jagannatha Hora - sterlitamak.jhd",
            "text": JHORA_EXPORT_TEXT,
        }

    payload = capture_jhora_witness_batch_exports(
        output_root=tmp_path / "batch",
        selected_case_ids={"sterlitamak-1998-04-30-1345"},
        jhora_exe="C:/fake/jhora.exe",
        process="jhora.exe",
        wait_seconds=0,
        connect_timeout_seconds=0,
        connect_interval_seconds=0,
        skip_existing=False,
        launch_jhora=fake_launch,
        capture_export=fake_capture,
        sleep=lambda seconds: None,
    )

    case_dir = tmp_path / "batch" / "sterlitamak-1998-04-30-1345"
    output = case_dir / "jhora-complete-calculations.txt"
    jhd = case_dir / "sterlitamak-1998-04-30-1345.jhd"
    assert payload["summary"] == {"selected": 1, "captured": 1, "skipped": 0, "failed": 0}
    assert output.read_text(encoding="utf-8") == JHORA_EXPORT_TEXT
    assert jhd.exists()
    assert launches == [("C:/fake/jhora.exe", str(jhd))]
    assert captures[0]["process"] == "jhora.exe"
    assert payload["results"][0]["expected_utc_offset"] == "+06:00"
    assert payload["results"][0]["parsed_utc_offset"] == "+06:00"


def test_capture_jhora_witness_batch_exports_rejects_timezone_mismatch(tmp_path):
    from apps.calculations.management.commands.capture_jhora_witness_batch_exports import (
        capture_jhora_witness_batch_exports,
    )

    payload = capture_jhora_witness_batch_exports(
        output_root=tmp_path / "batch",
        selected_case_ids={"sterlitamak-1998-04-30-1345"},
        jhora_exe="C:/fake/jhora.exe",
        process="jhora.exe",
        wait_seconds=0,
        connect_timeout_seconds=0,
        connect_interval_seconds=0,
        skip_existing=False,
        launch_jhora=lambda executable, source: None,
        capture_export=lambda **kwargs: {
            "status": "captured",
            "parsed_utc_offset": "+05:00",
            "text": JHORA_EXPORT_TEXT,
        },
        sleep=lambda seconds: None,
    )

    assert payload["summary"] == {"selected": 1, "captured": 0, "skipped": 0, "failed": 1}
    assert "timezone mismatch" in payload["results"][0]["error"]


def test_capture_jhora_witness_batch_exports_skips_existing_file(tmp_path):
    from apps.calculations.management.commands.capture_jhora_witness_batch_exports import (
        capture_jhora_witness_batch_exports,
    )

    case_dir = tmp_path / "batch" / "sterlitamak-1998-04-30-1345"
    case_dir.mkdir(parents=True)
    output = case_dir / "jhora-complete-calculations.txt"
    output.write_text("already captured", encoding="utf-8")

    payload = capture_jhora_witness_batch_exports(
        output_root=tmp_path / "batch",
        selected_case_ids={"sterlitamak-1998-04-30-1345"},
        jhora_exe="C:/fake/jhora.exe",
        process="jhora.exe",
        wait_seconds=0,
        connect_timeout_seconds=0,
        connect_interval_seconds=0,
        skip_existing=True,
        launch_jhora=lambda executable, source: pytest.fail("should not launch"),
        capture_export=lambda **kwargs: pytest.fail("should not capture"),
        sleep=lambda seconds: None,
    )

    assert payload["summary"] == {"selected": 1, "captured": 0, "skipped": 1, "failed": 0}
    assert payload["results"][0]["status"] == "skipped"
