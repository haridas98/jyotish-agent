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
            "settings": {"ayanamsa_degrees": 23.10},
            "grahas": [
                {"body": "Surya", "longitude": 9.99, "rashi": "Mesha"},
                {"body": "Chandra", "longitude": 39.99, "rashi": "Vrishabha"},
            ],
            "ascendant": {"longitude": 69.99, "rashi": "Mithuna"},
        },
        {
            "id": "offset-case",
            "jhora_metadata": {"ayanamsa_degrees": 23.09},
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
    assert report.diagnostics["ayanamsa"]["delta_arcseconds"] == 36.0
    assert report.diagnostics["ayanamsa"]["corrected_max_abs_delta_arcseconds"] == 0.0


def test_jhora_special_time_lagnas_report_formula_family_corrected_parity():
    report = compare_chart_to_fixture(
        {
            "classical": {
                "special_points": {
                    "vedic_points": {
                        "items": [
                            {"key": "bhava_lagna", "name": "Bhava Lagna", "longitude": 119.312663},
                            {"key": "hora_lagna", "name": "Hora Lagna", "longitude": 222.962663},
                            {"key": "ghati_lagna", "name": "Ghati Lagna", "longitude": 173.912663},
                        ]
                    }
                }
            }
        },
        {
            "id": "time-lagna-family-case",
            "tolerances": {"special_point_arcseconds": 1.0},
            "jhora_expected": {
                "special_points": {
                    "Bhava Lagna": {"longitude": 119.346867},
                    "Hora Lagna": {"longitude": 223.009736},
                    "Ghati Lagna": {"longitude": 173.998353},
                }
            },
        },
    )

    special = report.diagnostics["jhora_layers"]["special_points"]
    assert special["matched"] == 3
    assert special["failed"] == 0
    assert special["correction_profile"]["formula_family"] == "surya_at_sunrise_plus_elapsed_ghati"
    assert special["correction_profile"]["corrected"] == 3
    assert report.exact_matches["jhora.special_points.Bhava Lagna.longitude"] is True
    bhava_row = special["rows"][0]
    assert bhava_row["raw_passed"] is False
    assert bhava_row["passed"] is True
    assert bhava_row["corrected_delta_arcseconds"] <= 1.0


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


def test_compare_chart_to_fixture_normalizes_jhora_panchanga_names():
    report = compare_chart_to_fixture(
        {
            "panchanga": {
                "tithi": {"name": "Panchami", "paksha": "Shukla"},
                "vara": {"name": "Guruvara"},
                "yoga": {"name": "Sukarma"},
                "karana": {"name": "Bava"},
            }
        },
        {
            "id": "jhora-panchanga-aliases",
            "expected": {
                "panchanga": {
                    "tithi": "Sukla Panchami",
                    "vara": "Thursday",
                    "yoga": "Sukarman",
                    "karana": "Bava",
                }
            },
        },
    )

    assert report.exact_matches["panchanga.tithi"] is True
    assert report.exact_matches["panchanga.vara"] is True
    assert report.exact_matches["panchanga.yoga"] is True
    assert report.exact_matches["panchanga.karana"] is True


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
    assert report.diagnostics["vargas"] == {"checked": 3, "matched": 2, "failed": 1, "missing": 0}
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
                "vimshopaka_bala": {
                    "items": [
                        {
                            "body": "Surya",
                            "scheme_scores": {
                                "dashavarga": 12.10,
                                "shodasha": 12.93,
                                "saptavarga": 12.43,
                                "shadvarga": 14.40,
                            },
                        },
                        {
                            "body": "Chandra",
                            "scheme_scores": {
                                "dashavarga": 12.0,
                                "shodasha": 12.0,
                            },
                        },
                    ]
                },
                "special_points": {
                    "upagrahas": {
                        "items": [
                            {"key": "gulika", "name": "Gulika/Mandi", "longitude": 81.0},
                        ]
                    },
                    "vedic_points": {
                        "items": [
                            {"key": "hora_lagna", "name": "Hora Lagna", "longitude": 223.0},
                        ]
                    },
                },
                "yogas": {
                    "items": [
                        {"key": "ruchaka_mahapurusha", "name": "Ruchaka Mahapurusha"},
                        {"key": "viparita_harsha", "name": "Harsha Viparita Raja"},
                    ]
                },
            }
        },
        {
            "id": "jhora-classical-case",
            "jhora_metadata": {
                "profile_status": "unverified",
                "siddhanta_model": "drik_siddhanta",
                "ayanamsa": "Lahiri",
            },
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
                "vimsopaka": {
                    "Sun": {
                        "dasa_varga": {"score": 12.10},
                        "shodasa_varga": {"score": 12.93},
                        "sapta_varga": {"score": 12.43},
                        "shad_varga": {"score": 14.40},
                    },
                    "Moon": {
                        "dasa_varga": {"score": 16.13},
                        "shodasa_varga": {"score": 14.38},
                    },
                },
                "special_points": {
                    "Gulika": {"longitude": 81.0},
                    "Hora Lagna": {"longitude": 223.1},
                },
                "ui_tables": {
                    "identified": {
                        "active_yogas": {
                            "rows": [
                                [
                                    "Ruchaka",
                                    "D-1",
                                    "Ma",
                                    "Natural leader, enterprising and bold",
                                    "Mars in a kendra in moolatrikona or own or exaltation sign",
                                ],
                                [
                                    "Viparita Raja Yoga",
                                    "D-1",
                                    "Ju",
                                    "Success after pressures",
                                    "6th lord in 8th or 12th",
                                ],
                                [
                                    "Brahma (2)",
                                    "D-1",
                                    "Ju, Ve, Me",
                                    "Happy and learned",
                                    "Jupiter, Venus, Mercury in kendras",
                                ],
                            ]
                        }
                    }
                },
            },
        },
    )

    assert report.exact_matches["jhora.ashtakavarga.Su.Mesha"] is True
    assert report.exact_matches["jhora.ashtakavarga.Su.Meena"] is True
    assert report.exact_matches["jhora.shadbala.Sun.shadbala"] is True
    assert report.exact_matches["jhora.shadbala.Moon.shadbala"] is False
    assert report.diagnostics["jhora_layers"]["ashtakavarga"]["matched"] == 12
    assert report.diagnostics["jhora_profile"]["status"] == "unverified"
    assert report.diagnostics["jhora_profile"]["siddhanta_model"] == "drik_siddhanta"
    assert report.diagnostics["jhora_profile"]["ayanamsa"] == "Lahiri"
    assert report.diagnostics["jhora_layers"]["shadbala"]["matched"] == 1
    assert report.diagnostics["jhora_layers"]["vimsopaka"]["matched"] == 4
    assert report.diagnostics["jhora_layers"]["vimsopaka"]["failed"] == 2
    assert report.diagnostics["jhora_layers"]["special_points"]["matched"] == 1
    assert report.diagnostics["jhora_layers"]["special_points"]["failed"] == 1
    assert report.diagnostics["jhora_layers"]["active_yogas"]["checked"] == 3
    assert report.diagnostics["jhora_layers"]["active_yogas"]["matched"] == 2
    assert report.diagnostics["jhora_layers"]["active_yogas"]["failed"] == 1
    assert report.exact_matches["jhora.active_yogas.ruchaka"] is True
    assert report.exact_matches["jhora.active_yogas.brahma_2"] is False
    assert report.diagnostics["jhora_layers"]["shadbala"]["rows"][0] == {
        "body": "Surya",
        "jhora_body": "Sun",
        "expected": 343.31,
        "actual": 343.31,
        "delta": 0.0,
        "passed": True,
        "components": {},
        "expected_outputs": {},
        "actual_outputs": {},
        "subcomponents": {},
        "audit_flags": [],
    }
    assert report.diagnostics["jhora_layers"]["shadbala"]["rows"][1]["delta"] == -43.61
    assert report.passed is False


