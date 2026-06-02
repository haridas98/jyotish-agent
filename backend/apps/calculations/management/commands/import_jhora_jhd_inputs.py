from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.jhora_import import jhd_to_accuracy_fixture


class Command(BaseCommand):
    help = "Convert JHora .jhd sample inputs into draft accuracy fixture JSON files."

    def add_arguments(self, parser):
        parser.add_argument("path", help="JHora .jhd file or directory.")
        parser.add_argument("--output-dir", required=True)

    def handle(self, *args, **options):
        source = Path(options["path"])
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        files = _jhd_files(source)
        count = 0
        for item in files:
            fixture = jhd_to_accuracy_fixture(item.read_text(encoding="utf-8"), source_name=item.name)
            output_path = output_dir / f"{fixture['id']}.json"
            output_path.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Wrote {count} JHora draft fixtures to {output_dir}"))


def _jhd_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(path.glob("*.jhd"))
    raise CommandError(f"JHora path not found: {path}")
