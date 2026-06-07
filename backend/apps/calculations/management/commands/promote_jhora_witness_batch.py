from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _packet_fixture,
    _read_json,
    _resolve_paths,
)
from apps.calculations.management.commands.promote_jhora_witness_fixture import (
    DEFAULT_OUTPUT_DIR,
    promote_jhora_witness_fixture,
    promotion_blockers,
)


SCHEMA_VERSION = "jyotish-jhora-batch-promotion-v1"


class Command(BaseCommand):
    help = "Promote all ready reviewed JHora witness packets into the accuracy fixture suite."

    def add_arguments(self, parser):
        parser.add_argument(
            "--jhora-root",
            default=str(settings.ROOT_DIR / ".tmp" / "jhora"),
            help="Directory containing JHora packet/fixture artifacts.",
        )
        parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
        parser.add_argument("--overwrite", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--json", action="store_true")
        parser.add_argument("--fail-if-blocked", action="store_true")
        parser.add_argument("--fail-if-none-promoted", action="store_true")

    def handle(self, *args, **options):
        payload = promote_jhora_witness_batch(
            jhora_root=options["jhora_root"],
            output_dir=options["output_dir"],
            overwrite=options["overwrite"],
            dry_run=options["dry_run"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            self.stdout.write(_text_summary(payload))

        if options["fail_if_blocked"] and payload["summary"]["blocked_count"]:
            raise CommandError("Some JHora witness fixtures are blocked from promotion")
        if options["fail_if_none_promoted"] and not payload["summary"]["promoted_count"]:
            raise CommandError("No JHora witness fixtures were promoted")


def promote_jhora_witness_batch(
    *,
    jhora_root: str | Path,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    rows = []
    for case_path in _candidate_case_paths(Path(jhora_root)):
        rows.append(
            _promotion_row(
                case_path,
                output_dir=output_dir,
                overwrite=overwrite,
                dry_run=dry_run,
            )
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "jhora_root": str(jhora_root),
        "output_dir": str(output_dir),
        "dry_run": dry_run,
        "summary": _summary(rows),
        "cases": rows,
    }


def _promotion_row(
    case_path: Path,
    *,
    output_dir: str | Path,
    overwrite: bool,
    dry_run: bool,
) -> dict[str, Any]:
    packet_path, fixture_path = _resolve_paths(case_path)
    try:
        packet = _read_json(packet_path) if packet_path.exists() else {}
        fixture = _read_json(fixture_path) if fixture_path.exists() else _packet_fixture(packet)
    except CommandError as exc:
        return _row(case_path, status="load_error", blockers=[str(exc)])
    if not fixture:
        return _row(case_path, status="missing_fixture", blockers=["packet_or_fixture"])

    fixture_id = str(fixture.get("id") or packet.get("id") or case_path.name)
    blockers, accuracy_status = promotion_blockers(fixture)
    if blockers:
        return _row(
            case_path,
            fixture_id=fixture_id,
            status="blocked",
            blockers=blockers,
            accuracy_status=accuracy_status,
        )
    if dry_run:
        return _row(case_path, fixture_id=fixture_id, status="ready", accuracy_status=accuracy_status)

    try:
        promoted = promote_jhora_witness_fixture(
            case_path,
            output_dir=output_dir,
            overwrite=overwrite,
        )
    except CommandError as exc:
        return _row(
            case_path,
            fixture_id=fixture_id,
            status="failed",
            blockers=[str(exc)],
            accuracy_status=accuracy_status,
        )
    return _row(
        case_path,
        fixture_id=fixture_id,
        status="promoted",
        accuracy_status=accuracy_status,
        output_path=promoted["output_path"],
    )


def _candidate_case_paths(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    if not root.exists():
        return []
    seen: set[Path] = set()
    case_paths = []
    for path in [*sorted(root.rglob("packet.json")), *sorted(root.rglob("fixture.json"))]:
        key = path.parent
        if key in seen:
            continue
        seen.add(key)
        case_paths.append(key)
    return case_paths


def _row(
    case_path: Path,
    *,
    fixture_id: str = "",
    status: str,
    blockers: list[str] | None = None,
    accuracy_status: str = "",
    output_path: str = "",
) -> dict[str, Any]:
    return {
        "id": fixture_id,
        "case_path": str(case_path),
        "status": status,
        "blockers": blockers or [],
        "accuracy_status": accuracy_status,
        "output_path": output_path,
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "scanned_count": len(rows),
        "ready_count": sum(1 for row in rows if row["status"] == "ready"),
        "promoted_count": sum(1 for row in rows if row["status"] == "promoted"),
        "blocked_count": sum(1 for row in rows if row["status"] == "blocked"),
        "failed_count": sum(1 for row in rows if row["status"] in {"failed", "load_error", "missing_fixture"}),
    }


def _text_summary(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        f"scanned: {summary['scanned_count']}",
        f"ready: {summary['ready_count']}",
        f"promoted: {summary['promoted_count']}",
        f"blocked: {summary['blocked_count']}",
        f"failed: {summary['failed_count']}",
    ]
    for row in payload["cases"][:20]:
        details = ", ".join(row["blockers"]) if row["blockers"] else row.get("output_path") or row["accuracy_status"]
        lines.append(f"- {row['id'] or row['case_path']}: {row['status']} {details}".rstrip())
    return "\n".join(lines)
