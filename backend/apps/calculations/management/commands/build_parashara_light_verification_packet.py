from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.parashara_light_verification_packet import (
    build_parashara_light_verification_packet,
    write_parashara_light_verification_packet,
)


class Command(BaseCommand):
    help = "Build a local Parashara's Light verification packet for one birth chart."

    def add_arguments(self, parser):
        parser.add_argument("--id", default="pl7-sterlitamak-1998")
        parser.add_argument("--birth-date", required=True)
        parser.add_argument("--birth-time", required=True)
        parser.add_argument("--place-name", required=True)
        parser.add_argument("--timezone", required=True)
        parser.add_argument("--latitude", required=True, type=float)
        parser.add_argument("--longitude", required=True, type=float)
        parser.add_argument("--timezone-offset", default="")
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
        parser.add_argument("--pl-version", default="7.0.1")
        parser.add_argument("--pl-ui-state", default="")
        parser.add_argument("--screenshot", action="append", default=[])
        parser.add_argument("--manual-witness-values", default="")
        parser.add_argument("--reviewer", default="")
        parser.add_argument("--reviewed-at", default="")
        parser.add_argument("--output-dir", required=True)

    def handle(self, *args, **options):
        pl_ui_state = _read_optional_json(options["pl_ui_state"])
        manual_witness_values = _read_optional_json_list(options["manual_witness_values"])
        birth_input = {
            "birth_date": options["birth_date"],
            "birth_time": options["birth_time"],
            "place_name": options["place_name"],
            "timezone": options["timezone"],
            "timezone_offset": options["timezone_offset"],
            "latitude": options["latitude"],
            "longitude": options["longitude"],
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
        packet = build_parashara_light_verification_packet(
            birth_input,
            packet_id=options["id"],
            pl_ui_state=pl_ui_state,
            pl_ui_state_path=options["pl_ui_state"],
            screenshot_paths=options["screenshot"],
            manual_witness_values=manual_witness_values,
            reviewer=options["reviewer"],
            reviewed_at=options["reviewed_at"],
            pl_version=options["pl_version"],
        )
        paths = write_parashara_light_verification_packet(packet, options["output_dir"])
        self.stdout.write(json.dumps({"status": packet["status"], "paths": paths}, ensure_ascii=False, indent=2))


def _read_optional_json(path: str):
    if not path:
        return {}
    source = Path(path)
    if not source.exists():
        raise CommandError(f"Parashara's Light UI state file not found: {path}")
    return json.loads(source.read_text(encoding="utf-8"))


def _read_optional_json_list(path: str):
    if not path:
        return []
    source = Path(path)
    if not source.exists():
        raise CommandError(f"Manual witness values file not found: {path}")
    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise CommandError("Manual witness values file must contain a JSON array")
    return data
