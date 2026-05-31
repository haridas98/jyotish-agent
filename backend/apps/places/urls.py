from django.urls import path

from .views import PlacesSearchView

urlpatterns = [
    path("places/search", PlacesSearchView.as_view(), name="places-search"),
]

