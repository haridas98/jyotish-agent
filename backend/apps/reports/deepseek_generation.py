from __future__ import annotations

import json
import re
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
from .draft_generation import DraftGenerationUnavailable, _normalize_llm_output
from .models import GeneratedAnalysisDraft

DeepseekRunner = Callable[[str], dict[str, Any] | str]
DEEPSEEK_PROMPT_VERSION = "deepseek-overview-v1"

DEEPSEEK_CACHE_KEYS = (
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


def generate_birth_chart_deepseek_analysis(
    data: dict[str, Any],
    *,
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: CitationSearch | None = None,
    interpretation_provider: InterpretationProvider | None = None,
    deepseek_runner: DeepseekRunner | None = None,
    refresh_evidence: bool = True,
    private_research_mode: bool = True,
) -> dict[str, Any]:
    if provider is None and deepseek_runner is None:
        cached_output = _cached_deepseek_analysis(data)
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
    prompt = render_deepseek_analysis_prompt(packet, private_research_mode=private_research_mode)
    runner = deepseek_runner or free_deepseek_chat_client()
    output = _normalize_deepseek_output(runner(prompt))
    output["coverage_status"] = _coverage_status(output, private_research_mode)
    output["review_status"] = _review_status(private_research_mode, output)
    output["source_policy"] = _source_policy(private_research_mode)
    output["kind"] = "birth_chart_deepseek"
    output["provider"] = "free_deepseek"
    output["model"] = settings.FREE_DEEPSEEK_MODEL
    output["prompt_version"] = DEEPSEEK_PROMPT_VERSION
    output["engine_label"] = "Сгенерировано с помощью DeepSeek"

    record = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_deepseek",
        review_status=output["review_status"],
        source_policy=output["source_policy"],
        provider="free_deepseek",
        model=settings.FREE_DEEPSEEK_MODEL,
        input_snapshot=data,
        packet_snapshot=_record_packet_snapshot(packet),
        output_json=output,
        prompt_markdown=prompt,
    )
    output["id"] = record.id
    return output


def _cached_deepseek_analysis(data: dict[str, Any]) -> dict[str, Any] | None:
    for record in GeneratedAnalysisDraft.objects.filter(kind="birth_chart_deepseek").order_by("-id")[:10]:
        if not _deepseek_cache_input_matches(record.input_snapshot, data):
            continue
        output = dict(record.output_json or {})
        if output.get("prompt_version") != DEEPSEEK_PROMPT_VERSION:
            continue
        output["coverage_status"] = _coverage_status(output, True)
        output["review_status"] = _review_status(True, output)
        output["source_policy"] = output.get("source_policy") or record.source_policy
        output["kind"] = output.get("kind") or record.kind
        output["provider"] = output.get("provider") or record.provider or "free_deepseek"
        output["model"] = output.get("model") or record.model
        output["prompt_version"] = output.get("prompt_version") or DEEPSEEK_PROMPT_VERSION
        output["engine_label"] = output.get("engine_label") or "Сгенерировано с помощью DeepSeek"
        output["id"] = record.id
        return output
    return None


def _deepseek_cache_input_matches(snapshot: object, data: dict[str, Any]) -> bool:
    if not isinstance(snapshot, dict):
        return False
    for key in DEEPSEEK_CACHE_KEYS:
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
    for key in ("profile_id", "related_profile_ids"):
        if snapshot.get(key) or data.get(key):
            if snapshot.get(key) != data.get(key):
                return False
    return True


def render_deepseek_analysis_prompt(packet: dict[str, Any], *, private_research_mode: bool = True) -> str:
    source_policy = "private_shastra_research_first" if private_research_mode else "citation_first"
    return (
        "Ты DeepSeek внутри jyotish-agent. Не редактируй файлы и не запускай команды.\n"
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


def _deepseek_overview_packet(packet: dict[str, Any]) -> dict[str, Any]:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}
    chart = context.get("chart") if isinstance(context.get("chart"), dict) else {}
    return {
        "schema_version": packet.get("schema_version"),
        "status": packet.get("status"),
        "birth": context.get("birth"),
        "place": context.get("place"),
        "settings": context.get("settings"),
        "grahas": [_compact_graha(graha) for graha in _limit_list(chart.get("grahas", []), 12)],
        "houses": _limit_list(chart.get("houses", []), 12),
        "dashas": _compact_dashas(chart.get("dashas")),
        "person_summary": _compact_person_summary(context.get("person_summary", {})),
        "selected_profile_context": context.get("selected_profile_context", {}),
        "related_profile_context": context.get("related_profile_context", []),
        "current_period_context": context.get("current_period_context", {}),
        "baseline_sections": [_compact_section(section) for section in _limit_list(context.get("sections", []), 12)],
        "approved_shastra_citations": context.get("approved_shastra_citations", []),
        "shastra_source_traces": _compact_source_traces(context.get("shastra_source_traces")),
        "citations": _limit_list(packet.get("citations", []), 24),
    }


def _limit_list(value: Any, limit: int) -> list[Any]:
    return value[:limit] if isinstance(value, list) else []


