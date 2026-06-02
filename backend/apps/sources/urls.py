from django.urls import path

from .views import ResearchSearchView, SourceCoverageView, VLSearchView

urlpatterns = [
    path("sources/coverage", SourceCoverageView.as_view(), name="sources-coverage"),
    path("sources/research/search", ResearchSearchView.as_view(), name="sources-research-search"),
    path("sources/vl/search", VLSearchView.as_view(), name="sources-vl-search"),
]
