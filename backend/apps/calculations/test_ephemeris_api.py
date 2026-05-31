import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.calculations.ephemeris import EphemerisUnavailable


@pytest.mark.django_db
def test_ephemeris_status_reports_optional_dependency_state(monkeypatch):
    def raise_unavailable(self):
        raise EphemerisUnavailable("install pyswisseph")

    monkeypatch.setattr(
        "apps.calculations.views.SwissEphemerisProvider._load_swisseph",
        raise_unavailable,
    )

    response = APIClient().get(reverse("ephemeris-status"))

    assert response.status_code == 200
    assert response.data == {
        "provider": "swiss",
        "available": False,
        "detail": "install pyswisseph",
    }
