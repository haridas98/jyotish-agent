from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Capture Parashara's Light visible UI metadata into a local JSON artifact."

    def add_arguments(self, parser):
        parser.add_argument("--process", default="PL7.exe")
        parser.add_argument("--backend", default="uia", choices=["uia", "win32"])
        parser.add_argument("--output", required=True)
        parser.add_argument("--screenshot", default="")
        parser.add_argument("--max-controls", type=int, default=500)

    def handle(self, *args, **options):
        try:
            from pywinauto import Application
        except ImportError as exc:
            raise CommandError("pywinauto is required to capture Parashara's Light UI state") from exc

        try:
            app = Application(backend=options["backend"]).connect(path=options["process"])
            window = app.top_window()
        except Exception as exc:
            raise CommandError(f"Cannot connect to running Parashara's Light process: {exc}") from exc

        controls = _capture_controls(window, max_controls=options["max_controls"])
        payload = {
            "source": "parashara_light_ui_state",
            "captured_at": datetime.now(UTC).isoformat(),
            "process": options["process"],
            "backend": options["backend"],
            "window_title": window.window_text(),
            "control_count": len(controls),
            "max_controls": options["max_controls"],
            "class_summary": _class_summary(controls),
            "controls": controls,
            "artifact_policy": "private_audit_only_do_not_commit",
            "capture_notes": [
                "Parashara's Light 7 exposes most chart panes as Qt QWidget controls.",
                "Use this artifact with screenshots/manual exports as a PL black-box witness, not as copied proprietary data.",
            ],
        }

        screenshot_path = str(options.get("screenshot") or "").strip()
        if screenshot_path:
            _attach_screenshot(payload, window, Path(screenshot_path))

        target = Path(options["output"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(json.dumps({"status": "captured", "output": str(target)}, ensure_ascii=False, indent=2))


def _capture_controls(window, *, max_controls: int = 500) -> list[dict[str, Any]]:
    controls: list[dict[str, Any]] = []
    for index, control in enumerate(window.descendants()):
        if len(controls) >= max_controls:
            break
        payload = _control_payload(control, index=index)
        if payload is not None:
            controls.append(payload)
    return controls


def _control_payload(control, *, index: int) -> dict[str, Any] | None:
    try:
        text = str(control.window_text())
        class_name = str(control.class_name())
        rect = control.rectangle()
    except Exception:
        return None

    element_info = getattr(control, "element_info", None)
    control_type = str(getattr(element_info, "control_type", "") or "")
    info_class = str(getattr(element_info, "class_name", "") or "")
    class_name = class_name or info_class

    return {
        "index": index,
        "text": text,
        "class_name": class_name,
        "control_type": control_type,
        "rect": {
            "left": rect.left,
            "top": rect.top,
            "right": rect.right,
            "bottom": rect.bottom,
        },
    }


def _class_summary(controls: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter = Counter(
        (str(control.get("control_type") or ""), str(control.get("class_name") or ""))
        for control in controls
    )
    return [
        {"control_type": control_type, "class_name": class_name, "count": count}
        for (control_type, class_name), count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def _attach_screenshot(payload: dict[str, Any], window, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        image = window.capture_as_image()
        image.save(target)
    except Exception as exc:
        payload["screenshot_error"] = str(exc)
        return
    payload["screenshot"] = str(target)
