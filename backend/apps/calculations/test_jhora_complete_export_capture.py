from __future__ import annotations

import pytest
from django.core.management import call_command


JHORA_TEXT = """Natal Chart

Date:          April 30, 1998
Time:          13:45:00
Time Zone:     6:00:00 (East of GMT)
Place:         55 E 57' 01", 53 N 37' 49"
               Sterlitamak, Russia
"""


class FakeWindow:
    def __init__(self):
        self.focused = False
        self.menu_path = ""

    def set_focus(self):
        self.focused = True

    def menu_select(self, menu_path: str):
        self.menu_path = menu_path

    def window_text(self):
        return "Jagannatha Hora - sterlitamak-1998.jhd"


class FakeApp:
    def __init__(self, window: FakeWindow):
        self.window = window

    def top_window(self):
        return self.window


def test_capture_jhora_complete_export_reads_clipboard_after_menu():
    from apps.calculations.management.commands.capture_jhora_complete_export import (
        capture_jhora_complete_export,
    )

    window = FakeWindow()

    payload = capture_jhora_complete_export(
        process="jhora.exe",
        app_factory=lambda process: FakeApp(window),
        clipboard_reader=lambda: JHORA_TEXT,
        sleep=lambda seconds: None,
    )

    assert window.focused is True
    assert window.menu_path == "Edit->Copy complete calculations"
    assert payload["window_title"] == "Jagannatha Hora - sterlitamak-1998.jhd"
    assert payload["timezone_line"] == "Time Zone:     6:00:00 (East of GMT)"
    assert payload["parsed_utc_offset"] == "+06:00"
    assert payload["text"] == JHORA_TEXT


def test_capture_jhora_complete_export_rejects_missing_timezone_line():
    from apps.calculations.management.commands.capture_jhora_complete_export import (
        capture_jhora_complete_export,
    )

    with pytest.raises(RuntimeError, match="Time Zone"):
        capture_jhora_complete_export(
            process="jhora.exe",
            app_factory=lambda process: FakeApp(FakeWindow()),
            clipboard_reader=lambda: "not a complete export",
            sleep=lambda seconds: None,
        )


def test_capture_jhora_complete_export_command_writes_text(monkeypatch, tmp_path):
    import apps.calculations.management.commands.capture_jhora_complete_export as command_module

    monkeypatch.setattr(
        command_module,
        "capture_jhora_complete_export",
        lambda **kwargs: {
            "status": "captured",
            "captured_at": "2026-06-07T00:00:00+00:00",
            "process": kwargs["process"],
            "window_title": "Jagannatha Hora - sterlitamak-1998.jhd",
            "menu_path": kwargs["menu_path"],
            "chars": len(JHORA_TEXT),
            "timezone_line": "Time Zone:     6:00:00 (East of GMT)",
            "parsed_utc_offset": "+06:00",
            "text": JHORA_TEXT,
        },
    )
    output = tmp_path / "complete-calculations.txt"

    call_command(
        "capture_jhora_complete_export",
        "--output",
        str(output),
        "--expected-timezone-offset",
        "+06:00",
    )

    assert output.read_text(encoding="utf-8") == JHORA_TEXT


def test_capture_jhora_complete_export_command_rejects_expected_offset(monkeypatch, tmp_path):
    import apps.calculations.management.commands.capture_jhora_complete_export as command_module

    monkeypatch.setattr(
        command_module,
        "capture_jhora_complete_export",
        lambda **kwargs: {
            "status": "captured",
            "timezone_line": "Time Zone:     6:00:00 (East of GMT)",
            "parsed_utc_offset": "+06:00",
            "text": JHORA_TEXT,
        },
    )

    with pytest.raises(Exception, match="timezone mismatch"):
        call_command(
            "capture_jhora_complete_export",
            "--output",
            str(tmp_path / "complete-calculations.txt"),
            "--expected-timezone-offset",
            "+05:00",
        )
