from django.urls import path

from .views import (
    BirthAnalysisPacketView,
    BirthDraftAnalysisView,
    BirthReportView,
    CompatibilityAnalysisPacketView,
    ShastraConditionMatrixView,
)

urlpatterns = [
    path("reports/birth-chart", BirthReportView.as_view(), name="birth-report"),
    path(
        "reports/birth-chart/analysis-packet",
        BirthAnalysisPacketView.as_view(),
        name="birth-analysis-packet",
    ),
    path(
        "reports/birth-chart/draft-analysis",
        BirthDraftAnalysisView.as_view(),
        name="birth-draft-analysis",
    ),
    path(
        "reports/compatibility/analysis-packet",
        CompatibilityAnalysisPacketView.as_view(),
        name="compatibility-analysis-packet",
    ),
    path(
        "reports/shastra-condition-matrix",
        ShastraConditionMatrixView.as_view(),
        name="shastra-condition-matrix",
    ),
]
