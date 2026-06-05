from datetime import datetime

import pytest

from apps.calculations.classical import (
    argala_summary,
    ashtakavarga,
    baladi_avastha,
    classical_calculations,
    shadbala_summary,
    special_points,
    vimshopaka_bala,
    yoga_coverage,
    yoga_signatures,
    _abbreviated_ahargana,
    _hora_lord,
)
from apps.calculations.constants import RASHIS


def test_baladi_avastha_uses_odd_even_sign_direction():
    assert baladi_avastha(2.0) == {
        "state": "Bala",
        "strength": 0.25,
        "degree_band": "0-6",
    }
    assert baladi_avastha(32.0) == {
        "state": "Mrita",
        "strength": 0.0,
        "degree_band": "0-6",
    }
    assert baladi_avastha(44.0)["state"] == "Yuva"


def test_yoga_signatures_detect_common_chart_patterns():
    chart = {
        "grahas": [
            {"body": "Chandra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Guru", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Surya", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Budha", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Mangala", "rashi_index": 0, "rashi": "Mesha"},
        ]
    }

    keys = {item["key"] for item in yoga_signatures(chart)}

    assert "gaja_kesari" in keys
    assert "budha_aditya" in keys
    assert "chandra_mangala" in keys


def test_yoga_signatures_detect_mahapurusha_lunar_solar_and_amala_patterns():
    chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Chandra", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Mangala", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Budha", "rashi_index": 4, "rashi": "Simha"},
            {"body": "Guru", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Shukra", "rashi_index": 9, "rashi": "Makara"},
            {"body": "Shani", "rashi_index": 11, "rashi": "Meena"},
            {"body": "Surya", "rashi_index": 1, "rashi": "Vrishabha"},
        ],
    }

    rows = {item["key"]: item for item in yoga_signatures(chart)}

    assert rows["ruchaka_mahapurusha"]["status"] == "calculated_needs_citation"
    assert rows["durudhara"]["bodies"] == ["Budha", "Guru"]
    assert rows["veshi"]["bodies"] == ["Guru"]
    assert rows["voshi"]["bodies"] == ["Mangala"]
    assert rows["ubhayachari"]["status"] == "calculated_needs_citation"
    assert rows["amala"]["reference"] == "Lagna"


def test_yoga_signatures_detect_lordship_and_cancellation_patterns():
    chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Chandra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Mangala", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Budha", "rashi_index": 7, "rashi": "Vrischika"},
            {"body": "Guru", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Shukra", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Shani", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Surya", "rashi_index": 4, "rashi": "Simha"},
        ],
    }

    rows = {item["key"]: item for item in yoga_signatures(chart)}

    assert rows["dharma_karmadhipati_raja"]["bodies"] == ["Guru", "Shani"]
    assert rows["kendra_trikona_raja"]["reference"] == "Lagna"
    assert rows["second_lord_eleventh_lord_link"]["bodies"] == ["Shukra", "Shani"]
    assert rows["viparita_harsha"]["bodies"] == ["Budha"]
    assert rows["neecha_bhanga_raja"]["bodies"] == ["Mangala", "Chandra"]


def test_yoga_coverage_exposes_full_catalog_with_detected_and_pending_rows():
    chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Chandra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Guru", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Surya", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Budha", "rashi_index": 5, "rashi": "Kanya"},
        ],
    }

    payload = yoga_coverage(chart)
    rows = {row["key"]: row for row in payload["coverage"]}

    assert payload["summary"]["catalog_total"] >= 90
    assert payload["summary"]["detected_count"] >= 2
    assert rows["gaja_kesari"]["present"] is True
    assert rows["budha_aditya"]["present"] is True
    assert rows["sunapha"]["status"] == "checked_not_present"
    assert rows["pravrajya"]["status"] == "checked_not_present"
    assert rows["pravrajya"]["formula"]["description"]


def test_yoga_signatures_detect_nabhasa_and_sankhya_formula_groups():
    movable_one_house_chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Chandra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Mangala", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Budha", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Guru", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Shukra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Shani", "rashi_index": 0, "rashi": "Mesha"},
        ],
    }
    kendra_chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Chandra", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Mangala", "rashi_index": 6, "rashi": "Tula"},
            {"body": "Budha", "rashi_index": 9, "rashi": "Makara"},
            {"body": "Guru", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Shukra", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Shani", "rashi_index": 6, "rashi": "Tula"},
        ],
    }
    seven_house_chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Chandra", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Mangala", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Budha", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Guru", "rashi_index": 4, "rashi": "Simha"},
            {"body": "Shukra", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Shani", "rashi_index": 6, "rashi": "Tula"},
        ],
    }

    movable_keys = {item["key"] for item in yoga_signatures(movable_one_house_chart)}
    kendra_keys = {item["key"] for item in yoga_signatures(kendra_chart)}
    seven_house_keys = {item["key"] for item in yoga_signatures(seven_house_chart)}
    coverage = yoga_coverage(movable_one_house_chart)

    assert {"rajju_nabhasa", "gola_nabhasa"}.issubset(movable_keys)
    assert "kamala_nabhasa" in kendra_keys
    assert "nauka_nabhasa" in seven_house_keys
    assert coverage["summary"]["formula_pending_count"] == 0
    assert coverage["summary"]["calculation_pending_count"] == 0


