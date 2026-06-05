from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition, CalculationSettings, EphemerisUnavailable
from apps.calculations.primitives import zodiac_placement


class FakeProvider:
    def __init__(self):
        self.moment = None
        self.bodies = None
        self.settings = None

    def planet_positions(self, moment, bodies, settings):
        self.moment = moment
        self.bodies = bodies
        self.settings = settings
        return {
            "Surya": BodyPosition(
                body="Surya",
                longitude=30.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(30.0),
                declination=-12.5,
            )
        }


class FakeProviderWithMoon:
    def planet_positions(self, moment, bodies, settings):
        return {
            "Chandra": BodyPosition(
                body="Chandra",
                longitude=0.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(0.0),
            )
        }


class FakeProviderWithAyanamsa(FakeProvider):
    def ayanamsa_degrees(self, moment, settings):
        return 23.25


class SettingsSensitiveProvider:
    def planet_positions(self, moment, bodies, settings):
        rahu_longitude = 270.0 if settings.node_type == "true" else 271.0
        values = {
            "Surya": 30.0,
            "Chandra": 60.0,
            "Mangala": 90.0,
            "Budha": 120.0,
            "Guru": 150.0,
            "Shukra": 180.0,
            "Shani": 210.0,
            "Rahu": rahu_longitude,
            "Ketu": (rahu_longitude + 180.0) % 360.0,
        }
        return {
            body: BodyPosition(
                body=body,
                longitude=values[body],
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(values[body]),
            )
            for body in bodies
            if body in values
        }

    def ascendant_position(self, moment, latitude, longitude, settings):
        return BodyPosition(
            body="Lagna",
            longitude=90.0,
            latitude=None,
            distance_au=None,
            speed_longitude=None,
            placement=zodiac_placement(90.0),
        )


def test_build_birth_chart_uses_local_timezone_and_provider():
    from apps.calculations.chart import build_birth_chart

    provider = FakeProvider()

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=provider,
    )

    assert provider.moment == datetime(2000, 1, 1, 15, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
    assert provider.settings == CalculationSettings()
    assert provider.bodies == ["Surya", "Chandra", "Mangala", "Budha", "Guru", "Shukra", "Shani", "Rahu", "Ketu"]
    assert result["place"]["name"] == "Vrindavan"
    assert result["grahas"][0]["body"] == "Surya"
    assert result["grahas"][0]["declination"] == -12.5
    assert result["grahas"][0]["rashi"] == "Vrishabha"
    assert result["grahas"][0]["nakshatra"] == "Krittika"
    assert result["classical"]["avasthas"]["status"] == "calculated"
    assert result["classical"]["ashtakavarga"]["status"] == "partial_calculated_needs_jhora_profile_audit"
    assert result["shastra_audit"]["items_by_key"]["ashtakavarga"]["public_claim"] == "source_backed_single_jhora_fixture_verified"
    assert result["shastra_audit"]["items_by_key"]["shadbala"]["can_generate_client_interpretation"] is True


def test_build_birth_chart_accepts_explicit_calculation_settings():
    from apps.calculations.chart import build_birth_chart

    provider = FakeProvider()

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "node_type": "mean",
            "ayanamsa": "lahiri",
            "ephemeris": "swiss",
            "calculation_model": "drik_siddhanta",
            "house_system": "whole_sign",
            "bhava_system": "whole_sign",
            "varga_scheme": "parashara",
            "sunrise_source": "noaa",
            "timezone_source": "iana",
            "shadbala_profile": "bphs_classical",
        },
        provider=provider,
    )

    assert provider.settings == CalculationSettings(node_type="mean")
    assert result["settings"]["calculation_model"] == "drik_siddhanta"
    assert result["settings"]["node_type"] == "mean"
    assert result["settings"]["ayanamsa"] == "lahiri"
    assert result["settings"]["ephemeris"] == "swiss"
    assert result["settings"]["house_system"] == "whole_sign"
    assert result["settings"]["bhava_system"] == "whole_sign"
    assert result["settings"]["varga_scheme"] == "parashara"
    assert result["settings"]["sunrise_source"] == "noaa"
    assert result["settings"]["timezone_source"] == "iana"
    assert result["settings"]["shadbala_profile"] == "bphs_classical"


