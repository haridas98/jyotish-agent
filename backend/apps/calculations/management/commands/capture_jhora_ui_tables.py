from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Capture visible JHora Win32 ListView tables into a local JSON artifact."

    def add_arguments(self, parser):
        parser.add_argument("--process", default="jhora.exe")
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        try:
            from pywinauto import Application
        except ImportError as exc:
            raise CommandError("pywinauto is required to capture JHora UI tables") from exc

        try:
            app = Application(backend="win32").connect(path=options["process"])
            window = app.top_window()
        except Exception as exc:
            raise CommandError(f"Cannot connect to running JHora process: {exc}") from exc

        payload = {
            "source": "jhora_win32_listviews",
            "window_title": window.window_text(),
            "tables": _capture_tables(window),
        }
        payload["identified"] = _identify_strength_tables(payload["tables"])

        target = Path(options["output"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(json.dumps({"status": "captured", "output": str(target)}, ensure_ascii=False, indent=2))


def _capture_tables(window) -> list[dict[str, Any]]:
    tables: list[dict[str, Any]] = []
    for index, listview in enumerate(window.descendants(class_name="SysListView32")):
        try:
            texts = [str(text) for text in listview.texts()]
            rows = _flat_texts_to_rows(texts, listview.column_count())
            rect = listview.rectangle()
        except Exception:
            continue
        if not rows:
            continue
        tables.append(
            {
                "index": index,
                "row_count": len(rows),
                "column_count": listview.column_count(),
                "rect": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                },
                "rows": rows,
            }
        )
    return tables


def _flat_texts_to_rows(texts: list[str], column_count: int) -> list[list[str]]:
    if column_count <= 0:
        return []
    values = texts[1:] if texts and texts[0] == "" else texts
    return [
        values[index : index + column_count]
        for index in range(0, len(values), column_count)
        if any(value.strip() for value in values[index : index + column_count])
    ]


def _identify_strength_tables(tables: list[dict[str, Any]]) -> dict[str, Any]:
    identified: dict[str, Any] = {}
    for table in tables:
        rows = table.get("rows") if isinstance(table.get("rows"), list) else []
        column_count = table.get("column_count")
        row_count = table.get("row_count")
        if row_count == 7 and column_count == 6 and rows and rows[0][0] == "Sun":
            identified["shadbala_totals"] = {
                "columns": ["planet", "shadbala", "rupas", "percent_strength", "ishta_phala", "kashta_phala"],
                "rows": rows,
            }
        elif row_count == 9 and column_count == 5 and rows and rows[0][0] == "Sun":
            identified["vimsopaka_totals"] = {
                "columns": ["planet", "dasa_varga", "shodasa_varga", "sapta_varga", "shad_varga"],
                "rows": rows,
            }
        elif row_count and row_count >= 10 and column_count == 5 and rows and rows[0][1].startswith("D-"):
            identified["active_yogas"] = {
                "columns": ["yoga", "varga", "givers", "result", "definition"],
                "rows": rows,
            }
    return identified
