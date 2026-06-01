from datetime import datetime, timezone

from .vimshottari import active_vimshottari_periods, vimshottari_mahadashas


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
