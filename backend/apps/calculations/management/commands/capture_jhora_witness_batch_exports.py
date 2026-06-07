from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.calculations.jhora_jhd_export import jhd_text_from_birth_input
from apps.calculations.jhora_parity_suite import jhora_parity_suite_manifest
from apps.calculations.management.commands.capture_jhora_complete_export import (
    DEFAULT_JHORA_EXE,
    DEFAULT_MENU_PATH,
    capture_jhora_complete_export,
    _launch_jhora,
)

LaunchJhora = Callable[[str, str], None]
CaptureExport = Callable[..., dict[str, Any]]
Sleeper = Callable[[float], None]


class Command(BaseCommand):
    help = "Capture JHora complete-calculations exports for the witness batch queue."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-root",
            default=str(settings.ROOT_DIR / ".tmp" / "jhora" / "batch-queue"),
            help="Root directory containing per-case .jhd files and packet artifacts.",
        )
        parser.add_argument("--case-id", action="append", default=[])
        parser.add_argument("--process", default="jhora.exe")
        parser.add_argument("--jhora-exe", default=DEFAULT_JHORA_EXE)
        parser.add_argument("--menu-path", default=DEFAULT_MENU_PATH)
        parser.add_argument("--wait-seconds", type=float, default=1.0)
        parser.add_argument("--connect-timeout-seconds", type=float, default=8.0)
        parser.add_argument("--connect-interval-seconds", type=float, default=0.5)
        parser.add_argument("--skip-existing", action="store_true")
        parser.add_argument("--no-rebuild-packets", action="store_true")
        parser.add_argument("--json", action="store_true")
        parser.add_argument("--fail-on-error", action="store_true")

    def handle(self, *args, **options):
        try:
            from pywinauto import Application, clipboard
        except ImportError as exc:
            raise CommandError("pywinauto is required to capture JHora complete calculations") from exc

        payload = capture_jhora_witness_batch_exports(
            output_root=Path(options["output_root"]),
            selected_case_ids=set(options["case_id"]),
            jhora_exe=options["jhora_exe"],
            process=options["process"],
            menu_path=options["menu_path"],
            wait_seconds=float(options["wait_seconds"]),
            connect_timeout_seconds=float(options["connect_timeout_seconds"]),
            connect_interval_seconds=float(options["connect_interval_seconds"]),
            skip_existing=bool(options["skip_existing"]),
            launch_jhora=_launch_jhora,
            capture_export=capture_jhora_complete_export,
            app_factory=lambda process: Application(backend="win32").connect(path=process),
            clipboard_reader=clipboard.GetData,
        )

        if not options["no_rebuild_packets"]:
            for result in payload["results"]:
                if result["status"] == "captured":
                    call_command(
                        "build_jhora_witness_batch_packets",
                        "--case-id",
                        result["case_id"],
                        "--output-root",
                        str(payload["output_root"]),
                    )

        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(_text_summary(payload))

        if options["fail_on_error"] and payload["summary"]["failed"]:
            raise CommandError("One or more JHora batch exports failed")


def capture_jhora_witness_batch_exports(
    *,
    output_root: str | Path,
    selected_case_ids: set[str],
    jhora_exe: str,
    process: str,
    wait_seconds: float,
    connect_timeout_seconds: float,
    connect_interval_seconds: float,
    skip_existing: bool,
    launch_jhora: LaunchJhora,
    capture_export: CaptureExport,
    sleep: Sleeper = time.sleep,
    menu_path: str = DEFAULT_MENU_PATH,
    app_factory: Callable[[str], Any] | None = None,
    clipboard_reader: Callable[[], str] | None = None,
) -> dict[str, Any]:
    manifest = jhora_parity_suite_manifest()
    cases = [case for case in manifest["cases"] if not selected_case_ids or case["id"] in selected_case_ids]
    if selected_case_ids and len(cases) != len(selected_case_ids):
        available = {case["id"] for case in manifest["cases"]}
        missing = sorted(selected_case_ids - available)
        raise CommandError(f"Unknown case id(s): {', '.join(missing)}")

    root = Path(output_root)
    results = [
        _capture_case(
            case,
            root,
            jhora_exe=jhora_exe,
            process=process,
            menu_path=menu_path,
            wait_seconds=wait_seconds,
            connect_timeout_seconds=connect_timeout_seconds,
            connect_interval_seconds=connect_interval_seconds,
            skip_existing=skip_existing,
            launch_jhora=launch_jhora,
            capture_export=capture_export,
            sleep=sleep,
            app_factory=app_factory,
            clipboard_reader=clipboard_reader,
        )
        for case in cases
    ]
    return {
        "status": "ok" if all(result["status"] != "failed" for result in results) else "partial",
        "output_root": str(root),
        "summary": {
            "selected": len(cases),
            "captured": sum(1 for result in results if result["status"] == "captured"),
            "skipped": sum(1 for result in results if result["status"] == "skipped"),
            "failed": sum(1 for result in results if result["status"] == "failed"),
        },
        "results": results,
    }


