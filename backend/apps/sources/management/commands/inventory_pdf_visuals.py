from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.sources.pdf_visual_inventory import inventory_pdf_visuals


class Command(BaseCommand):
    help = "Inventory table/chart-like visual pages in a PDF and optionally render top pages."

    def add_arguments(self, parser):
        parser.add_argument("--pdf", required=True)
        parser.add_argument("--output-dir", default="../.tmp/pdf-visual-inventory")
        parser.add_argument("--json-output", default="")
        parser.add_argument("--render-top", type=int, default=30)
        parser.add_argument("--top-limit", type=int, default=30)
        parser.add_argument("--dpi", type=int, default=144)
        parser.add_argument("--max-text-chars", type=int, default=600)

    def handle(self, *args, **options):
        output_dir = Path(options["output_dir"])
        payload = inventory_pdf_visuals(
            pdf_path=Path(options["pdf"]),
            output_dir=output_dir,
            render_top=int(options["render_top"]),
            top_limit=int(options["top_limit"]),
            dpi=int(options["dpi"]),
            max_text_chars=int(options["max_text_chars"]),
        )
        json_output = (
            Path(options["json_output"]) if options["json_output"] else output_dir / "visual-inventory.json"
        )
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(
            json.dumps(
                {
                    "status": "ok",
                    "page_count": payload["page_count"],
                    "summary": payload["summary"],
                    "output": str(json_output),
                },
                ensure_ascii=False,
            )
        )
