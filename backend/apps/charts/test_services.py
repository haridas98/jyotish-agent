from datetime import date, datetime, time
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.calculations.constants import GRAHAS
from apps.calculations.ephemeris import BodyPosition, CalculationSettings
from apps.calculations.primitives import zodiac_placement

from .models import BirthProfile, DashaPeriod, Place, PlanetPosition, VargaPlacement
from .services import calculate_profile_chart


class FakeProvider:
    def __init__(self) -> None:
        self.settings: CalculationSettings | None = None

    def planet_positions(
        self,
        moment: datetime,
        bodies: list[str],
        settings: CalculationSettings,
    ) -> dict[str, BodyPosition]:
        self.settings = settings
        return {
            body: BodyPosition(
                body=body,
                longitude=10.0 + index,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=0.1,
                placement=zodiac_placement(10.0 + index),
            )
            for index, body in enumerate(bodies)
        }


@pytest.mark.django_db
def test_calculate_profile_chart_persists_positions_and_all_vargas():
    user = get_user_model().objects.create_user(username="haridas", password="strong-pass-108")
    place = Place.objects.create(
        external_id="in-vrindavan",
        name="Vrindavan",
        country_code="IN",
        latitude=Decimal("27.565000"),
        longitude=Decimal("77.659300"),
        timezone_name="Asia/Kolkata",
        metadata={"label": "Vrindavan, Uttar Pradesh, IN"},
    )
    profile = BirthProfile.objects.create(
        user=user,
        display_name="Test chart",
        birth_date=date(1990, 8, 15),
        birth_time=time(10, 24),
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        place=place,
        timezone_name="Asia/Kolkata",
    )

    provider = FakeProvider()
    calculation = calculate_profile_chart(profile, provider=provider)

    assert calculation.status == calculation.Status.COMPLETE
    assert provider.settings == CalculationSettings()
    assert calculation.result["birth"]["timezone"] == "Asia/Kolkata"
    assert PlanetPosition.objects.filter(calculation=calculation).count() == len(GRAHAS)
    assert VargaPlacement.objects.filter(calculation=calculation, varga="D9").count() == len(GRAHAS)
    assert VargaPlacement.objects.filter(calculation=calculation, varga="D60").count() == len(GRAHAS)
    assert DashaPeriod.objects.filter(calculation=calculation, system="vimshottari").count() == 9


@pytest.mark.django_db
def test_calculate_profile_chart_preserves_saved_place_external_id():
    user = get_user_model().objects.create_user(username="place-user", password="strong-pass-108")
    place = Place.objects.create(
        external_id="custom:sterlitamak-1998",
        name="Sterlitamak",
        country_code="RU",
        latitude=Decimal("53.630400"),
        longitude=Decimal("55.930800"),
        timezone_name="Asia/Yekaterinburg",
        metadata={"label": "Sterlitamak, Bashkortostan, RU"},
    )
    profile = BirthProfile.objects.create(
        user=user,
        display_name="Saved place chart",
        birth_date=date(1998, 4, 30),
        birth_time=time(13, 45),
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        place=place,
        timezone_name="Asia/Yekaterinburg",
    )

    calculation = calculate_profile_chart(profile, provider=FakeProvider())

    assert calculation.status == calculation.Status.COMPLETE
    assert calculation.input_snapshot["place_id"] == "custom:sterlitamak-1998"
    assert calculation.result["place"]["id"] == "custom:sterlitamak-1998"


@pytest.mark.django_db
def test_calculate_profile_chart_uses_saved_calculation_settings():
    user = get_user_model().objects.create_user(username="settings-user", password="strong-pass-108")
    place = Place.objects.create(
        external_id="in-vrindavan",
        name="Vrindavan",
        country_code="IN",
        latitude=Decimal("27.565000"),
        longitude=Decimal("77.659300"),
        timezone_name="Asia/Kolkata",
        metadata={"label": "Vrindavan, Uttar Pradesh, IN"},
    )
    profile = BirthProfile.objects.create(
        user=user,
        display_name="Mean node chart",
        birth_date=date(1990, 8, 15),
        birth_time=time(10, 24),
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        place=place,
        timezone_name="Asia/Kolkata",
        calculation_settings={
            "calculation_model": "drik_siddhanta",
            "ayanamsa": "lahiri",
            "node_type": "mean",
            "ephemeris": "swiss",
            "house_system": "whole_sign",
            "bhava_system": "whole_sign",
            "varga_scheme": "parashara",
            "sunrise_source": "noaa",
            "timezone_source": "iana",
            "shadbala_profile": "bphs_classical",
        },
    )
    provider = FakeProvider()

    calculation = calculate_profile_chart(profile, provider=provider)

    assert calculation.status == calculation.Status.COMPLETE
    assert provider.settings == CalculationSettings(node_type="mean")
    assert calculation.input_snapshot["node_type"] == "mean"
    assert calculation.result["settings"]["node_type"] == "mean"
