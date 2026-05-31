from __future__ import annotations

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.calculations.chart import ChartInputError
from apps.calculations.ephemeris import EphemerisUnavailable
from apps.interpretations.engine import public_interpretation_sections_for_chart
from apps.vl_integration.client import search_vl_documents

from .birth_report import compose_birth_report


class BirthReportView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        try:
            return Response(
                compose_birth_report(
                    request.data,
                    citation_search=vl_citation_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                )
            )
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


def vl_citation_search(query: str) -> list[dict[str, object]]:
    return search_vl_documents(
        settings.VL_DATABASE_URL,
        query,
        limit=3,
        public_base_url=settings.VL_PUBLIC_BASE_URL,
    )
