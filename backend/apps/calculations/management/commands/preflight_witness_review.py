from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand

from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _accuracy_status as jhora_accuracy_status,
)
from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _missing_review_evidence as missing_jhora_review_evidence,
)
from apps.calculations.management.commands.mark_parashara_light_witness_reviewed import (
    _manual_witness_status as parashara_light_manual_witness_status,
)
from apps.calculations.management.commands.mark_parashara_light_witness_reviewed import (
    _missing_review_evidence as missing_parashara_light_review_evidence,
)


class Command(BaseCommand):
    help = "Preview JHora/Parashara Light review marker status without changing packet files."

    def add_arguments(self, parser):
        parser.add_argument("--jhora", default="", help="JHora case directory, packet.json, or fixture.json.")
        parser.add_argument("--parashara-light", default="", help="PL case directory, packet.json, or fixture.json.")
        parser.add_argument("--reviewer", default="Haridas")
        parser.add_argument("--reviewed-at", default="")
        parser.add_argument("--safe-next-only", action="store_true")

    def handle(self, *args, **options):
        payload = build_witness_review_preflight(
            jhora_path=options["jhora"],
            parashara_light_path=options["parashara_light"],
            reviewer=options["reviewer"],
            reviewed_at=options["reviewed_at"],
        )
        if options["safe_next_only"]:
            self.stdout.write(_safe_next_summary(payload))
        else:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))


def build_witness_review_preflight(
    *,
    jhora_path: str | Path = "",
    parashara_light_path: str | Path = "",
    reviewer: str = "Haridas",
    reviewed_at: str = "",
) -> dict[str, Any]:
    jhora = _jhora_preflight(jhora_path, reviewer=reviewer, reviewed_at=reviewed_at) if jhora_path else _missing("jhora")
    parashara_light = (
        _parashara_light_preflight(parashara_light_path, reviewer=reviewer, reviewed_at=reviewed_at)
        if parashara_light_path
        else _missing("parashara_light")
    )
    parts = [row for row in (jhora, parashara_light) if row["available"]]
    blocked = any(row["missing_evidence"] for row in parts)
    ack_required = any(bool(row["ack_required"]) for row in parts)
    overall = {
        "reviewable": bool(parts) and not blocked,
        "ack_required": ack_required,
        "blocked": blocked,
    }
    return {
        "schema_version": "jyotish-witness-review-preflight-v1",
        "overall": overall,
        "seal_command": _seal_command(
            jhora_path,
            parashara_light_path,
            reviewer=reviewer,
            reviewed_at=reviewed_at,
            ack_required=ack_required,
        )
        if overall["reviewable"] and jhora_path and parashara_light_path
        else "",
        "jhora": jhora,
        "parashara_light": parashara_light,
    }


def _jhora_preflight(path: str | Path, *, reviewer: str, reviewed_at: str) -> dict[str, Any]:
    packet_path, fixture_path = _resolve_paths(Path(path))
    packet = _read_json(packet_path) if packet_path.exists() else {}
    fixture = _read_json(fixture_path) if fixture_path.exists() else _packet_fixture(packet)
    if not fixture:
        return _missing("jhora", path)
    missing = missing_jhora_review_evidence(fixture)
    status = "blocked" if missing else jhora_accuracy_status(fixture)
    ack_required = status == "diff_open"
    return {
        "available": True,
        "source": "jhora",
        "id": str(fixture.get("id") or packet.get("id") or fixture_path.parent.name),
        "status": status,
        "missing_evidence": missing,
        "ack_required": ack_required,
        "review_command": _review_command(
            "mark_jhora_witness_reviewed",
            path,
            reviewer=reviewer,
            reviewed_at=reviewed_at,
            ack_required=ack_required,
        )
        if not missing
        else "",
        "packet_path": str(packet_path) if packet_path.exists() else "",
        "fixture_path": str(fixture_path),
    }


