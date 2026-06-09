from __future__ import annotations

import re

from django.conf import settings
from django.shortcuts import get_object_or_404
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
from .deepseek_generation import generate_birth_chart_deepseek_analysis
from .models import GeneratedAnalysisDraft
from .nemotron_generation import generate_birth_chart_nemotron_analysis
from .qwen_generation import generate_birth_chart_qwen_analysis


MAIN_ANALYSIS_KINDS = {
    "birth_chart_codex_cli",
    "birth_chart_qwen",
    "birth_chart_deepseek",
    "birth_chart_nemotron",
    "compatibility_codex_cli",
}
CHAT_ANALYSIS_KINDS = {
    "birth_chart_codex_cli_chat",
    "compatibility_codex_cli_chat",
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


class BirthQwenAnalysisView(APIView):
    permission_classes = [PrivateAppAccess]

    def post(self, request):
        try:
            return Response(
                generate_birth_chart_qwen_analysis(
                    request.data,
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
            return Response(
                generate_birth_chart_deepseek_analysis(
                    request.data,
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
            return Response(
                generate_birth_chart_nemotron_analysis(
                    request.data,
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
    prefix = "compatibility" if record.kind.startswith("compatibility") else "birth"
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
