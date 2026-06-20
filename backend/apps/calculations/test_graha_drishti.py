import pytest

from apps.calculations.graha_drishti import (
    GRAHA_DRISHTI_METHOD_ID,
    build_graha_drishti_aspects,
    graha_drishti_method_contract,
)


def placement(body, rashi_index):
    return {"body": body, "rashi_index": rashi_index, "longitude": rashi_index * 30.0}


def house(number, rashi_index):
    return {"house": number, "rashi_index": rashi_index, "rashi": f"Rashi {number}"}


def test_parashara_graha_drishti_builds_transit_to_natal_house_and_graha_refs():
    transit_chart = {"grahas": [placement("Shani", 0), placement("Guru", 4), placement("Mangala", 8), placement("Surya", 2)]}
    natal_chart = {
        "grahas": [placement("Surya", 2), placement("Chandra", 6), placement("Budha", 9)],
        "houses": [house(index + 1, index) for index in range(12)],
    }

    aspects = build_graha_drishti_aspects(transit_chart, natal_chart)
    refs = {(item["sourceEntityRef"], item["targetEntityRef"], item["signDistance"], item["aspectKind"]) for item in aspects}

    assert ("transit:graha.SA", "natal:house.3", 3, "special_3rd") in refs
    assert ("transit:graha.SA", "natal:house.7", 7, "opposition_7th") in refs
    assert ("transit:graha.SA", "natal:house.10", 10, "special_10th") in refs
    assert ("transit:graha.JU", "natal:house.9", 5, "special_5th") in refs
    assert ("transit:graha.MA", "natal:house.4", 8, "special_8th") in refs
    assert ("transit:graha.SU", "natal:graha.MO", 5, "opposition_7th") not in refs
    assert all(item["methodId"] == GRAHA_DRISHTI_METHOD_ID for item in aspects)
    assert all(item["sourceContext"] == "transit" and item["targetContext"] == "natal" for item in aspects)
    assert all(item["sourceRuleIds"] == [] for item in aspects)


def test_parashara_graha_drishti_excludes_rahu_ketu_and_deduplicates_targets():
    transit_chart = {"grahas": [placement("Rahu", 0), placement("Ketu", 6), placement("Shani", 0), placement("Shani", 0)]}
    natal_chart = {
        "grahas": [placement("Surya", 2)],
        "houses": [house(index + 1, index) for index in range(12)],
    }

    aspects = build_graha_drishti_aspects(transit_chart, natal_chart)
    pairs = [(item["sourceEntityRef"], item["targetEntityRef"], item["aspectKind"]) for item in aspects]

    assert not any(item["sourceEntityRef"] in {"transit:graha.RA", "transit:graha.KE"} for item in aspects)
    assert len(pairs) == len(set(pairs))


def test_parashara_graha_drishti_direction_and_chart_style_do_not_change_results():
    transit_chart = {"grahas": [placement("Shani", 11)]}
    natal_chart = {
        "grahas": [placement("Surya", 1)],
        "houses": [house(index + 1, index) for index in range(12)],
    }

    north = build_graha_drishti_aspects(transit_chart, natal_chart, chart_style="north")
    south = build_graha_drishti_aspects(transit_chart, natal_chart, chart_style="south")
    reverse_target_chart = {"grahas": [placement("Shani", 7)]}
    reversed_direction = build_graha_drishti_aspects(natal_chart, reverse_target_chart, source_context="natal", target_context="transit")

    assert north == south
    assert north[0]["sourceEntityRef"].startswith("transit:")
    assert reversed_direction[0]["sourceEntityRef"].startswith("natal:")
    assert reversed_direction[0]["targetEntityRef"].startswith("transit:")


def test_parashara_graha_drishti_normalizes_sign_boundaries():
    transit_chart = {"grahas": [placement("Shani", 11)]}
    natal_chart = {
        "grahas": [placement("Surya", 1)],
        "houses": [house(index + 1, index) for index in range(12)],
    }

    aspects = build_graha_drishti_aspects(transit_chart, natal_chart)
    saturn_to_sun = next(item for item in aspects if item["targetEntityRef"] == "natal:graha.SU")

    assert saturn_to_sun["signDistance"] == 3
    assert saturn_to_sun["aspectKind"] == "special_3rd"


def test_parashara_graha_drishti_rejects_unknown_method_id():
    with pytest.raises(ValueError, match="unknown aspect method"):
        graha_drishti_method_contract(method_id="aspect.unknown.v1")