def test_yoga_signatures_detect_more_named_formula_groups():
    clustered_chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Chandra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Mangala", "rashi_index": 7, "rashi": "Vrischika"},
            {"body": "Budha", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Guru", "rashi_index": 7, "rashi": "Vrischika"},
            {"body": "Shukra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Shani", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Rahu", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Ketu", "rashi_index": 6, "rashi": "Tula"},
        ],
    }
    vesi_chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Chandra", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Mangala", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Budha", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Guru", "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Shukra", "rashi_index": 6, "rashi": "Tula"},
            {"body": "Shani", "rashi_index": 1, "rashi": "Vrishabha"},
        ],
    }

    rows = {item["key"]: item for item in yoga_signatures(clustered_chart)}
    vesi_rows = {item["key"]: item for item in yoga_signatures(vesi_chart)}

    assert rows["grahana"]["bodies"] == ["Chandra", "Surya", "Rahu"]
    assert rows["shakata"]["bodies"] == ["Chandra", "Guru"]
    assert rows["mangala_dosha"]["reference"] == "Lagna/Chandra/Shukra"
    assert rows["pravrajya"]["bodies"] == ["Chandra", "Shani", "Shukra", "Surya"]
    assert vesi_rows["subha_vesi"]["bodies"] == ["Budha"]
    assert vesi_rows["asubha_vesi"]["bodies"] == ["Mangala", "Shani"]


def test_yoga_signatures_detect_dhana_learning_and_raja_formula_groups():
    chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "rashi_index": 4, "rashi": "Simha"},
            {"body": "Chandra", "rashi_index": 10, "rashi": "Kumbha"},
            {"body": "Mangala", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Budha", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Guru", "rashi_index": 8, "rashi": "Dhanu"},
            {"body": "Shukra", "rashi_index": 6, "rashi": "Tula"},
            {"body": "Shani", "rashi_index": 10, "rashi": "Kumbha"},
        ],
    }

    rows = {item["key"]: item for item in yoga_signatures(chart)}

    assert rows["lagna_lord_kendra_trikona_raja"]["bodies"] == ["Mangala"]
    assert rows["lakshmi"]["reference"] == "Lagna"
    assert rows["saraswati"]["bodies"] == ["Budha", "Guru", "Shukra"]
    assert rows["vasumati"]["reference"] == "Lagna/Chandra"
    assert rows["chandra_guru_dhana"]["bodies"] == ["Chandra", "Guru"]
    assert rows["labha_lord_strength"]["bodies"] == ["Shani"]
    assert rows["bahu_dhana"]["status"] == "calculated_needs_citation"


def test_yoga_signatures_detect_remaining_rare_risk_and_status_groups():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "rashi_index": 4, "rashi": "Simha"},
            {"body": "Chandra", "rashi_index": 10, "rashi": "Kumbha"},
            {"body": "Mangala", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Budha", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Guru", "rashi_index": 8, "rashi": "Dhanu"},
            {"body": "Shukra", "rashi_index": 6, "rashi": "Tula"},
            {"body": "Shani", "rashi_index": 10, "rashi": "Kumbha"},
            {"body": "Rahu", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Ketu", "rashi_index": 8, "rashi": "Dhanu"},
        ],
    }

    rows = {item["key"]: item for item in yoga_signatures(chart)}
    coverage = yoga_coverage(chart)

    assert rows["sri_natha"]["bodies"] == ["Shukra"]
    assert rows["chamara"]["bodies"][0] == "Mangala"
    assert rows["indra"]["bodies"] == ["Shani"]
    assert rows["brahma"]["bodies"] == ["Guru", "Shukra"]
    assert rows["bhagya"]["bodies"] == ["Guru"]
    assert rows["mridanga"]["bodies"] == ["Mangala"]
    assert rows["vidyut"]["bodies"] == ["Budha", "Guru"]
    assert rows["parijata"]["reference"] == "Lagna"
    assert rows["vasishta"]["bodies"] == ["Guru"]
    assert coverage["summary"]["formula_pending_count"] == 0
    assert coverage["summary"]["calculation_pending_count"] == 0


def test_argala_summary_lists_primary_and_obstructing_houses_from_lagna():
    chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Chandra", "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Guru", "rashi_index": 3, "rashi": "Karka"},
            {"body": "Shani", "rashi_index": 10, "rashi": "Kumbha"},
            {"body": "Surya", "rashi_index": 11, "rashi": "Meena"},
        ],
    }

    summary = argala_summary(chart)

    assert summary["status"] == "calculated_primary_secondary_lagna_needs_exact_source_review"
    assert summary["scope"] == "primary_and_secondary_lagna_argala"
    assert summary["reference"] == "Lagna"
    assert [(row["level"], row["argala_house"], row["obstruction_house"]) for row in summary["pairs"]] == [
        ("primary", 2, 12),
        ("primary", 4, 10),
        ("primary", 11, 3),
        ("secondary", 5, 9),
    ]
    assert summary["pairs"][0]["net_effect"] == "obstructed"
    assert summary["pairs"][1]["net_effect"] == "active"
    assert summary["primary"] == [
        {"house": 2, "bodies": ["Chandra"]},
        {"house": 4, "bodies": ["Guru"]},
        {"house": 11, "bodies": ["Shani"]},
    ]
    assert summary["obstruction"] == [{"house": 12, "bodies": ["Surya"]}]
    assert summary["secondary"] == []
    assert summary["secondary_obstruction"] == []
    assert summary["net_effects"][3]["level"] == "combined"


def test_special_points_include_day_and_night_lots_without_upagraha_claims():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"longitude": 90.0},
        "grahas": [
            {"body": "Surya", "longitude": 40.0},
            {"body": "Chandra", "longitude": 70.0},
        ],
    }

    points = special_points(chart)

    assert points["status"] == "calculated_with_source_review"
    assert points["scope"] == "vedic_points_upagrahas_and_supporting_lots"
    assert points["arabic_lots"][0]["metadata"]["source_role"] == "supporting_non_shastra_point"
    assert points["arabic_lots"][0]["key"] == "part_of_fortune_day"
    assert points["arabic_lots"][0]["longitude"] == 120.0
    assert points["arabic_lots"][1]["longitude"] == 60.0
    assert points["upagrahas"]["status"] == "calculated_needs_jhora_audit"
    assert points["upagrahas"]["items"][0]["key"] == "gulika"
    assert points["upagrahas"]["items"][0]["local_time"] == "12:45"


