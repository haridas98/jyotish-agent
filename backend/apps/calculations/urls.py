from django.urls import path

from .views import (
    BirthChartView,
    CompatibilityView,
    DualCalculationView,
    EphemerisStatusView,
    JHoraAccuracyReportView,
    MuhurtaView,
    MundaneView,
    PrashnaView,
    TajakaView,
    TithiPraveshaView,
    TransitView,
    ZodiacPlacementView,
)

urlpatterns = [
    path("calculations/birth-chart", BirthChartView.as_view(), name="birth-chart"),
    path("calculations/dual", DualCalculationView.as_view(), name="dual-calculation"),
    path("calculations/transits", TransitView.as_view(), name="transits"),
    path("calculations/compatibility", CompatibilityView.as_view(), name="compatibility"),
    path("calculations/muhurta", MuhurtaView.as_view(), name="muhurta"),
    path("calculations/tithi-pravesha", TithiPraveshaView.as_view(), name="tithi-pravesha"),
    path("calculations/tajaka", TajakaView.as_view(), name="tajaka"),
    path("calculations/prashna", PrashnaView.as_view(), name="prashna"),
    path("calculations/mundane", MundaneView.as_view(), name="mundane"),
    path("calculations/zodiac-placement", ZodiacPlacementView.as_view(), name="zodiac-placement"),
    path("calculations/ephemeris/status", EphemerisStatusView.as_view(), name="ephemeris-status"),
    path("calculations/jhora-accuracy", JHoraAccuracyReportView.as_view(), name="jhora-accuracy"),
]
