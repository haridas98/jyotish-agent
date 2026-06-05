from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess

from .catalog import search_places
from .geocoding import geocode_places


class PlacesSearchView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        query = request.query_params.get("q", "")
        places = search_places(query)
        if not places:
            try:
                places = geocode_places(query)
            except Exception:
                places = []
        return Response({"items": [place.as_dict() for place in places]})