def test_build_birth_chart_includes_provider_ayanamsa_degrees_when_available():
    from apps.calculations.chart import build_birth_chart

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=FakeProviderWithAyanamsa(),
    )

    assert result["settings"]["ayanamsa_degrees"] == 23.25


def test_build_birth_chart_preserves_birth_time_seconds_for_precision():
    from apps.calculations.chart import build_birth_chart

    provider = FakeProvider()

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30:45",
            "place_name": "Vrindavan",
        },
        provider=provider,
    )

    assert provider.moment == datetime(2000, 1, 1, 15, 30, 45, tzinfo=ZoneInfo("Asia/Kolkata"))
    assert result["birth"]["time"] == "15:30:45"
    assert result["birth"]["local_datetime"] == "2000-01-01T15:30:45+05:30"


def test_build_birth_chart_rejects_invalid_calculation_settings():
    from apps.calculations.chart import ChartInputError, build_birth_chart

    with pytest.raises(ChartInputError, match="node_type"):
        build_birth_chart(
            {
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
                "node_type": "dragon",
            },
            provider=FakeProvider(),
        )


def test_build_birth_chart_rejects_unimplemented_surya_siddhanta_profile():
    from apps.calculations.chart import ChartInputError, build_birth_chart

    with pytest.raises(ChartInputError, match="surya_siddhanta"):
        build_birth_chart(
            {
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
                "calculation_model": "surya_siddhanta",
            },
            provider=FakeProvider(),
        )


def test_build_birth_chart_accepts_custom_place_with_coordinates():
    from apps.calculations.chart import build_birth_chart

    class ProviderWithAscendant(FakeProvider):
        def __init__(self):
            super().__init__()
            self.ascendant_args = None

        def ascendant_position(self, moment, latitude, longitude, settings):
            self.ascendant_args = (moment, latitude, longitude, settings)
            return BodyPosition(
                body="Lagna",
                longitude=90.0,
                latitude=None,
                distance_au=None,
                speed_longitude=None,
                placement=zodiac_placement(90.0),
            )

    provider = ProviderWithAscendant()

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Тестовый город",
            "timezone": "Asia/Yekaterinburg",
            "latitude": 56.8389,
            "longitude": 60.6057,
        },
        provider=provider,
    )

    assert provider.moment == datetime(2000, 1, 1, 15, 30, tzinfo=ZoneInfo("Asia/Yekaterinburg"))
    assert provider.ascendant_args[1:3] == (56.8389, 60.6057)
    assert result["place"]["id"] == "custom"
    assert result["place"]["name"] == "Тестовый город"
    assert result["place"]["label"] == "Тестовый город"
    assert result["place"]["latitude"] == 56.8389
    assert result["place"]["longitude"] == 60.6057


def test_build_birth_chart_reports_historical_utc_offset():
    from apps.calculations.chart import build_birth_chart

    result = build_birth_chart(
        {
            "birth_date": "2012-01-01",
            "birth_time": "12:00",
            "place_name": "Тестовая Москва",
            "timezone": "Europe/Moscow",
            "latitude": 55.7558,
            "longitude": 37.6173,
        },
        provider=FakeProvider(),
    )

    assert result["birth"]["timezone"] == "Europe/Moscow"
    assert result["birth"]["utc_offset"] == "+04:00"
    assert result["birth"]["utc_datetime"].endswith("08:00:00+00:00")


def test_build_birth_chart_uses_historical_sterlitamak_dst_offset():
    from apps.calculations.chart import build_birth_chart

    provider = FakeProvider()

    result = build_birth_chart(
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Sterlitamak",
        },
        provider=provider,
    )

    assert result["place"]["name"] == "Sterlitamak"
    assert result["birth"]["timezone"] == "Asia/Yekaterinburg"
    assert result["birth"]["utc_offset"] == "+06:00"
    assert result["birth"]["utc_datetime"].endswith("07:45:00+00:00")
    assert provider.moment == datetime(1998, 4, 30, 13, 45, tzinfo=ZoneInfo("Asia/Yekaterinburg"))


