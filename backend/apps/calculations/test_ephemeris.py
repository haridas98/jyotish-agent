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
    assert settings.calculation_model == "drik_siddhanta"
    assert settings.ayanamsa == "lahiri"
    assert settings.node_type == "true"
    assert settings.ephemeris == "swiss"
    assert settings.house_system == "whole_sign"
    assert settings.bhava_system == "whole_sign"
    assert settings.varga_scheme == "parashara"
    assert settings.sunrise_source == "noaa"
    assert settings.timezone_source == "iana"
    assert settings.shadbala_profile == "bphs_classical"


def test_calculation_settings_accepts_jpl_ephemeris():
    assert CalculationSettings(ephemeris="jpl").ephemeris == "jpl"


def test_calculation_settings_accepts_jhora_sunrise_profile():
    assert CalculationSettings(sunrise_source="swiss_center_no_refraction").sunrise_source == "swiss_center_no_refraction"


def test_calculation_settings_accepts_jhora_uma_shambhu_varga_profile():
    assert CalculationSettings(varga_scheme="jhora_uma_shambhu").varga_scheme == "jhora_uma_shambhu"


def test_calculation_settings_rejects_unimplemented_surya_siddhanta_model():
    with pytest.raises(ValueError, match="surya_siddhanta"):
        CalculationSettings(calculation_model="surya_siddhanta")


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
    assert positions["Surya"].ephemeris_engine == "swiss"
    assert positions["Surya"].ephemeris_flags == FakeSwe.FLG_SWIEPH | FakeSwe.FLG_SPEED | FakeSwe.FLG_SIDEREAL
    assert positions["Rahu"].longitude == 210
    assert positions["Ketu"].longitude == 30
    assert positions["Ketu"].latitude == pytest.approx(0.4)
    assert positions["Ketu"].ephemeris_engine == "swiss"
    assert positions["Ketu"].ephemeris_flags == FakeSwe.FLG_SWIEPH | FakeSwe.FLG_SPEED | FakeSwe.FLG_SIDEREAL


def test_swiss_provider_adds_drik_orbital_chesta_longitudes(monkeypatch):
    class FakeSwe:
        FLG_SWIEPH = 2
        FLG_SPEED = 256
        FLG_SIDEREAL = 65536
        FLG_HELCTR = 8
        SIDM_LAHIRI = 1
        EARTH = 14
        MARS = 4
        MERCURY = 2

        orbital_calls = []

        @classmethod
        def set_sid_mode(cls, sid_mode):
            cls.sid_mode = sid_mode

        @classmethod
        def deltat(cls, jd):
            return 0.001

        @classmethod
        def get_ayanamsa_ut(cls, jd):
            return 10.0

        @classmethod
        def calc_ut(cls, jd, body_id, flags):
            if body_id == cls.MARS:
                return (100.0, 0.0, 1.0, 0.7), flags
            if body_id == cls.MERCURY:
                return (150.0, 0.0, 1.0, 1.2), flags
            raise AssertionError(f"unexpected body id: {body_id}")

        @classmethod
        def get_orbital_elements(cls, jd_et, body_id, flags):
            cls.orbital_calls.append((round(jd_et, 6), body_id, flags))
            values = [0.0] * 50
            if body_id == cls.EARTH:
                values[9] = 30.0
            elif body_id == cls.MARS:
                values[9] = 90.0
            elif body_id == cls.MERCURY:
                values[9] = 50.0
            else:
                raise AssertionError(f"unexpected orbital body id: {body_id}")
            return tuple(values)

    monkeypatch.setattr("apps.calculations.ephemeris.import_module", lambda name: FakeSwe)

    positions = SwissEphemerisProvider().planet_positions(
        datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
        ["Mangala", "Budha"],
        CalculationSettings(),
    )

    assert positions["Mangala"].mean_longitude == 80.0
    assert positions["Mangala"].seeghrocha_longitude == 200.0
    assert positions["Budha"].mean_longitude == 200.0
    assert positions["Budha"].seeghrocha_longitude == 40.0
    assert all(call[2] & FakeSwe.FLG_HELCTR for call in FakeSwe.orbital_calls)


def test_swiss_provider_adds_equatorial_declination(monkeypatch):
    class FakeSwe:
        FLG_SWIEPH = 2
        FLG_SPEED = 256
        FLG_SIDEREAL = 65536
        FLG_EQUATORIAL = 2048
        SIDM_LAHIRI = 1
        SUN = 0

        calls = []

        @classmethod
        def set_sid_mode(cls, sid_mode):
            cls.sid_mode = sid_mode

        @classmethod
        def calc_ut(cls, jd, body_id, flags):
            cls.calls.append(flags)
            if flags & cls.FLG_EQUATORIAL:
                return (120.0, -12.5, 1.0, 0.0, 0.0, 0.0), flags
            return (30.0, 0.0, 1.0, 0.1), flags

    monkeypatch.setattr("apps.calculations.ephemeris.import_module", lambda name: FakeSwe)

    positions = SwissEphemerisProvider().planet_positions(
        datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
        ["Surya"],
        CalculationSettings(),
    )

    assert positions["Surya"].declination == -12.5
    equatorial_flags = [flags for flags in FakeSwe.calls if flags & FakeSwe.FLG_EQUATORIAL]
    assert equatorial_flags
    assert not equatorial_flags[0] & FakeSwe.FLG_SIDEREAL


def test_swiss_provider_marks_moshier_fallback_from_retflags(monkeypatch):
    class FakeSwe:
        FLG_SWIEPH = 2
        FLG_MOSEPH = 4
        FLG_SPEED = 256
        FLG_SIDEREAL = 65536
        SIDM_LAHIRI = 1
        SUN = 0

        @classmethod
        def set_sid_mode(cls, sid_mode):
            cls.sid_mode = sid_mode

        @classmethod
        def calc_ut(cls, jd, body_id, flags):
            return (30.0, 0.0, 1.0, 0.1), cls.FLG_MOSEPH | cls.FLG_SPEED | cls.FLG_SIDEREAL

    monkeypatch.setattr("apps.calculations.ephemeris.import_module", lambda name: FakeSwe)

    positions = SwissEphemerisProvider().planet_positions(
        datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
        ["Surya"],
        CalculationSettings(),
    )

    assert positions["Surya"].ephemeris_engine == "moshier"


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


def test_swiss_provider_calculates_sidereal_house_cusps(monkeypatch):
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
            return tuple(float(index * 30 + 5) for index in range(12)), (0, 0, 0, 0, 0, 0, 0, 0)

    monkeypatch.setattr("apps.calculations.ephemeris.import_module", lambda name: FakeSwe)

    cusps = SwissEphemerisProvider().house_cusps(
        datetime(2000, 1, 1, 12, tzinfo=timezone.utc),
        latitude=27.565,
        longitude=77.6593,
        settings=CalculationSettings(),
    )

    assert FakeSwe.sid_mode == FakeSwe.SIDM_LAHIRI
    assert FakeSwe.houses_args[1:] == (27.565, 77.6593, b"W", FakeSwe.FLG_SIDEREAL)
    assert cusps[0] == {"house": 1, "longitude": 5.0, "rashi": "Mesha", "rashi_index": 0}
    assert cusps[3]["longitude"] == 95.0
