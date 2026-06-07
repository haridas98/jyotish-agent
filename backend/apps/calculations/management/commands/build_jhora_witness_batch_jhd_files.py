from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.calculations.jhora_jhd_export import jhd_text_from_birth_input
from apps.calculations.jhora_parity_suite import jhora_parity_suite_manifest


class Command(BaseCommand):
    help = "Write JHora .jhd input files for the witness batch queue."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-root",
            default=str(settings.ROOT_DIR / ".tmp" / "jhora" / "batch-queue"),
            help="Root directory where per-case .jhd files are written.",
        )
        parser.add_argument("--case-id", action="append", default=[])
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        selected_case_ids = set(options["case_id"])
        manifest = jhora_parity_suite_manifest()
        cases = [case for case in manifest["cases"] if not selected_case_ids or case["id"] in selected_case_ids]
        if selected_case_ids and len(cases) != len(selected_case_ids):
            available = {case["id"] for case in manifest["cases"]}
            missing = sorted(selected_case_ids - available)
            raise CommandError(f"Unknown case id(s): {', '.join(missing)}")

        output_root = Path(options["output_root"])
        results = []
        for case in cases:
            case_id = str(case["id"])
            output_dir = output_root / case_id
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{case_id}.jhd"
            output_path.write_text(jhd_text_from_birth_input(case["input"]), encoding="utf-8")
            results.append(
                {
                    "case_id": case_id,
                    "group": case["group"],
                    "path": str(output_path),
                }
            )

        payload = {
            "status": "ok",
            "output_root": str(output_root),
            "summary": {"selected": len(cases), "written": len(results)},
            "results": results,
        }
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(_text_summary(payload))


def _text_summary(payload: dict) -> str:
    lines = [
        f"selected: {payload['summary']['selected']}",
        f"written: {payload['summary']['written']}",
        f"output_root: {payload['output_root']}",
    ]
    lines.extend(f"JHD {result['case_id']} -> {result['path']}" for result in payload["results"])
    return "\n".join(lines)
