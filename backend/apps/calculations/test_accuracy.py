from apps.calculations.accuracy import (
    angular_delta_arcseconds,
    compare_chart_to_fixture,
    compare_longitude,
)


def test_angular_delta_uses_shortest_wraparound_path():
    assert angular_delta_arcseconds(359.999, 0.001) == 7.2


def test_compare_longitude_marks_pass_when_within_tolerance():
    result = compare_longitude(
        body="Surya",
        expected_degrees=30.0,
        actual_degrees=30.0001,
        tolerance_arcseconds=0.5,
    )

    assert result.passed is True
    assert result.delta_arcseconds == 0.36


def test_compare_longitude_marks_fail_when_outside_tolerance():
    result = compare_longitude(
        body="Chandra",
        expected_degrees=120.0,
        actual_degrees=120.01,
        tolerance_arcseconds=10,
    )

    assert result.passed is False
    assert result.delta_arcseconds == 36


def test_compare_chart_to_fixture_reports_longitude_and_exact_matches():
    chart = {
        "grahas": [
            {
                "body": "Surya",
                "longitude": 120.0001,
                "rashi": "Karka",
                "nakshatra": "Ashlesha",
                "pada": 1,
            }
        ],
        "ascendant": {"longitude": 90.0002, "rashi": "Karka"},
        "panchanga": {"tithi": {"name": "Dvitiya"}, "yoga": {"name": "Vishkambha"}},
    }
    fixture = {
        "id": "sample-jhora-case",
        "tolerances": {"planet_longitude_arcseconds": 1.0, "lagna_arcseconds": 1.0},
        "expected": {
            "grahas": {
                "Surya": {
                    "longitude": 120.0,
                    "rashi": "Karka",
                    "nakshatra": "Ashlesha",
                    "pada": 1,
                }
            },
            "ascendant": {"longitude": 90.0, "rashi": "Karka"},
            "panchanga": {"tithi": "Dvitiya", "yoga": "Vishkambha"},
        },
    }

    report = compare_chart_to_fixture(chart, fixture)

    assert report.fixture_id == "sample-jhora-case"
    assert report.passed is True
    assert len(report.longitude_comparisons) == 2
    assert report.exact_matches["Surya.rashi"] is True
    assert report.exact_matches["panchanga.tithi"] is True


def test_compare_chart_to_fixture_checks_varga_placements():
    report = compare_chart_to_fixture(
        {
            "grahas": [{"body": "Surya", "longitude": 10.0, "rashi": "Mesha"}],
            "vargas": {
                "D9": {
                    "placements": [
                        {"body": "Lagna", "rashi": "Karka"},
                        {"body": "Surya", "rashi": "Mithuna"},
                    ]
                },
                "D60": {
                    "placements": [
                        {"body": "Surya", "rashi": "Kumbha"},
                    ]
                },
            },
        },
        {
            "id": "varga-case",
            "expected": {
                "grahas": {"Surya": {"longitude": 10.0, "rashi": "Mesha"}},
                "vargas": {
                    "D9": {
                        "Lagna": {"rashi": "Karka"},
                        "Surya": {"rashi": "Mithuna"},
                    },
                    "D60": {
                        "Surya": {"rashi": "Meena"},
                    },
                },
            },
        },
    )

    assert report.exact_matches["D9.Lagna.rashi"] is True
    assert report.exact_matches["D9.Surya.rashi"] is True
    assert report.exact_matches["D60.Surya.rashi"] is False
    assert report.passed is False
