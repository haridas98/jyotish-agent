from django.urls import path

from .views import VLSearchView

urlpatterns = [
    path("sources/vl/search", VLSearchView.as_view(), name="sources-vl-search"),
]