def _compact_graha(graha: Any) -> dict[str, Any]:
    if not isinstance(graha, dict):
        return {}
    keys = (
        "body",
        "longitude",
        "rashi",
        "rashi_index",
        "nakshatra",
        "nakshatra_index",
        "pada",
        "navamsa",
        "navamsa_index",
        "speed_longitude",
    )
    return {key: graha.get(key) for key in keys if key in graha}


def _compact_dashas(dashas: Any) -> dict[str, Any]:
    if not isinstance(dashas, dict):
        return {}
    vimshottari = dashas.get("vimshottari") if isinstance(dashas.get("vimshottari"), dict) else {}
    return {"vimshottari": {"mahadashas": _limit_list(vimshottari.get("mahadashas", []), 8)}}


def _compact_person_summary(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {
        "birth_context": value.get("birth_context"),
        "core_factors": value.get("core_factors"),
        "graha_houses": value.get("graha_houses"),
        "houses": value.get("houses"),
        "panchanga": value.get("panchanga"),
        "dasha": value.get("dasha"),
    }


def _compact_section(section: Any) -> dict[str, Any]:
    if not isinstance(section, dict):
        return {}
    return {
        "key": section.get("key"),
        "title": section.get("title"),
        "body": section.get("body"),
        "review_status": section.get("review_status"),
    }


def _compact_source_traces(source_traces: Any) -> list[dict[str, Any]]:
    if not isinstance(source_traces, dict):
        return []
    compact = []
    for trace in _limit_list(source_traces.get("traces"), 8):
        if not isinstance(trace, dict):
            continue
        source = trace.get("source") if isinstance(trace.get("source"), dict) else {}
        compact.append(
            {
                "condition_key": trace.get("condition_key"),
                "condition_title": trace.get("condition_title"),
                "work_title": source.get("work_title"),
                "reference": source.get("reference") or source.get("passage_reference"),
                "review_status": source.get("review_status"),
                "source_status": trace.get("source_status"),
                "interpretation_hint": trace.get("interpretation_hint"),
            }
        )
    return compact


def free_deepseek_chat_client() -> DeepseekRunner:
    endpoint = f"{settings.FREE_DEEPSEEK_API_BASE_URL}/chat/completions"
    model = settings.FREE_DEEPSEEK_MODEL

    def _client(prompt: str) -> str:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Ты DeepSeek, рабочий помощник jyotish-agent. Отвечай только валидным JSON по схеме пользователя.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": settings.FREE_DEEPSEEK_MAX_TOKENS,
            "temperature": 0.2,
            "stream": False,
            "user": "jyotish-agent",
        }
        api_request = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.FREE_DEEPSEEK_API_KEY or 'dummy-key'}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(api_request, timeout=settings.FREE_DEEPSEEK_TIMEOUT_SECONDS) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise DraftGenerationUnavailable(f"DeepSeek API returned {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise DraftGenerationUnavailable(f"DeepSeek API unavailable: {exc}") from exc
        except TimeoutError as exc:
            raise DraftGenerationUnavailable("DeepSeek API timed out") from exc
        return _extract_deepseek_text(response_payload)

    return _client


def _extract_deepseek_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first.get("text"), str):
                return first["text"]
    raise DraftGenerationUnavailable("DeepSeek response did not include text output")


def _normalize_deepseek_output(raw_output: dict[str, Any] | str) -> dict[str, Any]:
    output = _normalize_llm_output(raw_output)
    if not isinstance(raw_output, str):
        return output
    sections = _parse_deepseek_section_blocks(raw_output)
    if not sections:
        return output
    output = dict(output)
    output["language"] = output.get("language") or "ru"
    output["sections"] = sections
    return output


def _parse_deepseek_section_blocks(raw_output: str) -> list[dict[str, Any]]:
    matches = list(re.finditer(r"(?im)^Section\s+\d+\s*:\s*(.+?)\s*$", raw_output))
    sections = []
    for index, match in enumerate(matches):
        block_start = match.end()
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(raw_output)
        block = raw_output[block_start:block_end].strip()
        body = _text_after_label(block, "Body") or _strip_list_labels(block)
        section = {
            "title": match.group(1).strip(),
            "body": body.strip(),
            "citation_titles": [],
        }
        key_points = _json_array_after_label(block, "Key points")
        practical_steps = _json_array_after_label(block, "Practical steps")
        review_notes = _json_array_after_label(block, "Review notes")
        if key_points:
            section["key_points"] = key_points
        if practical_steps:
            section["practical_steps"] = practical_steps
        if review_notes:
            section["review_notes"] = review_notes
        sections.append(section)
    return [section for section in sections if section["title"] and section["body"]]


def _text_after_label(block: str, label: str) -> str:
    pattern = rf"(?ims)^{re.escape(label)}:\s*(.*?)(?=^Key points:|^Practical steps:|^Review notes:|\Z)"
    match = re.search(pattern, block)
    return match.group(1).strip() if match else ""


def _strip_list_labels(block: str) -> str:
    return re.sub(r"(?im)^(Key points|Practical steps|Review notes):.*$", "", block).strip()


def _json_array_after_label(block: str, label: str) -> list[str]:
    match = re.search(rf"(?im)^{re.escape(label)}:\s*(\[.*?\])\s*$", block)
    if not match:
        return []
    try:
        parsed = json.loads(match.group(1))
    except json.JSONDecodeError:
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []
