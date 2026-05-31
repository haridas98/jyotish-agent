from django.urls import path

from .views import DatabaseHealthView, HealthView, VLHealthView

urlpatterns = [
    path("health", HealthView.as_view(), name="health"),
    path("health/db", DatabaseHealthView.as_view(), name="health-db"),
    path("health/vl", VLHealthView.as_view(), name="health-vl"),
]