def test_special_points_include_solar_upagrahas_from_sun_longitude():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"longitude": 90.0},
        "grahas": [
            {"body": "Surya", "longitude": 10.0},
            {"body": "Chandra", "longitude": 70.0},
        ],
    }

    points = special_points(chart)
    rows = {point["key"]: point for point in points["upagrahas"]["items"]}

    assert rows["dhuma"]["longitude"] == 143.333333
    assert rows["vyatipata"]["longitude"] == 216.666667
    assert rows["parivesha"]["longitude"] == 36.666667
    assert rows["indrachapa"]["longitude"] == 323.333333
    assert rows["upaketu"]["longitude"] == 340.0
    assert rows["dhuma"]["calculation_note"] == "Solar upagraha from Surya longitude."


def test_special_points_splits_gulika_and_maandi_from_context():
    chart = {
        "upagraha_context": {
            "split_gulika_maandi": True,
            "gulika": {
                "period": "day",
                "segment": 3,
                "starts_at": "1998-04-30T10:32:11+06:00",
                "ends_at": "1998-04-30T12:23:08+06:00",
                "midpoint": "1998-04-30T11:27:39+06:00",
                "local_time": "11:27",
            },
            "gulika_start_ascendant": {"longitude": 81.2},
            "gulika_midpoint_ascendant": {"longitude": 91.55},
        },
        "grahas": [
            {"body": "Surya", "longitude": 10.0},
            {"body": "Chandra", "longitude": 70.0},
        ],
    }

    points = special_points(chart)
    rows = {point["key"]: point for point in points["upagrahas"]["items"]}

    assert points["status"] == "calculated_single_jhora_fixture_matched_core_catalog"
    assert points["upagrahas"]["status"] == "calculated_single_jhora_fixture_matched"
    assert points["upagrahas"]["verified_fixture"] == "sterlitamak_1998_jhora_special_points"
    assert rows["gulika"]["name"] == "Gulika"
    assert rows["gulika"]["longitude"] == 81.2
    assert rows["gulika"]["metadata"]["anchor"] == "segment_start"
    assert rows["maandi"]["name"] == "Maandi"
    assert rows["maandi"]["longitude"] == 91.55
    assert rows["maandi"]["metadata"]["anchor"] == "segment_midpoint"


def test_special_points_calculate_indu_lagna_when_lagna_and_moon_are_present():
    chart = {
        "ascendant": {"longitude": 0.0, "rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Chandra", "longitude": 90.0, "rashi_index": 3, "rashi": "Karka"},
            {"body": "Surya", "longitude": 40.0, "rashi_index": 1, "rashi": "Vrishabha"},
        ],
    }

    points = special_points(chart)
    rows = {point["key"]: point for point in points["vedic_points"]["items"]}

    assert points["vedic_points"]["status"] == "calculated_single_jhora_fixture_matched"
    assert rows["indu_lagna"]["rashi"] == "Kumbha"
    assert rows["indu_lagna"]["metadata"]["lagna_ninth_lord"] == "Guru"
    assert rows["indu_lagna"]["metadata"]["moon_ninth_lord"] == "Guru"
    assert rows["indu_lagna"]["metadata"]["kala_sum"] == 20
    assert rows["indu_lagna"]["metadata"]["audit_status"] == "single_jhora_fixture_matched"


def test_special_points_include_bhava_hora_and_ghati_lagnas():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "solar_day": {
            "sunrise": "2026-06-02T06:00:00+05:30",
            "sunset": "2026-06-02T18:00:00+05:30",
            "next_sunrise": "2026-06-03T06:00:00+05:30",
        },
        "special_lagna_context": {"surya_at_sunrise": {"longitude": 38.0}},
        "ascendant": {"longitude": 90.0, "rashi_index": 3, "rashi": "Karka"},
        "grahas": [
            {"body": "Surya", "longitude": 40.0, "rashi_index": 1, "rashi": "Vrishabha"},
            {"body": "Chandra", "longitude": 70.0, "rashi_index": 2, "rashi": "Mithuna"},
        ],
    }

    points = special_points(chart)
    rows = {point["key"]: point for point in points["vedic_points"]["items"]}

    assert {"bhava_lagna", "hora_lagna", "ghati_lagna"} <= set(rows)
    assert rows["bhava_lagna"]["metadata"]["audit_status"] == "single_jhora_fixture_matched"
    assert rows["bhava_lagna"]["longitude"] == 98.0
    assert rows["hora_lagna"]["metadata"]["base"] == "surya_at_sunrise"
    assert rows["ghati_lagna"]["metadata"]["degrees_per_ghati"] == 30.0
    assert rows["ghati_lagna"]["longitude"] == 338.0


def test_ashtakavarga_generates_bav_and_sav_constants():
    chart = {
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Chandra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Mangala", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Budha", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Guru", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Shukra", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Shani", "rashi_index": 0, "rashi": "Mesha"},
        ],
    }

    result = ashtakavarga(chart)

    assert result["status"] == "calculated_jhora_fixture_matched"
    assert result["bhinna"]["Surya"]["total"] == 48
    assert result["bhinna"]["Surya"]["scores"][0] == 3
    assert result["bhinna"]["Chandra"]["total"] == 49
    assert result["sarva"]["total"] == 337
    assert result["audit_status"] == "single_jhora_fixture_matched"
    assert result["verified_fixture"] == "sterlitamak_1998_jhora_profile_cells"
    assert "Brihat Jataka" in result["source_basis"]


