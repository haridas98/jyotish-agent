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
from .deepseek_generation import _deepseek_overview_packet
from .draft_generation import DraftGenerationUnavailable, _normalize_llm_output
from .models import GeneratedAnalysisDraft

QwenRunner = Callable[[str], dict[str, Any] | str]
QWEN_PROMPT_VERSION = "qwen-overview-v1"

QWEN_CACHE_KEYS = (
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


def generate_birth_chart_qwen_analysis(
    data: dict[str, Any],
    *,
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: CitationSearch | None = None,
    interpretation_provider: InterpretationProvider | None = None,
    qwen_runner: QwenRunner | None = None,
    refresh_evidence: bool = True,
    private_research_mode: bool = True,
) -> dict[str, Any]:
    if provider is None and qwen_runner is None:
        cached_output = _cached_qwen_analysis(data)
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
    prompt = render_qwen_analysis_prompt(packet, private_research_mode=private_research_mode)
    runner = qwen_runner or qwen_chat_completions_client()
    output = _normalize_llm_output(runner(prompt))
    output["coverage_status"] = _coverage_status(output, private_research_mode)
    output["review_status"] = _review_status(private_research_mode, output)
    output["source_policy"] = _source_policy(private_research_mode)
    output["kind"] = "birth_chart_qwen"
    output["provider"] = "qwen"
    output["model"] = settings.QWEN_MODEL
    output["prompt_version"] = QWEN_PROMPT_VERSION
    output["engine_label"] = "Сгенерировано с помощью QWEN"

    record = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_qwen",
        review_status=output["review_status"],
        source_policy=output["source_policy"],
        provider="qwen",
        model=settings.QWEN_MODEL,
        input_snapshot=data,
        packet_snapshot=_record_packet_snapshot(packet),
        output_json=output,
        prompt_markdown=prompt,
    )
    output["id"] = record.id
    return output


def _cached_qwen_analysis(data: dict[str, Any]) -> dict[str, Any] | None:
    for record in GeneratedAnalysisDraft.objects.filter(kind="birth_chart_qwen").order_by("-id")[:10]:
        if not _qwen_cache_input_matches(record.input_snapshot, data):
            continue
        output = dict(record.output_json or {})
        if output.get("prompt_version") != QWEN_PROMPT_VERSION:
            continue
        output["coverage_status"] = _coverage_status(output, True)
        output["review_status"] = _review_status(True, output)
        output["source_policy"] = output.get("source_policy") or record.source_policy
        output["kind"] = output.get("kind") or record.kind
        output["provider"] = output.get("provider") or record.provider or "qwen"
        output["model"] = output.get("model") or record.model
        output["prompt_version"] = output.get("prompt_version") or QWEN_PROMPT_VERSION
        output["engine_label"] = output.get("engine_label") or "Сгенерировано с помощью QWEN"
        output["id"] = record.id
        return output
    return None


def _qwen_cache_input_matches(snapshot: object, data: dict[str, Any]) -> bool:
    if not isinstance(snapshot, dict):
        return False
    for key in QWEN_CACHE_KEYS:
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


def render_qwen_analysis_prompt(packet: dict[str, Any], *, private_research_mode: bool = True) -> str:
    source_policy = "private_shastra_research_first" if private_research_mode else "citation_first"
    return (
        "You are QWEN inside jyotish-agent. Do not edit files and do not run commands.\n"
        "Return only valid JSON. Write a short Russian birth-chart overview, not a final full report.\n"
        "Use only facts and source hints from the JSON below. Do not invent citations, verse numbers, or links.\n"
        "Avoid fatalistic claims. Remedial advice must stay in a Vaishnava frame: Krishna shelter, sadhana, "
        "service to Vaishnavas, and Srila Prabhupada's guidance.\n"
        f"source_policy={source_policy}; review_status must stay draft/private_partial until human review.\n\n"
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
        "Make 5-8 sections: main picture, character/dharma, work/money, relationships, cautious health/risk, "
        "spiritual practice, what to verify in PL/JHora.\n\n"
        "OVERVIEW PACKET JSON:\n"
        "```json\n"
        f"{json.dumps(_deepseek_overview_packet(packet), ensure_ascii=False, indent=2)}\n"
        "```\n"
    )
def qwen_chat_completions_client() -> QwenRunner:
    endpoint = f"{settings.QWEN_API_BASE_URL}/chat/completions"
    model = settings.QWEN_MODEL

    def _client(prompt: str) -> str:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Ты QWEN, рабочий помощник jyotish-agent. Отвечай только валидным JSON по схеме пользователя.",
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        api_request = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.QWEN_API_KEY or 'dummy-key'}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(api_request, timeout=settings.QWEN_TIMEOUT_SECONDS) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise DraftGenerationUnavailable(f"QWEN API returned {exc.code}: {detail}") from exc
        except error.URLError as exc:
            raise DraftGenerationUnavailable(f"QWEN API unavailable: {exc}") from exc
        except TimeoutError as exc:
            raise DraftGenerationUnavailable("QWEN API timed out") from exc
        return _extract_qwen_text(response_payload)

    return _client


def _extract_qwen_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and isinstance(message.get("content"), str):
                return message["content"]
            if isinstance(first.get("text"), str):
                return first["text"]
    raise DraftGenerationUnavailable("QWEN response did not include text output")
