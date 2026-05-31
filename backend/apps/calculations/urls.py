from django.urls import path

from .views import BirthChartView, EphemerisStatusView, ZodiacPlacementView

urlpatterns = [
    path("calculations/birth-chart", BirthChartView.as_view(), name="birth-chart"),
    path("calculations/zodiac-placement", ZodiacPlacementView.as_view(), name="zodiac-placement"),
    path("calculations/ephemeris/status", EphemerisStatusView.as_view(), name="ephemeris-status"),
]
