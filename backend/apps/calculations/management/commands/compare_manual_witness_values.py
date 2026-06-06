from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.manual_witness_comparison import compare_manual_witness_values


class Command(BaseCommand):
    help = "Compare filled manual PL/JHora witness values against a packet or chart JSON."

    def add_arguments(self, parser):
        parser.add_argument("--packet", default="")
        parser.add_argument("--chart", default="")
        parser.add_argument("--manual-witness-values", required=True)
        parser.add_argument("--output", default="")

    def handle(self, *args, **options):
        chart = _read_chart(options["packet"], options["chart"])
        witness_values = _read_manual_values(options["manual_witness_values"])
        report = compare_manual_witness_values(chart, witness_values)
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if options["output"]:
            output = Path(options["output"])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(text, encoding="utf-8")
        self.stdout.write(text)


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


def _read_manual_values(path: str) -> list[dict]:
    source = Path(path)
    if not source.exists():
        raise CommandError(f"Manual witness values file not found: {source}")
    data = json.loads(source.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise CommandError("Manual witness values file must contain a JSON array")
    return data
