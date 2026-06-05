from __future__ import annotations

from django.conf import settings
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess
from apps.calculations.chart import ChartInputError
from apps.calculations.ephemeris import EphemerisUnavailable
from apps.interpretations.condition_matrix import shastra_condition_matrix
from apps.interpretations.evidence_matcher import approve_shastra_condition_evidence, shastra_evidence_payload
from apps.interpretations.engine import public_interpretation_sections_for_chart
from apps.interpretations.models import ShastraConditionEvidence
from apps.sources.citations import combined_citation_search, local_research_corpus_search

from .analysis_packet import build_analysis_packet, build_compatibility_analysis_packet
from .birth_report import compose_birth_report
from .codex_cli_generation import (
    ask_birth_chart_codex_cli_analysis,
    ask_compatibility_codex_cli_analysis,
    generate_birth_chart_codex_cli_analysis,
    generate_compatibility_codex_cli_analysis,
)
from .draft_generation import DraftGenerationUnavailable, generate_birth_chart_draft_analysis
from .models import GeneratedAnalysisDraft


class BirthReportView(APIView):
    permission_classes = [PrivateAppAccess]

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
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            packet = build_analysis_packet(
                request.data,
                citation_search=vl_citation_search,
                research_search=local_research_corpus_search,
                interpretation_provider=public_interpretation_sections_for_chart,
                include_prompt=_include_prompt(request),
            )
            if not _include_prompt(request):
                packet = {key: value for key, value in packet.items() if key != "prompt_markdown"}
            return Response(packet)
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class BirthDraftAnalysisView(APIView):
    permission_classes = [PrivateAppAccess]

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
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            force_regenerate = bool(request.data.get("force_regenerate"))
            chart_data = dict(request.data)
            chart_data.pop("force_regenerate", None)
            return Response(
                generate_birth_chart_codex_cli_analysis(
                    chart_data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                    refresh_evidence=False,
                    force_regenerate=force_regenerate,
                )
            )
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except (EphemerisUnavailable, DraftGenerationUnavailable) as exc:
            return Response({"error": str(exc)}, status=503)


class BirthCodexAnalysisChatView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            analysis_id = int(request.data.get("analysis_id") or 0)
            return Response(
                ask_birth_chart_codex_cli_analysis(
                    analysis_id=analysis_id,
                    question=str(request.data.get("question") or ""),
                    history=request.data.get("history") if isinstance(request.data.get("history"), list) else [],
                )
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        except GeneratedAnalysisDraft.DoesNotExist:
            return Response({"error": "analysis not found"}, status=404)
        except DraftGenerationUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class CompatibilityAnalysisPacketView(APIView):
    permission_classes = [PrivateAppAccess]

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


class CompatibilityCodexAnalysisView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(
                generate_compatibility_codex_cli_analysis(
                    request.data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    refresh_evidence=False,
                )
            )
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except (EphemerisUnavailable, DraftGenerationUnavailable) as exc:
            return Response({"error": str(exc)}, status=503)


class CompatibilityCodexAnalysisChatView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            analysis_id = int(request.data.get("analysis_id") or 0)
            return Response(
                ask_compatibility_codex_cli_analysis(
                    analysis_id=analysis_id,
                    question=str(request.data.get("question") or ""),
                    history=request.data.get("history") if isinstance(request.data.get("history"), list) else [],
                )
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        except GeneratedAnalysisDraft.DoesNotExist:
            return Response({"error": "analysis not found"}, status=404)
        except DraftGenerationUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class ShastraConditionMatrixView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        return Response(shastra_condition_matrix())


class ShastraEvidenceView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        raw_keys = str(request.query_params.get("keys", "")).strip()
        condition_keys = [key.strip() for key in raw_keys.split(",") if key.strip()] or None
        return Response(shastra_evidence_payload(condition_keys=condition_keys))


class ShastraEvidenceApproveView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, evidence_id: int):
        try:
            return Response(
                approve_shastra_condition_evidence(
                    evidence_id,
                    exact_reference=str(request.data.get("exact_reference") or ""),
                    approved_excerpt=str(request.data.get("approved_excerpt") or ""),
                    reviewer=str(request.data.get("reviewer") or ""),
                    notes=str(request.data.get("notes") or ""),
                )
            )
        except ShastraConditionEvidence.DoesNotExist:
            return Response({"error": "evidence not found"}, status=404)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)


def vl_citation_search(query: str) -> list[dict[str, object]]:
    return combined_citation_search(
        settings.VL_DATABASE_URL,
        query,
        limit=3,
        public_base_url=settings.VL_PUBLIC_BASE_URL,
    )


def _include_prompt(request) -> bool:
    return str(request.query_params.get("include_prompt") or "").lower() in {"1", "true", "yes"}
