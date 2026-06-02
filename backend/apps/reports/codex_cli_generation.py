from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

from django.conf import settings

from apps.calculations.ephemeris import EphemerisProvider
from apps.interpretations.evidence_matcher import build_shastra_evidence

from .analysis_packet import build_analysis_packet
from .birth_report import CitationSearch, InterpretationProvider
from .draft_generation import DraftGenerationUnavailable, _normalize_llm_output
from .models import GeneratedAnalysisDraft

CodexRunner = Callable[[str], str]


def generate_birth_chart_codex_cli_analysis(
    data: dict[str, Any],
    *,
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: CitationSearch | None = None,
    interpretation_provider: InterpretationProvider | None = None,
    codex_runner: CodexRunner | None = None,
    refresh_evidence: bool = True,
) -> dict[str, Any]:
    if refresh_evidence:
        build_shastra_evidence()
    packet = build_analysis_packet(
        data,
        provider=provider,
        citation_search=citation_search,
        research_search=research_search,
        interpretation_provider=interpretation_provider,
    )
    prompt = render_codex_cli_analysis_prompt(packet)
    raw_output = (codex_runner or codex_exec_runner)(prompt)
    output = _normalize_llm_output(raw_output)
    output["review_status"] = "draft"
    output["source_policy"] = "shastra_evidence_first"
    output["kind"] = "birth_chart_codex_cli"
    record = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli",
        review_status="draft",
        source_policy="shastra_evidence_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot=data,
        packet_snapshot=packet,
        output_json=output,
        prompt_markdown=prompt,
    )
    output["id"] = record.id
    return output


def render_codex_cli_analysis_prompt(packet: dict[str, Any]) -> str:
    packet_for_prompt = _compact_packet_for_codex_cli(packet)
    return (
        "Ты Codex CLI внутри jyotish-agent. Не редактируй файлы и не запускай команды.\n"
        "Задача: выдать конечный JSON-черновик анализа карты по цепочке "
        "условие -> фрагмент -> ссылка -> интерпретация.\n\n"
        "Правила:\n"
        "- используй chart facts как расчетные факты;\n"
        "- для шастр сначала используй shastra_evidence;\n"
        "- если evidence research_only, не цитируй дословно, а кратко перескажи и оставь review_notes;\n"
        "- не выдумывай главу, стих, переводчика или ссылку;\n"
        "- если inferred_reference имеет status != approved, явно отметь это в review_notes;\n"
        "- remedies формулируй через Кришну, садхану, служение вайшнавам и Шрилу Прабхупаду;\n"
        "- итог всегда draft до ручной проверки.\n\n"
        "OUTPUT JSON schema:\n"
        "{\n"
        '  "review_status": "draft",\n'
        '  "language": "ru",\n'
        '  "sections": [\n'
        "    {\n"
        '      "title": "string",\n'
        '      "body": "string",\n'
        '      "condition_keys": ["string"],\n'
        '      "evidence_references": ["string"],\n'
        '      "citation_titles": ["string"],\n'
        '      "review_notes": ["string"]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "PACKET JSON:\n"
        "```json\n"
        f"{json.dumps(packet_for_prompt, ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def _compact_packet_for_codex_cli(packet: dict[str, Any]) -> dict[str, Any]:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}
    relevant_keys = _relevant_condition_keys(packet)
    return {
        "schema_version": packet.get("schema_version"),
        "status": packet.get("status"),
        "generator_policy": packet.get("generator_policy"),
        "birth": context.get("birth", {}),
        "place": context.get("place", {}),
        "settings": context.get("settings", {}),
        "chart_facts": context.get("chart_facts", {}),
        "person_summary": context.get("person_summary", {}),
        "detected_yoga_source_map": context.get("detected_yoga_source_map", []),
        "sections": context.get("sections", []),
        "citations": packet.get("citations", []),
        "shastra_coverage_summary": (packet.get("shastra_coverage") or {}).get("summary", {}),
        "shastra_condition_summary": (packet.get("shastra_condition_matrix") or {}).get("summary", {}),
        "shastra_evidence": _compact_evidence(packet.get("shastra_evidence"), relevant_keys),
        "source_rules": (packet.get("shastra_evidence") or {}).get("prompt_rules", []),
    }


def _relevant_condition_keys(packet: dict[str, Any]) -> set[str]:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}
    keys = {
        "rashi_nakshatra_navamsa",
        "vimshottari",
        "avasthas",
        "yogas",
        "vaishnava_remedies",
        "lagna_and_body",
        "graha_placements",
        "moon_mind_and_dasha_seed",
        "bhava_topics",
    }
    for row in context.get("detected_yoga_source_map", []) or []:
        if isinstance(row, dict):
            key = str(row.get("catalog_key") or row.get("key") or "").strip()
            if key:
                keys.add(key)
    return keys


def _compact_evidence(evidence_payload: object, relevant_keys: set[str]) -> dict[str, Any]:
    if not isinstance(evidence_payload, dict):
        return {"conditions": []}
    rows = []
    for row in evidence_payload.get("conditions", []) or []:
        if not isinstance(row, dict):
            continue
        condition_key = str(row.get("condition_key") or "")
        if condition_key not in relevant_keys:
            continue
        rows.append(
            {
                "condition_key": condition_key,
                "condition_kind": row.get("condition_kind"),
                "condition_title": row.get("condition_title"),
                "condition_summary": row.get("condition_summary"),
                "evidence_status": row.get("evidence_status"),
                "evidence": [_compact_evidence_item(item) for item in (row.get("evidence") or [])[:2]],
            }
        )
    return {
        "schema_version": evidence_payload.get("schema_version"),
        "summary": {
            "conditions_in_prompt": len(rows),
            "evidence_items_in_prompt": sum(len(row["evidence"]) for row in rows),
        },
        "conditions": rows,
    }


def _compact_evidence_item(item: object) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {}
    return {
        "work_title": item.get("work_title"),
        "passage_reference": item.get("passage_reference"),
        "inferred_reference": item.get("inferred_reference"),
        "reference_status": item.get("reference_status"),
        "review_status": item.get("review_status"),
        "public_quote_policy": item.get("public_quote_policy"),
        "matched_terms": item.get("matched_terms", []),
        "snippet": str(item.get("snippet") or "")[:700],
    }


def codex_exec_runner(prompt: str) -> str:
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "codex-last-message.json"
        command = [
            "codex",
            "exec",
            "--cd",
            str(settings.ROOT_DIR),
            "--sandbox",
            "read-only",
            "--output-last-message",
            str(output_path),
            "-",
        ]
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=600,
            check=False,
        )
        if completed.returncode != 0:
            raise DraftGenerationUnavailable(completed.stderr or completed.stdout)
        if output_path.exists():
            return output_path.read_text(encoding="utf-8")
        return completed.stdout