def test_build_birth_chart_resolves_geonames_city_without_manual_coordinates():
    from apps.calculations.chart import build_birth_chart

    provider = FakeProvider()

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "12:00",
            "place_name": "Shymkent, Kazakhstan, KZ",
        },
        provider=provider,
    )

    assert result["place"]["id"] == "geonames:1518980"
    assert result["place"]["name"] == "Shymkent"
    assert result["place"]["country_code"] == "KZ"
    assert result["birth"]["timezone"] == "Asia/Almaty"
    assert provider.moment == datetime(2000, 1, 1, 12, 0, tzinfo=ZoneInfo("Asia/Almaty"))


def test_build_birth_chart_preserves_mean_seeghrocha_for_exact_chesta_bala():
    from apps.calculations.chart import build_birth_chart

    class ProviderWithChestaData(FakeProvider):
        def planet_positions(self, moment, bodies, settings):
            return {
                "Mangala": BodyPosition(
                    body="Mangala",
                    longitude=100.0,
                    latitude=0.0,
                    distance_au=1.0,
                    speed_longitude=0.7,
                    mean_longitude=80.0,
                    seeghrocha_longitude=200.0,
                    placement=zodiac_placement(100.0),
                )
            }

    result = build_birth_chart(
        {
            "birth_date": "2026-06-02",
            "birth_time": "10:00",
            "place_name": "Vrindavan",
        },
        provider=ProviderWithChestaData(),
    )

    mangala = next(row for row in result["grahas"] if row["body"] == "Mangala")
    shadbala_row = next(row for row in result["classical"]["shadbala"]["items"] if row["body"] == "Mangala")
    chesta = shadbala_row["subcomponents"]["chesta"]

    assert mangala["mean_longitude"] == 80.0
    assert mangala["seeghrocha_longitude"] == 200.0
    assert chesta["calculation_basis"] == "mean_true_seeghrocha"
    assert chesta["traditional_state"] == 36.67
    assert not any(flag["component"] == "chesta" for flag in shadbala_row["audit_flags"])


def test_build_birth_chart_accepts_manual_utc_offset_for_jhora_style_input():
    from apps.calculations.chart import build_birth_chart

    provider = FakeProvider()

    result = build_birth_chart(
        {
            "birth_date": "1998-04-30",
            "birth_time": "13:45",
            "place_name": "Sterlitamak",
            "timezone": "+6",
            "latitude": 53.37,
            "longitude": 55.57,
        },
        provider=provider,
    )

    assert result["birth"]["timezone"] == "+06:00"
    assert result["birth"]["utc_offset"] == "+06:00"
    assert result["birth"]["utc_datetime"].endswith("07:45:00+00:00")
    assert result["settings"]["timezone_source"] == "fixed_offset"
    assert provider.moment == datetime(
        1998,
        4,
        30,
        13,
        45,
        tzinfo=timezone(timedelta(hours=6), name="UTC+06:00"),
    )


def test_build_dual_calculation_report_compares_primary_to_jhora_profile():
    from apps.calculations.dual_calculation import build_dual_calculation_report

    result = build_dual_calculation_report(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "node_type": "true",
        },
        provider=SettingsSensitiveProvider(),
    )

    rahu = next(row for row in result["delta"]["grahas"] if row["body"] == "Rahu")

    assert result["status"] == "calculated_witness_mode"
    assert result["primary_calculation"]["settings"]["node_type"] == "true"
    assert result["jhora_profile_calculation"]["settings"]["node_type"] == "mean"
    assert rahu["signed_delta_arcseconds"] == 3600.0
    assert result["settings_diff"][3] == {
        "key": "node_type",
        "primary": "true",
        "jhora_profile": "mean",
        "matches": False,
    }
    assert result["authority_decision"]["accepted_track"] == "primary_calculation"
    assert result["authority_decision"]["needs_review"] is True


def test_build_birth_chart_rejects_missing_time():
    from apps.calculations.chart import ChartInputError, build_birth_chart

    with pytest.raises(ChartInputError, match="birth_time"):
        build_birth_chart(
            {
                "birth_date": "2000-01-01",
                "place_name": "Vrindavan",
            },
            provider=FakeProvider(),
        )


