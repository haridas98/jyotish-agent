from __future__ import annotations

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess
from apps.sources.citations import local_research_corpus_search
from apps.sources.coverage import source_coverage_matrix
from apps.sources.inventory import source_inventory_payload, work_passages_payload
from apps.sources.models import SourceWork
from apps.vl_integration.client import search_vl_documents


class VLSearchView(APIView):
    permission_classes = [PrivateAppAccess]

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
    permission_classes = [PrivateAppAccess]

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
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        return Response(source_coverage_matrix())


class SourceWorkListView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 300) or 300)
        except ValueError:
            return Response({"error": "limit must be an integer"}, status=400)
        return Response(source_inventory_payload(limit=min(max(1, limit), 1000)))


class SourceWorkPassageListView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request, work_slug: str):
        try:
            limit = int(request.query_params.get("limit", 25) or 25)
            offset = int(request.query_params.get("offset", 0) or 0)
        except ValueError:
            return Response({"error": "limit and offset must be integers"}, status=400)
        try:
            return Response(work_passages_payload(work_slug, limit=limit, offset=offset))
        except SourceWork.DoesNotExist:
            return Response({"error": "source work not found"}, status=404)
