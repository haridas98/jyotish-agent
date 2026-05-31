from django.urls import path

from .views import BirthProfileCalculateView, BirthProfileDetailView, BirthProfileListView

urlpatterns = [
    path("charts/profiles", BirthProfileListView.as_view(), name="chart-profile-list"),
    path("charts/profiles/<int:profile_id>", BirthProfileDetailView.as_view(), name="chart-profile-detail"),
    path(
        "charts/profiles/<int:profile_id>/calculate",
        BirthProfileCalculateView.as_view(),
        name="chart-profile-calculate",
    ),
]
