from __future__ import annotations

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.vl_integration.client import search_vl_documents


class VLSearchView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        query = str(request.query_params.get("q", "")).strip()
        if not query:
            return Response({"error": "q query parameter is required"}, status=400)

        return Response(
            {
                "items": search_vl_documents(
                    settings.VL_DATABASE_URL,
                    query,
                    limit=5,
                    public_base_url=settings.VL_PUBLIC_BASE_URL,
                )
            }
        )
