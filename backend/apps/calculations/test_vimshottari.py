from datetime import datetime, timezone

from .vimshottari import vimshottari_mahadashas


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
