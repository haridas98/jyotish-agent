from __future__ import annotations

import json
import re

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import PrivateAppAccess
from apps.calculations.chart import ChartInputError
from apps.calculations.ephemeris import EphemerisUnavailable
from apps.calculations.workflows import build_transit_report
from apps.charts.models import BirthProfile, ChartCalculation
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
    generate_birth_chart_codex_cli_analysis,
    generate_compatibility_codex_cli_analysis,
)
from .draft_generation import DraftGenerationUnavailable, _normalize_llm_output, generate_birth_chart_draft_analysis
from .deepseek_generation import free_deepseek_chat_client, generate_birth_chart_deepseek_analysis
from .models import GeneratedAnalysisDraft
from .nemotron_generation import generate_birth_chart_nemotron_analysis
from .qwen_generation import generate_birth_chart_qwen_analysis, qwen_chat_completions_client


MAIN_ANALYSIS_KINDS = {
    "birth_chart_codex_cli",
    "birth_chart_qwen",
    "birth_chart_deepseek",
    "birth_chart_nemotron",
    "current_day_transit_overview",
    "compatibility_codex_cli",
}
CHAT_ANALYSIS_KINDS = {
    "birth_chart_codex_cli_chat",
    "birth_chart_qwen_chat",
    "birth_chart_deepseek_chat",
    "current_day_qwen_chat",
    "current_day_deepseek_chat",
    "compatibility_codex_cli_chat",
    "compatibility_qwen_chat",
    "compatibility_deepseek_chat",
}
ALL_HISTORY_KINDS = MAIN_ANALYSIS_KINDS | CHAT_ANALYSIS_KINDS


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


class AnalysisHistoryView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request):
        kinds = _history_kinds(request.query_params.get("kind"))
        profile_id = _optional_int(request.query_params.get("profile_id"))
        limit = min(max(_optional_int(request.query_params.get("limit")) or 20, 1), 100)
        records = GeneratedAnalysisDraft.objects.filter(kind__in=kinds).order_by("-created_at")[:200]
        items = []
        for record in records:
            if profile_id is not None and not _record_mentions_profile(record, profile_id):
                continue
            items.append(_analysis_history_payload(record))
            if len(items) >= limit:
                break
        return Response({"items": items})


class AnalysisHistoryDetailView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request, analysis_id: int):
        record = get_object_or_404(GeneratedAnalysisDraft, id=analysis_id, kind__in=ALL_HISTORY_KINDS)
        return Response(
            {
                "analysis": _analysis_history_payload(record, include_output=True),
                "chat_messages": _chat_messages_for_analysis(record.id),
            }
        )


class AnalysisHistorySlugDetailView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request, analysis_slug: str):
        analysis_id = _analysis_id_from_slug(analysis_slug)
        if analysis_id is None:
            return Response({"error": "analysis slug must end with numeric id"}, status=404)
        record = get_object_or_404(GeneratedAnalysisDraft, id=analysis_id, kind__in=ALL_HISTORY_KINDS)
        return Response(
            {
                "analysis": _analysis_history_payload(record, include_output=True),
                "chat_messages": _chat_messages_for_analysis(record.id),
            }
        )


class AnalysisChatHistoryView(APIView):
    permission_classes = [PrivateAppAccess]

    def get(self, request, analysis_id: int):
        get_object_or_404(GeneratedAnalysisDraft, id=analysis_id, kind__in=MAIN_ANALYSIS_KINDS)
        return Response({"analysis_id": analysis_id, "messages": _chat_messages_for_analysis(analysis_id)})