def test_build_birth_chart_adds_vimshottari_when_moon_is_available():
    from apps.calculations.chart import build_birth_chart

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=FakeProviderWithMoon(),
    )

    periods = result["dashas"]["vimshottari"]["mahadashas"]
    assert periods[0]["lord"] == "Ketu"
    assert periods[0]["duration_years"] == 7.0
    assert result["dashas"]["extra"]["status"] == "partial_extra_dasha_catalog"
    assert result["dashas"]["extra"]["yogini"]["mahadashas"][0]["name"] == "Bhramari"
    assert result["dashas"]["extra"]["ashtottari"]["status"] == "metadata_only_needs_applicability_and_start_rule_audit"


def test_build_birth_chart_adds_panchanga_when_sun_and_moon_are_available():
    from apps.calculations.chart import build_birth_chart

    class FakeProviderWithSunMoon:
        def planet_positions(self, moment, bodies, settings):
            return {
                "Surya": BodyPosition(
                    body="Surya",
                    longitude=0.0,
                    latitude=0.0,
                    distance_au=1.0,
                    speed_longitude=1.0,
                    placement=zodiac_placement(0.0),
                ),
                "Chandra": BodyPosition(
                    body="Chandra",
                    longitude=13.0,
                    latitude=0.0,
                    distance_au=1.0,
                    speed_longitude=1.0,
                    placement=zodiac_placement(13.0),
                ),
            }

    result = build_birth_chart(
        {
            "birth_date": "2000-01-03",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=FakeProviderWithSunMoon(),
    )

    assert result["panchanga"]["tithi"]["name"] == "Dvitiya"
    assert result["panchanga"]["karana"]["name"] == "Balava"


def test_build_birth_chart_adds_lagna_and_whole_sign_houses_when_provider_supports_it():
    from apps.calculations.chart import build_birth_chart

    class FakeProviderWithLagna:
        def planet_positions(self, moment, bodies, settings):
            return {}

        def ascendant_position(self, moment, latitude, longitude, settings):
            return BodyPosition(
                body="Lagna",
                longitude=90.0,
                latitude=None,
                distance_au=None,
                speed_longitude=None,
                placement=zodiac_placement(90.0),
            )

        def house_cusps(self, moment, latitude, longitude, settings):
            return [
                {
                    "house": house,
                    "longitude": float((house - 1) * 30 + 2),
                    "rashi": zodiac_placement((house - 1) * 30 + 2).rashi,
                    "rashi_index": zodiac_placement((house - 1) * 30 + 2).rashi_index,
                }
                for house in range(1, 13)
            ]

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=FakeProviderWithLagna(),
    )

    assert result["ascendant"]["rashi"] == "Karka"
    assert result["houses"][0]["house"] == 1
    assert result["houses"][0]["rashi"] == "Karka"
    assert result["houses"][1]["rashi"] == "Simha"
    assert result["house_cusps"][0]["longitude"] == 2.0
    assert result["house_cusps"][3]["rashi"] == "Karka"


def test_build_birth_chart_adds_solar_day_and_gulika_context():
    from apps.calculations.chart import build_birth_chart

    class FakeProviderWithVariableLagna:
        def __init__(self):
            self.ascendant_moments = []

        def planet_positions(self, moment, bodies, settings):
            return {
                "Surya": BodyPosition(
                    body="Surya",
                    longitude=30.0,
                    latitude=0.0,
                    distance_au=1.0,
                    speed_longitude=1.0,
                    placement=zodiac_placement(30.0),
                ),
                "Chandra": BodyPosition(
                    body="Chandra",
                    longitude=60.0,
                    latitude=0.0,
                    distance_au=1.0,
                    speed_longitude=1.0,
                    placement=zodiac_placement(60.0),
                ),
            }

        def ascendant_position(self, moment, latitude, longitude, settings):
            self.ascendant_moments.append(moment)
            longitude_value = 90.0 if len(self.ascendant_moments) == 1 else 120.0
            return BodyPosition(
                body="Lagna",
                longitude=longitude_value,
                latitude=None,
                distance_au=None,
                speed_longitude=None,
                placement=zodiac_placement(longitude_value),
            )

    provider = FakeProviderWithVariableLagna()

    result = build_birth_chart(
        {
            "birth_date": "2026-06-02",
            "birth_time": "10:00",
            "place_name": "Vrindavan",
        },
        provider=provider,
    )

    assert result["solar_day"]["sunrise"].startswith("2026-06-02T05:")
    assert result["solar_day"]["sunset"].startswith("2026-06-02T19:")
    assert result["solar_day"]["day_periods"][0]["key"] == "rahu_kalam"
    assert provider.ascendant_moments[1].isoformat().startswith("2026-06-02T13:")
    upagraha = result["classical"]["special_points"]["upagrahas"]["items"][0]
    assert upagraha["key"] == "gulika"
    assert upagraha["longitude"] == 120.0
    assert upagraha["local_time"].startswith("13:")


