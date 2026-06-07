from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    mark_jhora_witness_reviewed,
)
from apps.calculations.management.commands.mark_parashara_light_witness_reviewed import (
    mark_parashara_light_witness_reviewed,
)
from apps.calculations.management.commands.preflight_witness_review import (
    build_witness_review_preflight,
)
from apps.calculations.management.commands.promote_jhora_witness_fixture import (
    DEFAULT_OUTPUT_DIR,
    promote_jhora_witness_fixture,
)


SCHEMA_VERSION = "jyotish-witness-case-seal-v1"


class Command(BaseCommand):
    help = "Mark reviewed JHora/Parashara Light witnesses and promote the JHora fixture in one gated step."

    def add_arguments(self, parser):
        parser.add_argument("--jhora", required=True, help="JHora case directory, packet.json, or fixture.json.")
        parser.add_argument(
            "--parashara-light",
            required=True,
            help="Parashara Light case directory, packet.json, or fixture.json.",
        )
        parser.add_argument("--reviewer", required=True)
        parser.add_argument("--reviewed-at", default="")
        parser.add_argument("--ack-diff-open", action="store_true")
        parser.add_argument("--promotion-output-dir", default=str(DEFAULT_OUTPUT_DIR))
        parser.add_argument("--overwrite-promotion", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        payload = seal_witness_case(
            jhora_path=options["jhora"],
            parashara_light_path=options["parashara_light"],
            reviewer=options["reviewer"],
            reviewed_at=options["reviewed_at"],
            ack_diff_open=options["ack_diff_open"],
            promotion_output_dir=options["promotion_output_dir"],
            overwrite_promotion=options["overwrite_promotion"],
            dry_run=options["dry_run"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(_text_summary(payload))


def seal_witness_case(
    *,
    jhora_path: str | Path,
    parashara_light_path: str | Path,
    reviewer: str,
    reviewed_at: str = "",
    ack_diff_open: bool = False,
    promotion_output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    overwrite_promotion: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    preflight = build_witness_review_preflight(
        jhora_path=jhora_path,
        parashara_light_path=parashara_light_path,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
    )
    _raise_if_not_sealable(preflight, ack_diff_open=ack_diff_open)
    if dry_run:
        return {
            "schema_version": SCHEMA_VERSION,
            "status": "ready",
            "dry_run": True,
            "preflight": preflight,
            "jhora_review": None,
            "parashara_light_review": None,
            "promotion": None,
        }

    parashara_light_review = mark_parashara_light_witness_reviewed(
        parashara_light_path,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        ack_diff_open=ack_diff_open,
    )
    jhora_review = mark_jhora_witness_reviewed(
        jhora_path,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
        ack_diff_open=ack_diff_open,
    )
    promotion = promote_jhora_witness_fixture(
        jhora_path,
        output_dir=promotion_output_dir,
        overwrite=overwrite_promotion,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "sealed",
        "dry_run": False,
        "preflight": preflight,
        "jhora_review": jhora_review,
        "parashara_light_review": parashara_light_review,
        "promotion": promotion,
    }


def _raise_if_not_sealable(preflight: dict[str, Any], *, ack_diff_open: bool) -> None:
    overall = preflight.get("overall") if isinstance(preflight.get("overall"), dict) else {}
    if not overall.get("reviewable"):
        raise CommandError(f"Witness case is not reviewable; blocked by: {', '.join(_missing(preflight))}")
    if overall.get("ack_required") and not ack_diff_open:
        raise CommandError("Witness case has open diffs; pass --ack-diff-open after manual review")


def _missing(preflight: dict[str, Any]) -> list[str]:
    missing = []
    for key in ("jhora", "parashara_light"):
        row = preflight.get(key) if isinstance(preflight.get(key), dict) else {}
        for item in row.get("missing_evidence") or []:
            value = f"{key}.{item}"
            if value not in missing:
                missing.append(value)
    return missing


def _text_summary(payload: dict[str, Any]) -> str:
    lines = [f"status: {payload['status']}", f"dry_run: {payload['dry_run']}"]
    preflight = payload.get("preflight") if isinstance(payload.get("preflight"), dict) else {}
    overall = preflight.get("overall") if isinstance(preflight.get("overall"), dict) else {}
    if overall:
        lines.append(f"ack_required: {overall.get('ack_required')}")
        lines.append(f"blocked: {overall.get('blocked')}")
    if payload.get("promotion"):
        lines.append(f"promoted: {payload['promotion']['output_path']}")
    return "\n".join(lines)
