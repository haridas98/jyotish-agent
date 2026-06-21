from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.calculations.management.commands.build_witness_parity_roadmap_report import _build_summary_from_settings
from apps.calculations.witness_core_review_preflight import build_witness_core_review_preflight
from apps.calculations.witness_parity_collection_plan import build_witness_parity_collection_plan


class Command(BaseCommand):
    help = "Build a safe non-mutating core parity review-row preflight report."

    def add_arguments(self, parser):
        parser.add_argument("--jhora-root", default=str(settings.ROOT_DIR / ".tmp" / "jhora"))
        parser.add_argument("--pl-root", default=str(settings.ROOT_DIR / ".tmp" / "pl7"))
        parser.add_argument("--core-report", default=str(settings.WITNESS_CORE_PARITY_REPORT_PATH))
        parser.add_argument("--collection-plan", default="")
        parser.add_argument(
            "--output",
            default=str(settings.ROOT_DIR / ".tmp" / "witness-review" / "core-review-preflight-report.json"),
        )
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        collection_plan = _collection_plan(options.get("collection_plan") or "")
        report = build_witness_core_review_preflight(
            jhora_root=options["jhora_root"],
            pl_root=options["pl_root"],
            core_report_path=options["core_report"],
            collection_plan=collection_plan,
            repo_root=settings.ROOT_DIR,
        )
        encoded = json.dumps(report, ensure_ascii=False, indent=2)
        output = str(options.get("output") or "").strip()
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(encoded, encoding="utf-8")
        summary = {
            "schema_version": report["schema_version"],
            "domain": report["domain"],
            "not_reviewed_count": report["summary"]["not_reviewed_count"],
            "release_gate_status": report["release_gate_status"],
            "command_smoke_matrix_status": report["command_smoke_matrix_status"],
        }
        self.stdout.write(json.dumps(report if options.get("json") else summary, ensure_ascii=False, indent=2))


def _collection_plan(path: str) -> dict:
    if path:
        payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
        return payload if isinstance(payload, dict) else {}
    return build_witness_parity_collection_plan(_build_summary_from_settings())