def _parashara_light_preflight(path: str | Path, *, reviewer: str, reviewed_at: str) -> dict[str, Any]:
    packet_path, fixture_path = _resolve_paths(Path(path))
    packet = _read_json(packet_path) if packet_path.exists() else {}
    fixture = _read_json(fixture_path) if fixture_path.exists() else _packet_fixture(packet)
    if not fixture:
        return _missing("parashara_light", path)
    missing = missing_parashara_light_review_evidence(fixture)
    status = "blocked" if missing else parashara_light_manual_witness_status(packet, fixture)
    ack_required = status == "diff_open"
    return {
        "available": True,
        "source": "parashara_light",
        "id": str(fixture.get("id") or packet.get("id") or fixture_path.parent.name),
        "status": status,
        "missing_evidence": missing,
        "ack_required": ack_required,
        "review_command": _review_command(
            "mark_parashara_light_witness_reviewed",
            path,
            reviewer=reviewer,
            reviewed_at=reviewed_at,
            ack_required=ack_required,
        )
        if not missing
        else "",
        "packet_path": str(packet_path) if packet_path.exists() else "",
        "fixture_path": str(fixture_path),
    }


def _review_command(
    command: str,
    path: str | Path,
    *,
    reviewer: str,
    reviewed_at: str,
    ack_required: bool,
) -> str:
    parts = [
        ".\\.venv\\Scripts\\python.exe",
        "manage.py",
        command,
        str(path),
        "--reviewer",
        reviewer,
    ]
    if reviewed_at:
        parts.extend(["--reviewed-at", reviewed_at])
    if ack_required:
        parts.append("--ack-diff-open")
    return " ".join(_ps_quote(part) for part in parts)


def _seal_command(
    jhora_path: str | Path,
    parashara_light_path: str | Path,
    *,
    reviewer: str,
    reviewed_at: str,
    ack_required: bool,
) -> str:
    parts = [
        ".\\.venv\\Scripts\\python.exe",
        "manage.py",
        "seal_witness_case",
        "--jhora",
        str(jhora_path),
        "--parashara-light",
        str(parashara_light_path),
        "--reviewer",
        reviewer,
    ]
    if reviewed_at:
        parts.extend(["--reviewed-at", reviewed_at])
    if ack_required:
        parts.append("--ack-diff-open")
    return " ".join(_ps_quote(part) for part in parts)


def _ps_quote(value: str) -> str:
    if value and not any(char.isspace() for char in value):
        return value
    return "'" + value.replace("'", "''") + "'"


def _resolve_paths(path: Path) -> tuple[Path, Path]:
    if path.name == "packet.json":
        return path, path.with_name("fixture.json")
    if path.name == "fixture.json":
        return path.with_name("packet.json"), path
    return path / "packet.json", path / "fixture.json"


def _packet_fixture(packet: dict[str, Any]) -> dict[str, Any]:
    fixture = packet.get("fixture") if isinstance(packet.get("fixture"), dict) else {}
    return fixture


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    return payload if isinstance(payload, dict) else {}


def _safe_next_summary(payload: dict[str, Any]) -> str:
    overall = payload.get("overall") if isinstance(payload.get("overall"), dict) else {}
    jhora = payload.get("jhora") if isinstance(payload.get("jhora"), dict) else {}
    parashara_light = (
        payload.get("parashara_light") if isinstance(payload.get("parashara_light"), dict) else {}
    )
    lines = [
        f"reviewable: {_bool_text(bool(overall.get('reviewable')))}",
        f"ack required: {_bool_text(bool(overall.get('ack_required')))}",
        f"blocked: {_bool_text(bool(overall.get('blocked')))}",
        f"jhora status: {jhora.get('status') or 'missing'}",
        f"parashara light status: {parashara_light.get('status') or 'missing'}",
    ]
    if overall.get("blocked"):
        lines.append("safe next step: resolve missing evidence before review")
    elif overall.get("ack_required"):
        lines.append("safe next step: human ACK required before mark/seal")
    elif overall.get("reviewable"):
        lines.append("safe next step: ready for explicit review command")
    else:
        lines.append("safe next step: capture JHora/PL packet or fixture first")
    return "\n".join(lines)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _missing(source: str, path: str | Path = "") -> dict[str, Any]:
    return {
        "available": False,
        "source": source,
        "id": "",
        "status": "missing",
        "missing_evidence": ["packet_or_fixture"],
        "ack_required": False,
        "review_command": "",
        "packet_path": "",
        "fixture_path": str(path),
    }
