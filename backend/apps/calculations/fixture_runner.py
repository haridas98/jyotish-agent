from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .accuracy import ChartAccuracyReport, compare_chart_to_fixture
from .chart import build_birth_chart
from .ephemeris import EphemerisProvider

AUTHORITATIVE_REVIEW_STATUSES = {"approved", "jhora_verified", "reviewed"}


@dataclass(frozen=True)
class FixtureRunResult:
    fixture_id: str
    source: str
    review_status: str
    authoritative: bool
    passed: bool
    chart: dict[str, Any]
    report: ChartAccuracyReport

    def as_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "source": self.source,
            "review_status": self.review_status,
            "authoritative": self.authoritative,
            "passed": self.passed,
            "report": asdict(self.report),
        }


def run_accuracy_fixture(
    fixture: dict[str, Any],
    provider: EphemerisProvider | None = None,
) -> FixtureRunResult:
    chart = build_birth_chart(fixture["input"], provider=provider)
    report = compare_chart_to_fixture(chart, fixture)
    review_status = str(fixture.get("review_status", "draft"))
    return FixtureRunResult(
        fixture_id=str(fixture.get("id", "")),
        source=str(fixture.get("source", "")),
        review_status=review_status,
        authoritative=review_status in AUTHORITATIVE_REVIEW_STATUSES,
        passed=report.passed,
        chart=chart,
        report=report,
    )


def load_accuracy_fixtures(path: str | Path) -> list[dict[str, Any]]:
    fixture_path = Path(path)
    if fixture_path.is_file():
        return [_load_fixture_file(fixture_path)]

    return [_load_fixture_file(item) for item in sorted(fixture_path.glob("*.json"))]


def run_accuracy_fixtures(path: str | Path) -> list[FixtureRunResult]:
    return [run_accuracy_fixture(fixture) for fixture in load_accuracy_fixtures(path)]


def _load_fixture_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Fixture must be a JSON object: {path}")
    if "id" not in data:
        data["id"] = path.stem
    return data
