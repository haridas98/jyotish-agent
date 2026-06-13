from __future__ import annotations

import hashlib
import json
import re
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess
from apps.calculations.chart import ChartInputError
from apps.calculations.ephemeris import EphemerisUnavailable
from apps.calculations.workflows import build_transit_report
from apps.charts.models import BirthProfile, BirthProfileRelationship, ChartCalculation
from apps.charts.services import calculate_profile_chart, profile_payload
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
    ask_current_day_codex_cli_analysis,
    generate_birth_chart_codex_cli_analysis,
    generate_compatibility_codex_cli_analysis,
)
from .draft_generation import DraftGenerationUnavailable
from .models import GeneratedAnalysisDraft, GeneratedAnalysisJob, input_summary_from_snapshot


MAIN_ANALYSIS_KINDS = {
    "birth_chart_codex_cli",
    "current_day_transit_overview",
    "compatibility_codex_cli",
}
CHAT_ANALYSIS_KINDS = {
    "birth_chart_codex_cli_chat",
    "compatibility_codex_cli_chat",
    "current_day_transit_overview_chat",
}
ALL_HISTORY_KINDS = MAIN_ANALYSIS_KINDS | CHAT_ANALYSIS_KINDS
CHAT_HISTORY_RECORD_LIMIT = 20


def _cache_digest(data: object) -> str:
    if hasattr(data, "dict"):
        data = data.dict()
    payload = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _birth_report_cache_key(data: object) -> str:
    return f"birth-report:v3:{_cache_digest(data)}"


def _current_day_report_cache_key(data: object) -> str:
    return f"current-day-report:v1:{_cache_digest(data)}"


class BirthReportView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            cache_key = _birth_report_cache_key(request.data)
            cached = cache.get(cache_key)
            if cached is not None:
                response = Response(cached)
                response["X-Jyotish-Cache"] = "hit"
                return response
            result = compose_birth_report(
                request.data,
                citation_search=vl_citation_search,
                interpretation_provider=public_interpretation_sections_for_chart,
            )
            cache.set(cache_key, result, timeout=getattr(settings, "BIRTH_REPORT_CACHE_SECONDS", 3600))
            response = Response(result)
            response["X-Jyotish-Cache"] = "miss"
            return response
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class AnalysisHistoryView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        kinds = _history_kinds(request.query_params.get("kind"))
        profile_id = _optional_int(request.query_params.get("profile_id"))
        limit = min(max(_optional_int(request.query_params.get("limit")) or 20, 1), 100)
        queryset = _owned_analysis_records(request).filter(kind__in=kinds)
        if profile_id is not None:
            queryset = queryset.filter(profile_links__profile_id=profile_id).distinct()
        records = list(
            queryset
            .defer("input_snapshot", "packet_snapshot", "output_json", "prompt_markdown")
            .order_by("-created_at")[:limit]
        )
        chat_counts = _chat_counts_for_records(records, request)
        items = [_analysis_history_payload(record, chat_count=chat_counts.get(record.id, 0)) for record in records]
        return Response({"items": items})


class AnalysisHistoryDetailView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, analysis_id: int):
        record = get_object_or_404(_owned_analysis_records(request), id=analysis_id, kind__in=ALL_HISTORY_KINDS)
        return Response(
            {
                "analysis": _analysis_history_payload(record, include_output=True),
                **_chat_history_payload(record),
            }
        )


class AnalysisHistorySlugDetailView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, analysis_slug: str):
        analysis_id = _analysis_id_from_slug(analysis_slug)
        if analysis_id is None:
            return Response({"error": "analysis slug must end with numeric id"}, status=404)
        record = get_object_or_404(_owned_analysis_records(request), id=analysis_id, kind__in=ALL_HISTORY_KINDS)
        return Response(
            {
                "analysis": _analysis_history_payload(record, include_output=True),
                **_chat_history_payload(record),
            }
        )


class AnalysisChatHistoryView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, analysis_id: int):
        record = get_object_or_404(_owned_analysis_records(request), id=analysis_id, kind__in=MAIN_ANALYSIS_KINDS)
        return Response({"analysis_id": analysis_id, **_chat_history_payload(record, messages_key="messages")})


class AnalysisUniversalChatView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request):
        try:
            analysis_id = int(request.data.get("analysis_id") or 0)
            return _codex_chat_response(
                "analysis_chat",
                _request_user(request),
                analysis_id,
                lambda: ask_saved_analysis(
                    analysis_id=analysis_id,
                    provider="codex",
                    question=str(request.data.get("question") or ""),
                    history=request.data.get("history") if isinstance(request.data.get("history"), list) else [],
                    user=_request_user(request),
                )
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        except GeneratedAnalysisDraft.DoesNotExist:
            return Response({"error": "analysis not found"}, status=404)
        except DraftGenerationUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class AnalysisGenerationJobListView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request):
        kind = str(request.query_params.get("kind") or "").strip()
        status = str(request.query_params.get("status") or "").strip()
        limit = min(max(_optional_int(request.query_params.get("limit")) or 20, 1), 100)
        jobs = GeneratedAnalysisJob.objects.filter(user=_request_user(request))
        if kind:
            jobs = jobs.filter(kind=kind)
        if status:
            jobs = jobs.filter(status=status)
        jobs = jobs.select_related("analysis").order_by("-created_at")[:limit]
        return Response({"jobs": [_analysis_generation_job_payload(job) for job in jobs]})


