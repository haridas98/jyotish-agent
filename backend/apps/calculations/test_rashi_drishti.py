import pytest

from apps.calculations.rashi_drishti import (
    RASHI_DRISHTI_METHOD_ID,
    RASHI_DRISHTI_RULE_DUAL_TO_DUAL,
    RASHI_DRISHTI_RULE_FIXED_TO_MOVABLE,
    RASHI_DRISHTI_RULE_GRAHA_PARTICIPATION,
    RASHI_DRISHTI_RULE_MOVABLE_TO_FIXED,
    RASHI_DRISHTI_SOURCE_RULE_IDS,
    build_rashi_drishti_aspects,
    rashi_drishti_method_contract,
)


def placement(body, rashi_index):
    return {"body": body, "rashi_index": rashi_index, "longitude": rashi_index * 30.0}


def house(number, rashi_index):
    return {"house": number, "rashi_index": rashi_index, "rashi": f"Rashi {number}"}


def test_parashara_rashi_drishti_builds_sign_based_transit_to_natal_refs():
    transit_chart = {"grahas": [placement("Surya", 0), placement("Shani", 1), placement("Guru", 2)]}
    natal_chart = {
        "grahas": [placement("Chandra", 4), placement("Mangala", 3), placement("Budha", 5)],
        "houses": [house(index + 1, index) for index in range(12)],
    }

    aspects = build_rashi_drishti_aspects(transit_chart, natal_chart)
    refs = {(item["sourceEntityRef"], item["targetEntityRef"], item["targetRashiIndex"], item["aspectKind"]) for item in aspects}

    assert ("transit:rashi.Aries", "natal:house.5", 4, "movable_to_fixed") in refs
    assert ("transit:rashi.Aries", "natal:house.2", 1, "movable_to_fixed") not in refs
    assert ("transit:rashi.Taurus", "natal:house.4", 3, "fixed_to_movable") in refs
    assert ("transit:rashi.Taurus", "natal:house.1", 0, "fixed_to_movable") not in refs
    assert ("transit:rashi.Gemini", "natal:house.6", 5, "dual_to_dual") in refs
    assert all(item["methodId"] == RASHI_DRISHTI_METHOD_ID for item in aspects)
    assert all(item["sourceContext"] == "transit" and item["targetContext"] == "natal" for item in aspects)
    assert all(item["sourceStatus"] == "verified" for item in aspects)
    assert {RASHI_DRISHTI_RULE_MOVABLE_TO_FIXED, RASHI_DRISHTI_RULE_GRAHA_PARTICIPATION}.issubset(
        next(
            item["sourceRuleIds"]
            for item in aspects
            if item["sourceEntityRef"] == "transit:rashi.Aries" and item["targetEntityRef"] == "natal:graha.MO"
        )
    )
    assert RASHI_DRISHTI_RULE_FIXED_TO_MOVABLE in next(
        item["sourceRuleIds"]
        for item in aspects
        if item["sourceEntityRef"] == "transit:rashi.Taurus" and item["targetEntityRef"] == "natal:house.4"
    )
    assert RASHI_DRISHTI_RULE_DUAL_TO_DUAL in next(
        item["sourceRuleIds"]
        for item in aspects
        if item["sourceEntityRef"] == "transit:rashi.Gemini" and item["targetEntityRef"] == "natal:house.6"
    )


def test_parashara_rashi_drishti_contract_exposes_verified_bphs_rules():
    contract = rashi_drishti_method_contract()

    assert contract["sourceStatus"] == "verified"
    assert contract["sourceRuleIds"] == RASHI_DRISHTI_SOURCE_RULE_IDS


def test_parashara_rashi_drishti_keeps_rahu_ketu_as_targets_with_participation_rule():
    transit_chart = {"grahas": [placement("Surya", 0)]}
    natal_chart = {
        "grahas": [placement("Rahu", 4), placement("Ketu", 7)],
        "houses": [house(index + 1, index) for index in range(12)],
    }

    aspects = build_rashi_drishti_aspects(transit_chart, natal_chart)
    target_rule_ids = {item["targetEntityRef"]: item["sourceRuleIds"] for item in aspects if item["targetKind"] == "graha"}

    assert target_rule_ids["natal:graha.RA"] == [
        RASHI_DRISHTI_RULE_MOVABLE_TO_FIXED,
        RASHI_DRISHTI_RULE_GRAHA_PARTICIPATION,
    ]
    assert target_rule_ids["natal:graha.KE"] == [
        RASHI_DRISHTI_RULE_MOVABLE_TO_FIXED,
        RASHI_DRISHTI_RULE_GRAHA_PARTICIPATION,
    ]


def test_parashara_rashi_drishti_deduplicates_source_signs_and_keeps_direction():
    transit_chart = {"grahas": [placement("Surya", 0), placement("Chandra", 0)]}
    natal_chart = {
        "grahas": [placement("Mangala", 4)],
        "houses": [house(index + 1, index) for index in range(12)],
    }

    aspects = build_rashi_drishti_aspects(transit_chart, natal_chart)
    pairs = [(item["sourceEntityRef"], item["targetEntityRef"], item["aspectKind"]) for item in aspects]

    assert len(pairs) == len(set(pairs))
    assert all(item["sourceEntityRef"].startswith("transit:rashi.") for item in aspects)
    assert all(item["targetEntityRef"].startswith("natal:") for item in aspects)


def test_parashara_rashi_drishti_chart_style_does_not_change_results():
    transit_chart = {"grahas": [placement("Surya", 0)]}
    natal_chart = {
        "grahas": [placement("Mangala", 4)],
        "houses": [house(index + 1, index) for index in range(12)],
    }

    north = build_rashi_drishti_aspects(transit_chart, natal_chart, chart_style="north")
    south = build_rashi_drishti_aspects(transit_chart, natal_chart, chart_style="south")

    assert north == south


def test_parashara_rashi_drishti_rejects_unknown_method_id():
    with pytest.raises(ValueError, match="unknown aspect method"):
        rashi_drishti_method_contract(method_id="aspect.unknown.v1")
