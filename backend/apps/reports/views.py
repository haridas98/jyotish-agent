from __future__ import annotations

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.calculations.chart import ChartInputError
from apps.calculations.ephemeris import EphemerisUnavailable
from apps.interpretations.condition_matrix import shastra_condition_matrix
from apps.interpretations.evidence_matcher import shastra_evidence_payload
from apps.interpretations.engine import public_interpretation_sections_for_chart
from apps.sources.citations import combined_citation_search, local_research_corpus_search

from .analysis_packet import build_analysis_packet, build_compatibility_analysis_packet
from .birth_report import compose_birth_report
from .codex_cli_generation import generate_birth_chart_codex_cli_analysis
from .draft_generation import DraftGenerationUnavailable, generate_birth_chart_draft_analysis


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


class BirthAnalysisPacketView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        try:
            return Response(
                build_analysis_packet(
                    request.data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                )
            )
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class BirthDraftAnalysisView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        try:
            return Response(
                generate_birth_chart_draft_analysis(
                    request.data,
                    citation_search=vl_citation_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                )
            )
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except (EphemerisUnavailable, DraftGenerationUnavailable) as exc:
            return Response({"error": str(exc)}, status=503)


class BirthCodexAnalysisView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        try:
            return Response(
                generate_birth_chart_codex_cli_analysis(
                    request.data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                )
            )
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except (EphemerisUnavailable, DraftGenerationUnavailable) as exc:
            return Response({"error": str(exc)}, status=503)


class CompatibilityAnalysisPacketView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        try:
            return Response(
                build_compatibility_analysis_packet(
                    request.data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                )
            )
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class ShastraConditionMatrixView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return Response(shastra_condition_matrix())


class ShastraEvidenceView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        raw_keys = str(request.query_params.get("keys", "")).strip()
        condition_keys = [key.strip() for key in raw_keys.split(",") if key.strip()] or None
        return Response(shastra_evidence_payload(condition_keys=condition_keys))


def vl_citation_search(query: str) -> list[dict[str, object]]:
    return combined_citation_search(
        settings.VL_DATABASE_URL,
        query,
        limit=3,
        public_base_url=settings.VL_PUBLIC_BASE_URL,
    )
