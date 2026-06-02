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


def test_compare_chart_to_fixture_reports_systematic_longitude_offset():
    report = compare_chart_to_fixture(
        {
            "grahas": [
                {"body": "Surya", "longitude": 9.99, "rashi": "Mesha"},
                {"body": "Chandra", "longitude": 39.99, "rashi": "Vrishabha"},
            ],
            "ascendant": {"longitude": 69.99, "rashi": "Mithuna"},
        },
        {
            "id": "offset-case",
            "expected": {
                "grahas": {
                    "Surya": {"longitude": 10.0, "rashi": "Mesha"},
                    "Chandra": {"longitude": 40.0, "rashi": "Vrishabha"},
                },
                "ascendant": {"longitude": 70.0, "rashi": "Mithuna"},
            },
        },
    )

    assert report.diagnostics["mean_signed_delta_arcseconds"] == -36.0
    assert report.diagnostics["median_abs_delta_arcseconds"] == 36.0
    assert report.diagnostics["max_abs_delta_arcseconds"] == 36.0
    assert report.diagnostics["systematic_offset_suspected"] is True


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


def test_compare_chart_to_fixture_checks_jhora_classical_layers():
    report = compare_chart_to_fixture(
        {
            "classical": {
                "ashtakavarga": {
                    "bhinna": {
                        "Surya": {
                            "scores": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                        }
                    }
                },
                "shadbala": {
                    "items": [
                        {"body": "Surya", "known_total": 343.31},
                        {"body": "Chandra", "known_total": 400.0},
                    ]
                },
            }
        },
        {
            "id": "jhora-classical-case",
            "jhora_expected": {
                "ashtakavarga": {
                    "Su": {
                        "Mesha": 1,
                        "Vrishabha": 2,
                        "Mithuna": 3,
                        "Karka": 4,
                        "Simha": 5,
                        "Kanya": 6,
                        "Tula": 7,
                        "Vrischika": 8,
                        "Dhanu": 9,
                        "Makara": 10,
                        "Kumbha": 11,
                        "Meena": 12,
                    }
                },
                "shadbala": {
                    "Sun": {"shadbala": 343.31},
                    "Moon": {"shadbala": 443.61},
                },
            },
        },
    )

    assert report.exact_matches["jhora.ashtakavarga.Su.Mesha"] is True
    assert report.exact_matches["jhora.ashtakavarga.Su.Meena"] is True
    assert report.exact_matches["jhora.shadbala.Sun.shadbala"] is True
    assert report.exact_matches["jhora.shadbala.Moon.shadbala"] is False
    assert report.diagnostics["jhora_layers"]["ashtakavarga"]["matched"] == 12
    assert report.diagnostics["jhora_layers"]["shadbala"]["matched"] == 1
    assert report.passed is False
