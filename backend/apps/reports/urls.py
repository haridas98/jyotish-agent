from django.urls import path

from .views import (
    BirthAnalysisPacketView,
    BirthCodexAnalysisView,
    BirthDraftAnalysisView,
    BirthReportView,
    CompatibilityAnalysisPacketView,
    ShastraConditionMatrixView,
    ShastraEvidenceView,
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
        "reports/birth-chart/codex-analysis",
        BirthCodexAnalysisView.as_view(),
        name="birth-codex-analysis",
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
    path(
        "reports/shastra-evidence",
        ShastraEvidenceView.as_view(),
        name="shastra-evidence",
    ),
]
