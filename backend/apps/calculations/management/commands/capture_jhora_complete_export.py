from __future__ import annotations

import json
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.witness_summary import _jhora_export_utc_offset


DEFAULT_JHORA_EXE = r"C:\Program Files (x86)\Jagannatha Hora\bin\jhora.exe"
DEFAULT_MENU_PATH = "Edit->Copy complete calculations"

AppFactory = Callable[[str], Any]
ClipboardReader = Callable[[], str]
Sleeper = Callable[[float], None]


class Command(BaseCommand):
    help = "Capture JHora Edit->Copy complete calculations into a local text artifact."

    def add_arguments(self, parser):
        parser.add_argument("--process", default="jhora.exe")
        parser.add_argument("--output", required=True)
        parser.add_argument("--expected-timezone-offset", default="")
        parser.add_argument("--menu-path", default=DEFAULT_MENU_PATH)
        parser.add_argument("--wait-seconds", type=float, default=1.0)
        parser.add_argument("--connect-timeout-seconds", type=float, default=8.0)
        parser.add_argument("--connect-interval-seconds", type=float, default=0.5)
        parser.add_argument("--launch-jhd", default="")
        parser.add_argument("--jhora-exe", default=DEFAULT_JHORA_EXE)

    def handle(self, *args, **options):
        if options["launch_jhd"]:
            _launch_jhora(options["jhora_exe"], options["launch_jhd"])
            time.sleep(max(float(options["wait_seconds"]), 0.0))

        try:
            from pywinauto import Application, clipboard
        except ImportError as exc:
            raise CommandError("pywinauto is required to capture JHora complete calculations") from exc

        try:
            payload = capture_jhora_complete_export(
                process=options["process"],
                menu_path=options["menu_path"],
                wait_seconds=float(options["wait_seconds"]),
                connect_timeout_seconds=float(options["connect_timeout_seconds"]),
                connect_interval_seconds=float(options["connect_interval_seconds"]),
                app_factory=lambda process: Application(backend="win32").connect(path=process),
                clipboard_reader=clipboard.GetData,
            )
        except Exception as exc:
            raise CommandError(str(exc)) from exc

        expected_offset = str(options["expected_timezone_offset"] or "").strip()
        if expected_offset and payload["parsed_utc_offset"] != expected_offset:
            raise CommandError(
                "JHora export timezone mismatch: "
                f"expected {expected_offset}, got {payload['parsed_utc_offset'] or 'missing'}"
            )

        target = Path(options["output"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload.pop("text"), encoding="utf-8")
        payload["output"] = str(target)
        payload["launch_jhd"] = str(options["launch_jhd"] or "")
        self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))


def capture_jhora_complete_export(
    *,
    process: str,
    menu_path: str = DEFAULT_MENU_PATH,
    wait_seconds: float = 1.0,
    connect_timeout_seconds: float = 8.0,
    connect_interval_seconds: float = 0.5,
    app_factory: AppFactory,
    clipboard_reader: ClipboardReader,
    sleep: Sleeper = time.sleep,
) -> dict[str, Any]:
    deadline = time.monotonic() + max(connect_timeout_seconds, 0.0)
    last_error: Exception | None = None
    while True:
        try:
            window = _connect_top_window(
                process=process,
                app_factory=app_factory,
                timeout_seconds=0.0,
                interval_seconds=connect_interval_seconds,
                sleep=sleep,
            )
            window.set_focus()
            sleep(max(wait_seconds, 0.0))
            window.menu_select(menu_path)
            sleep(max(wait_seconds, 0.0))
            text = str(clipboard_reader() or "")
            timezone_line = _line_by_prefix(text.splitlines(), "Time Zone:")
            parsed_offset = _jhora_export_utc_offset(timezone_line)
            if not timezone_line:
                raise ValueError("Clipboard does not contain a JHora Time Zone line")
            if not parsed_offset:
                raise ValueError(f"Cannot parse JHora timezone line: {timezone_line}")
            return {
                "status": "captured",
                "captured_at": datetime.now(UTC).isoformat(),
                "process": process,
                "window_title": str(window.window_text()),
                "menu_path": menu_path,
                "chars": len(text),
                "timezone_line": timezone_line.strip(),
                "parsed_utc_offset": parsed_offset,
                "text": text,
            }
        except Exception as exc:
            last_error = exc
            if time.monotonic() >= deadline:
                break
            sleep(max(connect_interval_seconds, 0.0))
    raise RuntimeError(f"Cannot capture JHora complete calculations: {last_error}") from last_error


def _connect_top_window(
    *,
    process: str,
    app_factory: AppFactory,
    timeout_seconds: float,
    interval_seconds: float,
    sleep: Sleeper,
) -> Any:
    deadline = time.monotonic() + max(timeout_seconds, 0.0)
    last_error: Exception | None = None
    while True:
        try:
            app = app_factory(process)
            window = app.top_window()
            window.window_text()
            return window
        except Exception as exc:
            last_error = exc
            if time.monotonic() >= deadline:
                break
            sleep(max(interval_seconds, 0.0))
    raise RuntimeError(f"Cannot connect to JHora top window: {last_error}") from last_error


def _launch_jhora(jhora_exe: str, jhd_path: str) -> None:
    executable = Path(jhora_exe)
    source = Path(jhd_path)
    if not executable.exists():
        raise CommandError(f"JHora executable not found: {executable}")
    if not source.exists():
        raise CommandError(f"JHora .jhd file not found: {source}")
    subprocess.Popen([str(executable), str(source)])


def _line_by_prefix(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line
    return ""
