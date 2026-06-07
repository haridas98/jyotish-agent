from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.calculations.fixture_runner import AUTHORITATIVE_REVIEW_STATUSES
from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _accuracy_status as jhora_accuracy_status,
)
from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _missing_review_evidence as missing_jhora_review_evidence,
)
from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _packet_fixture,
    _read_json,
    _resolve_paths,
)


SCHEMA_VERSION = "jyotish-jhora-accuracy-fixture-promotion-v1"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "accuracy"


class Command(BaseCommand):
    help = "Promote a reviewed JHora witness packet into the authoritative accuracy fixture suite."

    def add_arguments(self, parser):
        parser.add_argument("case_path", help="Reviewed JHora case directory, packet.json, or fixture.json path.")
        parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
        parser.add_argument("--filename", default="", help="Output JSON filename. Defaults to <fixture id>.json.")
        parser.add_argument("--overwrite", action="store_true")
        parser.add_argument("--json", action="store_true")

    def handle(self, *args, **options):
        payload = promote_jhora_witness_fixture(
            options["case_path"],
            output_dir=options["output_dir"],
            filename=options["filename"],
            overwrite=options["overwrite"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(f"{payload['status']} {payload['id']} -> {payload['output_path']}")


def promote_jhora_witness_fixture(
    case_path: str | Path,
    *,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    filename: str = "",
    overwrite: bool = False,
) -> dict[str, Any]:
    packet_path, fixture_path = _resolve_paths(Path(case_path))
    packet = _read_json(packet_path) if packet_path.exists() else {}
    fixture = _read_json(fixture_path) if fixture_path.exists() else _packet_fixture(packet)
    if not fixture:
        raise CommandError(f"No fixture found at {fixture_path} or inside {packet_path}")

    blockers, accuracy_status = promotion_blockers(fixture)
    if blockers:
        raise CommandError(f"Cannot promote JHora witness fixture; blocked by: {', '.join(blockers)}")

    fixture_id = str(fixture.get("id") or packet.get("id") or fixture_path.parent.name).strip()
    if not fixture_id:
        raise CommandError("Cannot promote JHora witness fixture; fixture id is required")
    output_root = Path(output_dir)
    output_name = filename.strip() or f"{_safe_filename(fixture_id)}.json"
    if not output_name.endswith(".json"):
        output_name += ".json"
    output_path = output_root / output_name
    if output_path.exists() and not overwrite:
        raise CommandError(f"Output fixture already exists: {output_path}")

    promoted = copy.deepcopy(fixture)
    promoted["id"] = fixture_id
    promoted["source"] = str(promoted.get("source") or "jhora_reviewed_witness")
    promoted["promotion_metadata"] = _promotion_metadata(
        promoted,
        case_path=case_path,
        packet_path=packet_path if packet_path.exists() else None,
        fixture_path=fixture_path if fixture_path.exists() else None,
        accuracy_status=accuracy_status,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(promoted, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "promoted",
        "id": fixture_id,
        "review_status": promoted["review_status"],
        "accuracy_status": accuracy_status,
        "output_path": str(output_path),
    }


def promotion_blockers(fixture: dict[str, Any]) -> tuple[list[str], str]:
    blockers: list[str] = []
    review_status = str(fixture.get("review_status") or "draft")
    if review_status not in AUTHORITATIVE_REVIEW_STATUSES:
        blockers.append("authoritative_review_status")
    blockers.extend(missing_jhora_review_evidence(fixture))

    metadata = fixture.get("jhora_metadata") if isinstance(fixture.get("jhora_metadata"), dict) else {}
    if not str(metadata.get("reviewer") or "").strip():
        blockers.append("reviewer")
    if not str(metadata.get("reviewed_at") or "").strip():
        blockers.append("reviewed_at")
    if not _has_expected_data(fixture):
        blockers.append("expected_or_jhora_expected")

    accuracy_status = str(metadata.get("accuracy_status") or "")
    if not accuracy_status:
        accuracy_status = jhora_accuracy_status(fixture)
    if accuracy_status == "not_checked":
        blockers.append("accuracy_status_checked")
    if accuracy_status == "diff_open" and not bool(metadata.get("accuracy_diff_acknowledged")):
        blockers.append("accuracy_diff_acknowledgement")
    return _dedupe(blockers), accuracy_status


def _promotion_metadata(
    fixture: dict[str, Any],
    *,
    case_path: str | Path,
    packet_path: Path | None,
    fixture_path: Path | None,
    accuracy_status: str,
) -> dict[str, Any]:
    metadata = fixture.get("promotion_metadata") if isinstance(fixture.get("promotion_metadata"), dict) else {}
    metadata.update(
        {
            "schema_version": SCHEMA_VERSION,
            "promotion_status": "authoritative_accuracy_fixture",
            "gate": "reviewed_jhora_witness",
            "accuracy_status": accuracy_status,
            "source_case_path": str(case_path),
            "source_packet_path": str(packet_path or ""),
            "source_fixture_path": str(fixture_path or ""),
            "promoted_at": timezone.now().isoformat(),
        }
    )
    return metadata


def _has_expected_data(fixture: dict[str, Any]) -> bool:
    return _has_content(fixture.get("expected")) or _has_content(fixture.get("jhora_expected"))


def _has_content(value: Any) -> bool:
    if isinstance(value, dict):
        return any(_has_content(item) for item in value.values())
    if isinstance(value, list):
        return any(_has_content(item) for item in value)
    return value not in (None, "")


def _safe_filename(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip(".-")
    return safe or "jhora-fixture"


def _dedupe(values: list[str]) -> list[str]:
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result
