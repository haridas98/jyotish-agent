from django.urls import path

from .views import (
    ResearchSearchView,
    SourceCoverageView,
    SourceWorkListView,
    SourceWorkPassageListView,
    VLSearchView,
)

urlpatterns = [
    path("sources/coverage", SourceCoverageView.as_view(), name="sources-coverage"),
    path("sources/research/search", ResearchSearchView.as_view(), name="sources-research-search"),
    path("sources/works", SourceWorkListView.as_view(), name="sources-work-list"),
    path("sources/works/<slug:work_slug>/passages", SourceWorkPassageListView.as_view(), name="sources-work-passages"),
    path("sources/vl/search", VLSearchView.as_view(), name="sources-vl-search"),
]