def test_build_birth_chart_adds_shodasha_varga_payload():
    from apps.calculations.chart import build_birth_chart

    class FakeProviderWithGrahaAndLagna:
        def planet_positions(self, moment, bodies, settings):
            return {
                "Surya": BodyPosition(
                    body="Surya",
                    longitude=30.0,
                    latitude=0.0,
                    distance_au=1.0,
                    speed_longitude=1.0,
                    placement=zodiac_placement(30.0),
                )
            }

        def ascendant_position(self, moment, latitude, longitude, settings):
            return BodyPosition(
                body="Lagna",
                longitude=90.0,
                latitude=None,
                distance_au=None,
                speed_longitude=None,
                placement=zodiac_placement(90.0),
            )

    result = build_birth_chart(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=FakeProviderWithGrahaAndLagna(),
    )

    assert "D2" in result["vargas"]
    assert "D60" in result["vargas"]
    d9 = result["vargas"]["D9"]

    assert d9["name"] == "Navamsa"
    assert d9["placements"][0] == {
        "body": "Lagna",
        "rashi_index": 3,
        "rashi": "Karka",
    }
    assert d9["placements"][1] == {
        "body": "Surya",
        "rashi_index": 9,
        "rashi": "Makara",
    }


@pytest.mark.django_db
def test_birth_chart_api_returns_400_for_bad_input():
    response = APIClient().post(reverse("birth-chart"), {"birth_date": "2000-01-01"}, format="json")

    assert response.status_code == 400
    assert "birth_time" in response.data["error"]


@pytest.mark.django_db
def test_birth_chart_api_returns_503_when_ephemeris_missing(monkeypatch):
    def raise_unavailable(data):
        raise EphemerisUnavailable("install pyswisseph")

    monkeypatch.setattr("apps.calculations.views.build_birth_chart", raise_unavailable)

    response = APIClient().post(
        reverse("birth-chart"),
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 503
    assert response.data["error"] == "install pyswisseph"


@pytest.mark.django_db
def test_birth_chart_api_returns_chart(monkeypatch):
    def fake_build(data):
        return {
            "calculation_version": "mvp-0.1",
            "place": {"name": data["place_name"], "latitude": 27.58, "longitude": 77.7},
            "grahas": [{"body": "Surya", "longitude": 30.0, "rashi": "Vrishabha"}],
        }

    monkeypatch.setattr("apps.calculations.views.build_birth_chart", fake_build)

    response = APIClient().post(
        reverse("birth-chart"),
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["grahas"][0]["body"] == "Surya"


@pytest.mark.django_db
def test_dual_calculation_api_returns_report(monkeypatch):
    def fake_dual(data):
        return {
            "status": "calculated_witness_mode",
            "primary_calculation": {"key": "jyotish_agent_primary"},
            "jhora_profile_calculation": {"key": "jhora_drik_profile"},
            "settings_diff": [],
            "delta": {"exact_match": True},
            "authority_decision": {"accepted_track": "primary_calculation"},
        }

    monkeypatch.setattr("apps.calculations.views.build_dual_calculation_report", fake_dual)

    response = APIClient().post(
        reverse("dual-calculation"),
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == "calculated_witness_mode"
    assert response.data["authority_decision"]["accepted_track"] == "primary_calculation"
