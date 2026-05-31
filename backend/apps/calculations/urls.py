from django.urls import path

from .views import EphemerisStatusView, ZodiacPlacementView

urlpatterns = [
    path("calculations/zodiac-placement", ZodiacPlacementView.as_view(), name="zodiac-placement"),
    path("calculations/ephemeris/status", EphemerisStatusView.as_view(), name="ephemeris-status"),
]
