from django.urls import path

from .views import ResearchSearchView, VLSearchView

urlpatterns = [
    path("sources/research/search", ResearchSearchView.as_view(), name="sources-research-search"),
    path("sources/vl/search", VLSearchView.as_view(), name="sources-vl-search"),
]
