import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.calculations.accuracy import ChartAccuracyReport
from apps.calculations.fixture_runner import FixtureRunResult


def _result(passed: bool, *, review_status: str = "draft", authoritative: bool = False) -> FixtureRunResult:
    return FixtureRunResult(
        fixture_id="case-1",
        source="unit-test",
        review_status=review_status,
        authoritative=authoritative,
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
    assert payload["summary"] == {
        "total": 1,
        "passed": 1,
        "failed": 0,
        "authoritative": 0,
        "authoritative_passed": 0,
        "authoritative_failed": 0,
        "jhora_verified": 0,
        "review_status_counts": {"draft": 1},
    }
    assert payload["results"][0]["fixture_id"] == "case-1"


def test_run_accuracy_fixtures_command_can_fail_on_diff(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "apps.calculations.management.commands.run_accuracy_fixtures.run_accuracy_fixtures",
        lambda path: [_result(False)],
    )

    with pytest.raises(CommandError, match="Accuracy fixtures failed"):
        call_command("run_accuracy_fixtures", str(tmp_path), "--fail-on-diff")


def test_run_accuracy_fixtures_command_can_fail_on_authoritative_diff(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "apps.calculations.management.commands.run_accuracy_fixtures.run_accuracy_fixtures",
        lambda path: [_result(False, review_status="jhora_verified", authoritative=True)],
    )

    with pytest.raises(CommandError, match="Authoritative accuracy fixtures failed"):
        call_command("run_accuracy_fixtures", str(tmp_path), "--fail-on-authoritative-diff")


def test_run_accuracy_fixtures_command_enforces_minimum_authoritative_counts(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "apps.calculations.management.commands.run_accuracy_fixtures.run_accuracy_fixtures",
        lambda path: [_result(True, review_status="reviewed", authoritative=True)],
    )

    with pytest.raises(CommandError, match="JHora verified accuracy fixture count"):
        call_command("run_accuracy_fixtures", str(tmp_path), "--min-authoritative", "1", "--min-jhora-verified", "1")
