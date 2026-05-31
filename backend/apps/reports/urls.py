from django.urls import path

from .views import BirthReportView

urlpatterns = [
    path("reports/birth-chart", BirthReportView.as_view(), name="birth-report"),
]
