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
        "extra_dashas",
        "avasthas",
        "ashtakavarga",
        "shadbala",
        "vimshopaka",
        "yogas",
        "argala",
        "upagrahas",
        "special_points",
        "transits",
        "tithi_pravesha",
        "tajaka",
        "prashna",
        "mundane",
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
    assert payload["items_by_key"]["ashtakavarga"]["public_claim"] == "source_backed_single_jhora_fixture_verified"
    assert (
        payload["items_by_key"]["shadbala"]["implementation_status"]
        == "calculated_source_backed_jhora_profile_divergence"
    )
    assert payload["items_by_key"]["shadbala"]["can_generate_client_interpretation"] is True
    assert (
        payload["items_by_key"]["vimshopaka"]["implementation_status"]
        == "calculated_bphs_varga_viswa_jhora_fixture_matched"
    )
    assert payload["items_by_key"]["vimshopaka"]["can_generate_client_interpretation"] is True
    assert payload["items_by_key"]["tithi_pravesha"]["implementation_status"] == "baseline_calculated_needs_jhora_tajaka_audit"
    assert payload["items_by_key"]["extra_dashas"]["implementation_status"] == "partial_extra_dasha_catalog"
    assert payload["items_by_key"]["tajaka"]["implementation_status"] == "baseline_calculated_needs_full_tajaka_audit"
    assert payload["items_by_key"]["prashna"]["implementation_status"] == "baseline_calculated_needs_prashna_tradition_review"
    assert payload["items_by_key"]["mundane"]["implementation_status"] == "baseline_event_chart_needs_mundane_rules_review"
    assert (
        payload["items_by_key"]["upagrahas"]["implementation_status"]
        == "calculated_single_jhora_fixture_matched_core_catalog"
    )
    assert payload["items_by_key"]["upagrahas"]["can_generate_client_interpretation"] is True
    assert (
        payload["items_by_key"]["argala"]["implementation_status"]
        == "calculated_primary_lagna_needs_exact_source_review"
    )
    assert (
        payload["items_by_key"]["special_points"]["implementation_status"]
        == "calculated_single_jhora_fixture_matched_core_catalog"
    )
    assert payload["items_by_key"]["special_points"]["can_generate_client_interpretation"] is True
    assert "classical-point-source-review" not in payload["items_by_key"]["special_points"]["source_priority"]
    assert (
        payload["items_by_key"]["compatibility"]["implementation_status"]
        == "multi_factor_calculated_needs_shastra_review"
    )
