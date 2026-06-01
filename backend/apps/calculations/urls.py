from django.urls import path

from .views import (
    BirthChartView,
    CompatibilityView,
    EphemerisStatusView,
    MuhurtaView,
    TransitView,
    ZodiacPlacementView,
)

urlpatterns = [
    path("calculations/birth-chart", BirthChartView.as_view(), name="birth-chart"),
    path("calculations/transits", TransitView.as_view(), name="transits"),
    path("calculations/compatibility", CompatibilityView.as_view(), name="compatibility"),
    path("calculations/muhurta", MuhurtaView.as_view(), name="muhurta"),
    path("calculations/zodiac-placement", ZodiacPlacementView.as_view(), name="zodiac-placement"),
    path("calculations/ephemeris/status", EphemerisStatusView.as_view(), name="ephemeris-status"),
]
