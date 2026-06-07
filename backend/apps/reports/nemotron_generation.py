from __future__ import annotations

import json
from typing import Any, Callable
from urllib import error, request

from django.conf import settings

from apps.calculations.ephemeris import EphemerisProvider
from apps.interpretations.evidence_matcher import build_shastra_evidence

from .analysis_packet import build_analysis_packet
from .birth_report import CitationSearch, InterpretationProvider
from .codex_cli_generation import (
    _coverage_status,
    _record_packet_snapshot,
    _review_status,
    _source_policy,
)
from .deepseek_generation import _deepseek_overview_packet, _normalize_deepseek_output
from .draft_generation import DraftGenerationUnavailable
from .models import GeneratedAnalysisDraft

NemotronRunner = Callable[[str], dict[str, Any] | str]
NEMOTRON_PROMPT_VERSION = "nemotron-overview-v1"

NEMOTRON_CACHE_KEYS = (
    "birth_date",
    "birth_time",
    "gender",
    "timezone",
    "latitude",
    "longitude",
    "zodiac",
    "calculation_model",
    "ayanamsa",
    "node_type",
    "ephemeris",
    "house_system",
    "bhava_system",
    "varga_scheme",
    "sunrise_source",
    "timezone_source",
    "shadbala_profile",
)


def generate_birth_chart_nemotron_analysis(
    data: dict[str, Any],
    *,
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: CitationSearch | None = None,
    interpretation_provider: InterpretationProvider | None = None,
    nemotron_runner: NemotronRunner | None = None,
    refresh_evidence: bool = True,
    private_research_mode: bool = True,
) -> dict[str, Any]:
    if provider is None and nemotron_runner is None:
        cached_output = _cached_nemotron_analysis(data)
        if cached_output is not None:
            return cached_output
    if refresh_evidence:
        build_shastra_evidence()
    packet = build_analysis_packet(
        data,
        provider=provider,
        citation_search=citation_search,
        research_search=research_search,
        interpretation_provider=interpretation_provider,
        include_prompt=False,
    )
    prompt = render_nemotron_analysis_prompt(packet, private_research_mode=private_research_mode)
    runner = nemotron_runner or nemotron_chat_completions_client()
    output = _normalize_deepseek_output(runner(prompt))
    output["coverage_status"] = _coverage_status(output, private_research_mode)
    output["review_status"] = _review_status(private_research_mode, output)
    output["source_policy"] = _source_policy(private_research_mode)
    output["kind"] = "birth_chart_nemotron"
    output["provider"] = "nemotron"
    output["model"] = settings.NEMOTRON_MODEL
    output["prompt_version"] = NEMOTRON_PROMPT_VERSION
    output["engine_label"] = "Сгенерировано с помощью Nemotron"

    record = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_nemotron",
        review_status=output["review_status"],
        source_policy=output["source_policy"],
        provider="nemotron",
        model=settings.NEMOTRON_MODEL,
        input_snapshot=data,
        packet_snapshot=_record_packet_snapshot(packet),
        output_json=output,
        prompt_markdown=prompt,
    )
    output["id"] = record.id
    return output


def _cached_nemotron_analysis(data: dict[str, Any]) -> dict[str, Any] | None:
    for record in GeneratedAnalysisDraft.objects.filter(kind="birth_chart_nemotron").order_by("-id")[:10]:
        if not _nemotron_cache_input_matches(record.input_snapshot, data):
            continue
        output = dict(record.output_json or {})
        if output.get("prompt_version") != NEMOTRON_PROMPT_VERSION:
            continue
        output["coverage_status"] = _coverage_status(output, True)
        output["review_status"] = _review_status(True, output)
        output["source_policy"] = output.get("source_policy") or record.source_policy
        output["kind"] = output.get("kind") or record.kind
        output["provider"] = output.get("provider") or record.provider or "nemotron"
        output["model"] = output.get("model") or record.model
        output["prompt_version"] = output.get("prompt_version") or NEMOTRON_PROMPT_VERSION
        output["engine_label"] = output.get("engine_label") or "Сгенерировано с помощью Nemotron"
        output["id"] = record.id
        return output
    return None