def test_ashtakavarga_matches_sterlitamak_jhora_profile_cells():
    chart = {
        "ascendant": {"rashi_index": 3, "rashi": "Karka"},
        "grahas": [
            {"body": "Surya", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Chandra", "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Mangala", "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Budha", "rashi_index": 11, "rashi": "Meena"},
            {"body": "Guru", "rashi_index": 10, "rashi": "Kumbha"},
            {"body": "Shukra", "rashi_index": 11, "rashi": "Meena"},
            {"body": "Shani", "rashi_index": 0, "rashi": "Mesha"},
        ],
    }

    result = ashtakavarga(chart)

    assert result["rule_profile"] == "jhora_parity_brihat_jataka_standard"
    assert result["bhinna"]["Chandra"]["scores"][8:12] == [5, 4, 5, 3]
    assert result["bhinna"]["Shukra"]["scores"][3:5] == [6, 4]
    assert result["sarva"]["total"] == 337


def test_shadbala_summary_adds_natural_exaltation_and_directional_components():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "longitude": 10.0, "rashi_index": 0, "rashi": "Mesha", "speed_longitude": 1.0},
            {"body": "Shani", "longitude": 20.0, "rashi_index": 0, "rashi": "Mesha", "speed_longitude": -0.02},
        ],
    }

    result = shadbala_summary(chart)
    rows = {row["body"]: row for row in result["items"]}

    assert result["status"] == "calculated_needs_jhora_component_audit"
    assert result["coverage"]["missing_components"] == []
    assert "kala_abda_masa_vara_hora" not in result["coverage"]["approx_components"]
    assert "drik_bala" in result["coverage"]["implemented_components"]
    assert result["coverage"]["public_interpretation_status"] == "blocked_until_jhora_component_audit"
    assert result["coverage"]["chesta_input_quality"]["luminary_kala_derived_bodies"] == ["Surya"]
    assert result["coverage"]["chesta_input_quality"]["speed_classified_bodies"] == ["Shani"]
    assert result["component_table"]["status"] == "calculated_bphs_component_audit_table"
    assert "sthana_total" in result["component_table"]["columns"]
    assert "kala_total" in result["component_table"]["columns"]
    assert rows["Surya"]["components"]["naisargika"] == 60.0
    assert rows["Surya"]["rupas"] == pytest.approx(rows["Surya"]["known_total"] / 60.0, abs=0.01)
    assert rows["Surya"]["required_virupas"] == 300.0
    assert rows["Surya"]["subcomponents"]["sthana"]["uccha"] == 60.0
    assert rows["Surya"]["subcomponents"]["sthana"]["saptavargaja"] > 0
    assert rows["Surya"]["subcomponents"]["dig"]["whole_sign_proxy"] == 30.0
    assert rows["Surya"]["subcomponents"]["kala"]["natonnata"] == 50.0
    assert rows["Shani"]["components"]["naisargika"] == 8.57
    assert rows["Shani"]["subcomponents"]["sthana"]["uccha"] == 0.0
    assert rows["Shani"]["subcomponents"]["chesta"]["traditional_state"] == 60.0
    assert rows["Shani"]["subcomponents"]["kala"]["natonnata"] == 10.0
    assert rows["Shani"]["percent_strength"] == pytest.approx(rows["Shani"]["known_total"] / 3.0, abs=0.01)
    assert any(flag["component"] == "dig" for flag in rows["Surya"]["audit_flags"])


def test_shadbala_summary_uses_classical_required_virupa_thresholds():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "longitude": 10.0, "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Chandra", "longitude": 70.0, "rashi_index": 2, "rashi": "Mithuna"},
            {"body": "Mangala", "longitude": 210.0, "rashi_index": 7, "rashi": "Vrischika"},
            {"body": "Budha", "longitude": 349.0, "rashi_index": 11, "rashi": "Meena"},
            {"body": "Guru", "longitude": 240.0, "rashi_index": 8, "rashi": "Dhanu"},
            {"body": "Shukra", "longitude": 330.0, "rashi_index": 11, "rashi": "Meena"},
            {"body": "Shani", "longitude": 60.0, "rashi_index": 2, "rashi": "Mithuna"},
        ],
    }

    rows = {row["body"]: row for row in shadbala_summary(chart)["items"]}

    assert rows["Surya"]["required_virupas"] == 300.0
    assert rows["Chandra"]["required_virupas"] == 360.0
    assert rows["Mangala"]["required_virupas"] == 300.0
    assert rows["Budha"]["required_virupas"] == 420.0
    assert rows["Guru"]["required_virupas"] == 390.0
    assert rows["Shukra"]["required_virupas"] == 330.0
    assert rows["Shani"]["required_virupas"] == 300.0


