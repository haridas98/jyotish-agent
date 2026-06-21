from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.witness_jaimini_varga_parity import (
    DEFAULT_VARGA_CODES,
    build_witness_jaimini_varga_parity_report,
    render_jaimini_varga_parity_markdown,
)


class Command(BaseCommand):
    help = "Build a diagnostic Jaimini varga parity gap report from reviewed witness packets."

    def add_arguments(self, parser):
        parser.add_argument("--witness-dir", default=str(settings.ROOT_DIR / ".tmp" / "jhora"))
        parser.add_argument("--pl-root", default=str(settings.ROOT_DIR / ".tmp" / "pl7"))
        parser.add_argument(
            "--output",
            default=str(settings.ROOT_DIR / ".tmp" / "witness-review" / "jaimini-varga-parity-report.json"),
        )
        parser.add_argument(
            "--markdown-output",
            default=str(settings.ROOT_DIR / ".tmp" / "witness-review" / "jaimini-varga-parity-report.md"),
        )
        parser.add_argument("--target-reviewed-count", type=int, default=20)
        parser.add_argument("--varga-codes", default=",".join(DEFAULT_VARGA_CODES))
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        codes = tuple(_normalize_codes(options.get("varga_codes") or ""))
        report = build_witness_jaimini_varga_parity_report(
            witness_dir=options["witness_dir"],
            pl_root=options["pl_root"],
            target_reviewed_count=options["target_reviewed_count"],
            varga_codes=codes,
        )
        output = Path(options["output"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        markdown_output = str(options.get("markdown_output") or "").strip()
        if markdown_output:
            markdown_path = Path(markdown_output)
            markdown_path.parent.mkdir(parents=True, exist_ok=True)
            markdown_path.write_text(render_jaimini_varga_parity_markdown(report), encoding="utf-8")
        if options["json"]:
            self.stdout.write(
                json.dumps(
                    {
                        "schema_version": report["schema_version"],
                        "summary": report["summary"],
                        "readiness_summary": report["readiness_summary"],
                        "output": str(output),
                        "markdown_output": markdown_output,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            summary = report["summary"]
            self.stdout.write(
                "\n".join(
                    [
                        f"cases: {summary['case_count']}",
                        f"comparable: {summary['comparable_count']}",
                        f"passed: {summary['passed_count']}",
                        f"failed: {summary['failed_count']}",
                        f"missing: {summary['missing_witness_count']}",
                        f"not comparable: {summary['not_comparable_count']}",
                        f"output: {output}",
                    ]
                )
            )


def _normalize_codes(value: str) -> list[str]:
    codes = []
    for item in value.split(","):
        code = item.strip().upper()
        if code and code[0].isdigit():
            code = f"D{code}"
        if code:
            codes.append(code)
    return codes or list(DEFAULT_VARGA_CODES)
