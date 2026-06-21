from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_argala_parity import (
    build_witness_argala_parity_report,
    render_argala_parity_markdown,
)


class Command(BaseCommand):
    help = "Build a diagnostic Argala parity report from reviewed witness packets."

    def add_arguments(self, parser):
        parser.add_argument("--jhora-root", default=str(settings.ROOT_DIR / ".tmp" / "jhora"))
        parser.add_argument("--pl-root", default=str(settings.ROOT_DIR / ".tmp" / "pl7"))
        parser.add_argument(
            "--output",
            default=str(settings.ROOT_DIR / ".tmp" / "witness-review" / "argala-parity-report.json"),
        )
        parser.add_argument(
            "--markdown-output",
            default=str(settings.ROOT_DIR / ".tmp" / "witness-review" / "argala-parity-report.md"),
        )
        parser.add_argument("--target-reviewed-count", type=int, default=20)
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        report = build_witness_argala_parity_report(
            jhora_root=options["jhora_root"],
            pl_root=options["pl_root"],
            target_reviewed_count=options["target_reviewed_count"],
        )
        output = Path(options["output"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        markdown_output = str(options.get("markdown_output") or "").strip()
        if markdown_output:
            markdown_path = Path(markdown_output)
            markdown_path.parent.mkdir(parents=True, exist_ok=True)
            markdown_path.write_text(render_argala_parity_markdown(report), encoding="utf-8")
        if options["json"]:
            self.stdout.write(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            summary = report["summary"]
            self.stdout.write(
                "\n".join(
                    [
                        f"cases: {summary['case_count']}",
                        f"comparable: {summary['comparable_count']}",
                        f"passed: {summary['passed_count']}",
                        f"failed: {summary['failed_count']}",
                        f"output: {output}",
                    ]
                )
            )