def _capture_case(
    case: dict[str, Any],
    output_root: Path,
    *,
    jhora_exe: str,
    process: str,
    menu_path: str,
    wait_seconds: float,
    connect_timeout_seconds: float,
    connect_interval_seconds: float,
    skip_existing: bool,
    launch_jhora: LaunchJhora,
    capture_export: CaptureExport,
    sleep: Sleeper,
    app_factory: Callable[[str], Any] | None,
    clipboard_reader: Callable[[], str] | None,
) -> dict[str, Any]:
    case_id = str(case["id"])
    output_dir = output_root / case_id
    output_dir.mkdir(parents=True, exist_ok=True)
    jhd_path = output_dir / f"{case_id}.jhd"
    if not jhd_path.exists():
        jhd_path.write_text(jhd_text_from_birth_input(case["input"]), encoding="utf-8")

    output_path = output_dir / "jhora-complete-calculations.txt"
    expected_offset = _expected_utc_offset(case["input"])
    if skip_existing and output_path.exists():
        return {
            "status": "skipped",
            "case_id": case_id,
            "group": case["group"],
            "output": str(output_path),
            "expected_utc_offset": expected_offset,
        }

    try:
        launch_jhora(jhora_exe, str(jhd_path))
        sleep(max(wait_seconds, 0.0))
        payload = capture_export(
            process=process,
            menu_path=menu_path,
            wait_seconds=wait_seconds,
            connect_timeout_seconds=connect_timeout_seconds,
            connect_interval_seconds=connect_interval_seconds,
            app_factory=app_factory,
            clipboard_reader=clipboard_reader,
        )
        parsed_offset = str(payload.get("parsed_utc_offset") or "")
        if parsed_offset != expected_offset:
            raise ValueError(f"timezone mismatch: expected {expected_offset}, got {parsed_offset or 'missing'}")

        text = str(payload.get("text") or "")
        output_path.write_text(text, encoding="utf-8")
        return {
            "status": "captured",
            "case_id": case_id,
            "group": case["group"],
            "output": str(output_path),
            "chars": len(text),
            "window_title": str(payload.get("window_title") or ""),
            "expected_utc_offset": expected_offset,
            "parsed_utc_offset": parsed_offset,
        }
    except Exception as exc:  # noqa: BLE001 - batch capture must report per-case blockers.
        return {
            "status": "failed",
            "case_id": case_id,
            "group": case["group"],
            "output": str(output_path),
            "expected_utc_offset": expected_offset,
            "error": str(exc),
        }


def _expected_utc_offset(data: dict[str, Any]) -> str:
    explicit = str(data.get("timezone_offset") or "").strip()
    if explicit:
        return _normalize_utc_offset(explicit)

    naive = datetime.fromisoformat(f"{data['birth_date']}T{data['birth_time']}")
    offset = naive.replace(tzinfo=ZoneInfo(str(data.get("timezone") or "UTC"))).utcoffset()
    seconds = int(offset.total_seconds()) if offset is not None else 0
    return _offset_seconds_to_string(seconds)


def _normalize_utc_offset(value: str) -> str:
    sign = -1 if value.startswith("-") else 1
    normalized = value.lstrip("+-")
    hours_text, _, minutes_text = normalized.partition(":")
    seconds = sign * ((int(hours_text) * 3600) + (int(minutes_text or "0") * 60))
    return _offset_seconds_to_string(seconds)


def _offset_seconds_to_string(seconds: int) -> str:
    sign = "+" if seconds >= 0 else "-"
    seconds = abs(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def _text_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"selected: {summary['selected']}",
        f"captured: {summary['captured']}",
        f"skipped: {summary['skipped']}",
        f"failed: {summary['failed']}",
        f"output_root: {payload['output_root']}",
    ]
    for result in payload["results"]:
        if result["status"] == "captured":
            lines.append(
                "CAPTURE "
                f"{result['case_id']} -> {result['output']} "
                f"({result['parsed_utc_offset']}, {result['chars']} chars)"
            )
        elif result["status"] == "skipped":
            lines.append(f"SKIP {result['case_id']} -> {result['output']}")
        else:
            lines.append(f"FAIL {result['case_id']}: {result['error']}")
    return "\n".join(lines)
