from apps.calculations.classical import (
    argala_summary,
    baladi_avastha,
    classical_calculations,
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
    assert points["upagrahas"]["status"] == "pending_jhora_audit"


def test_classical_calculations_payload_is_explicit_about_audited_and_pending_layers():
    chart = {
        "ascendant": {"longitude": 90.0, "rashi_index": 3, "rashi": "Karka"},
        "grahas": [
            {"body": "Surya", "longitude": 120.0, "rashi_index": 4, "rashi": "Simha"},
            {"body": "Chandra", "longitude": 132.0, "rashi_index": 4, "rashi": "Simha"},
            {"body": "Guru", "longitude": 220.0, "rashi_index": 7, "rashi": "Vrischika"},
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
    assert payload["yogas"]["items"][0]["key"] == "gaja_kesari"
    assert payload["vimshopaka_bala"]["status"] == "draft_needs_jhora_audit"
    assert payload["ashtakavarga"]["status"] == "pending_jhora_audit"
    assert payload["shadbala"]["status"] == "pending_jhora_audit"
