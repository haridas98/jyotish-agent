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
    _has_full_report_coverage,
    _record_packet_snapshot,
    _review_status,
    _source_policy,
    render_codex_cli_analysis_prompt,
    render_codex_cli_repair_prompt,
)
from .draft_generation import DraftGenerationUnavailable, _normalize_llm_output
from .models import GeneratedAnalysisDraft

QwenRunner = Callable[[str], dict[str, Any] | str]

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
    if private_research_mode and not _has_full_report_coverage(output):
        output = _normalize_llm_output(
            runner(
                render_qwen_repair_prompt(
                    packet,
                    output,
                    private_research_mode=private_research_mode,
                )
            )
        )
    output["coverage_status"] = _coverage_status(output, private_research_mode)
    output["review_status"] = _review_status(private_research_mode, output)
    output["source_policy"] = _source_policy(private_research_mode)
    output["kind"] = "birth_chart_qwen"
    output["provider"] = "qwen"
    output["model"] = settings.QWEN_MODEL
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
        output["coverage_status"] = _coverage_status(output, True)
        output["review_status"] = _review_status(True, output)
        output["source_policy"] = output.get("source_policy") or record.source_policy
        output["kind"] = output.get("kind") or record.kind
        output["provider"] = output.get("provider") or record.provider or "qwen"
        output["model"] = output.get("model") or record.model
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
    prompt = render_codex_cli_analysis_prompt(packet, private_research_mode=private_research_mode)
    return prompt.replace(
        "Ты Codex CLI внутри jyotish-agent. Не редактируй файлы и не запускай команды.",
        "Ты QWEN внутри jyotish-agent. Не редактируй файлы и не запускай команды.",
        1,
    )


def render_qwen_repair_prompt(
    packet: dict[str, Any],
    previous_output: dict[str, Any],
    *,
    private_research_mode: bool = True,
) -> str:
    prompt = render_codex_cli_repair_prompt(
        packet,
        previous_output,
        private_research_mode=private_research_mode,
    )
    return prompt.replace("EXPAND INCOMPLETE REPORT.", "EXPAND INCOMPLETE QWEN REPORT.", 1)


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