class AnalysisGenerationJobDetailView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def get(self, request, job_id: int):
        job = get_object_or_404(
            GeneratedAnalysisJob.objects.select_related("analysis"),
            id=job_id,
            user=_request_user(request),
        )
        return Response({"job": _analysis_generation_job_payload(job)})


class BirthAnalysisPacketView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            data = _birth_analysis_data_for_request(request)
            packet = build_analysis_packet(
                data,
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
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request):
        return Response(
            {
                "error": "draft_analysis_disabled",
                "message": "OpenAI draft analysis is disabled. Use /api/reports/birth-chart/codex-analysis.",
            },
            status=410,
        )


class BirthCodexAnalysisView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request):
        try:
            force_regenerate = bool(request.data.get("force_regenerate"))
            chart_data = _birth_analysis_data_for_request(request)
            chart_data.pop("force_regenerate", None)
            access_response = _birth_codex_access_response(request, chart_data, force_regenerate=force_regenerate)
            if access_response is not None:
                return access_response
            user = _request_user(request)
            return _codex_generation_response(
                "birth_chart_codex_cli",
                user,
                chart_data,
                lambda: generate_birth_chart_codex_cli_analysis(
                    chart_data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                    refresh_evidence=False,
                    force_regenerate=force_regenerate,
                    user=user,
                )
            )
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except (EphemerisUnavailable, DraftGenerationUnavailable) as exc:
            return Response({"error": str(exc)}, status=503)


class BirthCodexAnalysisChatView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request):
        try:
            analysis_id = int(request.data.get("analysis_id") or 0)
            get_object_or_404(_owned_analysis_records(request), id=analysis_id, kind="birth_chart_codex_cli")
            return _codex_chat_response(
                "birth_chart_codex_cli_chat",
                _request_user(request),
                analysis_id,
                lambda: ask_birth_chart_codex_cli_analysis(
                    analysis_id=analysis_id,
                    question=str(request.data.get("question") or ""),
                    history=request.data.get("history") if isinstance(request.data.get("history"), list) else [],
                    user=_request_user(request),
                )
            )
        except ValueError as exc:
            return Response({"error": str(exc)}, status=400)
        except GeneratedAnalysisDraft.DoesNotExist:
            return Response({"error": "analysis not found"}, status=404)
        except DraftGenerationUnavailable as exc:
            return Response({"error": str(exc)}, status=503)


class BirthCurrentDayOverviewView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request):
        try:
            data = _birth_analysis_data_for_request(request)
            now = timezone.localtime()
            data.setdefault("as_of_date", now.date().isoformat())
            data.setdefault("as_of_time", now.time().isoformat(timespec="minutes"))
            cache_key = _current_day_report_cache_key(data)
            transit_report = cache.get(cache_key)
            cache_status = "hit"
            if transit_report is None:
                transit_report = build_transit_report(data)
                cache.set(cache_key, transit_report, timeout=getattr(settings, "CURRENT_DAY_REPORT_CACHE_SECONDS", 1800))
                cache_status = "miss"
            output = _current_day_overview_output(data, transit_report)
            record = _current_day_overview_record_for_request(_request_user(request), data)
            if record is None:
                record = GeneratedAnalysisDraft.objects.create(
                    kind="current_day_transit_overview",
                    review_status="calculation_draft",
                    source_policy="calculation_first",
                    provider="internal_transit",
                    model="workflow-v1",
                    input_snapshot=data,
                    packet_snapshot={"transit_report": transit_report},
                    output_json=output,
                    prompt_markdown="",
                    user=_request_user(request),
                )
            else:
                record.review_status = "calculation_draft"
                record.source_policy = "calculation_first"
                record.provider = "internal_transit"
                record.model = "workflow-v1"
                record.input_snapshot = data
                record.packet_snapshot = {"transit_report": transit_report}
                record.output_json = output
                record.prompt_markdown = ""
                record.save(
                    update_fields=[
                        "review_status",
                        "source_policy",
                        "provider",
                        "model",
                        "input_snapshot",
                        "input_summary",
                        "packet_snapshot",
                        "output_json",
                        "engine_label",
                        "first_section_title",
                        "excerpt",
                        "section_count",
                        "prompt_markdown",
                    ]
                )
            output["id"] = record.id
            response = Response(output)
            response["X-Jyotish-Transit-Cache"] = cache_status
            return response
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except EphemerisUnavailable as exc:
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
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request):
        try:
            data, error_response = _compatibility_analysis_data_for_request(request)
            if error_response is not None:
                return error_response
            user = _request_user(request)
            return _codex_generation_response(
                "compatibility_codex_cli",
                user,
                data,
                lambda: generate_compatibility_codex_cli_analysis(
                    data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    refresh_evidence=False,
                    user=user,
                )
            )
        except (ChartInputError, ValueError) as exc:
            return Response({"error": str(exc)}, status=400)
        except (EphemerisUnavailable, DraftGenerationUnavailable) as exc:
            return Response({"error": str(exc)}, status=503)


