from __future__ import annotations

import json

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


def _summary(results) -> dict[str, int]:
    return {
        "total": len(results),
        "passed": sum(1 for result in results if result.passed),
        "failed": sum(1 for result in results if not result.passed),
        "authoritative": sum(1 for result in results if result.authoritative),
    }


def _text_summary(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        f"fixtures: {summary['total']}",
        f"passed: {summary['passed']}",
        f"failed: {summary['failed']}",
        f"authoritative: {summary['authoritative']}",
    ]
    for result in payload["results"]:
        status = "PASS" if result["passed"] else "FAIL"
        lines.append(f"{status} {result['fixture_id']} source={result['source']}")
    return "\n".join(lines)
