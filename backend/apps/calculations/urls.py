from django.urls import path

from .views import ZodiacPlacementView

urlpatterns = [
    path("calculations/zodiac-placement", ZodiacPlacementView.as_view(), name="zodiac-placement"),
]

