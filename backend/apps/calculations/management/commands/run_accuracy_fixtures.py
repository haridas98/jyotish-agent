from __future__ import annotations

import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.calculations.fixture_runner import run_accuracy_fixtures


class Command(BaseCommand):
    help = "Run chart accuracy fixtures and report comparison results."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Fixture JSON file or directory with JSON fixtures.")
        parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
        parser.add_argument(
            "--fail-on-diff",
            action="store_true",
            help="Exit with error if any fixture fails.",
        )
        parser.add_argument(
            "--fail-on-authoritative-diff",
            action="store_true",
            help="Exit with error if any authoritative fixture fails.",
        )
        parser.add_argument(
            "--min-authoritative",
            type=int,
            default=0,
            help="Exit with error unless at least this many authoritative fixtures are present.",
        )
        parser.add_argument(
            "--min-jhora-verified",
            type=int,
            default=0,
            help="Exit with error unless at least this many jhora_verified fixtures are present.",
        )

    def handle(self, *args, **options):
        results = run_accuracy_fixtures(options["path"])
        payload = {
            "summary": _summary(results),
            "results": [result.as_dict() for result in results],
        }

        if options["json"]:
            self.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
        else:
            self.stdout.write(_text_summary(payload))

        if options["fail_on_diff"] and payload["summary"]["failed"]:
            raise CommandError("Accuracy fixtures failed")
        if options["fail_on_authoritative_diff"] and payload["summary"]["authoritative_failed"]:
            raise CommandError("Authoritative accuracy fixtures failed")
        if payload["summary"]["authoritative"] < options["min_authoritative"]:
            raise CommandError("Authoritative accuracy fixture count is below required minimum")
        if payload["summary"]["jhora_verified"] < options["min_jhora_verified"]:
            raise CommandError("JHora verified accuracy fixture count is below required minimum")


def _summary(results) -> dict[str, Any]:
    review_status_counts: dict[str, int] = {}
    for result in results:
        review_status_counts[result.review_status] = review_status_counts.get(result.review_status, 0) + 1
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.passed),
        "failed": sum(1 for result in results if not result.passed),
        "authoritative": sum(1 for result in results if result.authoritative),
        "authoritative_passed": sum(1 for result in results if result.authoritative and result.passed),
        "authoritative_failed": sum(1 for result in results if result.authoritative and not result.passed),
        "jhora_verified": review_status_counts.get("jhora_verified", 0),
        "review_status_counts": review_status_counts,
    }


def _text_summary(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        f"fixtures: {summary['total']}",
        f"passed: {summary['passed']}",
        f"failed: {summary['failed']}",
        f"authoritative: {summary['authoritative']}",
        f"authoritative passed: {summary['authoritative_passed']}",
        f"authoritative failed: {summary['authoritative_failed']}",
        f"jhora verified: {summary['jhora_verified']}",
    ]
    for result in payload["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(f"{status} {result['fixture_id']} source={result['source']}")
    return "\n".join(lines)
