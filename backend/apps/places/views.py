from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

from .catalog import search_places


class PlacesSearchView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        query = request.query_params.get("q", "")
        return Response({"items": [place.as_dict() for place in search_places(query)]})