def _nemotron_cache_input_matches(snapshot: object, data: dict[str, Any]) -> bool:
    if not isinstance(snapshot, dict):
        return False
    for key in NEMOTRON_CACHE_KEYS:
        if key not in snapshot or key not in data:
            return False
        if key in {"latitude", "longitude"}:
            try:
                if abs(float(snapshot[key]) - float(data[key])) > 0.0001:
                    return False
            except (TypeError, ValueError):
                return False
        elif snapshot.get(key) != data.get(key):
            return False
    return True


def render_nemotron_analysis_prompt(packet: dict[str, Any], *, private_research_mode: bool = True) -> str:
    source_policy = "private_shastra_research_first" if private_research_mode else "citation_first"
    return (
        "Ты Nemotron внутри jyotish-agent. Не редактируй файлы и не запускай команды.\n"
        "Сделай короткий русский обзор натальной карты, а не полный финальный отчёт.\n"
        "Опирайся только на факты и источники из JSON ниже. Не выдумывай цитаты, номера стихов или ссылки.\n"
        "Не давай фатальных обещаний и не советуй independent demigod worship.\n"
        "Если remedial вывод связан с грахами, формулируй через прибежище у Кришны, садхану, служение вайшнавам и наставления Шрилы Прабхупады.\n"
        f"source_policy={source_policy}; review_status должен оставаться draft/private_partial до проверки человеком.\n\n"
        "OUTPUT JSON schema:\n"
        "{\n"
        '  "review_status": "private_partial",\n'
        '  "language": "ru",\n'
        '  "sections": [\n'
        "    {\n"
        '      "title": "string",\n'
        '      "body": "string",\n'
        '      "citation_titles": ["string"],\n'
        '      "key_points": ["string"],\n'
        '      "practical_steps": ["string"],\n'
        '      "review_notes": ["string"]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Сделай 5-8 sections: главное, характер/дхарма, работа/деньги, отношения, здоровье/риски осторожно, духовная практика, что проверить в PL/JHora.\n\n"
        "OVERVIEW PACKET JSON:\n"
        "```json\n"
        f"{json.dumps(_deepseek_overview_packet(packet), ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def nemotron_chat_completions_client() -> NemotronRunner:
    endpoint = f"{settings.OPENROUTER_API_BASE_URL}/chat/completions"
    model = settings.NEMOTRON_MODEL

    def _client(prompt: str) -> str:
        if not settings.OPENROUTER_API_KEY:
            raise DraftGenerationUnavailable("OPENROUTER_API_KEY is missing")
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Ты Nemotron, рабочий помощник jyotish-agent. Отвечай только валидным JSON по схеме пользователя.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": settings.NEMOTRON_MAX_TOKENS,
            "temperature": 0.2,
            "stream": False,
        }
        api_request = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=_openrouter_headers(),
            method="POST",
        )
        try:
            with request.urlopen(api_request, timeout=settings.NEMOTRON_TIMEOUT_SECONDS) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise DraftGenerationUnavailable(f"Nemotron API returned {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise DraftGenerationUnavailable(f"Nemotron API unavailable: {exc}") from exc
        except TimeoutError as exc:
            raise DraftGenerationUnavailable("Nemotron API timed out") from exc
        return _extract_nemotron_text(response_payload)

    return _client


def _openrouter_headers() -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if settings.OPENROUTER_HTTP_REFERER:
        headers["HTTP-Referer"] = settings.OPENROUTER_HTTP_REFERER
    if settings.OPENROUTER_APP_TITLE:
        headers["X-OpenRouter-Title"] = settings.OPENROUTER_APP_TITLE
    return headers


def _extract_nemotron_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first.get("text"), str):
                return first["text"]
    raise DraftGenerationUnavailable("Nemotron response did not include text output")