def test_shadbala_summary_calculates_full_component_groups_with_audit_flags():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"longitude": 0.0, "rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "longitude": 10.0, "rashi_index": 0, "rashi": "Mesha", "speed_longitude": 1.0},
            {"body": "Chandra", "longitude": 70.0, "rashi_index": 2, "rashi": "Mithuna", "speed_longitude": 13.0},
            {"body": "Mangala", "longitude": 210.0, "rashi_index": 7, "rashi": "Vrischika", "speed_longitude": -0.2},
            {"body": "Guru", "longitude": 240.0, "rashi_index": 8, "rashi": "Dhanu", "speed_longitude": 0.08},
            {"body": "Shani", "longitude": 60.0, "rashi_index": 2, "rashi": "Mithuna", "speed_longitude": 0.03},
        ],
        "vargas": {
            "D1": {"placements": [{"body": "Surya", "rashi": "Mesha"}, {"body": "Guru", "rashi": "Dhanu"}]},
            "D2": {"placements": [{"body": "Surya", "rashi": "Simha"}, {"body": "Guru", "rashi": "Meena"}]},
            "D3": {"placements": [{"body": "Surya", "rashi": "Mesha"}, {"body": "Guru", "rashi": "Dhanu"}]},
            "D7": {"placements": [{"body": "Surya", "rashi": "Simha"}, {"body": "Guru", "rashi": "Meena"}]},
            "D9": {"placements": [{"body": "Surya", "rashi": "Mesha"}, {"body": "Guru", "rashi": "Dhanu"}]},
            "D12": {"placements": [{"body": "Surya", "rashi": "Simha"}, {"body": "Guru", "rashi": "Meena"}]},
            "D30": {"placements": [{"body": "Surya", "rashi": "Mesha"}, {"body": "Guru", "rashi": "Dhanu"}]},
        },
    }

    result = shadbala_summary(chart)
    rows = {row["body"]: row for row in result["items"]}

    assert result["status"] == "calculated_needs_jhora_component_audit"
    assert result["coverage"]["missing_components"] == []
    assert "kala_abda_masa_vara_hora" not in result["coverage"]["approx_components"]
    assert "drik_bala" in result["coverage"]["implemented_components"]
    assert rows["Surya"]["subcomponents"]["sthana"]["saptavargaja"] > 0
    assert rows["Surya"]["subcomponents"]["dig"]["exact"] == 26.67
    assert rows["Surya"]["subcomponents"]["kala"]["natonnata"] == 50.0
    assert rows["Mangala"]["subcomponents"]["chesta"]["traditional_state"] == 60.0
    assert rows["Guru"]["subcomponents"]["drik"]["value"] < 0
    assert any(flag["component"] == "drik" for flag in rows["Guru"]["audit_flags"])
    assert rows["Surya"]["known_total"] == round(sum(rows["Surya"]["components"].values()), 2)
    table_rows = {row["body"]: row for row in result["component_table"]["rows"]}
    assert table_rows["Surya"]["sthana_total"] == rows["Surya"]["subcomponents"]["sthana"]["total"]
    assert table_rows["Surya"]["total"] == rows["Surya"]["known_total"]


def test_shadbala_dig_bala_uses_real_house_cusps_when_available():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"longitude": 0.0, "rashi_index": 0, "rashi": "Mesha"},
        "house_cusps": [
            {"house": house, "longitude": float((house - 1) * 30)}
            for house in range(1, 13)
        ],
        "grahas": [
            {"body": "Surya", "longitude": 100.0, "rashi_index": 3, "rashi": "Karka", "speed_longitude": 1.0},
        ],
    }

    row = shadbala_summary(chart)["items"][0]

    assert row["subcomponents"]["dig"]["cusp_source"] == "house_cusps"
    assert row["subcomponents"]["dig"]["nil_cusp"] == 90.0
    assert row["subcomponents"]["dig"]["exact"] == 3.33
    assert not any(flag["component"] == "dig" for flag in row["audit_flags"])


def test_shadbala_ayana_bala_prefers_ephemeris_declination():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"longitude": 0.0, "rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {
                "body": "Surya",
                "longitude": 0.0,
                "declination": -10.0,
                "rashi_index": 0,
                "rashi": "Mesha",
                "speed_longitude": 1.0,
            },
        ],
    }

    row = shadbala_summary(chart)["items"][0]

    assert row["subcomponents"]["kala"]["ayana"] == 34.41


def test_hora_lord_uses_bphs_sunrise_to_sunrise_24_part_rule():
    chart = {
        "solar_day": {
            "sunrise": "1998-04-30T06:50:20+06:00",
            "sunset": "1998-04-30T21:37:45+06:00",
            "next_sunrise": "1998-05-01T06:48:18+06:00",
        }
    }

    assert _hora_lord(chart, datetime.fromisoformat("1998-04-30T13:45:00+06:00")) == "Shani"


def test_shadbala_abda_masa_uses_santhanam_abbreviated_ahargana():
    assert _abbreviated_ahargana(datetime.fromisoformat("1984-06-01T12:00:00+00:00")) == 65295

    chart = {
        "birth": {"local_datetime": "1984-06-01T12:00:00+00:00"},
        "solar_day": {
            "sunrise": "1984-06-01T06:00:00+00:00",
            "sunset": "1984-06-01T18:00:00+00:00",
            "next_sunrise": "1984-06-02T06:00:00+00:00",
        },
        "ascendant": {"longitude": 0.0, "rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Guru", "longitude": 240.0, "rashi_index": 8, "rashi": "Dhanu"},
            {"body": "Shukra", "longitude": 330.0, "rashi_index": 11, "rashi": "Meena"},
        ],
    }

    rows = {row["body"]: row for row in shadbala_summary(chart)["items"]}
    guru_kala = rows["Guru"]["subcomponents"]["kala"]["abda_masa_vara_hora"]
    shukra_kala = rows["Shukra"]["subcomponents"]["kala"]["abda_masa_vara_hora"]

    assert guru_kala["lords"]["abda"] == "Guru"
    assert shukra_kala["lords"]["masa"] == "Shukra"
    assert shukra_kala["lords"]["vara"] == "Shukra"
    assert guru_kala["components"]["abda"] == 15.0
    assert shukra_kala["components"]["masa"] == 30.0
    assert shukra_kala["components"]["vara"] == 45.0
    assert "approx" not in guru_kala["method_note"].lower()


def test_shadbala_dina_lord_uses_sunrise_to_sunrise_day():
    chart = {
        "birth": {"local_datetime": "1984-06-01T05:00:00+00:00"},
        "solar_day": {
            "sunrise": "1984-06-01T06:00:00+00:00",
            "sunset": "1984-06-01T18:00:00+00:00",
            "next_sunrise": "1984-06-02T06:00:00+00:00",
        },
        "ascendant": {"longitude": 0.0, "rashi_index": 0, "rashi": "Mesha"},
        "grahas": [{"body": "Guru", "longitude": 240.0, "rashi_index": 8, "rashi": "Dhanu"}],
    }

    row = shadbala_summary(chart)["items"][0]
    dina = row["subcomponents"]["kala"]["abda_masa_vara_hora"]

    assert dina["lords"]["vara"] == "Guru"
    assert dina["components"]["vara"] == 45.0


