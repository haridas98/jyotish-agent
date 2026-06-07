from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.fixture_runner import run_accuracy_fixture
from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _packet_fixture as jhora_packet_fixture,
)
from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _read_json as read_jhora_json,
)
from apps.calculations.management.commands.mark_jhora_witness_reviewed import (
    _resolve_paths as resolve_jhora_paths,
)
from apps.calculations.management.commands.mark_parashara_light_witness_reviewed import (
    _packet_fixture as pl_packet_fixture,
)
from apps.calculations.management.commands.mark_parashara_light_witness_reviewed import (
    _read_json as read_pl_json,
)
from apps.calculations.management.commands.mark_parashara_light_witness_reviewed import (
    _resolve_paths as resolve_pl_paths,
)
from apps.calculations.management.commands.preflight_witness_review import (
    _safe_next_summary,
)
from apps.calculations.management.commands.preflight_witness_review import (
    build_witness_review_preflight,
)
from apps.calculations.parashara_light_packet_report import load_parashara_light_packet_report


SCHEMA_VERSION = "jyotish-witness-review-packet-v1"


class Command(BaseCommand):
    help = "Build a compact markdown review packet before sealing a JHora/Parashara Light witness case."

    def add_arguments(self, parser):
        parser.add_argument("--jhora", required=True, help="JHora case directory, packet.json, or fixture.json.")
        parser.add_argument(
            "--parashara-light",
            required=True,
            help="Parashara Light case directory, packet.json, or fixture.json.",
        )
        parser.add_argument("--reviewer", default="Haridas")
        parser.add_argument("--reviewed-at", default="")
        parser.add_argument("--output", default="")
        parser.add_argument("--json", action="store_true")
        parser.add_argument("--include-review-commands", action="store_true")

    def handle(self, *args, **options):
        payload = build_witness_review_packet(
            jhora_path=options["jhora"],
            parashara_light_path=options["parashara_light"],
            reviewer=options["reviewer"],
            reviewed_at=options["reviewed_at"],
            output=options["output"],
            include_review_commands=options["include_review_commands"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            if payload["output_path"]:
                self.stdout.write(f"written {payload['output_path']}")
            else:
                self.stdout.write(payload["markdown"])


def build_witness_review_packet(
    *,
    jhora_path: str | Path,
    parashara_light_path: str | Path,
    reviewer: str = "Haridas",
    reviewed_at: str = "",
    output: str | Path = "",
    include_review_commands: bool = False,
) -> dict[str, Any]:
    preflight = build_witness_review_preflight(
        jhora_path=jhora_path,
        parashara_light_path=parashara_light_path,
        reviewer=reviewer,
        reviewed_at=reviewed_at,
    )
    jhora_summary = _jhora_summary(jhora_path)
    pl_summary = _parashara_light_summary(parashara_light_path)
    markdown = _markdown(
        preflight=preflight,
        jhora=jhora_summary,
        parashara_light=pl_summary,
        include_review_commands=include_review_commands,
    )
    output_path = ""
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(markdown, encoding="utf-8")
        output_path = str(target)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "written" if output_path else ("reviewable" if preflight["overall"]["reviewable"] else "blocked"),
        "output_path": output_path,
        "include_review_commands": include_review_commands,
        "preflight": preflight,
        "jhora": jhora_summary,
        "parashara_light": pl_summary,
        "markdown": markdown,
    }


def _jhora_summary(path: str | Path) -> dict[str, Any]:
    packet_path, fixture_path = resolve_jhora_paths(Path(path))
    packet = read_jhora_json(packet_path) if packet_path.exists() else {}
    fixture = read_jhora_json(fixture_path) if fixture_path.exists() else jhora_packet_fixture(packet)
    if not fixture:
        raise CommandError(f"No JHora fixture found at {fixture_path} or inside {packet_path}")
    metadata = fixture.get("jhora_metadata") if isinstance(fixture.get("jhora_metadata"), dict) else {}
    capture_files = fixture.get("capture_files") if isinstance(fixture.get("capture_files"), dict) else {}
    expected = fixture.get("expected") if isinstance(fixture.get("expected"), dict) else {}
    grahas = expected.get("grahas") if isinstance(expected.get("grahas"), dict) else {}
    jhora_expected = fixture.get("jhora_expected") if isinstance(fixture.get("jhora_expected"), dict) else {}
    screenshots = capture_files.get("screenshots") if isinstance(capture_files.get("screenshots"), list) else []
    return {
        "id": str(fixture.get("id") or packet.get("id") or fixture_path.parent.name),
        "review_status": str(fixture.get("review_status") or "draft"),
        "capture_status": str(metadata.get("capture_status") or ""),
        "timezone_offset": str(metadata.get("timezone_offset") or ""),
        "ayanamsa": str(metadata.get("ayanamsa") or ""),
        "expected_graha_count": len(grahas),
        "has_expected_ascendant": isinstance(expected.get("ascendant"), dict),
        "jhora_expected_layers": sorted(jhora_expected.keys()),
        "screenshots_count": len([item for item in screenshots if str(item).strip()]),
        "diff_summary": _jhora_diff_summary(fixture),
        "packet_path": str(packet_path) if packet_path.exists() else "",
        "fixture_path": str(fixture_path),
    }


def _parashara_light_summary(path: str | Path) -> dict[str, Any]:
    packet_path, fixture_path = resolve_pl_paths(Path(path))
    packet = read_pl_json(packet_path) if packet_path.exists() else {}
    fixture = read_pl_json(fixture_path) if fixture_path.exists() else pl_packet_fixture(packet)
    if not fixture:
        raise CommandError(f"No Parashara Light fixture found at {fixture_path} or inside {packet_path}")
    report = load_parashara_light_packet_report(packet_path if packet_path.exists() else fixture_path)
    comparison = report.get("manual_witness_comparison") if isinstance(report.get("manual_witness_comparison"), dict) else {}
    summary = comparison.get("summary") if isinstance(comparison.get("summary"), dict) else {}
    completion = comparison.get("completion") if isinstance(comparison.get("completion"), dict) else {}
    metadata = fixture.get("pl_metadata") if isinstance(fixture.get("pl_metadata"), dict) else {}
    return {
        "id": str(fixture.get("id") or packet.get("id") or fixture_path.parent.name),
        "review_status": str(fixture.get("review_status") or "draft"),
        "capture_status": str(metadata.get("capture_status") or ""),
        "manual_status": str(comparison.get("status") or "not_checked"),
        "manual_values_count": int(summary.get("manual_values_count") or 0),
        "manual_failed_count": int(summary.get("failed_count") or 0),
        "manual_completion_percent": int(completion.get("completion_percent") or 0),
        "manual_diff_summary": _manual_diff_summary(comparison),
        "packet_path": str(packet_path) if packet_path.exists() else "",
        "fixture_path": str(fixture_path),
    }


def _markdown(
    *,
    preflight: dict[str, Any],
    jhora: dict[str, Any],
    parashara_light: dict[str, Any],
    include_review_commands: bool,
) -> str:
    overall = preflight["overall"]
    jhora_preflight = preflight["jhora"]
    pl_preflight = preflight["parashara_light"]
    lines = [
        "# Witness Review Packet",
        "",
        f"- Reviewable: {_yes_no(overall['reviewable'])}",
        f"- ACK required: {_yes_no(overall['ack_required'])}",
        f"- Blocked: {_yes_no(overall['blocked'])}",
        f"- safe next step: {_safe_next_step(preflight)}",
        "",
        "## Open Diffs",
        "",
        f"- JHora failed: {jhora['diff_summary']['failed_count']}",
        *_diff_lines(jhora["diff_summary"], prefix="JHora"),
        f"- Parashara Light failed: {parashara_light['manual_diff_summary']['failed_count']}",
        *_diff_lines(parashara_light["manual_diff_summary"], prefix="PL"),
        "",
        "## JHora",
        "",
        f"- ID: `{jhora['id']}`",
        f"- status: {jhora_preflight['status']}",
        f"- Review status: `{jhora['review_status']}`",
        f"- Preflight status: `{jhora_preflight['status']}`",
        f"- Missing evidence: {_missing(jhora_preflight)}",
        f"- Timezone offset: `{jhora['timezone_offset']}`",
        f"- Ayanamsa: `{jhora['ayanamsa']}`",
        f"- Expected grahas: {jhora['expected_graha_count']}",
        f"- Expected ascendant: {_yes_no(jhora['has_expected_ascendant'])}",
        f"- JHora layers: {', '.join(jhora['jhora_expected_layers']) or 'none'}",
        f"- Screenshots: {jhora['screenshots_count']}",
        f"- Fixture: `{jhora['fixture_path']}`",
        "",
        "## Parashara Light",
        "",
        f"- ID: `{parashara_light['id']}`",
        f"- status: {pl_preflight['status']}",
        f"- Review status: `{parashara_light['review_status']}`",
        f"- Preflight status: `{pl_preflight['status']}`",
        f"- Missing evidence: {_missing(pl_preflight)}",
        f"- Manual witness status: `{parashara_light['manual_status']}`",
        f"- Manual values: {parashara_light['manual_values_count']}",
        f"- Manual failed: {parashara_light['manual_failed_count']}",
        f"- Manual completion: {parashara_light['manual_completion_percent']}%",
        f"- Fixture: `{parashara_light['fixture_path']}`",
        "",
        "## Human ACK",
        "",
        "Do not run seal until manual evidence review and diff ACK are complete.",
        "",
        "- Confirm that JHora settings, PL settings, screenshots and copied/clicked values were reviewed.",
        "- If ACK is required, only run the seal command after accepting the listed open diffs as reviewed witnesses.",
        "",
    ]
    if include_review_commands:
        lines[6:6] = [f"- Seal command: `{preflight.get('seal_command') or ''}`"]
        _insert_after(
            lines,
            f"- Missing evidence: {_missing(jhora_preflight)}",
            f"- Review command: `{jhora_preflight.get('review_command') or ''}`",
        )
        _insert_after(
            lines,
            f"- Missing evidence: {_missing(pl_preflight)}",
            f"- Review command: `{pl_preflight.get('review_command') or ''}`",
            last=True,
        )
    return "\n".join(lines)


def _jhora_diff_summary(fixture: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(fixture.get("input"), dict):
        return _empty_diff_summary(status="not_checked")
    if not any(isinstance(fixture.get(key), expected_type) for key, expected_type in _EXPECTED_KEYS):
        return _empty_diff_summary(status="not_checked")
    result = run_accuracy_fixture(fixture)
    report = result.report
    rows: list[dict[str, Any]] = []
    for comparison in report.longitude_comparisons:
        if comparison.passed:
            continue
        rows.append(
            {
                "field": f"{comparison.body}.longitude",
                "witness": round(comparison.expected_degrees, 6),
                "calculated": round(comparison.actual_degrees, 6),
                "delta_arcseconds": comparison.delta_arcseconds,
            }
        )
    for field, passed in report.exact_matches.items():
        if passed:
            continue
        rows.append({"field": field, "witness": "expected", "calculated": "calculated"})
    for field in report.missing_fields:
        rows.append({"field": field, "witness": "expected", "calculated": "missing"})
    return {
        "status": "matched" if result.passed else "diff_open",
        "failed_count": len(rows),
        "sample": rows[:10],
    }


def _manual_diff_summary(comparison: dict[str, Any]) -> dict[str, Any]:
    diffs = comparison.get("diffs") if isinstance(comparison.get("diffs"), list) else []
    rows = [
        {
            "field": f"{diff.get('body')}.{diff.get('field')}",
            "witness": diff.get("witness"),
            "calculated": diff.get("calculated"),
        }
        for diff in diffs
        if isinstance(diff, dict) and not diff.get("passed") and not diff.get("missing")
    ]
    return {
        "status": str(comparison.get("status") or "not_checked"),
        "failed_count": len(rows),
        "sample": rows[:10],
    }


def _empty_diff_summary(*, status: str) -> dict[str, Any]:
    return {"status": status, "failed_count": 0, "sample": []}


_EXPECTED_KEYS = (
    ("expected", dict),
    ("jhora_expected", dict),
    ("external_expected", list),
)


def _diff_lines(summary: dict[str, Any], *, prefix: str) -> list[str]:
    sample = summary.get("sample") if isinstance(summary.get("sample"), list) else []
    return [
        f"  - {prefix} {row.get('field')}: witness={row.get('witness')} calculated={row.get('calculated')}"
        for row in sample[:5]
        if isinstance(row, dict)
    ]


def _safe_next_step(preflight: dict[str, Any]) -> str:
    for line in _safe_next_summary(preflight).splitlines():
        if line.startswith("safe next step: "):
            return line.removeprefix("safe next step: ")
    return "review preflight first"


def _insert_after(lines: list[str], anchor: str, value: str, *, last: bool = False) -> None:
    if last:
        index = len(lines) - 1 - lines[::-1].index(anchor)
    else:
        index = lines.index(anchor)
    lines.insert(index + 1, value)


def _missing(row: dict[str, Any]) -> str:
    missing = row.get("missing_evidence") if isinstance(row.get("missing_evidence"), list) else []
    return ", ".join(str(item) for item in missing) if missing else "none"


def _yes_no(value: object) -> str:
    return "yes" if bool(value) else "no"
