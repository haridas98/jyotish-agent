from django.urls import path

from .views import BirthAnalysisPacketView, BirthReportView, CompatibilityAnalysisPacketView

urlpatterns = [
    path("reports/birth-chart", BirthReportView.as_view(), name="birth-report"),
    path(
        "reports/birth-chart/analysis-packet",
        BirthAnalysisPacketView.as_view(),
        name="birth-analysis-packet",
    ),
    path(
        "reports/compatibility/analysis-packet",
        CompatibilityAnalysisPacketView.as_view(),
        name="compatibility-analysis-packet",
    ),
]