def test_shadbala_chesta_uses_mean_true_seeghrocha_when_available():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"longitude": 0.0, "rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {
                "body": "Mangala",
                "longitude": 100.0,
                "mean_longitude": 80.0,
                "seeghrocha_longitude": 200.0,
                "rashi_index": 3,
                "rashi": "Karka",
                "speed_longitude": 0.7,
            },
        ],
    }

    row = shadbala_summary(chart)["items"][0]
    coverage = shadbala_summary(chart)["coverage"]
    chesta = row["subcomponents"]["chesta"]

    assert chesta["calculation_basis"] == "mean_true_seeghrocha"
    assert chesta["source_reference"].startswith("BPHS/Santhanam")
    assert chesta["cheshta_kendra"] == 110.0
    assert chesta["traditional_state"] == 36.67
    assert coverage["chesta_input_quality"]["exact_mean_true_seeghrocha_bodies"] == ["Mangala"]
    assert coverage["chesta_input_quality"]["speed_classified_bodies"] == []
    assert not any(flag["component"] == "chesta" for flag in row["audit_flags"])


def test_shadbala_drik_uses_bphs_drishti_pinda_not_coarse_fraction():
    chart = {
        "birth": {"local_datetime": "2026-06-02T10:00:00+05:30"},
        "ascendant": {"longitude": 0.0, "rashi_index": 0, "rashi": "Mesha"},
        "grahas": [
            {"body": "Surya", "longitude": 10.0, "rashi_index": 0, "rashi": "Mesha"},
            {"body": "Guru", "longitude": 240.0, "rashi_index": 8, "rashi": "Dhanu"},
        ],
    }

    rows = {row["body"]: row for row in shadbala_summary(chart)["items"]}
    drik = rows["Surya"]["subcomponents"]["drik"]

    assert drik["calculation_basis"] == "bphs_ch26_drishti_pinda"
    assert drik["aspects"][0]["from"] == "Guru"
    assert drik["aspects"][0]["separation"] == 130.0
    assert drik["aspects"][0]["drishti_pinda"] == 50.0
    assert drik["value"] == 50.0


def test_vimshopaka_bala_uses_weighted_varga_schemes_not_support_count_proxy():
    chart = {
        "grahas": [{"body": "Surya", "rashi": "Simha"}],
        "vargas": {
            code: {"placements": [{"body": "Surya", "rashi": "Simha"}]}
            for code in (
                "D1",
                "D2",
                "D3",
                "D4",
                "D7",
                "D9",
                "D10",
                "D12",
                "D16",
                "D20",
                "D24",
                "D27",
                "D30",
                "D40",
                "D45",
                "D60",
            )
        },
    }

    result = vimshopaka_bala(chart)
    row = result["items"][0]

    assert result["status"] == "calculated_bphs_varga_viswa_jhora_fixture_matched"
    assert result["dignity_profile"] == "bphs_varga_viswa_with_jhora_node_profile"
    assert row["body"] == "Surya"
    assert row["primary_scheme"] == "shodasha"
    assert row["score"] == 20.0
    assert row["percentage"] == 100.0
    assert row["scheme_scores"]["shadvarga"] == 20.0
    assert row["scheme_scores"]["saptavarga"] == 20.0
    assert row["scheme_scores"]["dashavarga"] == 20.0
    assert row["scheme_scores"]["shodasha"] == 20.0
    assert row["varga_scores"]["D1"]["weight"] == 3.5
    assert row["varga_scores"]["D1"]["dignity"] == "own"
    assert row["varga_scores"]["D1"]["factor"] == 1.0


def test_vimshopaka_bala_scores_friend_neutral_enemy_and_debilitation_dignities():
    chart = {
        "grahas": [{"body": "Surya", "rashi": "Simha"}],
        "vargas": {
            "D1": {"placements": [{"body": "Surya", "rashi": "Simha"}]},
            "D2": {"placements": [{"body": "Surya", "rashi": "Karka"}]},
            "D3": {"placements": [{"body": "Surya", "rashi": "Kanya"}]},
            "D9": {"placements": [{"body": "Surya", "rashi": "Tula"}]},
            "D12": {"placements": [{"body": "Surya", "rashi": "Makara"}]},
            "D30": {"placements": [{"body": "Surya", "rashi": "Mesha"}]},
        },
    }

    result = vimshopaka_bala(chart)
    row = result["items"][0]

    assert row["scheme_scores"]["shadvarga"] == 12.7
    assert row["varga_scores"]["D2"]["dignity"] == "friend"
    assert row["varga_scores"]["D2"]["factor"] == 0.75
    assert row["varga_scores"]["D3"]["dignity"] == "neutral"
    assert row["varga_scores"]["D3"]["factor"] == 0.5
    assert row["varga_scores"]["D9"]["dignity"] == "enemy"
    assert row["varga_scores"]["D9"]["factor"] == 0.35
    assert row["varga_scores"]["D12"]["dignity"] == "enemy"
    assert row["varga_scores"]["D12"]["factor"] == 0.35
    assert row["varga_scores"]["D30"]["dignity"] == "friend"
    assert row["varga_scores"]["D30"]["factor"] == 0.75


def test_vimshopaka_bala_uses_bphs_sapta_and_dasha_varga_weights():
    chart = {
        "grahas": [{"body": "Surya", "rashi": "Simha"}],
        "vargas": {
            "D7": {"placements": [{"body": "Surya", "rashi": "Simha"}]},
            "D9": {"placements": [{"body": "Surya", "rashi": "Tula"}]},
            "D12": {"placements": [{"body": "Surya", "rashi": "Simha"}]},
            "D30": {"placements": [{"body": "Surya", "rashi": "Karka"}]},
            "D60": {"placements": [{"body": "Surya", "rashi": "Simha"}]},
        },
    }

    row = vimshopaka_bala(chart)["items"][0]

    assert row["varga_scores"]["D7"]["weight"] == 0.5
    assert row["scheme_scores"]["saptavarga"] == 7.88
    assert row["scheme_scores"]["dashavarga"] == 9.65


