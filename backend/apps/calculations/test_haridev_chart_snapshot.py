import json
from pathlib import Path

import pytest

from apps.calculations.chart import build_birth_chart
from apps.calculations.ephemeris import EphemerisUnavailable


SNAPSHOT = Path(__file__).parent / "fixtures" / "haridev_chart_snapshot.json"


def test_haridev_birth_chart_snapshot_protects_core_calculations():
    expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    try:
        chart = build_birth_chart(
            {
                "birth_date": "1998-04-30",
                "birth_time": "13:45",
                "place_name": "Sterlitamak",
                "latitude": 53.6304,
                "longitude": 55.9308,
                "timezone": "Asia/Yekaterinburg",
                "ayanamsa": "lahiri",
                "node_type": "true",
                "calculation_model": "drik_siddhanta",
                "house_system": "whole_sign",
                "bhava_system": "whole_sign",
                "varga_scheme": "parashara",
                "timezone_source": "iana",
            }
        )
    except EphemerisUnavailable as exc:
        pytest.skip(str(exc))

    assert chart["birth"]["utc_offset"] == expected["birth"]["utc_offset"]
    assert chart["birth"]["utc_datetime"] == expected["birth"]["utc_datetime"]
    assert compact_placement(chart["ascendant"]) == expected["ascendant"]

    grahas = {row["body"]: compact_graha(row) for row in chart["grahas"]}
    assert grahas == expected["grahas"]

    vargas = {
        code: {
            placement["body"]: placement["rashi"]
            for placement in chart["vargas"][code]["placements"]
            if placement["body"] in expected["vargas"][code]
        }
        for code in expected["vargas"]
    }
    assert vargas == expected["vargas"]

    assert chart["panchanga"]["tithi"]["name"] == expected["panchanga"]["tithi"]
    assert chart["panchanga"]["tithi"]["paksha"] == expected["panchanga"]["paksha"]
    assert chart["panchanga"]["vara"]["name"] == expected["panchanga"]["vara"]
    assert chart["panchanga"]["yoga"]["name"] == expected["panchanga"]["yoga"]
    assert chart["panchanga"]["karana"]["name"] == expected["panchanga"]["karana"]

    lords = [period["lord"] for period in chart["dashas"]["vimshottari"]["mahadashas"][:3]]
    assert lords == expected["vimshottari"]


def compact_placement(row):
    return {
        "rashi": row["rashi"],
        "nakshatra": row["nakshatra"],
        "pada": row["pada"],
        "navamsa": row["navamsa"],
    }


def compact_graha(row):
    return [row["rashi"], row["nakshatra"], row["pada"], row["navamsa"]]
