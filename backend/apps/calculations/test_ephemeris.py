from datetime import datetime, timezone

import pytest

from apps.calculations.ephemeris import (
    CalculationSettings,
    EphemerisUnavailable,
    SwissEphemerisProvider,
)


def test_calculation_settings_defaults_match_mvp_policy():
    settings = CalculationSettings()

    assert settings.zodiac == "sidereal"
    assert settings.ayanamsa == "lahiri"
    assert settings.node_type == "true"
    assert settings.ephemeris == "swiss"


def test_swiss_provider_reports_optional_dependency_when_missing(monkeypatch):
    def fail_import(name: str):
        if name == "swisseph":
            raise ImportError("missing swisseph")
        raise AssertionError(f"unexpected import: {name}")

    monkeypatch.setattr("apps.calculations.ephemeris.import_module", fail_import)

    with pytest.raises(EphemerisUnavailable, match="pyswisseph"):
        SwissEphemerisProvider().planet_positions(
            datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
            ["Surya"],
            CalculationSettings(),
        )


def test_swiss_provider_maps_positions_and_derives_ketu(monkeypatch):
    class FakeSwe:
        FLG_SWIEPH = 2
        FLG_SPEED = 256
        FLG_SIDEREAL = 65536
        SIDM_LAHIRI = 1
        SUN = 0
        TRUE_NODE = 11

        sid_mode = None
        calls = []

        @classmethod
        def set_sid_mode(cls, sid_mode):
            cls.sid_mode = sid_mode

        @classmethod
        def calc_ut(cls, jd, body_id, flags):
            cls.calls.append((round(jd, 1), body_id, flags))
            if body_id == cls.SUN:
                return (30.0, 1.0, 0.9, 0.1), flags
            if body_id == cls.TRUE_NODE:
                return (210.0, -0.4, 1.0, -0.05), flags
            raise AssertionError(f"unexpected body id: {body_id}")

    monkeypatch.setattr("apps.calculations.ephemeris.import_module", lambda name: FakeSwe)

    positions = SwissEphemerisProvider().planet_positions(
        datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
        ["Surya", "Rahu", "Ketu"],
        CalculationSettings(),
    )

    assert FakeSwe.sid_mode == FakeSwe.SIDM_LAHIRI
    assert positions["Surya"].longitude == 30
    assert positions["Surya"].placement.rashi == "Vrishabha"
    assert positions["Rahu"].longitude == 210
    assert positions["Ketu"].longitude == 30
    assert positions["Ketu"].latitude == pytest.approx(0.4)