def test_compare_chart_to_fixture_checks_external_service_layers_without_authority_claim():
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
                        {"body": "Surya", "known_total": 300.0},
                    ]
                },
            }
        },
        {
            "id": "external-service-case",
            "external_expected": [
                {
                    "id": "vedaansh",
                    "name": "Vedaansh",
                    "authority_tier": "black_box_service",
                    "expected": {
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
                        },
                    },
                }
            ],
        },
    )

    external = report.diagnostics["external_layers"]["vedaansh"]

    assert report.exact_matches["external.vedaansh.ashtakavarga.Su.Mesha"] is True
    assert report.exact_matches["external.vedaansh.shadbala.Sun.shadbala"] is False
    assert external["name"] == "Vedaansh"
    assert external["authority_tier"] == "black_box_service"
    assert external["ashtakavarga"]["matched"] == 12
    assert external["shadbala"]["failed"] == 1
    assert report.diagnostics["authority"]["black_box_services"] == 1


def test_compare_chart_to_fixture_can_skip_unconfirmed_external_capture():
    report = compare_chart_to_fixture(
        {"classical": {}},
        {
            "id": "raw-external-case",
            "external_expected": [
                {
                    "id": "vedic_horo",
                    "name": "Vedic-Horo",
                    "authority_tier": "black_box_service",
                    "compare": False,
                    "skip_reason": "visual cell order not confirmed",
                    "expected": {
                        "ashtakavarga": {
                            "Su": {"Mesha": 5},
                        },
                    },
                }
            ],
        },
    )

    assert report.passed is True
    assert report.exact_matches == {}
    assert report.diagnostics["external_layers"]["vedic_horo"]["skipped"] is True
    assert report.diagnostics["external_layers"]["vedic_horo"]["reason"] == "visual cell order not confirmed"
