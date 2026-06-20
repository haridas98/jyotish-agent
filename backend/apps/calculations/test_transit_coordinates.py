from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps.calculations.chart import build_birth_chart
from apps.calculations.transit_coordinates import transit_coordinate_snapshot

SNAPSHOT = Path(__file__).parent / "fixtures" / "transit_coordinate_golden_v1.json"


@pytest.mark.parametrize("case", json.loads(SNAPSHOT.read_text(encoding="utf-8"))["cases"])
def test_transit_coordinates_match_independent_golden_snapshot(case):
    actual_chart = build_birth_chart(case["input"])
    actual = transit_coordinate_snapshot(actual_chart)

    assert actual == case["expected"]
