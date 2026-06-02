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


def test_calculation_settings_accepts_jpl_ephemeris():
    assert CalculationSettings(ephemeris="jpl").ephemeris == "jpl"


def test_calculation_settings_rejects_unknown_ephemeris():
    with pytest.raises(ValueError, match="ephemeris"):
        CalculationSettings(ephemeris="toy")


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


def test_swiss_provider_uses_jpl_flag_when_requested(monkeypatch):
    class FakeSwe:
        FLG_SWIEPH = 2
        FLG_JPLEPH = 1
        FLG_SPEED = 256
        FLG_SIDEREAL = 65536
        SIDM_LAHIRI = 1
        SUN = 0

        jpl_file = None
        ephe_path = None
        calls = []

        @classmethod
        def set_sid_mode(cls, sid_mode):
            cls.sid_mode = sid_mode

        @classmethod
        def set_ephe_path(cls, path):
            cls.ephe_path = path

        @classmethod
        def set_jpl_file(cls, path):
            cls.jpl_file = path

        @classmethod
        def calc_ut(cls, jd, body_id, flags):
            cls.calls.append((round(jd, 1), body_id, flags))
            return (30.0, 0.0, 1.0, 0.1), flags

    monkeypatch.setenv("SWISSEPH_EPHE_PATH", r"C:\ephe")
    monkeypatch.setenv("SWISSEPH_JPL_FILE", "de441.eph")
    monkeypatch.setattr("apps.calculations.ephemeris.import_module", lambda name: FakeSwe)

    SwissEphemerisProvider().planet_positions(
        datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
        ["Surya"],
        CalculationSettings(ephemeris="jpl"),
    )

    assert FakeSwe.ephe_path == r"C:\ephe"
    assert FakeSwe.jpl_file == "de441.eph"
    assert FakeSwe.calls[0][2] & FakeSwe.FLG_JPLEPH
    assert not FakeSwe.calls[0][2] & FakeSwe.FLG_SWIEPH


def test_swiss_provider_requires_jpl_file_setting_for_jpl(monkeypatch):
    class FakeSwe:
        FLG_SWIEPH = 2
        FLG_JPLEPH = 1
        FLG_SPEED = 256
        FLG_SIDEREAL = 65536
        SIDM_LAHIRI = 1
        SUN = 0

        @classmethod
        def set_sid_mode(cls, sid_mode):
            cls.sid_mode = sid_mode

    monkeypatch.delenv("SWISSEPH_JPL_FILE", raising=False)
    monkeypatch.setattr("apps.calculations.ephemeris.import_module", lambda name: FakeSwe)

    with pytest.raises(EphemerisUnavailable, match="SWISSEPH_JPL_FILE"):
        SwissEphemerisProvider().planet_positions(
            datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
            ["Surya"],
            CalculationSettings(ephemeris="jpl"),
        )


def test_swiss_provider_calculates_sidereal_lagna(monkeypatch):
    class FakeSwe:
        FLG_SIDEREAL = 65536
        SIDM_LAHIRI = 1
        sid_mode = None
        houses_args = None

        @classmethod
        def set_sid_mode(cls, sid_mode):
            cls.sid_mode = sid_mode

        @classmethod
        def houses_ex(cls, jd, latitude, longitude, hsys=b"P", flags=0):
            cls.houses_args = (round(jd, 1), latitude, longitude, hsys, flags)
            return tuple(float(index * 30) for index in range(12)), (123.4, 0, 0, 0, 0, 0, 0, 0)

    monkeypatch.setattr("apps.calculations.ephemeris.import_module", lambda name: FakeSwe)

    lagna = SwissEphemerisProvider().ascendant_position(
        datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
        latitude=27.565,
        longitude=77.6593,
        settings=CalculationSettings(),
    )

    assert FakeSwe.sid_mode == FakeSwe.SIDM_LAHIRI
    assert FakeSwe.houses_args[1:] == (27.565, 77.6593, b"W", FakeSwe.FLG_SIDEREAL)
    assert lagna.body == "Lagna"
    assert lagna.longitude == 123.4
    assert lagna.placement.rashi == "Simha"
