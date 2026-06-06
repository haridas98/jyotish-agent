from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.manual_witness_comparison import manual_witness_template_from_chart


class Command(BaseCommand):
    help = "Build a JSON template for manual PL/JHora witness values from a chart or packet."

    def add_arguments(self, parser):
        parser.add_argument("--packet", default="")
        parser.add_argument("--chart", default="")
        parser.add_argument("--source", default="pl7")
        parser.add_argument("--output", required=True)

    def handle(self, *args, **options):
        chart = _read_chart(options["packet"], options["chart"])
        template = manual_witness_template_from_chart(chart, source=options["source"])
        output = Path(options["output"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(template, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(json.dumps({"status": "written", "count": len(template), "output": str(output)}))


def _read_chart(packet_path: str, chart_path: str) -> dict:
    if bool(packet_path) == bool(chart_path):
        raise CommandError("Pass exactly one of --packet or --chart")
    source = Path(packet_path or chart_path)
    if not source.exists():
        raise CommandError(f"Source JSON not found: {source}")
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    if packet_path:
        chart = data.get("jyotish_agent_chart") if isinstance(data, dict) else None
        if not isinstance(chart, dict):
            raise CommandError("Packet JSON does not contain jyotish_agent_chart")
        return chart
    if not isinstance(data, dict):
        raise CommandError("Chart JSON must contain an object")
    return data
