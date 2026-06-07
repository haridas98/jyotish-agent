from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Attach a filled manual witness values JSON array to a packet/fixture pair."

    def add_arguments(self, parser):
        parser.add_argument("--packet", default="", help="Path to packet.json.")
        parser.add_argument("--fixture", default="", help="Path to fixture.json.")
        parser.add_argument("--manual-witness-values", required=True)
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        if bool(options["packet"]) == bool(options["fixture"]):
            raise CommandError("Pass exactly one of --packet or --fixture")
        payload = attach_manual_witness_values(
            options["packet"] or options["fixture"],
            options["manual_witness_values"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(f"{payload['status']} {payload['id']} manual values: {payload['count']}")


def attach_manual_witness_values(
    target_path: str | Path,
    manual_witness_values_path: str | Path,
) -> dict[str, Any]:
    if not str(target_path).strip():
        raise CommandError("Pass --packet or --fixture")
    target = Path(target_path)
    packet_path, fixture_path = _resolve_paths(target)
    manual_path = Path(manual_witness_values_path)
    values = _read_manual_values(manual_path)

    packet = _read_json(packet_path) if packet_path.exists() else {}
    fixture = _read_json(fixture_path) if fixture_path.exists() else _packet_fixture(packet)
    if not fixture:
        raise CommandError(f"No fixture found at {fixture_path} or inside {packet_path}")

    capture_files = fixture.get("capture_files") if isinstance(fixture.get("capture_files"), dict) else {}
    capture_files["manual_witness_values"] = str(manual_path)
    fixture["capture_files"] = capture_files
    fixture["manual_witness_source"] = str(manual_path)
    fixture["manual_witness_values"] = values

    if packet:
        packet["fixture"] = fixture
        _write_json(packet_path, packet)
    _write_json(fixture_path, fixture)

    return {
        "status": "updated",
        "id": str(fixture.get("id") or packet.get("id") or fixture_path.parent.name),
        "count": len(values),
        "manual_witness_values": str(manual_path),
        "packet_path": str(packet_path) if packet_path.exists() else "",
        "fixture_path": str(fixture_path),
    }


def _resolve_paths(path: Path) -> tuple[Path, Path]:
    if path.name == "packet.json":
        return path, path.with_name("fixture.json")
    if path.name == "fixture.json":
        return path.with_name("packet.json"), path
    return path / "packet.json", path / "fixture.json"


def _packet_fixture(packet: dict[str, Any]) -> dict[str, Any]:
    fixture = packet.get("fixture") if isinstance(packet.get("fixture"), dict) else {}
    return fixture


def _read_manual_values(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise CommandError(f"Manual witness values file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise CommandError("Manual witness values file must contain a JSON array")
    if not all(isinstance(row, dict) for row in data):
        raise CommandError("Manual witness values JSON array must contain only objects")
    return data


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CommandError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise CommandError(f"JSON must be an object: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
