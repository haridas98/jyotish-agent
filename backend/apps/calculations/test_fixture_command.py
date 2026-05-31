import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.calculations.accuracy import ChartAccuracyReport
from apps.calculations.fixture_runner import FixtureRunResult


def _result(passed: bool) -> FixtureRunResult:
    return FixtureRunResult(
        fixture_id="case-1",
        source="unit-test",
        review_status="draft",
        authoritative=False,
        passed=passed,
        chart={},
        report=ChartAccuracyReport(
            fixture_id="case-1",
            longitude_comparisons=[],
            exact_matches={},
            missing_fields=[],
            passed=passed,
        ),
    )


def test_run_accuracy_fixtures_command_outputs_json(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "apps.calculations.management.commands.run_accuracy_fixtures.run_accuracy_fixtures",
        lambda path: [_result(True)],
    )
    stdout = StringIO()

    call_command("run_accuracy_fixtures", str(tmp_path), "--json", stdout=stdout)

    payload = json.loads(stdout.getvalue())
    assert payload["summary"] == {"total": 1, "passed": 1, "failed": 0, "authoritative": 0}
    assert payload["results"][0]["fixture_id"] == "case-1"


def test_run_accuracy_fixtures_command_can_fail_on_diff(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "apps.calculations.management.commands.run_accuracy_fixtures.run_accuracy_fixtures",
        lambda path: [_result(False)],
    )

    with pytest.raises(CommandError, match="Accuracy fixtures failed"):
        call_command("run_accuracy_fixtures", str(tmp_path), "--fail-on-diff")
