from __future__ import annotations

import hashlib

from django.conf import settings
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess

from .catalog import search_places
from .geocoding import geocode_places


class PlacesSearchView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        query = request.query_params.get("q", "")
        cache_key = _places_search_cache_key(query)
        cached = cache.get(cache_key)
        if isinstance(cached, list):
            response = Response({"items": cached})
            response["X-Jyotish-Cache"] = "hit"
            return response
        places = search_places(query)
        if not places:
            try:
                places = geocode_places(query)
            except Exception:
                places = []
        payload = [place.as_dict() for place in places]
        cache.set(cache_key, payload, timeout=getattr(settings, "PLACES_SEARCH_CACHE_SECONDS", 86400))
        response = Response({"items": payload})
        response["X-Jyotish-Cache"] = "miss"
        return response


def _places_search_cache_key(query: object) -> str:
    normalized = " ".join(str(query or "").strip().lower().split())[:160]
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return f"places:search:v1:{digest}"
