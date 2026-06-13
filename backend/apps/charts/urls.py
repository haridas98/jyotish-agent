from django.urls import path

from .views import (
    BirthProfileCalculateView,
    BirthProfileDetailView,
    BirthProfileListView,
    BirthProfileRelationshipActionView,
    BirthProfileRelationshipDetailView,
    BirthProfileRelationshipInboxView,
    BirthProfileRelationshipListView,
)

urlpatterns = [
    path("charts/profiles", BirthProfileListView.as_view(), name="chart-profile-list"),
    path("charts/profiles/<int:profile_id>", BirthProfileDetailView.as_view(), name="chart-profile-detail"),
    path("charts/profile-relationships", BirthProfileRelationshipListView.as_view(), name="chart-profile-relationship-list"),
    path(
        "charts/profile-relationships/inbox",
        BirthProfileRelationshipInboxView.as_view(),
        name="chart-profile-relationship-inbox",
    ),
    path(
        "charts/profile-relationships/<int:relationship_id>",
        BirthProfileRelationshipDetailView.as_view(),
        name="chart-profile-relationship-detail",
    ),
    path(
        "charts/profile-relationships/<int:relationship_id>/action",
        BirthProfileRelationshipActionView.as_view(),
        name="chart-profile-relationship-action",
    ),
    path(
        "charts/profiles/<int:profile_id>/calculate",
        BirthProfileCalculateView.as_view(),
        name="chart-profile-calculate",
    ),
]
