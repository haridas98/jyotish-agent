from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.calculations.jhora_parity_suite import jhora_parity_suite_manifest
from apps.calculations.manual_witness_comparison import manual_witness_template_from_chart
from apps.calculations.parashara_light_verification_packet import (
    build_parashara_light_verification_packet,
    write_parashara_light_verification_packet,
)


SCHEMA_VERSION = "jyotish-parashara-light-witness-batch-packets-v1"


class Command(BaseCommand):
    help = "Build draft Parashara Light witness packet directories for the JHora parity batch."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-root",
            default=str(settings.ROOT_DIR / ".tmp" / "pl7" / "batch-queue"),
            help="Directory where one PL witness packet directory per case will be written.",
        )
        parser.add_argument("--case-id", action="append", default=[])
        parser.add_argument("--pl-version", default="7.0.1")
        parser.add_argument("--calculation-model", default="drik_siddhanta")
        parser.add_argument("--ayanamsa", default="lahiri")
        parser.add_argument("--node-type", default="true")
        parser.add_argument("--ephemeris", default="swiss")
        parser.add_argument("--house-system", default="whole_sign")
        parser.add_argument("--bhava-system", default="whole_sign")
        parser.add_argument("--varga-scheme", default="parashara")
        parser.add_argument("--sunrise-source", default="noaa")
        parser.add_argument("--timezone-source", default="iana")
        parser.add_argument("--shadbala-profile", default="bphs_classical")
        parser.add_argument("--source", default="pl7")
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--fail-if-errors", action="store_true")
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        payload = build_parashara_light_witness_batch_packets(
            output_root=options["output_root"],
            case_ids=options["case_id"],
            pl_version=options["pl_version"],
            calculation_model=options["calculation_model"],
            ayanamsa=options["ayanamsa"],
            node_type=options["node_type"],
            ephemeris=options["ephemeris"],
            house_system=options["house_system"],
            bhava_system=options["bhava_system"],
            varga_scheme=options["varga_scheme"],
            sunrise_source=options["sunrise_source"],
            timezone_source=options["timezone_source"],
            shadbala_profile=options["shadbala_profile"],
            source=options["source"],
            force=options["force"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(_text_summary(payload))

        if options["fail_if_errors"] and payload["summary"]["error_count"]:
            raise CommandError("One or more Parashara Light batch packets failed to build")


def build_parashara_light_witness_batch_packets(
    *,
    output_root: str | Path,
    case_ids: list[str] | tuple[str, ...] = (),
    pl_version: str = "7.0.1",
    calculation_model: str = "drik_siddhanta",
    ayanamsa: str = "lahiri",
    node_type: str = "true",
    ephemeris: str = "swiss",
    house_system: str = "whole_sign",
    bhava_system: str = "whole_sign",
    varga_scheme: str = "parashara",
    sunrise_source: str = "noaa",
    timezone_source: str = "iana",
    shadbala_profile: str = "bphs_classical",
    source: str = "pl7",
    force: bool = False,
) -> dict[str, Any]:
    manifest = jhora_parity_suite_manifest()
    selected_ids = {str(case_id) for case_id in case_ids if str(case_id).strip()}
    output_dir = Path(output_root)
    created: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []

    for case in manifest["cases"]:
        case_id = str(case["id"])
        if selected_ids and case_id not in selected_ids:
            continue
        case_dir = output_dir / case_id
        packet_path = case_dir / "packet.json"
        if packet_path.exists() and not force:
            skipped.append({"id": case_id, "reason": "packet_exists"})
            continue
        try:
            row = _build_case_packet(
                case,
                case_dir=case_dir,
                pl_version=pl_version,
                calculation_model=calculation_model,
                ayanamsa=ayanamsa,
                node_type=node_type,
                ephemeris=ephemeris,
                house_system=house_system,
                bhava_system=bhava_system,
                varga_scheme=varga_scheme,
                sunrise_source=sunrise_source,
                timezone_source=timezone_source,
                shadbala_profile=shadbala_profile,
                source=source,
            )
        except Exception as exc:  # noqa: BLE001 - batch scaffold should report per-case failures.
            errors.append({"id": case_id, "error": str(exc)})
            continue
        created.append(row)

    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "metadata": {
            "generated_at": timezone.now().isoformat(),
            "pl_version": pl_version,
            "source": source,
            "force": force,
            "case_ids": sorted(selected_ids),
        },
        "summary": {
            "created_count": len(created),
            "skipped_count": len(skipped),
            "error_count": len(errors),
            "output_root": str(output_dir),
            "index_path": str(output_dir / "_index.json"),
        },
        "created": created,
        "skipped": skipped,
        "errors": errors,
    }
    (output_dir / "_index.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def _build_case_packet(
    case: dict[str, Any],
    *,
    case_dir: Path,
    pl_version: str,
    calculation_model: str,
    ayanamsa: str,
    node_type: str,
    ephemeris: str,
    house_system: str,
    bhava_system: str,
    varga_scheme: str,
    sunrise_source: str,
    timezone_source: str,
    shadbala_profile: str,
    source: str,
) -> dict[str, Any]:
    case_id = str(case["id"])
    birth_input = dict(case.get("input") or {})
    birth_input.update(
        {
            "calculation_model": calculation_model,
            "ayanamsa": ayanamsa,
            "node_type": node_type,
            "ephemeris": ephemeris,
            "house_system": house_system,
            "bhava_system": bhava_system,
            "varga_scheme": varga_scheme,
            "sunrise_source": sunrise_source,
            "timezone_source": timezone_source,
            "shadbala_profile": shadbala_profile,
        }
    )
    packet_id = f"{source}-{case_id}"
    packet = build_parashara_light_verification_packet(
        birth_input,
        packet_id=packet_id,
        pl_version=pl_version,
    )
    paths = write_parashara_light_verification_packet(packet, case_dir)
    manual_template = manual_witness_template_from_chart(packet["jyotish_agent_chart"], source=source)
    template_path = case_dir / "manual-values-template.json"
    template_path.write_text(json.dumps(manual_template, ensure_ascii=False, indent=2), encoding="utf-8")
    paths["manual_values_template"] = str(template_path)
    return {
        "id": case_id,
        "packet_id": packet_id,
        "status": packet["status"],
        "review_status": packet["fixture"]["review_status"],
        "manual_template_count": len(manual_template),
        "paths": paths,
    }


def _text_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"created: {summary['created_count']}",
        f"skipped: {summary['skipped_count']}",
        f"errors: {summary['error_count']}",
        f"output: {summary['output_root']}",
        f"index: {summary['index_path']}",
    ]
    for row in payload["created"][:20]:
        lines.append(f"- {row['id']}: {row['paths']['packet']} ({row['manual_template_count']} manual rows)")
    return "\n".join(lines)