def test_vimshopaka_bala_includes_rahu_and_ketu_for_jhora_parity():
    chart = {
        "grahas": [
            {"body": "Rahu", "rashi": "Simha"},
            {"body": "Ketu", "rashi": "Kumbha"},
        ],
        "vargas": {
            "D1": {
                "placements": [
                    {"body": "Rahu", "rashi": "Simha"},
                    {"body": "Ketu", "rashi": "Kumbha"},
                ]
            }
        },
    }

    result = vimshopaka_bala(chart)
    rows = {row["body"]: row for row in result["items"]}

    assert set(rows) == {"Rahu", "Ketu"}
    assert rows["Rahu"]["varga_scores"]["D1"]["dignity"] == "enemy"
    assert rows["Rahu"]["varga_scores"]["D1"]["sign_lord"] == "Surya"
    assert rows["Ketu"]["varga_scores"]["D1"]["dignity"] == "friend"
    assert rows["Ketu"]["varga_scores"]["D1"]["factor"] == 0.75


def test_vimshopaka_bala_uses_temporary_relationships_inside_each_varga():
    chart = {
        "grahas": [
            {"body": "Mangala", "rashi": "Mesha", "rashi_index": 0},
            {"body": "Shani", "rashi": "Mesha", "rashi_index": 0},
        ],
        "vargas": {
            "D1": {"placements": [{"body": "Mangala", "rashi": "Mesha"}, {"body": "Shani", "rashi": "Mesha"}]},
            "D2": {"placements": [{"body": "Mangala", "rashi": "Vrishabha"}, {"body": "Shani", "rashi": "Mesha"}]},
            "D3": {"placements": [{"body": "Mangala", "rashi": "Simha"}, {"body": "Shani", "rashi": "Mesha"}]},
            "D9": {"placements": [{"body": "Mangala", "rashi": "Kanya"}, {"body": "Shani", "rashi": "Mesha"}]},
            "D12": {"placements": [{"body": "Mangala", "rashi": "Vrischika"}, {"body": "Shani", "rashi": "Mesha"}]},
            "D30": {"placements": [{"body": "Mangala", "rashi": "Mithuna"}, {"body": "Shani", "rashi": "Mesha"}]},
        },
    }

    rows = {row["body"]: row for row in vimshopaka_bala(chart)["items"]}

    assert rows["Shani"]["scheme_scores"]["shadvarga"] == 5.75
    assert rows["Shani"]["varga_scores"]["D2"]["dignity"] == "neutral"
    assert rows["Shani"]["varga_scores"]["D2"]["temporary_relationship"] == "temporary_friend"


def test_vimshopaka_bala_matches_sterlitamak_jhora_node_profile():
    chart = _sterlitamak_vimshopaka_fixture_chart()

    rows = {row["body"]: row for row in vimshopaka_bala(chart)["items"]}

    assert rows["Chandra"]["scheme_scores"]["shodasha"] == 14.38
    assert rows["Rahu"]["scheme_scores"] == {
        "shadvarga": 9.8,
        "saptavarga": 11.68,
        "dashavarga": 9.5,
        "shodasha": 7.95,
    }
    assert rows["Ketu"]["scheme_scores"] == {
        "shadvarga": 16.15,
        "saptavarga": 14.75,
        "dashavarga": 15.08,
        "shodasha": 14.9,
    }
    assert rows["Rahu"]["varga_scores"]["D20"]["natural_relationship"] == "neutral"
    assert rows["Rahu"]["varga_scores"]["D27"]["natural_relationship"] == "enemy"
    assert rows["Ketu"]["varga_scores"]["D3"]["natural_relationship"] == "neutral"


def test_classical_calculations_payload_is_explicit_about_audited_and_pending_layers():
    chart = {
        "ascendant": {"longitude": 90.0, "rashi_index": 3, "rashi": "Karka"},
        "grahas": [
            {"body": "Surya", "longitude": 120.0, "rashi_index": 4, "rashi": "Simha"},
            {"body": "Chandra", "longitude": 132.0, "rashi_index": 4, "rashi": "Simha"},
            {"body": "Mangala", "longitude": 140.0, "rashi_index": 4, "rashi": "Simha"},
            {"body": "Budha", "longitude": 150.0, "rashi_index": 5, "rashi": "Kanya"},
            {"body": "Guru", "longitude": 220.0, "rashi_index": 7, "rashi": "Vrischika"},
            {"body": "Shukra", "longitude": 225.0, "rashi_index": 7, "rashi": "Vrischika"},
            {"body": "Shani", "longitude": 230.0, "rashi_index": 7, "rashi": "Vrischika"},
        ],
        "vargas": {
            "D1": {
                "placements": [
                    {"body": "Surya", "rashi": "Simha"},
                    {"body": "Chandra", "rashi": "Simha"},
                ]
            }
        },
    }

    payload = classical_calculations(chart)

    assert payload["avasthas"]["baladi"][0]["body"] == "Surya"
    assert payload["yogas"]["status"] == "calculated_with_catalog_coverage_needs_citation"
    assert payload["yogas"]["items"][0]["key"] == "gaja_kesari"
    assert payload["yogas"]["summary"]["catalog_total"] >= 90
    assert payload["yogas"]["coverage"]
    assert payload["vimshopaka_bala"]["status"] == "calculated_bphs_varga_viswa_jhora_fixture_matched"
    assert payload["ashtakavarga"]["sarva"]["total"] == 337
    assert payload["shadbala"]["items"][0]["body"] == "Surya"


