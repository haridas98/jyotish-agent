from __future__ import annotations

import json
import re
from typing import Any, Callable

from apps.calculations.ephemeris import EphemerisProvider

from .analysis_packet import build_analysis_packet
from .birth_report import CitationSearch, InterpretationProvider
from .models import GeneratedAnalysisDraft

LLMClient = Callable[[str], dict[str, Any] | str]


class DraftGenerationUnavailable(RuntimeError):
    pass


def generate_birth_chart_draft_analysis(
    data: dict[str, Any],
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: CitationSearch | None = None,
    interpretation_provider: InterpretationProvider | None = None,
    llm_client: LLMClient | None = None,
    user: Any | None = None,
) -> dict[str, Any]:
    packet = build_analysis_packet(
        data,
        provider=provider,
        citation_search=citation_search,
        research_search=research_search,
        interpretation_provider=interpretation_provider,
    )
    return generate_draft_analysis_for_packet(
        packet,
        input_snapshot=data,
        kind="birth_chart",
        llm_client=llm_client or disabled_legacy_draft_client(),
        provider="disabled_legacy",
        model="disabled_legacy",
        user=user,
    )


def generate_draft_analysis_for_packet(
    packet: dict[str, Any],
    *,
    input_snapshot: dict[str, Any],
    kind: str,
    llm_client: LLMClient,
    provider: str,
    model: str,
    user: Any | None = None,
) -> dict[str, Any]:
    prompt = str(packet.get("prompt_markdown") or "")
    if not prompt:
        raise ValueError("packet.prompt_markdown is required")
    raw_output = llm_client(prompt)
    output = _normalize_llm_output(raw_output)
    output["review_status"] = "draft"
    output["source_policy"] = "citation_first"
    output["kind"] = kind

    record = GeneratedAnalysisDraft.objects.create(
        kind=kind,
        review_status="draft",
        source_policy="citation_first",
        provider=provider,
        model=model,
        input_snapshot=input_snapshot,
        packet_snapshot=packet,
        output_json=output,
        prompt_markdown=prompt,
        user=user if getattr(user, "is_authenticated", False) else None,
    )
    output["id"] = record.id
    return output


def disabled_legacy_draft_client() -> LLMClient:
    def _client(prompt: str) -> dict[str, Any] | str:
        raise DraftGenerationUnavailable("legacy draft analysis is disabled; use codex_cli generation")

    return _client


def _normalize_llm_output(raw_output: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(raw_output, dict):
        output = dict(raw_output)
    else:
        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            parsed = _parse_json_fence(raw_output)
        output = parsed if isinstance(parsed, dict) else {"sections": parsed}
    output.setdefault("language", "ru")
    output.setdefault("sections", [])
    return output


def _parse_json_fence(raw_output: str) -> dict[str, Any]:
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_output, flags=re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(1))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    return {"sections": [{"title": "Черновик", "body": raw_output, "citation_titles": []}]}