class AnalysisUniversalChatView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            analysis_id = int(request.data.get("analysis_id") or 0)
            provider = str(request.data.get("provider") or "qwen").strip().lower()
            return Response(
                ask_saved_analysis(
                    analysis_id=analysis_id,
                    provider=provider,
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
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            data = _birth_analysis_data_for_request(request)
            return Response(
                generate_birth_chart_draft_analysis(
                    data,
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
            chart_data = _birth_analysis_data_for_request(request)
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


class BirthQwenAnalysisView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            data = _birth_analysis_data_for_request(request)
            return Response(
                generate_birth_chart_qwen_analysis(
                    data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                    refresh_evidence=False,
                )
            )
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except (EphemerisUnavailable, DraftGenerationUnavailable) as exc:
            return Response({"error": str(exc)}, status=503)


class BirthDeepseekAnalysisView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            data = _birth_analysis_data_for_request(request)
            return Response(
                generate_birth_chart_deepseek_analysis(
                    data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                    refresh_evidence=False,
                )
            )
        except ChartInputError as exc:
            return Response({"error": str(exc)}, status=400)
        except (EphemerisUnavailable, DraftGenerationUnavailable) as exc:
            return Response({"error": str(exc)}, status=503)


class BirthNemotronAnalysisView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        if not getattr(settings, "NEMOTRON_ANALYSIS_ENABLED", False):
            return Response({"error": "Nemotron analysis is disabled"}, status=404)
        try:
            data = _birth_analysis_data_for_request(request)
            return Response(
                generate_birth_chart_nemotron_analysis(
                    data,
                    citation_search=vl_citation_search,
                    research_search=local_research_corpus_search,
                    interpretation_provider=public_interpretation_sections_for_chart,
                    refresh_evidence=False,
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


class BirthCurrentDayOverviewView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            data = _birth_analysis_data_for_request(request)
            now = timezone.localtime()
            data.setdefault("as_of_date", now.date().isoformat())
            data.setdefault("as_of_time", now.time().isoformat(timespec="minutes"))
            transit_report = build_transit_report(data)
            output = _current_day_overview_output(data, transit_report)
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
            )
            output["id"] = record.id
            return Response(output)
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


def ask_saved_analysis(
    *,
    analysis_id: int,
    provider: str,
    question: str,
    history: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    report = GeneratedAnalysisDraft.objects.get(id=analysis_id, kind__in=MAIN_ANALYSIS_KINDS)
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("question is required")

    if provider in {"codex", "codex_cli"}:
        if report.kind == "birth_chart_codex_cli":
            return ask_birth_chart_codex_cli_analysis(
                analysis_id=analysis_id,
                question=clean_question,
                history=history or [],
            )
        if report.kind == "compatibility_codex_cli":
            return ask_compatibility_codex_cli_analysis(
                analysis_id=analysis_id,
                question=clean_question,
                history=history or [],
            )
        raise ValueError("Codex chat is available only for Codex reports")

    if provider in {"qwen", "qwen_chat"}:
        runner = qwen_chat_completions_client()
        provider_name = "qwen"
        model_name = settings.QWEN_MODEL
    elif provider in {"deepseek", "free_deepseek"}:
        runner = free_deepseek_chat_client()
        provider_name = "free_deepseek"
        model_name = settings.FREE_DEEPSEEK_MODEL
    else:
        raise ValueError("provider must be codex, qwen, or deepseek")

    prompt = _saved_analysis_chat_prompt(report, clean_question, history=history or [], provider=provider_name)
    output = _normalize_llm_output(runner(prompt))
    answer = str(output.get("answer") or "").strip() or _fallback_answer(output)
    result = {
        "kind": _chat_kind_for(report.kind, provider_name),
        "analysis_id": report.id,
        "question": clean_question,
        "answer": answer,
        "language": output.get("language", "ru"),
        "review_status": "private_final",
        "source_policy": report.source_policy or "private_shastra_research_first",
        "evidence_references": output.get("evidence_references", []),
        "source_traces": output.get("source_traces", []),
        "history_used": len(_compact_chat_history_items(history or [])),
    }
    record = GeneratedAnalysisDraft.objects.create(
        kind=str(result["kind"]),
        review_status="private_final",
        source_policy=str(result["source_policy"]),
        provider=provider_name,
        model=model_name,
        input_snapshot={
            "analysis_id": report.id,
            "question": clean_question,
            "history": _compact_chat_history_items(history or []),
        },
        packet_snapshot={"analysis": _compact_saved_analysis_for_chat(report)},
        output_json=result,
        prompt_markdown=prompt,
    )
    result["id"] = record.id
    return result


def _birth_analysis_data_for_request(request) -> dict[str, object]:
    data = _request_data_dict(request)
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        return data

    profile_id = _optional_int(data.get("profile_id"))
    if profile_id is not None:
        profile = BirthProfile.objects.filter(id=profile_id, user=user).select_related("place").first()
        if profile is not None:
            data["selected_profile_context"] = _profile_context(profile)

    related_ids = _int_list(data.get("related_profile_ids"))
    if related_ids:
        profiles = BirthProfile.objects.filter(id__in=related_ids, user=user).select_related("place")
        by_id = {profile.id: profile for profile in profiles}
        data["related_profile_context"] = [
            _profile_context(by_id[profile_id])
            for profile_id in related_ids
            if profile_id in by_id
        ]
    return data


def _request_data_dict(request) -> dict[str, object]:
    if isinstance(request.data, dict):
        return dict(request.data)
    return {key: request.data.get(key) for key in request.data}


def _profile_context(profile: BirthProfile) -> dict[str, object]:
    calculation = profile.calculations.filter(status=ChartCalculation.Status.COMPLETE).order_by("-created_at").first()
    if calculation is None:
        calculation = calculate_profile_chart(profile)
    payload = {
        "profile": profile_payload(profile),
        "chart": _compact_chart(calculation.result if calculation.status == ChartCalculation.Status.COMPLETE else {}),
        "calculation_status": calculation.status,
        "calculation_error": calculation.error,
        "latest_reviews": _latest_profile_reviews(profile.id),
    }
    return payload


def _latest_profile_reviews(profile_id: int) -> list[dict[str, object]]:
    records = (
        GeneratedAnalysisDraft.objects.filter(kind__in=MAIN_ANALYSIS_KINDS, input_snapshot__profile_id=profile_id)
        .exclude(kind="current_day_transit_overview")
        .order_by("-created_at")[:3]
    )
    return [
        {
            "id": record.id,
            "kind": record.kind,
            "provider": record.provider,
            "created_at": record.created_at.isoformat(),
            "excerpt": _record_excerpt(record),
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
                "practical_steps": ["Для точного текста запустить вопрос по этому обзору через Qwen или DeepSeek."],
                "review_notes": [],
            },
        ],
    }


def _saved_analysis_chat_prompt(
    report: GeneratedAnalysisDraft,
    question: str,
    *,
    history: list[dict[str, object]],
    provider: str,
) -> str:
    return (
        f"You are {provider} inside jyotish-agent. Return only valid JSON.\n"
        "Answer in Russian to the user's question using the saved Jyotish analysis JSON below.\n"
        "Do not invent citations, verse numbers, or fatalistic guarantees. If data is missing, say what is missing.\n"
        "Keep practical advice Krishna-centered and non-medical/non-legal/non-financial.\n\n"
        'OUTPUT JSON schema: {"answer":"string","evidence_references":["string"],"source_traces":[]}\n\n'
        f"QUESTION:\n{question}\n\n"
        "CHAT HISTORY JSON:\n"
        f"{json.dumps(_compact_chat_history_items(history), ensure_ascii=False, indent=2)}\n\n"
        "SAVED ANALYSIS JSON:\n"
        f"{json.dumps(_compact_saved_analysis_for_chat(report), ensure_ascii=False, indent=2)}\n"
    )


def _compact_saved_analysis_for_chat(report: GeneratedAnalysisDraft) -> dict[str, object]:
    output = report.output_json if isinstance(report.output_json, dict) else {}
    packet = report.packet_snapshot if isinstance(report.packet_snapshot, dict) else {}
    sections = output.get("sections") if isinstance(output.get("sections"), list) else []
    return {
        "id": report.id,
        "kind": report.kind,
        "provider": report.provider,
        "model": report.model,
        "review_status": report.review_status,
        "source_policy": report.source_policy,
        "input_snapshot": report.input_snapshot if isinstance(report.input_snapshot, dict) else {},
        "sections": [
            {
                "title": section.get("title"),
                "body": _short_text(section.get("body"), 1800),
                "key_points": _short_string_list(section.get("key_points"), limit=6),
                "practical_steps": _short_string_list(section.get("practical_steps"), limit=6),
                "review_notes": _short_string_list(section.get("review_notes"), limit=6),
            }
            for section in sections[:12]
            if isinstance(section, dict)
        ],
        "packet_context": _compact_packet_context(packet),
    }


def _compact_packet_context(packet: dict[str, object]) -> dict[str, object]:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}
    transit_report = packet.get("transit_report") if isinstance(packet.get("transit_report"), dict) else {}
    return {
        "birth": context.get("birth", {}),
        "place": context.get("place", {}),
        "selected_profile_context": context.get("selected_profile_context", {}),
        "related_profile_context": context.get("related_profile_context", []),
        "current_period_context": context.get("current_period_context", {}),
        "transit_report": transit_report,
    }


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


def _chat_kind_for(report_kind: str, provider: str) -> str:
    suffix = "deepseek" if provider == "free_deepseek" else "qwen"
    if report_kind.startswith("compatibility"):
        return f"compatibility_{suffix}_chat"
    if report_kind.startswith("current_day"):
        return f"current_day_{suffix}_chat"
    return f"birth_chart_{suffix}_chat"


def _fallback_answer(output: dict[str, object]) -> str:
    sections = output.get("sections")
    if isinstance(sections, list) and sections:
        first = sections[0]
        if isinstance(first, dict):
            return str(first.get("body") or first.get("answer") or "").strip()
    return ""


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


def _analysis_history_payload(record: GeneratedAnalysisDraft, *, include_output: bool = False) -> dict[str, object]:
    output = record.output_json if isinstance(record.output_json, dict) else {}
    sections = output.get("sections") if isinstance(output.get("sections"), list) else []
    payload: dict[str, object] = {
        "id": record.id,
        "slug": _analysis_slug(record),
        "kind": record.kind,
        "provider": record.provider,
        "model": record.model,
        "review_status": record.review_status,
        "source_policy": record.source_policy,
        "engine_label": output.get("engine_label") or _history_kind_label(record.kind),
        "section_count": len(sections),
        "created_at": record.created_at.isoformat(),
        "input_snapshot": record.input_snapshot if isinstance(record.input_snapshot, dict) else {},
        "chat_count": _chat_record_count(record.id) if record.kind in MAIN_ANALYSIS_KINDS else 0,
    }
    if sections and isinstance(sections[0], dict):
        payload["first_section_title"] = sections[0].get("title") or ""
        payload["excerpt"] = str(sections[0].get("body") or "")[:360]
    elif record.kind in CHAT_ANALYSIS_KINDS:
        payload["excerpt"] = str(output.get("answer") or "")[:360]
    if include_output:
        payload["output_json"] = output
        payload["prompt_markdown"] = record.prompt_markdown
    return payload


def _analysis_slug(record: GeneratedAnalysisDraft) -> str:
    snapshot = record.input_snapshot if isinstance(record.input_snapshot, dict) else {}
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
        "birth_chart_qwen_chat": "QWEN диалог по личному обзору",
        "birth_chart_deepseek_chat": "DeepSeek диалог по личному обзору",
        "current_day_qwen_chat": "QWEN диалог по текущему дню",
        "current_day_deepseek_chat": "DeepSeek диалог по текущему дню",
        "compatibility_qwen_chat": "QWEN диалог по совместимости",
        "compatibility_deepseek_chat": "DeepSeek диалог по совместимости",
    }
    if kind in extra_labels:
        return extra_labels[kind]
    return {
        "birth_chart_codex_cli": "Codex личный обзор",
        "birth_chart_qwen": "QWEN личный обзор",
        "birth_chart_deepseek": "DeepSeek личный обзор",
        "birth_chart_nemotron": "Nemotron личный обзор",
        "compatibility_codex_cli": "Codex совместимость",
        "birth_chart_codex_cli_chat": "Диалог по личному обзору",
        "compatibility_codex_cli_chat": "Диалог по совместимости",
    }.get(kind, kind)


def _chat_record_count(analysis_id: int) -> int:
    return GeneratedAnalysisDraft.objects.filter(kind__in=CHAT_ANALYSIS_KINDS, input_snapshot__analysis_id=analysis_id).count()


def _chat_messages_for_analysis(analysis_id: int) -> list[dict[str, object]]:
    records = GeneratedAnalysisDraft.objects.filter(
        kind__in=CHAT_ANALYSIS_KINDS,
        input_snapshot__analysis_id=analysis_id,
    ).order_by("created_at", "id")
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