def _sterlitamak_vimshopaka_fixture_chart():
    varga_rashis = {
        "D1": {
            "Rahu": "Simha",
            "Ketu": "Kumbha",
            "Mangala": "Mesha",
            "Guru": "Kumbha",
            "Budha": "Meena",
            "Shukra": "Meena",
            "Shani": "Mesha",
            "Surya": "Mesha",
            "Chandra": "Mithuna",
        },
        "D2": {
            "Rahu": "Dhanu",
            "Ketu": "Dhanu",
            "Mangala": "Vrishabha",
            "Guru": "Makara",
            "Budha": "Kumbha",
            "Shukra": "Meena",
            "Shani": "Mesha",
            "Surya": "Vrishabha",
            "Chandra": "Simha",
        },
        "D3": {
            "Rahu": "Dhanu",
            "Ketu": "Mithuna",
            "Mangala": "Simha",
            "Guru": "Tula",
            "Budha": "Karka",
            "Shukra": "Meena",
            "Shani": "Mesha",
            "Surya": "Simha",
            "Chandra": "Mithuna",
        },
        "D4": {
            "Rahu": "Vrischika",
            "Ketu": "Vrishabha",
            "Mangala": "Tula",
            "Guru": "Vrischika",
            "Budha": "Kanya",
            "Shukra": "Meena",
            "Shani": "Mesha",
            "Surya": "Tula",
            "Chandra": "Kanya",
        },
        "D7": {
            "Rahu": "Vrischika",
            "Ketu": "Vrishabha",
            "Mangala": "Simha",
            "Guru": "Karka",
            "Budha": "Makara",
            "Shukra": "Kanya",
            "Shani": "Mesha",
            "Surya": "Karka",
            "Chandra": "Karka",
        },
        "D9": {
            "Rahu": "Simha",
            "Ketu": "Kumbha",
            "Mangala": "Kanya",
            "Guru": "Vrishabha",
            "Budha": "Dhanu",
            "Shukra": "Karka",
            "Shani": "Mesha",
            "Surya": "Simha",
            "Chandra": "Dhanu",
        },
        "D10": {
            "Rahu": "Dhanu",
            "Ketu": "Mithuna",
            "Mangala": "Tula",
            "Guru": "Tula",
            "Budha": "Vrishabha",
            "Shukra": "Vrischika",
            "Shani": "Mesha",
            "Surya": "Kanya",
            "Chandra": "Simha",
        },
        "D12": {
            "Rahu": "Makara",
            "Ketu": "Karka",
            "Mangala": "Vrischika",
            "Guru": "Dhanu",
            "Budha": "Tula",
            "Shukra": "Meena",
            "Shani": "Mesha",
            "Surya": "Tula",
            "Chandra": "Kanya",
        },
        "D16": {
            "Rahu": "Meena",
            "Ketu": "Meena",
            "Mangala": "Kumbha",
            "Guru": "Kanya",
            "Budha": "Tula",
            "Shukra": "Makara",
            "Shani": "Mesha",
            "Surya": "Dhanu",
            "Chandra": "Mesha",
        },
        "D20": {
            "Rahu": "Kanya",
            "Ketu": "Kanya",
            "Mangala": "Mesha",
            "Guru": "Vrishabha",
            "Budha": "Kanya",
            "Shukra": "Kanya",
            "Shani": "Vrishabha",
            "Surya": "Kumbha",
            "Chandra": "Makara",
        },
        "D24": {
            "Rahu": "Mithuna",
            "Ketu": "Mithuna",
            "Mangala": "Vrischika",
            "Guru": "Mesha",
            "Budha": "Tula",
            "Shukra": "Simha",
            "Shani": "Kanya",
            "Surya": "Simha",
            "Chandra": "Kumbha",
        },
        "D27": {
            "Rahu": "Mesha",
            "Ketu": "Tula",
            "Mangala": "Kanya",
            "Guru": "Kanya",
            "Budha": "Mithuna",
            "Shukra": "Meena",
            "Shani": "Vrishabha",
            "Surya": "Mithuna",
            "Chandra": "Vrishabha",
        },
        "D30": {
            "Rahu": "Dhanu",
            "Ketu": "Dhanu",
            "Mangala": "Mithuna",
            "Guru": "Tula",
            "Budha": "Meena",
            "Shukra": "Vrishabha",
            "Shani": "Mesha",
            "Surya": "Dhanu",
            "Chandra": "Kumbha",
        },
        "D40": {
            "Rahu": "Tula",
            "Ketu": "Tula",
            "Mangala": "Vrishabha",
            "Guru": "Kumbha",
            "Budha": "Dhanu",
            "Shukra": "Makara",
            "Shani": "Mithuna",
            "Surya": "Makara",
            "Chandra": "Meena",
        },
        "D45": {
            "Rahu": "Mesha",
            "Ketu": "Mesha",
            "Mangala": "Simha",
            "Guru": "Tula",
            "Budha": "Vrishabha",
            "Shukra": "Meena",
            "Shani": "Mithuna",
            "Surya": "Meena",
            "Chandra": "Dhanu",
        },
        "D60": {
            "Rahu": "Vrischika",
            "Ketu": "Vrishabha",
            "Mangala": "Vrishabha",
            "Guru": "Vrishabha",
            "Budha": "Mithuna",
            "Shukra": "Karka",
            "Shani": "Karka",
            "Surya": "Vrischika",
            "Chandra": "Tula",
        },
    }
    return {
        "grahas": [
            {"body": body, "rashi": rashi, "rashi_index": RASHIS.index(rashi)}
            for body, rashi in varga_rashis["D1"].items()
        ],
        "vargas": {
            code: {
                "placements": [
                    {"body": body, "rashi": rashi, "rashi_index": RASHIS.index(rashi)}
                    for body, rashi in placements.items()
                ]
            }
            for code, placements in varga_rashis.items()
        },
    }
