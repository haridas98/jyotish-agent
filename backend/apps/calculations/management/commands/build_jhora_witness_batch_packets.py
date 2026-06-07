from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.calculations.jhora_parity_suite import jhora_parity_suite_manifest
from apps.calculations.jhora_verification_packet import (
    build_jhora_verification_packet,
    write_jhora_verification_packet,
)


class Command(BaseCommand):
    help = "Build draft JHora verification packets for the witness batch queue."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-root",
            default=str(settings.ROOT_DIR / ".tmp" / "jhora" / "batch-queue"),
            help="Root directory where per-case packet directories are written.",
        )
        parser.add_argument(
            "--case-id",
            action="append",
            default=[],
            help="Limit generation to one case id. May be passed multiple times.",
        )
        parser.add_argument("--calculation-model", default="drik_siddhanta")
        parser.add_argument("--ayanamsa", default="lahiri")
        parser.add_argument("--node-type", default="mean")
        parser.add_argument("--ephemeris", default="swiss")
        parser.add_argument("--house-system", default="whole_sign")
        parser.add_argument("--bhava-system", default="whole_sign")
        parser.add_argument("--varga-scheme", default="parashara")
        parser.add_argument("--sunrise-source", default="noaa")
        parser.add_argument("--timezone-source", default="iana")
        parser.add_argument("--shadbala-profile", default="bphs_classical")
        parser.add_argument("--jhora-version", default="8.0")
        parser.add_argument("--json", action="store_true")
        parser.add_argument(
            "--fail-on-error",
            action="store_true",
            help="Raise CommandError if any selected packet cannot be built.",
        )

    def handle(self, *args, **options):
        selected_case_ids = set(options["case_id"])
        cases = [
            case
            for case in jhora_parity_suite_manifest()["cases"]
            if not selected_case_ids or case["id"] in selected_case_ids
        ]
        if selected_case_ids and len(cases) != len(selected_case_ids):
            available = {case["id"] for case in jhora_parity_suite_manifest()["cases"]}
            missing = sorted(selected_case_ids - available)
            raise CommandError(f"Unknown case id(s): {', '.join(missing)}")

        output_root = Path(options["output_root"])
        results = [_build_case_packet(case, output_root, options) for case in cases]
        payload = {
            "status": "ok" if all(result["status"] == "written" for result in results) else "partial",
            "output_root": str(output_root),
            "summary": {
                "selected": len(cases),
                "written": sum(1 for result in results if result["status"] == "written"),
                "failed": sum(1 for result in results if result["status"] == "failed"),
            },
            "results": results,
        }
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(_text_summary(payload))

        if options["fail_on_error"] and payload["summary"]["failed"]:
            raise CommandError("One or more JHora batch packets failed")


def _build_case_packet(case: dict[str, Any], output_root: Path, options: dict[str, Any]) -> dict[str, Any]:
    case_id = str(case["id"])
    output_dir = output_root / case_id
    birth_input = _birth_input(case["input"], options)
    jhora_export_path = output_dir / "jhora-complete-calculations.txt"
    jhora_export_text = jhora_export_path.read_text(encoding="utf-8") if jhora_export_path.exists() else ""
    jhora_ui_table_dump_path = output_dir / "jhora-ui-tables.json"
    jhora_ui_table_dump = (
        json.loads(jhora_ui_table_dump_path.read_text(encoding="utf-8"))
        if jhora_ui_table_dump_path.exists()
        else {}
    )
    try:
        packet = build_jhora_verification_packet(
            birth_input,
            packet_id=case_id,
            jhora_export_text=jhora_export_text,
            jhora_export_path=str(jhora_export_path) if jhora_export_text else "",
            jhora_ui_table_dump=jhora_ui_table_dump,
            jhora_ui_table_dump_path=str(jhora_ui_table_dump_path) if jhora_ui_table_dump else "",
            jhora_version=options["jhora_version"],
        )
        paths = write_jhora_verification_packet(packet, output_dir)
    except Exception as exc:  # noqa: BLE001 - batch command must report per-case capture blockers.
        return {
            "status": "failed",
            "case_id": case_id,
            "group": case["group"],
            "label": case["label"],
            "error": str(exc),
        }
    return {
        "status": "written",
        "case_id": case_id,
        "group": case["group"],
        "label": case["label"],
        "packet_status": packet["status"],
        "review_status": packet["fixture"]["review_status"],
        "output_dir": str(output_dir),
        "paths": paths,
    }


def _birth_input(case_input: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    return {
        **dict(case_input),
        "calculation_model": options["calculation_model"],
        "ayanamsa": options["ayanamsa"],
        "node_type": options["node_type"],
        "ephemeris": options["ephemeris"],
        "house_system": options["house_system"],
        "bhava_system": options["bhava_system"],
        "varga_scheme": options["varga_scheme"],
        "sunrise_source": options["sunrise_source"],
        "timezone_source": options["timezone_source"],
        "shadbala_profile": options["shadbala_profile"],
    }


def _text_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"selected: {summary['selected']}",
        f"written: {summary['written']}",
        f"failed: {summary['failed']}",
        f"output_root: {payload['output_root']}",
    ]
    for result in payload["results"]:
        if result["status"] == "written":
            lines.append(f"WRITE {result['case_id']} -> {result['output_dir']}")
        else:
            lines.append(f"FAIL {result['case_id']}: {result['error']}")
    return "\n".join(lines)
