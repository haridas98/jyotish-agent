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
    def planet_positions(
        self,
        moment: datetime,
        bodies: list[str],
        settings: CalculationSettings,
    ) -> dict[str, BodyPosition]:
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

    calculation = calculate_profile_chart(profile, provider=FakeProvider())

    assert calculation.status == calculation.Status.COMPLETE
    assert calculation.result["birth"]["timezone"] == "Asia/Kolkata"
    assert PlanetPosition.objects.filter(calculation=calculation).count() == len(GRAHAS)
    assert VargaPlacement.objects.filter(calculation=calculation, varga="D9").count() == len(GRAHAS)
    assert VargaPlacement.objects.filter(calculation=calculation, varga="D60").count() == len(GRAHAS)
    assert DashaPeriod.objects.filter(calculation=calculation, system="vimshottari").count() == 9
