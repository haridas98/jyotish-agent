from django.urls import path

from .views import BirthAnalysisPacketView, BirthReportView

urlpatterns = [
    path("reports/birth-chart", BirthReportView.as_view(), name="birth-report"),
    path(
        "reports/birth-chart/analysis-packet",
        BirthAnalysisPacketView.as_view(),
        name="birth-analysis-packet",
    ),
]
