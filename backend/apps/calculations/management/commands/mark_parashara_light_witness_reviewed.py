from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


DEFAULT_REVIEW_STATUS = "reviewed"
ALLOWED_REVIEW_STATUSES = {"reviewed", "approved"}


class Command(BaseCommand):
    help = "Mark a reviewed Parashara's Light witness packet after manual evidence review."

    def add_arguments(self, parser):
        parser.add_argument("case_path", help="Case directory, packet.json, or fixture.json path.")
        parser.add_argument("--reviewer", required=True)
        parser.add_argument("--reviewed-at", default="")
        parser.add_argument(
            "--review-status",
            choices=sorted(ALLOWED_REVIEW_STATUSES),
            default=DEFAULT_REVIEW_STATUS,
        )
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        payload = mark_parashara_light_witness_reviewed(
            options["case_path"],
            reviewer=options["reviewer"],
            reviewed_at=options["reviewed_at"],
            review_status=options["review_status"],
            force=options["force"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(
                f"{payload['status']} {payload['id']} -> {payload['review_status']} "
                f"({payload['reviewer']}, {payload['reviewed_at']})"
            )


def mark_parashara_light_witness_reviewed(
    case_path: str | Path,
    *,
    reviewer: str,
    reviewed_at: str = "",
    review_status: str = DEFAULT_REVIEW_STATUS,
    force: bool = False,
) -> dict[str, Any]:
    reviewer = reviewer.strip()
    if not reviewer:
        raise CommandError("reviewer is required")
    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise CommandError(f"review_status must be one of: {', '.join(sorted(ALLOWED_REVIEW_STATUSES))}")

    packet_path, fixture_path = _resolve_paths(Path(case_path))
    packet = _read_json(packet_path) if packet_path.exists() else {}
    fixture = _read_json(fixture_path) if fixture_path.exists() else _packet_fixture(packet)
    if not fixture:
        raise CommandError(f"No fixture found at {fixture_path} or inside {packet_path}")

    missing = _missing_review_evidence(fixture)
    if missing and not force:
        raise CommandError(f"Cannot mark Parashara's Light witness reviewed; missing: {', '.join(missing)}")

    timestamp = reviewed_at.strip() or timezone.now().isoformat()
    metadata = fixture.get("pl_metadata") if isinstance(fixture.get("pl_metadata"), dict) else {}
    metadata["reviewer"] = reviewer
    metadata["reviewed_at"] = timestamp
    metadata["profile_status"] = "reviewed"
    fixture["pl_metadata"] = metadata
    fixture["review_status"] = review_status

    if packet:
        packet["fixture"] = fixture
        _write_json(packet_path, packet)
    _write_json(fixture_path, fixture)

    return {
        "status": "updated",
        "id": str(fixture.get("id") or packet.get("id") or fixture_path.parent.name),
        "review_status": review_status,
        "reviewer": reviewer,
        "reviewed_at": timestamp,
        "packet_path": str(packet_path) if packet_path.exists() else "",
        "fixture_path": str(fixture_path),
        "forced": force,
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


def _missing_review_evidence(fixture: dict[str, Any]) -> list[str]:
    metadata = fixture.get("pl_metadata") if isinstance(fixture.get("pl_metadata"), dict) else {}
    capture_files = fixture.get("capture_files") if isinstance(fixture.get("capture_files"), dict) else {}
    screenshots = capture_files.get("screenshots")
    manual_values = fixture.get("manual_witness_values")
    missing = []
    if not (str(capture_files.get("ui_state") or "").strip() or metadata.get("capture_status") == "ui_state_captured"):
        missing.append("pl_ui_state")
    if not any(
        str(metadata.get(key) or "").strip()
        for key in ("siddhanta_model", "ayanamsa", "timezone_offset", "house_system", "node_type")
    ):
        missing.append("pl_settings_evidence")
    if not (isinstance(screenshots, list) and any(str(item).strip() for item in screenshots)):
        missing.append("pl_screenshots")
    if not (isinstance(manual_values, list) and any(isinstance(item, dict) for item in manual_values)):
        missing.append("manual_witness_values")
    return missing


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