class CompatibilityCodexAnalysisChatView(APIView):
    permission_classes = [PrivateAppAccess, IsAuthenticated]

    def post(self, request):
        try:
            analysis_id = int(request.data.get("analysis_id") or 0)
            get_object_or_404(_owned_analysis_records(request), id=analysis_id, kind="compatibility_codex_cli")
            return _codex_chat_response(
                "compatibility_codex_cli_chat",
                _request_user(request),
                analysis_id,
                lambda: ask_compatibility_codex_cli_analysis(
                    analysis_id=analysis_id,
                    question=str(request.data.get("question") or ""),
                    history=request.data.get("history") if isinstance(request.data.get("history"), list) else [],
                    user=_request_user(request),
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


def ask_saved_analysis(
    *,
    analysis_id: int,
    provider: str,
    question: str,
    history: list[dict[str, object]] | None = None,
    user=None,
) -> dict[str, object]:
    report = _owned_analysis_queryset(user).get(id=analysis_id, kind__in=MAIN_ANALYSIS_KINDS)
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("question is required")

    if provider in {"codex", "codex_cli"}:
        if report.kind == "birth_chart_codex_cli":
            return ask_birth_chart_codex_cli_analysis(
                analysis_id=analysis_id,
                question=clean_question,
                history=history or [],
                user=user,
            )
        if report.kind == "current_day_transit_overview":
            return ask_current_day_codex_cli_analysis(
                analysis_id=analysis_id,
                question=clean_question,
                history=history or [],
                user=user,
            )
        if report.kind == "compatibility_codex_cli":
            return ask_compatibility_codex_cli_analysis(
                analysis_id=analysis_id,
                question=clean_question,
                history=history or [],
                user=user,
            )
        raise ValueError("Codex chat is available only for Codex reports")

    raise ValueError("provider must be codex")


def _request_user(request):
    user = getattr(request, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return user
    return None


def _owned_analysis_records(request):
    return _owned_analysis_queryset(_request_user(request))


def _owned_analysis_queryset(user):
    records = GeneratedAnalysisDraft.objects.all()
    if user is None:
        return records.none()
    return records.filter(user=user)


def _codex_generation_response(kind: str, user, data: dict[str, object], generate):
    lock_key = _codex_generation_lock_key(kind, user, data)
    lock_seconds = getattr(settings, "CODEX_ANALYSIS_LOCK_SECONDS", 900)
    if not cache.add(lock_key, "running", timeout=lock_seconds):
        return Response(
            {
                "error": "analysis_generation_in_progress",
                "message": (
                    "Codex-разбор уже выполняется для этих данных. "
                    "Дождитесь результата, чтобы не запускать второй тяжёлый процесс."
                ),
                "retry_after_seconds": min(lock_seconds, 60),
            },
            status=409,
        )
    concurrency_response = _codex_generation_concurrency_response(user)
    if concurrency_response is not None:
        cache.delete(lock_key)
        return concurrency_response
    if getattr(settings, "CODEX_GENERATION_QUEUE_ENABLED", False):
        try:
            existing_job = _active_generation_job_for_input(kind, user, data)
            job = existing_job or _create_queued_generation_job(kind, user, data)
            return Response(
                {
                    "queued": True,
                    "job": _analysis_generation_job_payload(job),
                    "message": "Codex-разбор уже в очереди." if existing_job else "Codex-разбор поставлен в очередь. Он появится в истории после обработки воркером.",
                },
                status=202,
            )
        finally:
            cache.delete(lock_key)
    job = _create_running_generation_job(kind, user, data)
    try:
        output = generate()
        _finish_generation_job(job, output)
        return Response(output)
    except Exception as exc:
        _fail_generation_job(job, exc)
        raise
    finally:
        cache.delete(lock_key)


def _codex_generation_lock_key(kind: str, user, data: dict[str, object]) -> str:
    payload = {
        key: value
        for key, value in data.items()
        if key
        not in {
            "billing_context",
            "force_regenerate",
            "related_profile_context",
            "selected_profile_context",
        }
    }
    owner = getattr(user, "id", "anonymous") or "anonymous"
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"reports:codex-generation-lock:{kind}:{owner}:{digest}"


def _codex_generation_concurrency_response(user) -> Response | None:
    if user is None:
        return None
    limit = max(int(getattr(settings, "CODEX_MAX_RUNNING_GENERATIONS_PER_USER", 1)), 0)
    if limit <= 0:
        return None
    stale_seconds = max(int(getattr(settings, "CODEX_RUNNING_GENERATION_STALE_SECONDS", 1800)), 60)
    stale_before = timezone.now() - timedelta(seconds=stale_seconds)
    running_count = GeneratedAnalysisJob.objects.filter(
        user=user,
        status=GeneratedAnalysisJob.Status.RUNNING,
        started_at__gte=stale_before,
    ).count()
    if running_count < limit:
        return None
    return Response(
        {
            "error": "analysis_user_generation_limit",
            "message": "У вас уже выполняется тяжёлый Codex-разбор. Дождитесь результата перед запуском следующего.",
            "running_count": running_count,
            "limit": limit,
            "retry_after_seconds": 60,
        },
        status=429,
    )


def _create_running_generation_job(kind: str, user, data: dict[str, object]) -> GeneratedAnalysisJob | None:
    if user is None:
        return None
    return GeneratedAnalysisJob.objects.create(
        user=user,
        kind=kind,
        status=GeneratedAnalysisJob.Status.RUNNING,
        input_summary=input_summary_from_snapshot(data, kind),
        request_snapshot=data,
        started_at=timezone.now(),
    )


def _create_queued_generation_job(kind: str, user, data: dict[str, object]) -> GeneratedAnalysisJob:
    if user is None:
        raise ValueError("queued Codex generation requires authenticated user")
    return GeneratedAnalysisJob.objects.create(
        user=user,
        kind=kind,
        status=GeneratedAnalysisJob.Status.QUEUED,
        input_summary=input_summary_from_snapshot(data, kind),
        request_snapshot=data,
    )


def _active_generation_job_for_input(kind: str, user, data: dict[str, object]) -> GeneratedAnalysisJob | None:
    if user is None:
        return None
    return (
        GeneratedAnalysisJob.objects.filter(
            user=user,
            kind=kind,
            status__in=[GeneratedAnalysisJob.Status.QUEUED, GeneratedAnalysisJob.Status.RUNNING],
            input_summary=input_summary_from_snapshot(data, kind),
        )
        .order_by("created_at", "id")
        .first()
    )


def _finish_generation_job(job: GeneratedAnalysisJob | None, output: object) -> None:
    if job is None:
        return
    analysis_id = _optional_int(output.get("id") if isinstance(output, dict) else None)
    job.status = GeneratedAnalysisJob.Status.COMPLETE
    job.completed_at = timezone.now()
    if analysis_id is not None and GeneratedAnalysisDraft.objects.filter(id=analysis_id).exists():
        job.analysis_id = analysis_id
    job.save(update_fields=["status", "completed_at", "analysis", "updated_at"])


def _fail_generation_job(job: GeneratedAnalysisJob | None, exc: Exception) -> None:
    if job is None:
        return
    job.status = GeneratedAnalysisJob.Status.FAILED
    job.error = str(exc)[:4000]
    job.completed_at = timezone.now()
    job.save(update_fields=["status", "error", "completed_at", "updated_at"])


def _codex_chat_response(kind: str, user, analysis_id: int, ask):
    lock_key = _codex_chat_lock_key(kind, user, analysis_id)
    lock_seconds = getattr(settings, "CODEX_CHAT_LOCK_SECONDS", 300)
    if not cache.add(lock_key, "running", timeout=lock_seconds):
        return Response(
            {
                "error": "analysis_chat_in_progress",
                "message": (
                    "Codex уже отвечает по этому отчёту. "
                    "Дождитесь ответа, чтобы не запускать второй тяжёлый процесс."
                ),
                "retry_after_seconds": min(lock_seconds, 60),
            },
            status=409,
        )
    try:
        return Response(ask())
    finally:
        cache.delete(lock_key)


def _codex_chat_lock_key(kind: str, user, analysis_id: int) -> str:
    owner = getattr(user, "id", "anonymous") or "anonymous"
    return f"reports:codex-chat-lock:{kind}:{owner}:{analysis_id}"


def _birth_codex_access_response(request, chart_data: dict[str, object], *, force_regenerate: bool) -> Response | None:
    user = _request_user(request)
    if user is None:
        return None
    profile_id = _optional_int(chart_data.get("profile_id"))
    if profile_id is None:
        return Response(
            {
                "error": "profile_id_required",
                "message": "AI-разбор доступен только для сохранённой личной карты. Сохраните карту как «моя карта» или выберите её из профиля.",
            },
            status=400,
        )
    profile = BirthProfile.objects.filter(id=profile_id, user=user).only("id", "display_name", "is_self_profile").first()
    if profile is None:
        return Response({"error": "profile not found"}, status=404)
    if not profile.is_self_profile:
        return Response(
            {
                "error": "payment_required",
                "payment_required": True,
                "billing_scope": "other_profile_ai_analysis",
                "message": "AI-разбор чужой сохранённой карты требует оплаты. Карту можно хранить и смотреть бесплатно.",
                "profile_id": profile.id,
                "profile_label": profile.display_name,
            },
            status=402,
        )
    existing = _latest_birth_codex_for_profile(user, profile.id)
    if existing is None:
        chart_data["billing_context"] = {
            "free_personal_analysis": True,
            "profile_id": profile.id,
            "profile_label": profile.display_name,
        }
        return None
    output = dict(existing.output_json or {})
    output["id"] = existing.id
    output["kind"] = output.get("kind") or existing.kind
    output["review_status"] = output.get("review_status") or existing.review_status
    output["source_policy"] = output.get("source_policy") or existing.source_policy
    output["billing_status"] = "free_personal_analysis_already_used"
    output["billing_message"] = "Первый бесплатный личный AI-разбор уже был создан; возвращён сохранённый отчёт."
    if force_regenerate:
        output["force_regenerate_ignored"] = True
    return Response(output)


def _latest_birth_codex_for_profile(user, profile_id: int) -> GeneratedAnalysisDraft | None:
    return (
        GeneratedAnalysisDraft.objects.filter(
            user=user,
            kind="birth_chart_codex_cli",
            profile_links__profile_id=profile_id,
            profile_links__role="primary",
        )
        .defer("input_snapshot", "packet_snapshot", "output_json", "prompt_markdown")
        .distinct()
        .order_by("-created_at", "-id")
        .first()
    )


def _birth_analysis_data_for_request(request) -> dict[str, object]:
    data = _request_data_dict(request)
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        return data

    profile_id = _optional_int(data.get("profile_id"))
    selected_profile: BirthProfile | None = None
    if profile_id is not None:
        profile = BirthProfile.objects.filter(id=profile_id, user=user).select_related("place").first()
        if profile is not None:
            selected_profile = profile
            data["selected_profile_context"] = _profile_context(profile, viewer_user=user)

    related_ids = _int_list(data.get("related_profile_ids"))
    related_contexts: list[dict[str, object]] = []
    seen_related_profile_ids: set[int] = set()
    selected_profile_id = selected_profile.id if selected_profile is not None else None
    if related_ids:
        profiles = BirthProfile.objects.filter(id__in=related_ids, user=user).select_related("place")
        by_id = {profile.id: profile for profile in profiles}
        for related_id in related_ids:
            if related_id == selected_profile_id or related_id not in by_id or related_id in seen_related_profile_ids:
                continue
            related_contexts.append(_profile_context(by_id[related_id], viewer_user=user))
            seen_related_profile_ids.add(related_id)
    if selected_profile is not None:
        for relationship in _accepted_profile_relationships(user, selected_profile):
            if relationship.related_profile_id in seen_related_profile_ids:
                continue
            context = _profile_context(relationship.related_profile, viewer_user=user)
            context["relationship"] = {
                "role": relationship.role,
                "link_status": relationship.link_status,
                "relationship_id": relationship.id,
                "direction": "accepted",
                "requested_user": relationship.requested_user.username if relationship.requested_user_id else None,
            }
            related_contexts.append(context)
            seen_related_profile_ids.add(relationship.related_profile_id)
    if related_contexts:
        data["related_profile_context"] = related_contexts
    return data


def _compatibility_analysis_data_for_request(request) -> tuple[dict[str, object], Response | None]:
    data = _request_data_dict(request)
    user = _request_user(request)
    if user is None:
        return data, None

    profile_ids: list[int] = []
    for key in ("person_a", "person_b"):
        person = data.get(key)
        if not isinstance(person, dict):
            continue
        profile_id = _optional_int(person.get("profile_id"))
        if profile_id is None:
            continue
        if not BirthProfile.objects.filter(id=profile_id, user=user).exists():
            return data, Response({"error": "profile not found"}, status=404)
        profile_ids.append(profile_id)

    relationship_context, error_response = _trusted_compatibility_relationship_context(
        user,
        data.get("relationship_context"),
        profile_ids,
    )
    if error_response is not None:
        return data, error_response
    if relationship_context:
        data["relationship_context"] = relationship_context
    return data, None


def _trusted_compatibility_relationship_context(user, raw_context: object, profile_ids: list[int]) -> tuple[dict[str, object], Response | None]:
    context = dict(raw_context) if isinstance(raw_context, dict) else {}
    requested_role = str(context.get("role") or BirthProfileRelationship.Role.PARTNER).strip()
    if requested_role not in BirthProfileRelationship.Role.values:
        requested_role = BirthProfileRelationship.Role.OTHER

    relationship = None
    relationship_id = _optional_int(context.get("relationship_id"))
    if relationship_id is not None:
        relationship = (
            BirthProfileRelationship.objects.select_related("requested_user")
            .filter(id=relationship_id, user=user)
            .first()
        )
        if relationship is None:
            return {}, Response({"error": "relationship not found"}, status=404)
    elif len(profile_ids) == 2:
        left, right = profile_ids
        relationship = (
            BirthProfileRelationship.objects.select_related("requested_user")
            .filter(user=user)
            .filter(
                Q(profile_id=left, related_profile_id=right)
                | Q(profile_id=right, related_profile_id=left)
            )
            .order_by("-updated_at")
            .first()
        )

    if relationship is None:
        return {
            "role": requested_role,
            "link_status": BirthProfileRelationship.LinkStatus.PRIVATE,
            "consent_policy": "private_manual_pair_no_registered_link",
        }, None

    return {
        "role": relationship.role,
        "relationship_id": relationship.id,
        "profile_id": relationship.profile_id,
        "related_profile_id": relationship.related_profile_id,
        "link_status": relationship.link_status,
        "requested_user": relationship.requested_user.username if relationship.requested_user_id else None,
        "consent_policy": (
            "registered_user_link_accepted"
            if relationship.link_status == BirthProfileRelationship.LinkStatus.ACCEPTED
            else "private_saved_relation_until_user_link_accepted"
        ),
    }, None


def _accepted_profile_relationships(user, profile: BirthProfile) -> list[BirthProfileRelationship]:
    return list(
        BirthProfileRelationship.objects.filter(
            user=user,
            profile=profile,
            link_status=BirthProfileRelationship.LinkStatus.ACCEPTED,
        )
        .select_related("related_profile", "related_profile__place", "requested_user")
        .order_by("-updated_at")
    )


def _request_data_dict(request) -> dict[str, object]:
    if isinstance(request.data, dict):
        return dict(request.data)
    return {key: request.data.get(key) for key in request.data}


def _profile_context(profile: BirthProfile, *, viewer_user=None) -> dict[str, object]:
    calculation = profile.calculations.filter(status=ChartCalculation.Status.COMPLETE).order_by("-created_at").first()
    if calculation is None:
        calculation = calculate_profile_chart(profile)
    payload = {
        "profile": profile_payload(profile),
        "chart": _compact_chart(calculation.result if calculation.status == ChartCalculation.Status.COMPLETE else {}),
        "calculation_status": calculation.status,
        "calculation_error": calculation.error,
        "latest_reviews": _latest_profile_reviews(profile.id, viewer_user=viewer_user),
    }
    return payload


def _latest_profile_reviews(profile_id: int, *, viewer_user=None) -> list[dict[str, object]]:
    profile = BirthProfile.objects.filter(id=profile_id).only("user_id").first()
    user_id = profile.user_id if profile is not None else None
    records = GeneratedAnalysisDraft.objects.filter(
        kind__in=MAIN_ANALYSIS_KINDS,
        profile_links__profile_id=profile_id,
    ).exclude(kind="current_day_transit_overview")
    if getattr(viewer_user, "is_authenticated", False):
        records = records.filter(Q(user=viewer_user) | Q(user__isnull=True))
    elif user_id is not None:
        records = records.filter(Q(user_id=user_id) | Q(user__isnull=True))
    records = (
        records.defer("input_snapshot", "packet_snapshot", "output_json", "prompt_markdown")
        .distinct()
        .order_by("-created_at")[:3]
    )
    return [
        {
            "id": record.id,
            "kind": record.kind,
            "provider": record.provider,
            "created_at": record.created_at.isoformat(),
            "excerpt": _short_text(record.excerpt, 420),
        }
        for record in records
    ]


def _current_day_overview_output(data: dict[str, object], transit_report: dict[str, object]) -> dict[str, object]:
    transits = transit_report.get("transits") if isinstance(transit_report.get("transits"), list) else []
    slow = [row for row in transits if isinstance(row, dict) and row.get("body") in {"Guru", "Shani", "Rahu", "Ketu"}]
    personal = [row for row in transits if isinstance(row, dict) and row.get("body") in {"Surya", "Chandra", "Mangala", "Budha", "Shukra"}]
    as_of = transit_report.get("as_of") if isinstance(transit_report.get("as_of"), dict) else {}
    return {
        "kind": "current_day_transit_overview",
        "provider": "internal_transit",
        "model": "workflow-v1",
        "engine_label": "Текущий день по транзитам",
        "review_status": "calculation_draft",
        "source_policy": "calculation_first",
        "language": "ru",
        "as_of": as_of,
        "sections": [
            {
                "title": "Фон дня",
                "body": _transit_sentence(as_of, personal[:5]),
                "citation_titles": [],
                "key_points": _transit_points(personal[:5]),
                "practical_steps": ["Сверять выводы с натальной картой и текущими дашами.", "Не делать окончательных решений только по транзиту."],
                "review_notes": ["Это расчётный черновик: публичная интерпретация требует шастра-проверки."],
            },
            {
                "title": "Медленные грахи",
                "body": _transit_sentence(as_of, slow),
                "citation_titles": [],
                "key_points": _transit_points(slow),
                "practical_steps": ["Смотреть дома от лагны и Луны.", "Отмечать повторяющиеся темы, а не разовые страхи."],
                "review_notes": ["Правила гочары ещё находятся в слое teacher-review."],
            },
            {
                "title": "Контекст запроса",
                "body": "Обзор сохранён отдельно, поэтому по нему можно задавать вопросы в истории. Если выбраны связанные карты, их контекст передаётся в AI-запросы личного обзора.",
                "citation_titles": [],
                "key_points": [
                    f"Дата рождения: {data.get('birth_date') or '-'}",
                    f"Текущий момент: {as_of.get('date') or '-'} {as_of.get('time') or ''}",
                ],
                "practical_steps": ["Для точного текста запустить вопрос по этому обзору через Codex CLI."],
                "review_notes": [],
            },
        ],
    }


def _current_day_overview_record_for_request(user, data: dict[str, object]) -> GeneratedAnalysisDraft | None:
    if user is None:
        return None
    target_key = _current_day_history_key(data)
    if not target_key:
        return None
    candidates = (
        GeneratedAnalysisDraft.objects.filter(
            user=user,
            kind="current_day_transit_overview",
            input_summary__as_of_date=target_key.get("as_of_date"),
        )
        .only("id", "input_summary")
        .order_by("-created_at", "-id")[:20]
    )
    for record in candidates:
        if _current_day_history_key(record.input_summary) == target_key:
            return record
    return None


def _current_day_history_key(data: object) -> dict[str, object]:
    summary = input_summary_from_snapshot(data, "current_day_transit_overview") if isinstance(data, dict) else {}
    if not summary.get("as_of_date"):
        return {}
    summary.pop("as_of_time", None)
    return summary


def _compact_chart(chart: object) -> dict[str, object]:
    if not isinstance(chart, dict):
        return {}
    return {
        "birth": chart.get("birth", {}),
        "place": chart.get("place", {}),
        "ascendant": chart.get("ascendant", {}),
        "grahas": chart.get("grahas", [])[:12] if isinstance(chart.get("grahas"), list) else [],
        "houses": chart.get("houses", [])[:12] if isinstance(chart.get("houses"), list) else [],
        "panchanga": chart.get("panchanga", {}),
        "dashas": chart.get("dashas", {}),
    }


def _record_excerpt(record: GeneratedAnalysisDraft) -> str:
    output = record.output_json if isinstance(record.output_json, dict) else {}
    sections = output.get("sections") if isinstance(output.get("sections"), list) else []
    if sections and isinstance(sections[0], dict):
        return _short_text(sections[0].get("body"), 420)
    return _short_text(output.get("answer"), 420)


def _transit_sentence(as_of: dict[str, object], rows: list[object]) -> str:
    points = _transit_points(rows)
    when = f"{as_of.get('date') or '-'} {as_of.get('time') or ''}".strip()
    if not points:
        return f"На {when} транзитные показатели не подготовлены."
    return f"На {when}: " + "; ".join(points) + "."


def _transit_points(rows: list[object]) -> list[str]:
    points = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        house_lagna = row.get("house_from_lagna") or "-"
        house_moon = row.get("house_from_moon") or "-"
        points.append(f"{row.get('body')} в {row.get('rashi')} ({house_lagna} от лагны, {house_moon} от Луны)")
    return points


def _compact_chat_history_items(history: list[dict[str, object]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for item in history[-8:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        content = _short_text(item.get("content"), 1200)
        if role in {"user", "assistant"} and content:
            items.append({"role": role, "content": content})
    return items


def _int_list(value: object) -> list[int]:
    if isinstance(value, list):
        raw_items = value
    else:
        raw_items = str(value or "").split(",")
    result = []
    for item in raw_items:
        parsed = _optional_int(item)
        if parsed is not None and parsed not in result:
            result.append(parsed)
    return result[:12]


def _short_string_list(value: object, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_short_text(item, 300) for item in value[:limit] if _short_text(item, 300)]


def _short_text(value: object, limit: int) -> str:
    text = str(value or "").strip()
    return text if len(text) <= limit else f"{text[:limit].rstrip()}..."


def vl_citation_search(query: str) -> list[dict[str, object]]:
    return combined_citation_search(
        settings.VL_DATABASE_URL,
        query,
        limit=3,
        public_base_url=settings.VL_PUBLIC_BASE_URL,
    )


def _include_prompt(request) -> bool:
    return str(request.query_params.get("include_prompt") or "").lower() in {"1", "true", "yes"}


def _history_kinds(raw_value: object) -> list[str]:
    if not raw_value:
        return sorted(MAIN_ANALYSIS_KINDS)
    requested = [item.strip() for item in str(raw_value).split(",") if item.strip()]
    allowed = [item for item in requested if item in ALL_HISTORY_KINDS]
    return allowed or sorted(MAIN_ANALYSIS_KINDS)


def _optional_int(raw_value: object) -> int | None:
    if raw_value in {None, ""}:
        return None
    try:
        return int(str(raw_value))
    except (TypeError, ValueError):
        return None


def _record_mentions_profile(record: GeneratedAnalysisDraft, profile_id: int) -> bool:
    snapshot = record.input_snapshot if isinstance(record.input_snapshot, dict) else {}
    if snapshot.get("profile_id") == profile_id:
        return True
    for key in ("person_a", "person_b"):
        person = snapshot.get(key)
        if isinstance(person, dict) and person.get("profile_id") == profile_id:
            return True
    related_ids = snapshot.get("related_profile_ids")
    return isinstance(related_ids, list) and profile_id in related_ids


def _chat_counts_for_records(records: list[GeneratedAnalysisDraft], request) -> dict[int, int]:
    user = _request_user(request)
    ids = [record.id for record in records if record.kind in MAIN_ANALYSIS_KINDS]
    if user is None or not ids:
        return {}
    rows = (
        GeneratedAnalysisDraft.objects.filter(
            kind__in=CHAT_ANALYSIS_KINDS,
            user=user,
            parent_analysis_id__in=ids,
        )
        .values("parent_analysis_id")
        .annotate(count=Count("id"))
    )
    counts: dict[int, int] = {}
    for row in rows:
        analysis_id = _optional_int(row.get("parent_analysis_id"))
        if analysis_id is not None:
            counts[analysis_id] = int(row.get("count") or 0)
    return counts


def _analysis_history_payload(record: GeneratedAnalysisDraft, *, include_output: bool = False, chat_count: int | None = None) -> dict[str, object]:
    output = record.output_json if include_output and isinstance(record.output_json, dict) else {}
    input_data = (
        record.input_snapshot
        if include_output and isinstance(record.input_snapshot, dict)
        else record.input_summary if isinstance(record.input_summary, dict) else {}
    )
    payload: dict[str, object] = {
        "id": record.id,
        "slug": _analysis_slug(record, snapshot=input_data),
        "kind": record.kind,
        "provider": record.provider,
        "model": record.model,
        "review_status": record.review_status,
        "source_policy": record.source_policy,
        "engine_label": record.engine_label or (output.get("engine_label") if output else "") or _history_kind_label(record.kind),
        "section_count": record.section_count,
        "created_at": record.created_at.isoformat(),
        "input_summary": input_data,
        "input_snapshot": input_data,
        "chat_count": (chat_count if chat_count is not None else _chat_record_count(record)) if record.kind in MAIN_ANALYSIS_KINDS else 0,
    }
    if record.first_section_title:
        payload["first_section_title"] = record.first_section_title
    if record.excerpt:
        payload["excerpt"] = record.excerpt[:360]
    if include_output:
        payload["output_json"] = output
        payload["packet_snapshot"] = record.packet_snapshot if isinstance(record.packet_snapshot, dict) else {}
        payload["prompt_markdown"] = record.prompt_markdown
    return payload


def _analysis_generation_job_payload(job: GeneratedAnalysisJob) -> dict[str, object]:
    analysis = job.analysis
    return {
        "id": job.id,
        "kind": job.kind,
        "status": job.status,
        "input_summary": job.input_summary if isinstance(job.input_summary, dict) else {},
        "analysis_id": analysis.id if analysis is not None else None,
        "analysis_slug": _analysis_slug(analysis, snapshot=analysis.input_summary) if analysis is not None else "",
        "error": job.error,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }


def _analysis_slug(record: GeneratedAnalysisDraft, *, snapshot: dict[str, object] | None = None) -> str:
    snapshot = snapshot if isinstance(snapshot, dict) else record.input_snapshot if isinstance(record.input_snapshot, dict) else {}
    prefix = "compatibility" if record.kind.startswith("compatibility") else "today" if record.kind.startswith("current_day") else "birth"
    provider = _slug_part(record.provider or record.kind.replace("_", "-"))
    if record.kind in CHAT_ANALYSIS_KINDS:
        analysis_id = snapshot.get("analysis_id") or "analysis"
        return _join_slug_parts("chat", str(analysis_id), provider, str(record.id))
    if prefix == "compatibility":
        person_a = snapshot.get("person_a") if isinstance(snapshot.get("person_a"), dict) else {}
        person_b = snapshot.get("person_b") if isinstance(snapshot.get("person_b"), dict) else {}
        return _join_slug_parts(
            "compatibility",
            _date_time_slug(person_a),
            _date_time_slug(person_b),
            provider,
            str(record.id),
        )
    if prefix == "today":
        return _join_slug_parts("today", _date_time_slug(snapshot), provider, str(record.id))
    return _join_slug_parts("birth", _date_time_slug(snapshot), provider, str(record.id))


def _date_time_slug(snapshot: dict[str, object]) -> str:
    date = _slug_part(str(snapshot.get("birth_date") or "date"))
    time = _slug_part(str(snapshot.get("birth_time") or "").replace(":", "")) or "time"
    place = _slug_part(str(snapshot.get("place_name") or snapshot.get("place_id") or "place"))
    return _join_slug_parts(date, time, place)


def _join_slug_parts(*parts: str) -> str:
    return "-".join(part for part in (_slug_part(part) for part in parts) if part)


def _slug_part(value: str) -> str:
    value = value.strip().lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9а-яё-]+", "-", value)
    return re.sub(r"-{2,}", "-", value).strip("-")[:80]


def _analysis_id_from_slug(value: str) -> int | None:
    match = re.search(r"(\d+)$", value.strip())
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _history_kind_label(kind: str) -> str:
    extra_labels = {
        "current_day_transit_overview": "Текущий день",
        "current_day_transit_overview_chat": "Диалог по текущему дню",
    }
    if kind in extra_labels:
        return extra_labels[kind]
    return {
        "birth_chart_codex_cli": "Codex личный обзор",
        "compatibility_codex_cli": "Codex совместимость",
        "birth_chart_codex_cli_chat": "Диалог по личному обзору",
        "compatibility_codex_cli_chat": "Диалог по совместимости",
    }.get(kind, kind)


def _chat_record_count(record: GeneratedAnalysisDraft) -> int:
    count = GeneratedAnalysisDraft.objects.filter(
        kind__in=CHAT_ANALYSIS_KINDS,
        parent_analysis=record,
        user_id=record.user_id,
    ).count()
    if count:
        return count
    return GeneratedAnalysisDraft.objects.filter(
        kind__in=CHAT_ANALYSIS_KINDS,
        parent_analysis__isnull=True,
        input_snapshot__analysis_id=record.id,
        user_id=record.user_id,
    ).count()


def _chat_history_payload(record: GeneratedAnalysisDraft, *, messages_key: str = "chat_messages") -> dict[str, object]:
    total = _chat_record_count(record)
    return {
        messages_key: _chat_messages_for_analysis(record, limit=CHAT_HISTORY_RECORD_LIMIT),
        "chat_record_total": total,
        "chat_record_limit": CHAT_HISTORY_RECORD_LIMIT,
        "chat_truncated": total > CHAT_HISTORY_RECORD_LIMIT,
    }


def _chat_messages_for_analysis(record: GeneratedAnalysisDraft, *, limit: int = CHAT_HISTORY_RECORD_LIMIT) -> list[dict[str, object]]:
    records_qs = GeneratedAnalysisDraft.objects.filter(
        kind__in=CHAT_ANALYSIS_KINDS,
        parent_analysis=record,
        user_id=record.user_id,
    ).only("id", "input_snapshot", "output_json", "created_at").order_by("-created_at", "-id")
    records = list(records_qs[:limit])
    if not records:
        records_qs = GeneratedAnalysisDraft.objects.filter(
            kind__in=CHAT_ANALYSIS_KINDS,
            parent_analysis__isnull=True,
            input_snapshot__analysis_id=record.id,
            user_id=record.user_id,
        ).only("id", "input_snapshot", "output_json", "created_at").order_by("-created_at", "-id")
        records = list(records_qs[:limit])
    records.reverse()
    messages: list[dict[str, object]] = []
    for record in records:
        snapshot = record.input_snapshot if isinstance(record.input_snapshot, dict) else {}
        output = record.output_json if isinstance(record.output_json, dict) else {}
        question = str(output.get("question") or snapshot.get("question") or "").strip()
        answer = str(output.get("answer") or "").strip()
        if question:
            messages.append(
                {
                    "role": "user",
                    "content": question,
                    "analysis_message_id": record.id,
                    "created_at": record.created_at.isoformat(),
                }
            )
        if answer:
            messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "analysis_message_id": record.id,
                    "created_at": record.created_at.isoformat(),
                }
            )
    return messages
