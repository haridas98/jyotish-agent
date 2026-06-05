from datetime import datetime, timezone

from .dasha_systems import ashtottari_metadata_payload, yogini_mahadashas, yogini_payload


def test_yogini_dasha_starts_from_moon_nakshatra_plus_three_rule():
    birth_moment = datetime(2000, 1, 1, tzinfo=timezone.utc)

    periods = yogini_mahadashas(0.0, birth_moment, count=3)

    assert [period.name for period in periods] == ["Bhramari", "Bhadrika", "Ulka"]
    assert [period.lord for period in periods] == ["Mangala", "Budha", "Shani"]
    assert periods[0].duration_years == 4.0


def test_yogini_dasha_balances_first_period_by_nakshatra_fraction():
    birth_moment = datetime(2000, 1, 1, tzinfo=timezone.utc)
    midpoint_of_ashwini = 6.666666666666667

    payload = yogini_payload(midpoint_of_ashwini, birth_moment, count=1)

    assert payload["status"] == "baseline_calculated_needs_jhora_audit"
    assert payload["mahadashas"][0]["name"] == "Bhramari"
    assert payload["mahadashas"][0]["duration_years"] == 2.0


def test_ashtottari_payload_is_metadata_only_until_start_rule_audit():
    payload = ashtottari_metadata_payload()

    assert payload["status"] == "metadata_only_needs_applicability_and_start_rule_audit"
    assert payload["cycle_years"] == 108.0
    assert [item["lord"] for item in payload["sequence"]] == [
        "Surya",
        "Chandra",
        "Mangala",
        "Budha",
        "Shani",
        "Guru",
        "Rahu",
        "Shukra",
    ]
