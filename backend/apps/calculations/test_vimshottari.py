from datetime import datetime, timezone

from .vimshottari import active_vimshottari_periods, vimshottari_mahadashas, vimshottari_payload


def test_vimshottari_starts_with_ketu_at_beginning_of_ashwini():
    birth_moment = datetime(2000, 1, 1, tzinfo=timezone.utc)

    periods = vimshottari_mahadashas(0.0, birth_moment, count=2)

    assert [period.lord for period in periods] == ["Ketu", "Shukra"]
    assert periods[0].starts_at == birth_moment
    assert periods[0].duration_years == 7.0
    assert periods[1].duration_years == 20.0


def test_vimshottari_balances_current_lord_by_remaining_nakshatra_fraction():
    birth_moment = datetime(2000, 1, 1, tzinfo=timezone.utc)
    midpoint_of_bharani = 13.333333333333334 + 6.666666666666667

    periods = vimshottari_mahadashas(midpoint_of_bharani, birth_moment, count=1)

    assert periods[0].lord == "Shukra"
    assert periods[0].duration_years == 10.0


def test_active_vimshottari_finds_current_mahadasha_and_antardasha():
    birth_moment = datetime(2000, 1, 1, tzinfo=timezone.utc)
    as_of = datetime(2000, 7, 1, tzinfo=timezone.utc)

    active = active_vimshottari_periods(0.0, birth_moment, as_of)

    assert active["mahadasha"]["lord"] == "Ketu"
    assert active["antardasha"]["lord"] == "Shukra"
    assert active["antardasha"]["parent_lord"] == "Ketu"
    assert len(active["mahadasha_antardashas"]) == 9
    assert active["mahadasha_antardashas"][0]["lord"] == "Ketu"
    assert active["mahadasha_antardashas"][1]["lord"] == "Shukra"
    assert active["mahadasha_antardashas"][1]["parent_lord"] == "Ketu"
    assert active["as_of"] == "2000-07-01T00:00:00+00:00"


def test_active_vimshottari_returns_none_when_date_is_outside_generated_range():
    birth_moment = datetime(2000, 1, 1, tzinfo=timezone.utc)
    as_of = datetime(2200, 1, 1, tzinfo=timezone.utc)

    active = active_vimshottari_periods(0.0, birth_moment, as_of)

    assert active["mahadasha"] is None
    assert active["antardasha"] is None
    assert active["mahadasha_antardashas"] == []


def test_vimshottari_payload_exposes_method_balance_and_antardashas():
    birth_moment = datetime(2000, 1, 1, tzinfo=timezone.utc)

    payload = vimshottari_payload(0.0, birth_moment, count=9)

    assert payload["methodId"] == "dasha.vimshottari.parashara.v1"
    assert payload["methodVersion"] == "1"
    assert payload["sourceAnchor"] == "BPHS 46.2-16"
    assert payload["year_length_days"] == 365.25
    assert payload["moon_nakshatra_index"] == 0
    assert payload["birth_balance_fraction"] == 1.0
    assert [period["lord"] for period in payload["mahadashas"]] == [
        "Ketu",
        "Shukra",
        "Surya",
        "Chandra",
        "Mangala",
        "Rahu",
        "Guru",
        "Shani",
        "Budha",
    ]
    first = payload["mahadashas"][0]
    assert first["starts_at"] == "2000-01-01T00:00:00+00:00"
    assert first["ends_at"] == "2006-12-31T18:00:00+00:00"
    assert first["boundary_policy"] == "start_inclusive_end_exclusive"
    assert len(first["antardashas"]) == 9
    assert [period["lord"] for period in first["antardashas"][:2]] == ["Ketu", "Shukra"]
    assert first["antardashas"][0]["parent_lord"] == "Ketu"
    assert first["antardashas"][0]["level"] == 2