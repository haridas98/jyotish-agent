from __future__ import annotations

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.sources.citations import local_research_corpus_search
from apps.sources.coverage import source_coverage_matrix
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


class ResearchSearchView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        query = str(request.query_params.get("q", "")).strip()
        if not query:
            return Response({"error": "q query parameter is required"}, status=400)
        try:
            limit = int(request.query_params.get("limit", 5) or 5)
        except ValueError:
            return Response({"error": "limit must be an integer"}, status=400)
        return Response({"items": local_research_corpus_search(query, limit=min(limit, 20))})


class SourceCoverageView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return Response(source_coverage_matrix())
