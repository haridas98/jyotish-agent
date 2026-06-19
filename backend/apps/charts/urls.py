from django.urls import path

from .views import (
    BirthProfileCalculateView,
    BirthProfileDetailView,
    BirthProfileListView,
    BirthProfileRelationshipActionView,
    BirthProfileRelationshipDetailView,
    BirthProfileRelationshipInboxView,
    BirthProfileRelationshipListView,
    BirthProfileWorkbenchView,
    ChartRelationshipDetailView,
    ChartRelationshipListView,
    D1WorkbenchDevCheckView,
    DashaWorkbenchDevCheckView,
)

urlpatterns = [
    path("dev/d1-workbench-check", D1WorkbenchDevCheckView.as_view(), name="dev-d1-workbench-check"),
    path("dev/varga-workbench-check", D1WorkbenchDevCheckView.as_view(), name="dev-varga-workbench-check"),
    path("dev/dasha-workbench-check", DashaWorkbenchDevCheckView.as_view(), name="dev-dasha-workbench-check"),
    path("charts", BirthProfileListView.as_view(), name="chart-list"),
    path("charts/<int:profile_id>", BirthProfileDetailView.as_view(), name="chart-detail"),
    path("charts/<int:profile_id>/workbench", BirthProfileWorkbenchView.as_view(), name="chart-workbench"),
    path("charts/profiles", BirthProfileListView.as_view(), name="chart-profile-list"),
    path("charts/profiles/<int:profile_id>", BirthProfileDetailView.as_view(), name="chart-profile-detail"),
    path("charts/profile-relationships", BirthProfileRelationshipListView.as_view(), name="chart-profile-relationship-list"),
    path("relationships", ChartRelationshipListView.as_view(), name="relationship-list"),
    path("relationships/<int:relationship_id>", ChartRelationshipDetailView.as_view(), name="relationship-detail"),
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
