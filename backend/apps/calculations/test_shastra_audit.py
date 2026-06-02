from apps.calculations.shastra_audit import (
    CALCULATION_SHASTRA_AUDIT,
    shastra_audit_payload,
    validate_shastra_audit,
)


def test_shastra_audit_registry_covers_public_calculation_layers():
    keys = {item["key"] for item in CALCULATION_SHASTRA_AUDIT}

    assert {
        "rashi_nakshatra_navamsa",
        "vargas_d2_d60",
        "panchanga",
        "vimshottari",
        "avasthas",
        "ashtakavarga",
        "shadbala",
        "vimshopaka",
        "yogas",
        "argala",
        "upagrahas",
        "special_points",
        "transits",
        "compatibility",
        "muhurta",
    } <= keys


def test_source_backed_claims_have_source_and_review_status():
    assert validate_shastra_audit() == []


def test_shastra_audit_payload_marks_verified_and_partial_layers():
    payload = shastra_audit_payload()

    assert payload["policy"] == "shastra_first_black_box_second"
    assert payload["summary"]["source_backed"] >= 3
    assert payload["summary"]["partial_or_audit"] >= 5
    assert payload["items_by_key"]["ashtakavarga"]["source_priority"][0] == "brhat-jataka"
    assert payload["items_by_key"]["ashtakavarga"]["public_claim"] == "source_backed_not_jhora_verified"
    assert payload["items_by_key"]["shadbala"]["implementation_status"] == "partial"
    assert payload["items_by_key"]["shadbala"]["can_generate_client_interpretation"] is False
    assert payload["items_by_key"]["vimshopaka"]["implementation_status"] == "calculated_needs_jhora_audit"
    assert payload["items_by_key"]["vimshopaka"]["can_generate_client_interpretation"] is False
    assert payload["items_by_key"]["upagrahas"]["implementation_status"] == "calculated_needs_jhora_audit"
