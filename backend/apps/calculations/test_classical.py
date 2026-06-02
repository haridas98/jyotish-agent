from apps.calculations.classical import (
    argala_summary,
    ashtakavarga,
    baladi_avastha,
    classical_calculations,
    shadbala_summary,
    special_points,
    yoga_signatures,
)


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

    assert summary["reference"] == "Lagna"
    assert summary["primary"] == [
        {"house": 2, "bodies": ["Chandra"]},
        {"house": 4, "bodies": ["Guru"]},
        {"house": 11, "bodies": ["Shani"]},
    ]
    assert summary["obstruction"] == [{"house": 12, "bodies": ["Surya"]}]


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

    assert points["arabic_lots"][0]["key"] == "part_of_fortune_day"
    assert points["arabic_lots"][0]["longitude"] == 120.0
    assert points["arabic_lots"][1]["longitude"] == 60.0
    assert points["upagrahas"]["status"] == "calculated_needs_jhora_audit"
    assert points["upagrahas"]["items"][0]["key"] == "gulika"
    assert points["upagrahas"]["items"][0]["local_time"] == "12:45"


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

    assert points["vedic_points"]["status"] == "calculated_needs_source_audit"
    assert rows["indu_lagna"]["rashi"] == "Kumbha"
    assert rows["indu_lagna"]["metadata"]["lagna_ninth_lord"] == "Guru"
    assert rows["indu_lagna"]["metadata"]["moon_ninth_lord"] == "Guru"
    assert rows["indu_lagna"]["metadata"]["kala_sum"] == 20


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

    assert result["status"] == "calculated_source_backed_needs_jhora_profile_audit"
    assert result["bhinna"]["Surya"]["total"] == 48
    assert result["bhinna"]["Surya"]["scores"][0] == 3
    assert result["bhinna"]["Chandra"]["total"] == 49
    assert result["sarva"]["total"] == 337
    assert result["audit_status"] == "jhora_profile_diff_open"
    assert "Brihat Jataka" in result["source_basis"]


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

    assert result["status"] == "partial_calculated_needs_jhora_audit"
    assert rows["Surya"]["components"]["naisargika"] == 60.0
    assert rows["Surya"]["components"]["uccha"] == 60.0
    assert rows["Surya"]["components"]["sthana"] == 60.0
    assert rows["Surya"]["components"]["chesta"] == 15.0
    assert rows["Surya"]["components"]["kala"] == 60.0
    assert rows["Shani"]["components"]["naisargika"] == 8.57
    assert rows["Shani"]["components"]["uccha"] == 0.0
    assert rows["Shani"]["components"]["sthana"] == 0.0
    assert rows["Shani"]["components"]["chesta"] == 60.0
    assert rows["Shani"]["components"]["kala"] == 0.0


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
    assert payload["yogas"]["status"] == "partial_calculated_needs_citation"
    assert payload["yogas"]["items"][0]["key"] == "gaja_kesari"
    assert payload["vimshopaka_bala"]["status"] == "partial_calculated_needs_jhora_audit"
    assert payload["ashtakavarga"]["sarva"]["total"] == 337
    assert payload["shadbala"]["items"][0]["body"] == "Surya"
