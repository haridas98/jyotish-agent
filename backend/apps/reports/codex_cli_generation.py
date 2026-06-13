from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

from django.conf import settings

from apps.calculations.ephemeris import EphemerisProvider
from apps.interpretations.evidence_matcher import build_shastra_evidence

from .analysis_packet import build_analysis_packet, build_compatibility_analysis_packet
from .birth_report import CitationSearch, InterpretationProvider
from .draft_generation import DraftGenerationUnavailable, _normalize_llm_output
from .models import GeneratedAnalysisDraft, input_summary_from_snapshot

CodexRunner = Callable[[str], dict[str, Any] | str]

MIN_FULL_REPORT_SECTIONS = 22
MIN_COMPATIBILITY_REPORT_SECTIONS = 14

FULL_REPORT_SECTION_BLUEPRINT: tuple[dict[str, Any], ...] = (
    {"key": "birth_context_and_method", "title": "Данные рождения и метод расчёта"},
    {"key": "personality_core", "title": "Ядро личности: лагна, управитель лагны, тело и характер"},
    {"key": "moon_mind", "title": "Луна, ум, эмоции, сон и внутренняя устойчивость"},
    {"key": "sun_identity", "title": "Солнце, воля, отец, авторитет и самоуважение"},
    {"key": "career_and_work", "title": "Карьера, призвание, статус и десятый дом"},
    {"key": "money_and_resources", "title": "Деньги, речь, ресурсы, накопление и 2/11 дома"},
    {"key": "education_and_intelligence", "title": "Обучение, интеллект, 4/5 дома, Будха и Гуру"},
    {"key": "marriage_and_relationships", "title": "Брак, отношения, 7 дом, Шукра, Мангала и совместимость"},
    {"key": "family_home_mother", "title": "Дом, мать, недвижимость, внутренний покой и 4 дом"},
    {"key": "father_guru_dharma", "title": "Отец, учителя, дхарма, удача и 9 дом"},
    {"key": "children_creativity", "title": "Дети, творчество, пунья и 5 дом"},
    {"key": "health_energy_risks", "title": "Здоровье, энергия, 1/6/8/12 дома и осторожные риски"},
    {"key": "spiritual_life", "title": "Духовная жизнь, садхана, служение и вайшнавская рамка"},
    {"key": "panchanga", "title": "Панчанга рождения: титхи, вара, накшатра, йога, карана"},
    {"key": "nakshatra_psychology", "title": "Накшатры и пады ключевых грах"},
    {"key": "vargas", "title": "Варги D2-D60: подтверждения и уточнения"},
    {"key": "dashas_timing", "title": "Даши и временные периоды жизни"},
    {"key": "yogas", "title": "Йоги: условия, шастра, сила, ограничения"},
    {"key": "avasthas_and_bala", "title": "Авастхи, шадбала, вимшопака и сила грах"},
    {"key": "ashtakavarga_argala_special_points", "title": "Аштакаварга, аргала, упаграхи и специальные точки"},
    {"key": "difficult_patterns_and_cancellations", "title": "Сложные комбинации, отмены, защита и зрелое чтение"},
    {"key": "practical_plan", "title": "Практический план: что развивать, чего избегать, как действовать"},
    {"key": "source_logic", "title": "Источники и логика: условие -> шастра -> интерпретация"},
)

COMPATIBILITY_REPORT_SECTION_BLUEPRINT: tuple[dict[str, Any], ...] = (
    {"key": "compatibility_context_and_method", "title": "Данные двух карт и метод совместимости"},
    {"key": "person_a_profile", "title": "Карта A: характер, лагна, Луна и зрелость для брака"},
    {"key": "person_b_profile", "title": "Карта B: характер, лагна, Луна и зрелость для брака"},
    {"key": "lagna_and_life_direction", "title": "Лагны и направление жизни"},
    {"key": "moon_mind_emotional_match", "title": "Луны, ум, эмоциональный ритм и привычки"},
    {"key": "seventh_house_marriage_capacity", "title": "7 дом, управители брака и способность к союзу"},
    {"key": "venus_mars_relationship_dynamic", "title": "Шукра, Мангала, влечение и конфликтность"},
    {"key": "guru_dharma_family_values", "title": "Гуру, дхарма, семейные ценности и наставничество"},
    {"key": "second_fourth_eighth_twelfth_houses", "title": "Семья, дом, близость, расходы и скрытые напряжения"},
    {"key": "dashas_and_timing", "title": "Даши и временной контекст отношений"},
    {"key": "ashtakuta_supporting_metric", "title": "Ашта-кута как вспомогательная метрика"},
    {"key": "risk_cancellations_and_maturity", "title": "Риски, смягчения, зрелость и зоны проверки"},
    {"key": "vaishnava_practical_guidance", "title": "Практические выводы в гаудия-вайшнавской рамке"},
    {"key": "source_logic", "title": "Условие -> шастра -> интерпретация"},
)


def generate_birth_chart_codex_cli_analysis(
    data: dict[str, Any],
    *,
    user: Any | None = None,
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: CitationSearch | None = None,
    interpretation_provider: InterpretationProvider | None = None,
    codex_runner: CodexRunner | None = None,
    refresh_evidence: bool = True,
    private_research_mode: bool = True,
    force_regenerate: bool = False,
) -> dict[str, Any]:
    if private_research_mode and provider is None and codex_runner is None and not force_regenerate:
        cached_output = _cached_full_codex_analysis(data, user=user)
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
    prompt = render_codex_cli_analysis_prompt(packet, private_research_mode=private_research_mode)
    runner = codex_runner or configured_analysis_runner
    provider_name, model_name = _analysis_provider_metadata(codex_runner)
    raw_output = runner(prompt)
    output = _normalize_llm_output(raw_output)
    if private_research_mode and not _has_full_report_coverage(output):
        repair_prompt = render_codex_cli_repair_prompt(
            packet,
            output,
            private_research_mode=private_research_mode,
        )
        output = _normalize_llm_output(runner(repair_prompt))
    output["coverage_status"] = _coverage_status(output, private_research_mode)
    output["review_status"] = _review_status(private_research_mode, output)
    output["source_policy"] = _source_policy(private_research_mode)
    output["kind"] = "birth_chart_codex_cli"
    record = GeneratedAnalysisDraft.objects.create(
        user=_analysis_user(user),
        kind="birth_chart_codex_cli",
        review_status=output["review_status"],
        source_policy=_source_policy(private_research_mode),
        provider=provider_name,
        model=model_name,
        input_snapshot=data,
        packet_snapshot=_record_packet_snapshot(packet),
        output_json=output,
        prompt_markdown=prompt,
    )
    output["id"] = record.id
    return output


def generate_compatibility_codex_cli_analysis(
    data: dict[str, Any],
    *,
    user: Any | None = None,
    provider: EphemerisProvider | None = None,
    citation_search: CitationSearch | None = None,
    research_search: CitationSearch | None = None,
    codex_runner: CodexRunner | None = None,
    refresh_evidence: bool = True,
    private_research_mode: bool = True,
) -> dict[str, Any]:
    if refresh_evidence:
        build_shastra_evidence()
    packet = build_compatibility_analysis_packet(
        data,
        provider=provider,
        citation_search=citation_search,
        research_search=research_search,
    )
    prompt = render_codex_cli_compatibility_prompt(packet, private_research_mode=private_research_mode)
    runner = codex_runner or configured_analysis_runner
    provider_name, model_name = _analysis_provider_metadata(codex_runner)
    output = _normalize_llm_output(runner(prompt))
    if private_research_mode and not _has_compatibility_report_coverage(output):
        output = _normalize_llm_output(
            runner(
                render_codex_cli_compatibility_repair_prompt(
                    packet,
                    output,
                    private_research_mode=private_research_mode,
                )
            )
        )
    output["coverage_status"] = _compatibility_coverage_status(output, private_research_mode)
    output["review_status"] = _compatibility_review_status(private_research_mode, output)
    output["source_policy"] = _source_policy(private_research_mode)
    output["kind"] = "compatibility_codex_cli"
    record = GeneratedAnalysisDraft.objects.create(
        user=_analysis_user(user),
        kind="compatibility_codex_cli",
        review_status=output["review_status"],
        source_policy=_source_policy(private_research_mode),
        provider=provider_name,
        model=model_name,
        input_snapshot=data,
        packet_snapshot=_record_packet_snapshot(packet),
        output_json=output,
        prompt_markdown=prompt,
    )
    output["id"] = record.id
    return output


def _cached_full_codex_analysis(data: dict[str, Any], *, user: Any | None = None) -> dict[str, Any] | None:
    records = GeneratedAnalysisDraft.objects.filter(
        kind="birth_chart_codex_cli",
        review_status="private_final",
    )
    owner = _analysis_user(user)
    records = records.filter(user=owner) if owner is not None else records.filter(user__isnull=True)
    input_summary = input_summary_from_snapshot(data, "birth_chart_codex_cli")
    if input_summary:
        records = records.filter(input_summary=input_summary)
    candidates = records.only("id", "kind", "source_policy", "input_snapshot").order_by("-id")[:10]
    for record in candidates:
        if not _input_snapshot_matches(record.input_snapshot, data):
            continue
        output_record = records.only("id", "kind", "source_policy", "output_json").get(id=record.id)
        output = dict(output_record.output_json or {})
        if not _has_full_report_coverage(output):
            continue
        output["coverage_status"] = _coverage_status(output, True)
        output["review_status"] = _review_status(True, output)
        output["source_policy"] = output.get("source_policy") or output_record.source_policy
        output["kind"] = output.get("kind") or output_record.kind
        output["id"] = output_record.id
        return output
    return None


def _input_snapshot_matches(snapshot: object, data: dict[str, Any]) -> bool:
    if not isinstance(snapshot, dict):
        return False
    return all(snapshot.get(key) == value for key, value in data.items())


def _analysis_user(user: Any | None) -> Any | None:
    if user is not None and getattr(user, "is_authenticated", False):
        return user
    return None


def _get_owned_report(analysis_id: int, kind: str, *, user: Any | None = None) -> GeneratedAnalysisDraft:
    report = GeneratedAnalysisDraft.objects.get(id=analysis_id, kind=kind)
    owner = _analysis_user(user)
    if owner is None and report.user_id is not None:
        raise GeneratedAnalysisDraft.DoesNotExist
    if owner is not None and report.user_id != owner.id:
        raise GeneratedAnalysisDraft.DoesNotExist
    return report


def ask_birth_chart_codex_cli_analysis(
    *,
    analysis_id: int,
    question: str,
    history: list[dict[str, Any]] | None = None,
    codex_runner: CodexRunner | None = None,
    user: Any | None = None,
) -> dict[str, Any]:
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("question is required")
    report = _get_owned_report(analysis_id, "birth_chart_codex_cli", user=user)
    prompt = render_codex_cli_analysis_chat_prompt(report, clean_question, history=history or [])
    runner = codex_runner or configured_analysis_runner
    provider_name, model_name = _analysis_provider_metadata(codex_runner)
    output = _normalize_llm_output(runner(prompt))
    answer = str(output.get("answer") or "").strip()
    if not answer:
        answer = _fallback_answer_from_sections(output)
    result = {
        "kind": "birth_chart_codex_cli_chat",
        "analysis_id": report.id,
        "question": clean_question,
        "answer": answer,
        "language": output.get("language", "ru"),
        "review_status": "private_final",
        "source_policy": report.source_policy or "private_shastra_research_first",
        "evidence_references": output.get("evidence_references", []),
        "source_traces": output.get("source_traces", []),
        "history_used": len(_compact_chat_history(history or [])),
    }
    record = GeneratedAnalysisDraft.objects.create(
        user=report.user,
        parent_analysis=report,
        kind="birth_chart_codex_cli_chat",
        review_status="private_final",
        source_policy=result["source_policy"],
        provider=provider_name,
        model=model_name,
        input_snapshot={"analysis_id": report.id, "question": clean_question, "history": _compact_chat_history(history or [])},
        packet_snapshot={"analysis": _compact_report_for_chat(report)},
        output_json=result,
        prompt_markdown=prompt,
    )
    result["id"] = record.id
    return result


def ask_current_day_codex_cli_analysis(
    *,
    analysis_id: int,
    question: str,
    history: list[dict[str, Any]] | None = None,
    codex_runner: CodexRunner | None = None,
    user: Any | None = None,
) -> dict[str, Any]:
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("question is required")
    report = _get_owned_report(analysis_id, "current_day_transit_overview", user=user)
    prompt = render_codex_cli_analysis_chat_prompt(report, clean_question, history=history or [])
    runner = codex_runner or configured_analysis_runner
    provider_name, model_name = _analysis_provider_metadata(codex_runner)
    output = _normalize_llm_output(runner(prompt))
    answer = str(output.get("answer") or "").strip() or _fallback_answer_from_sections(output)
    result = {
        "kind": "current_day_transit_overview_chat",
        "analysis_id": report.id,
        "question": clean_question,
        "answer": answer,
        "language": output.get("language", "ru"),
        "review_status": "private_final",
        "source_policy": report.source_policy or "calculation_first",
        "evidence_references": output.get("evidence_references", []),
        "source_traces": output.get("source_traces", []),
        "history_used": len(_compact_chat_history(history or [])),
    }
    record = GeneratedAnalysisDraft.objects.create(
        user=report.user,
        parent_analysis=report,
        kind="current_day_transit_overview_chat",
        review_status="private_final",
        source_policy=result["source_policy"],
        provider=provider_name,
        model=model_name,
        input_snapshot={"analysis_id": report.id, "question": clean_question, "history": _compact_chat_history(history or [])},
        packet_snapshot={"analysis": _compact_report_for_chat(report)},
        output_json=result,
        prompt_markdown=prompt,
    )
    result["id"] = record.id
    return result


def ask_compatibility_codex_cli_analysis(
    *,
    analysis_id: int,
    question: str,
    history: list[dict[str, Any]] | None = None,
    codex_runner: CodexRunner | None = None,
    user: Any | None = None,
) -> dict[str, Any]:
    clean_question = question.strip()
    if not clean_question:
        raise ValueError("question is required")
    report = _get_owned_report(analysis_id, "compatibility_codex_cli", user=user)
    prompt = render_codex_cli_compatibility_chat_prompt(report, clean_question, history=history or [])
    runner = codex_runner or configured_analysis_runner
    provider_name, model_name = _analysis_provider_metadata(codex_runner)
    output = _normalize_llm_output(runner(prompt))
    answer = str(output.get("answer") or "").strip() or _fallback_answer_from_sections(output)
    result = {
        "kind": "compatibility_codex_cli_chat",
        "analysis_id": report.id,
        "question": clean_question,
        "answer": answer,
        "language": output.get("language", "ru"),
        "review_status": "private_final",
        "source_policy": report.source_policy or "private_shastra_research_first",
        "evidence_references": output.get("evidence_references", []),
        "source_traces": output.get("source_traces", []),
        "history_used": len(_compact_chat_history(history or [])),
    }
    record = GeneratedAnalysisDraft.objects.create(
        user=report.user,
        parent_analysis=report,
        kind="compatibility_codex_cli_chat",
        review_status="private_final",
        source_policy=result["source_policy"],
        provider=provider_name,
        model=model_name,
        input_snapshot={"analysis_id": report.id, "question": clean_question, "history": _compact_chat_history(history or [])},
        packet_snapshot={"analysis": _compact_compatibility_report_for_chat(report)},
        output_json=result,
        prompt_markdown=prompt,
    )
    result["id"] = record.id
    return result


def render_codex_cli_analysis_chat_prompt(
    report: GeneratedAnalysisDraft,
    question: str,
    *,
    history: list[dict[str, Any]] | None = None,
) -> str:
    return (
        "Ты Codex CLI внутри jyotish-agent. Не редактируй файлы и не запускай команды.\n"
        "Задача: ответить на вопрос пользователя по уже сохранённому астрологическому разбору.\n"
        "Пиши по-русски, понятно человеку, без фатализма. Не советуй independent demigod worship; "
        "практические выводы формулируй через Кришну, садхану, служение вайшнавам и наставления Шрилы Прабхупады.\n"
        "Если вопрос требует данных, которых нет в отчёте, прямо скажи, чего не хватает.\n"
        "Отвечай JSON без markdown.\n\n"
        "OUTPUT JSON schema:\n"
        "{\n"
        '  "answer": "string",\n'
        '  "evidence_references": ["string"],\n'
        '  "source_traces": [\n'
        "    {\n"
        '      "condition_key": "string",\n'
        '      "work_title": "string",\n'
        '      "reference": "string",\n'
        '      "source_status": "string",\n'
        '      "short_excerpt": "string",\n'
        '      "interpretation": "string"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        f"QUESTION:\n{question}\n\n"
        "CHAT HISTORY JSON:\n"
        "```json\n"
        f"{json.dumps(_compact_chat_history(history or []), ensure_ascii=False, indent=2)}\n"
        "```\n\n"
        "SAVED ANALYSIS JSON:\n"
        "```json\n"
        f"{json.dumps(_compact_report_for_chat(report), ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def render_codex_cli_compatibility_chat_prompt(
    report: GeneratedAnalysisDraft,
    question: str,
    *,
    history: list[dict[str, Any]] | None = None,
) -> str:
    return (
        "Ты Codex CLI внутри jyotish-agent. Не редактируй файлы и не запускай команды.\n"
        "Задача: ответить на вопрос пользователя по уже сохранённому разбору совместимости двух астрологических карт.\n"
        "Пиши по-русски, понятно человеку, без фатализма. Ашта-кута является только вспомогательным слоем; "
        "отвечай по двум картам целиком: лагны, Луны, 7 дом, Шукра/Мангала, Гуру, дома семьи/близости, даши и зрелость.\n"
        "Не советуй independent demigod worship; практические выводы формулируй через Кришну, садхану, служение вайшнавам, "
        "садху-сангу и наставления Шрилы Прабхупады.\n"
        "Не давай окончательный брачный приговор вместо старшего вайшнавского review. Если данных не хватает, прямо скажи, чего не хватает.\n"
        "Отвечай JSON без markdown.\n\n"
        "OUTPUT JSON schema:\n"
        "{\n"
        '  "answer": "string",\n'
        '  "evidence_references": ["string"],\n'
        '  "source_traces": [\n'
        "    {\n"
        '      "condition_key": "string",\n'
        '      "work_title": "string",\n'
        '      "reference": "string",\n'
        '      "source_status": "string",\n'
        '      "short_excerpt": "string",\n'
        '      "interpretation": "string"\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        f"QUESTION:\n{question}\n\n"
        "CHAT HISTORY JSON:\n"
        "```json\n"
        f"{json.dumps(_compact_chat_history(history or []), ensure_ascii=False, indent=2)}\n"
        "```\n\n"
        "SAVED COMPATIBILITY ANALYSIS JSON:\n"
        "```json\n"
        f"{json.dumps(_compact_compatibility_report_for_chat(report), ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def _compact_report_for_chat(report: GeneratedAnalysisDraft) -> dict[str, Any]:
    output = report.output_json if isinstance(report.output_json, dict) else {}
    sections = output.get("sections") if isinstance(output.get("sections"), list) else []
    compact_sections: list[dict[str, Any]] = []
    for section in sections[:30]:
        if not isinstance(section, dict):
            continue
        compact_sections.append(
            {
                "title": section.get("title"),
                "body": _short_text(section.get("body"), 2400),
                "key_points": _compact_string_list(section.get("key_points"), limit=6),
                "practical_steps": _compact_string_list(section.get("practical_steps"), limit=6),
                "condition_keys": _compact_string_list(section.get("condition_keys"), limit=10),
                "evidence_references": _compact_string_list(section.get("evidence_references"), limit=10),
                "source_traces": _compact_source_trace_rows(section.get("source_traces"), limit=8),
                "review_notes": _compact_string_list(section.get("review_notes"), limit=6),
            }
        )
    compact = {
        "id": report.id,
        "review_status": report.review_status,
        "source_policy": report.source_policy,
        "input_snapshot": report.input_snapshot,
        "coverage_status": output.get("coverage_status"),
        "sections": compact_sections,
    }
    packet = report.packet_snapshot if isinstance(report.packet_snapshot, dict) else {}
    if report.kind == "birth_chart_codex_cli" and packet:
        compact["analysis_packet"] = _compact_packet_for_codex_cli(packet)
    return compact


def _compact_compatibility_report_for_chat(report: GeneratedAnalysisDraft) -> dict[str, Any]:
    compact = _compact_report_for_chat(report)
    packet = report.packet_snapshot if isinstance(report.packet_snapshot, dict) else {}
    if packet:
        compact["compatibility_packet"] = _compact_compatibility_packet_for_codex_cli(packet)
    return compact


def _compact_chat_history(history: list[dict[str, Any]]) -> list[dict[str, str]]:
    compact: list[dict[str, str]] = []
    for item in history[-8:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get("role") or "").strip().lower()
        if role not in {"user", "assistant"}:
            continue
        content = _short_text(item.get("content"), 1200)
        if content:
            compact.append({"role": role, "content": content})
    return compact


def _compact_source_trace_rows(value: object, *, limit: int) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in value[:limit]:
        if not isinstance(item, dict):
            continue
        rows.append(
            {
                "condition_key": item.get("condition_key"),
                "work_title": item.get("work_title"),
                "reference": item.get("reference"),
                "source_status": item.get("source_status"),
                "short_excerpt": _short_text(item.get("short_excerpt"), 300),
                "interpretation": _short_text(item.get("interpretation"), 500),
            }
        )
    return rows


def _compact_string_list(value: object, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_short_text(item, 300) for item in value[:limit] if _short_text(item, 300)]


def _short_text(value: object, limit: int) -> str:
    text = str(value or "").strip()
    return text if len(text) <= limit else f"{text[:limit].rstrip()}..."


def _fallback_answer_from_sections(output: dict[str, Any]) -> str:
    sections = output.get("sections")
    if isinstance(sections, list) and sections:
        first = sections[0]
        if isinstance(first, dict):
            return str(first.get("body") or first.get("answer") or "").strip()
    return ""


def _record_packet_snapshot(packet: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in packet.items() if key != "prompt_markdown"}


def render_codex_cli_analysis_prompt(packet: dict[str, Any], *, private_research_mode: bool = True) -> str:
    packet_for_prompt = _compact_packet_for_codex_cli(packet)
    mode_rules = (
        "PRIVATE RESEARCH MODE:\n"
        "- проект локальный; research-only фрагменты можно использовать как рабочие источники для полноценного личного разбора;\n"
        "- не называй research-only фрагменты публично утвержденными;\n"
        "- можно приводить только короткие выдержки, до 25 слов на источник, остальное пересказывай;\n"
        "- каждый вывод оформляй цепочкой: условие -> фрагмент/ссылка -> интерпретация;\n"
        "- если ссылка inferred/needs_review, используй ее как рабочую, но пометь status в source_traces.\n"
        if private_research_mode
        else (
            "PUBLIC REVIEW MODE:\n"
            "- используй дословно только approved_shastra_citations;\n"
            "- research-only evidence можно только пересказывать и помечать review_notes.\n"
        )
    )
    return (
        "Ты Codex CLI внутри jyotish-agent. Не редактируй файлы и не запускай команды.\n"
        "Задача: выдать нормальный русский JSON-разбор карты понятным человеческим языком.\n\n"
        f"{mode_rules}\n"
        f"{_private_research_scope_rules() if private_research_mode else ''}"
        f"{_full_report_contract()}\n"
        "Правила анализа:\n"
        "- используй chart facts как расчетные факты, не как фатальный приговор;\n"
        "- сначала опирайся на approved_shastra_citations, затем на shastra_evidence;\n"
        "- не выдумывай главу, стих, переводчика или ссылку;\n"
        "- если данных не хватает, прямо напиши это в review_notes;\n"
        "- не советуй independent demigod worship;\n"
        "- remedies формулируй через Кришну, садхану, служение вайшнавам и Шрилу Прабхупаду;\n"
        "- сделай содержательные разделы: ядро личности, Луна и ум, панчанга, даши, йоги, силы/риски, практические выводы;\n"
        "- body пиши как понятный текст для человека: спокойно, живо, без таблиц и без сухой технической формулы;\n"
        "- не начинай body словами Условие, Фрагмент, Ссылка или Интерпретация;\n"
        "- техническую цепочку условие -> источник -> вывод клади только в source_traces;\n"
        "- key_points дай как 2-4 коротких вывода простыми словами;\n"
        "- practical_steps дай как 2-4 практичных шага в вайшнавской рамке.\n\n"
        "OUTPUT JSON schema:\n"
        "{\n"
        f'  "review_status": "{_review_status(private_research_mode)}",\n'
        '  "language": "ru",\n'
        '  "source_policy": "private_shastra_research_first",\n'
        '  "sections": [\n'
        "    {\n"
        '      "title": "string",\n'
        '      "body": "string",\n'
        '      "key_points": ["string"],\n'
        '      "practical_steps": ["string"],\n'
        '      "condition_keys": ["string"],\n'
        '      "evidence_references": ["string"],\n'
        '      "citation_titles": ["string"],\n'
        '      "source_traces": [\n'
        "        {\n"
        '          "condition_key": "string",\n'
        '          "work_title": "string",\n'
        '          "reference": "string",\n'
        '          "source_status": "approved|research_only|inferred_needs_review",\n'
        '          "short_excerpt": "string",\n'
        '          "interpretation": "string"\n'
        "        }\n"
        "      ],\n"
        '      "review_notes": ["string"]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "PACKET JSON:\n"
        "```json\n"
        f"{json.dumps(packet_for_prompt, ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def render_codex_cli_repair_prompt(
    packet: dict[str, Any],
    previous_output: dict[str, Any],
    *,
    private_research_mode: bool = True,
) -> str:
    packet_for_prompt = _compact_packet_for_codex_cli(packet)
    return (
        "EXPAND INCOMPLETE REPORT.\n"
        "The previous JSON report was too short and must be replaced, not summarized.\n"
        f"{'PRIVATE RESEARCH MODE' if private_research_mode else 'PUBLIC REVIEW MODE'} still applies.\n"
        f"{_private_research_scope_rules() if private_research_mode else ''}"
        f"{_full_report_contract()}\n"
        "Original writing rules still apply:\n"
        "- body пиши как понятный текст для человека: спокойно, живо, без таблиц и без сухой технической формулы;\n"
        "- техническую цепочку условие -> источник -> вывод клади только в source_traces;\n"
        "Return a complete Russian JSON report using the same OUTPUT JSON schema. "
        "Do not mention that this is a retry.\n\n"
        "PREVIOUS OUTPUT JSON:\n"
        "```json\n"
        f"{json.dumps(previous_output, ensure_ascii=False, indent=2)}\n"
        "```\n\n"
        "PACKET JSON:\n"
        "```json\n"
        f"{json.dumps(packet_for_prompt, ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def render_codex_cli_compatibility_prompt(packet: dict[str, Any], *, private_research_mode: bool = True) -> str:
    packet_for_prompt = _compact_compatibility_packet_for_codex_cli(packet)
    mode_rules = (
        "PRIVATE RESEARCH MODE:\n"
        "- проект локальный; research-only фрагменты можно использовать как рабочие источники для личного разбора;\n"
        "- не называй research-only фрагменты публично утвержденными;\n"
        "- короткие выдержки держи краткими; основной текст пересказывай своими словами;\n"
        "- каждый важный вывод оформляй через source_traces: условие -> фрагмент/ссылка -> интерпретация.\n"
        if private_research_mode
        else (
            "PUBLIC REVIEW MODE:\n"
            "- используй дословно только approved_shastra_citations;\n"
            "- research-only evidence можно только пересказывать и помечать review_notes.\n"
        )
    )
    return (
        "Ты Codex CLI внутри jyotish-agent. Не редактируй файлы и не запускай команды.\n"
        "Задача: выдать полноценный русский JSON-разбор совместимости двух карт для личного использования.\n"
        "Ashtakuta is only one supporting metric; never make an ashtakuta-only verdict.\n\n"
        f"{mode_rules}\n"
        f"{_private_research_scope_rules() if private_research_mode else ''}"
        f"{_compatibility_report_contract()}\n"
        "Правила анализа:\n"
        "- сравни обе карты с разных ракурсов: лагны, Луны, 7 дом, управители брака, Шукра/Мангала, Гуру, 2/4/8/12 дома, даши и практическая зрелость;\n"
        "- расчеты считай техническими фактами, а не фатальным приговором;\n"
        "- не выдумывай главы, стихи, переводчиков или ссылки;\n"
        "- не советуй independent demigod worship;\n"
        "- remedial выводы формулируй через Кришну, садхану, служение вайшнавам, садху-сангу и наставления Шрилы Прабхупады;\n"
        "- не давай окончательный брачный приговор вместо старшего вайшнавского review;\n"
        "- body пиши как понятный человеческий текст, без сухой таблицы;\n"
        "- техническую цепочку условие -> источник -> вывод клади только в source_traces.\n\n"
        "OUTPUT JSON schema:\n"
        "{\n"
        f'  "review_status": "{_compatibility_review_status(private_research_mode)}",\n'
        '  "language": "ru",\n'
        '  "source_policy": "private_shastra_research_first",\n'
        '  "sections": [\n'
        "    {\n"
        '      "title": "string",\n'
        '      "body": "string",\n'
        '      "key_points": ["string"],\n'
        '      "practical_steps": ["string"],\n'
        '      "condition_keys": ["string"],\n'
        '      "evidence_references": ["string"],\n'
        '      "citation_titles": ["string"],\n'
        '      "source_traces": [\n'
        "        {\n"
        '          "condition_key": "string",\n'
        '          "work_title": "string",\n'
        '          "reference": "string",\n'
        '          "source_status": "approved|research_only|inferred_needs_review",\n'
        '          "short_excerpt": "string",\n'
        '          "interpretation": "string"\n'
        "        }\n"
        "      ],\n"
        '      "review_notes": ["string"]\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "COMPATIBILITY PACKET JSON:\n"
        "```json\n"
        f"{json.dumps(packet_for_prompt, ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def render_codex_cli_compatibility_repair_prompt(
    packet: dict[str, Any],
    previous_output: dict[str, Any],
    *,
    private_research_mode: bool = True,
) -> str:
    return (
        "EXPAND INCOMPLETE COMPATIBILITY REPORT.\n"
        "The previous JSON report was too short and must be replaced, not summarized.\n"
        f"{'PRIVATE RESEARCH MODE' if private_research_mode else 'PUBLIC REVIEW MODE'} still applies.\n"
        f"{_private_research_scope_rules() if private_research_mode else ''}"
        f"{_compatibility_report_contract()}\n"
        "Return a complete Russian JSON report using the same OUTPUT JSON schema. "
        "Do not mention that this is a retry.\n\n"
        "PREVIOUS OUTPUT JSON:\n"
        "```json\n"
        f"{json.dumps(previous_output, ensure_ascii=False, indent=2)}\n"
        "```\n\n"
        "COMPATIBILITY PACKET JSON:\n"
        "```json\n"
        f"{json.dumps(_compact_compatibility_packet_for_codex_cli(packet), ensure_ascii=False, indent=2)}\n"
        "```\n"
    )


def _full_report_contract() -> str:
    return (
        "FULL REPORT CONTRACT:\n"
        f"- Generate minimum {MIN_FULL_REPORT_SECTIONS} sections; do not collapse the chart into overview only.\n"
        "- Each section body should be a developed human-readable explanation, normally 1200-2500 characters.\n"
        "- Cover every life area in full_report_blueprint: personality, mind, Sun, career_and_work, "
        "money, education, marriage_and_relationships, family, father/guru/dharma, children, health, "
        "spiritual life, panchanga, nakshatras, vargas, dashas, yogas, avasthas/bala, ashtakavarga, "
        "argala/special points, difficult patterns and practical plan.\n"
        "- For every section include condition_keys/evidence_references/source_traces when the packet has evidence.\n"
        "- Use the chain condition/factor -> shastra reference -> interpretation in source_traces.\n"
    )


def _private_research_scope_rules() -> str:
    return (
        "PRIVATE SHASTRA CORPUS RULES:\n"
        "- source_inventory lists every imported shastra/work available to this private service.\n"
        "- research_context is valid private evidence for this personal analysis; do not ignore it because review_status is research_only.\n"
        "- Search scope is the whole imported SourcePassage corpus; use all relevant works represented in source_inventory/research_context/source_traces.\n"
        "- Put research-only references in source_traces with source_status=research_only; approved status is only required for public release.\n"
        "- When exact chapter/verse is not known, state the work and passage reference honestly instead of inventing verse numbers.\n\n"
    )


def _compatibility_report_contract() -> str:
    return (
        "FULL COMPATIBILITY REPORT CONTRACT:\n"
        f"- Generate minimum {MIN_COMPATIBILITY_REPORT_SECTIONS} sections; do not collapse compatibility into ashtakuta.\n"
        "- Each section body should be developed human-readable explanation, normally 900-1800 characters.\n"
        "- Cover every section in compatibility_report_blueprint: individual chart A, individual chart B, lagna, Moon, "
        "7th house, Venus/Mars, Guru/dharma, family/home/intimacy houses, dashas/timing, ashtakuta as support, risks, "
        "Vaishnava guidance and source logic.\n"
        "- For every section include condition_keys/evidence_references/source_traces when the packet has evidence.\n"
        "- Use the chain condition/factor -> shastra reference -> interpretation in source_traces.\n"
    )


def _compact_packet_for_codex_cli(packet: dict[str, Any]) -> dict[str, Any]:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}
    chart = context.get("chart") if isinstance(context.get("chart"), dict) else {}
    relevant_keys = _relevant_condition_keys(packet)
    return {
        "schema_version": packet.get("schema_version"),
        "status": packet.get("status"),
        "generator_policy": packet.get("generator_policy"),
        "source_inventory": _compact_source_inventory(packet.get("source_inventory") or context.get("source_inventory")),
        "full_report_blueprint": list(FULL_REPORT_SECTION_BLUEPRINT),
        "birth": context.get("birth", {}),
        "place": context.get("place", {}),
        "settings": context.get("settings", {}),
        "chart_facts": context.get("chart_facts", {}),
        "chart_layers": _compact_chart_layers(chart, context.get("person_summary")),
        "person_summary": _compact_person_summary(context.get("person_summary")),
        "selected_profile_context": context.get("selected_profile_context", {}),
        "related_profile_context": context.get("related_profile_context", []),
        "current_period_context": context.get("current_period_context", {}),
        "yoga_coverage": _compact_yoga_coverage(((context.get("chart") or {}).get("classical") or {}).get("yogas")),
        "detected_yoga_source_map": _compact_yoga_source_map(context.get("detected_yoga_source_map", [])),
        "workflow_interpretation_library": context.get("workflow_interpretation_library", {}),
        "jhora_parity_suite": _compact_jhora_parity_suite(context.get("jhora_parity_suite")),
        "sections": _compact_report_sections(context.get("sections", [])),
        "citations": _compact_citations(packet.get("citations", [])),
        "research_context": _compact_research_context(packet.get("research_context")),
        "approved_shastra_citations": _compact_approved_shastra_citations(
            packet.get("approved_shastra_citations")
        ),
        "shastra_coverage_summary": (packet.get("shastra_coverage") or {}).get("summary", {}),
        "shastra_condition_summary": (packet.get("shastra_condition_matrix") or {}).get("summary", {}),
        "shastra_evidence": _compact_evidence(packet.get("shastra_evidence"), relevant_keys),
        "shastra_source_traces": _compact_source_traces(packet.get("shastra_source_traces"), relevant_keys),
        "source_rules": (packet.get("shastra_evidence") or {}).get("prompt_rules", []),
    }


def _compact_compatibility_packet_for_codex_cli(packet: dict[str, Any]) -> dict[str, Any]:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}
    person_a = context.get("person_a") if isinstance(context.get("person_a"), dict) else {}
    person_b = context.get("person_b") if isinstance(context.get("person_b"), dict) else {}
    compatibility = context.get("compatibility") if isinstance(context.get("compatibility"), dict) else {}
    relevant_keys = _compatibility_relevant_condition_keys(packet)
    return {
        "schema_version": packet.get("schema_version"),
        "status": packet.get("status"),
        "generator_policy": packet.get("generator_policy"),
        "source_inventory": _compact_source_inventory(packet.get("source_inventory") or context.get("source_inventory")),
        "compatibility_report_blueprint": list(COMPATIBILITY_REPORT_SECTION_BLUEPRINT),
        "person_a": {
            "input": person_a.get("input", {}),
            "chart": _compact_birth_chart_for_compatibility(person_a.get("chart")),
        },
        "person_b": {
            "input": person_b.get("input", {}),
            "chart": _compact_birth_chart_for_compatibility(person_b.get("chart")),
        },
        "relationship_context": context.get("relationship_context", {}),
        "compatibility": {
            "status": compatibility.get("status"),
            "coverage": compatibility.get("coverage", {}),
            "score": compatibility.get("score", {}),
            "assessment": compatibility.get("assessment", {}),
            "vaishnava_note": compatibility.get("vaishnava_note"),
            "moon": compatibility.get("moon", {}),
            "kuta_rows": compatibility.get("kuta_rows", []),
            "analysis": compatibility.get("analysis", {}),
            "interpretation_plan": compatibility.get("interpretation_plan", {}),
        },
        "citations": _compact_citations(packet.get("citations", [])),
        "research_context": _compact_research_context(packet.get("research_context")),
        "approved_shastra_citations": _compact_approved_shastra_citations(
            packet.get("approved_shastra_citations")
        ),
        "citation_requests": list(packet.get("citation_requests", []) or [])[:20],
        "shastra_coverage_summary": (packet.get("shastra_coverage") or {}).get("summary", {}),
        "shastra_condition_summary": (packet.get("shastra_condition_matrix") or {}).get("summary", {}),
        "shastra_evidence": _compact_evidence(packet.get("shastra_evidence"), relevant_keys),
        "shastra_source_traces": _compact_source_traces(packet.get("shastra_source_traces"), relevant_keys),
        "jhora_parity_suite": _compact_jhora_parity_suite(context.get("jhora_parity_suite")),
        "source_rules": (packet.get("shastra_evidence") or {}).get("prompt_rules", []),
    }


def _compact_birth_chart_for_compatibility(chart: object) -> dict[str, Any]:
    chart_data = chart if isinstance(chart, dict) else {}
    classical = chart_data.get("classical") if isinstance(chart_data.get("classical"), dict) else {}
    return {
        "birth": chart_data.get("birth", {}),
        "place": chart_data.get("place", {}),
        "settings": chart_data.get("settings", {}),
        "ascendant": _compact_graha_position(chart_data.get("ascendant")),
        "grahas": [_compact_graha_position(row) for row in (chart_data.get("grahas") or []) if isinstance(row, dict)][:12],
        "houses": list(chart_data.get("houses") or [])[:12],
        "panchanga": chart_data.get("panchanga", {}),
        "vargas": _compact_key_vargas(chart_data.get("vargas")),
        "dashas": _compact_dashas(chart_data.get("dashas") if isinstance(chart_data.get("dashas"), dict) else {}),
        "classical": {
            "vimshopaka": _compact_body_scores((classical.get("vimshopaka_bala") or {}).get("items")),
            "shadbala": _compact_body_scores((classical.get("shadbala") or {}).get("items")),
            "ashtakavarga": _compact_ashtakavarga(classical.get("ashtakavarga")),
            "argala": classical.get("argala", {}),
            "special_points": _compact_special_points(classical.get("special_points")),
        },
    }


def _compact_graha_position(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    allowed = {
        "body",
        "longitude",
        "rashi",
        "nakshatra",
        "pada",
        "navamsa",
        "house",
        "dignity",
        "retrograde",
    }
    return {key: value.get(key) for key in allowed if key in value}


def _compact_key_vargas(vargas: object) -> dict[str, Any]:
    if not isinstance(vargas, dict):
        return {}
    result: dict[str, Any] = {}
    for code in ("D1", "D7", "D9", "D10", "D12", "D30", "D60"):
        chart = vargas.get(code)
        if not isinstance(chart, dict):
            continue
        result[code] = {
            "name": chart.get("name"),
            "placements": [
                {"body": row.get("body"), "rashi": row.get("rashi")}
                for row in (chart.get("placements") or [])
                if isinstance(row, dict)
            ][:12],
        }
    return result


def _compact_source_inventory(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"summary": {}, "works": []}
    works = []
    for item in (payload.get("works") or [])[:180]:
        if not isinstance(item, dict):
            continue
        works.append(
            {
                "slug": item.get("slug"),
                "title": item.get("title"),
                "author": item.get("author"),
                "edition": item.get("edition"),
                "language_code": item.get("language_code"),
                "source_class": item.get("source_class"),
                "review_status": item.get("review_status"),
                "passage_count": item.get("passage_count"),
                "rights_status": item.get("rights_status"),
            }
        )
    return {
        "schema_version": payload.get("schema_version"),
        "summary": payload.get("summary", {}),
        "works": works,
    }


def _compact_research_context(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"status": "not_configured", "items": []}
    items = []
    for item in (payload.get("items") or [])[:80]:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "title": item.get("title"),
                "work_title": item.get("work_title"),
                "body": _short_text(item.get("body"), 900),
                "review_status": item.get("review_status"),
                "work_review_status": item.get("work_review_status"),
                "rights_status": item.get("rights_status"),
                "public_quote_policy": item.get("public_quote_policy"),
                "is_public_citation": item.get("is_public_citation"),
            }
        )
    return {
        "status": payload.get("status"),
        "public_quote_policy": payload.get("public_quote_policy"),
        "search_scope": payload.get("search_scope"),
        "items": items,
    }


def _compact_person_summary(summary: object) -> dict[str, Any]:
    if not isinstance(summary, dict):
        return {}
    allowed_keys = {
        "birth_context",
        "core_factors",
        "graha_houses",
        "houses",
        "panchanga",
        "dasha",
    }
    return {key: summary[key] for key in allowed_keys if key in summary}


def _compact_chart_layers(chart: object, person_summary: object) -> dict[str, Any]:
    chart_data = chart if isinstance(chart, dict) else {}
    summary = person_summary if isinstance(person_summary, dict) else {}
    classical = chart_data.get("classical") if isinstance(chart_data.get("classical"), dict) else {}
    dashas = chart_data.get("dashas") if isinstance(chart_data.get("dashas"), dict) else {}
    return {
        "graha_positions": list(summary.get("graha_houses") or [])[:12],
        "house_topics": list(summary.get("houses") or [])[:12],
        "detailed_graha_strength_context": _compact_detailed_positions(summary.get("detailed_positions")),
        "vargas": _compact_vargas(chart_data.get("vargas")),
        "dashas": _compact_dashas(dashas),
        "classical": {
            "avasthas": _compact_avasthas((classical.get("avasthas") or {}).get("baladi")),
            "vimshopaka": _compact_body_scores((classical.get("vimshopaka_bala") or {}).get("items")),
            "shadbala": _compact_body_scores((classical.get("shadbala") or {}).get("items")),
            "ashtakavarga": _compact_ashtakavarga(classical.get("ashtakavarga")),
            "argala": classical.get("argala", {}),
            "special_points": _compact_special_points(classical.get("special_points")),
        },
    }


def _compact_detailed_positions(rows: object) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    allowed = {
        "body",
        "chara_karaka",
        "sign_degrees_dms",
        "rashi",
        "rashi_lord",
        "navamsa",
        "nakshatra",
        "pada",
        "house",
        "ruled_houses",
        "dignity",
        "retrograde",
    }
    return [{key: row.get(key) for key in allowed if key in row} for row in rows if isinstance(row, dict)][:12]


def _compact_vargas(vargas: object) -> dict[str, Any]:
    if not isinstance(vargas, dict):
        return {}
    result = {}
    for code, chart in vargas.items():
        if not isinstance(chart, dict):
            continue
        result[str(code)] = {
            "name": chart.get("name"),
            "placements": [
                {
                    "body": row.get("body"),
                    "rashi": row.get("rashi"),
                }
                for row in (chart.get("placements") or [])
                if isinstance(row, dict)
            ][:12],
        }
    return result


def _compact_dashas(dashas: dict[str, Any]) -> dict[str, Any]:
    vimshottari = dashas.get("vimshottari") if isinstance(dashas.get("vimshottari"), dict) else {}
    extra = dashas.get("extra") if isinstance(dashas.get("extra"), dict) else {}
    return {
        "vimshottari": {
            "system": vimshottari.get("system"),
            "mahadashas": list(vimshottari.get("mahadashas") or [])[:12],
        },
        "extra": {
            "status": extra.get("status"),
            "yogini": {
                "mahadashas": list(((extra.get("yogini") or {}).get("mahadashas") or []))[:8],
            }
            if isinstance(extra.get("yogini"), dict)
            else {},
            "ashtottari": extra.get("ashtottari", {}),
        },
    }


def _compact_avasthas(rows: object) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    return [
        {
            "body": row.get("body"),
            "state": row.get("state"),
            "strength": row.get("strength"),
            "degree_band": row.get("degree_band"),
        }
        for row in rows
        if isinstance(row, dict)
    ][:12]


def _compact_body_scores(rows: object) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    compact = []
    for row in rows[:12]:
        if not isinstance(row, dict):
            continue
        compact.append(
            {
                "body": row.get("body"),
                "score": row.get("score"),
                "known_total": row.get("known_total"),
                "percentage": row.get("percentage"),
                "components": row.get("components"),
                "supportive_vargas": row.get("supportive_vargas"),
            }
        )
    return compact


def _compact_ashtakavarga(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    return {
        "status": payload.get("status"),
        "sarva": payload.get("sarva"),
        "bhinna_totals": {
            body: row.get("total")
            for body, row in (payload.get("bhinna") or {}).items()
            if isinstance(row, dict)
        },
    }


def _compact_special_points(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    return {
        "arabic_lots": payload.get("arabic_lots", []),
        "upagrahas": (payload.get("upagrahas") or {}).get("items", []),
        "vedic_points": (payload.get("vedic_points") or {}).get("items", []),
    }


def _compact_jhora_parity_suite(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    return {
        "case_count": payload.get("case_count"),
        "groups": payload.get("groups"),
        "capture_policy": payload.get("capture_policy"),
    }


def _compact_yoga_source_map(rows: object) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    compact = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        compact.append(
            {
                "key": row.get("catalog_key") or row.get("key"),
                "name": row.get("name"),
                "detected_status": row.get("detected_status"),
                "source_mapping_status": row.get("source_mapping_status"),
                "public_release_policy": row.get("public_release_policy"),
                "category": row.get("category"),
                "source_priority": row.get("source_priority", []),
                "formula": _compact_formula(row.get("formula")),
                "source_anchors": _compact_source_anchors(row.get("source_anchors")),
                "source_anchor_status": row.get("source_anchor_status"),
                "definition_scope": row.get("definition_scope"),
                "source_link_count": row.get("source_link_count", 0),
                "evidence_status": row.get("evidence_status"),
                "approved_citation_count": row.get("approved_citation_count", 0),
                "bodies": row.get("bodies", []),
                "reference": row.get("reference"),
            }
        )
    return compact


def _compact_yoga_coverage(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"summary": {}, "detected": [], "pending_formula_sample": []}
    coverage = payload.get("coverage", [])
    if not isinstance(coverage, list):
        coverage = []
    detected = []
    pending = []
    for row in coverage:
        if not isinstance(row, dict):
            continue
        compact_row = {
            "key": row.get("key"),
            "name": row.get("name"),
            "category": row.get("category"),
            "status": row.get("status"),
            "bodies": row.get("bodies", []),
            "source_priority": row.get("source_priority", []),
            "formula": row.get("formula", {}),
        }
        if row.get("present"):
            detected.append(compact_row)
        elif row.get("status") == "formula_pending" and len(pending) < 20:
            pending.append(compact_row)
    return {
        "summary": payload.get("summary", {}),
        "detected": detected,
        "pending_formula_sample": pending,
    }


def _compact_formula(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {
        "description": value.get("description"),
        "status": value.get("status"),
        "source_basis": value.get("source_basis"),
        "anchor_status": value.get("anchor_status"),
    }


def _compact_source_anchors(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    anchors = []
    for anchor in value[:2]:
        if not isinstance(anchor, dict):
            continue
        anchors.append(
            {
                "condition_key": anchor.get("condition_key"),
                "work_title": anchor.get("work_title"),
                "reference": anchor.get("reference"),
                "reference_status": anchor.get("reference_status"),
                "public_quote_policy": anchor.get("public_quote_policy"),
                "source_url": anchor.get("source_url"),
                "condition_formula": str(anchor.get("condition_formula") or "")[:220],
                "source_summary": str(anchor.get("source_summary") or "")[:220],
                "interpretation_hint": str(anchor.get("interpretation_hint") or "")[:220],
            }
        )
    return anchors


def _compact_report_sections(sections: object) -> list[dict[str, Any]]:
    if not isinstance(sections, list):
        return []
    compact = []
    for section in sections:
        if not isinstance(section, dict):
            continue
        compact.append(
            {
                "key": section.get("key"),
                "title": section.get("title"),
                "review_status": section.get("review_status"),
                "body": str(section.get("body") or "")[:500],
                "citation_titles": [
                    str(citation.get("title") or citation.get("work_title") or "")
                    for citation in section.get("citations", [])
                    if isinstance(citation, dict)
                ][:3],
            }
        )
    return compact


def _compact_citations(citations: object) -> list[dict[str, Any]]:
    if not isinstance(citations, list):
        return []
    compact = []
    for citation in citations[:5]:
        if not isinstance(citation, dict):
            continue
        compact.append(
            {
                "title": citation.get("title"),
                "work_title": citation.get("work_title"),
                "public_url": citation.get("public_url"),
                "snippet": str(citation.get("snippet") or "")[:280],
            }
        )
    return compact


def _compact_approved_shastra_citations(payload: object) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"summary": {"approved_evidence_items": 0}, "items": []}
    items = []
    for item in payload.get("items", []) or []:
        if not isinstance(item, dict):
            continue
        items.append(
            {
                "condition_key": item.get("condition_key"),
                "condition_title": item.get("condition_title"),
                "work_title": item.get("work_title"),
                "reference": item.get("reference"),
                "excerpt": str(item.get("excerpt") or "")[:320],
                "public_quote_policy": item.get("public_quote_policy"),
            }
        )
    return {
        "summary": (payload.get("summary") or {}),
        "items": items[:20],
    }


def _relevant_condition_keys(packet: dict[str, Any]) -> set[str]:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}
    keys = {
        "rashi_nakshatra_navamsa",
        "vargas_d2_d60",
        "panchanga",
        "vimshottari",
        "avasthas",
        "ashtakavarga",
        "shadbala",
        "vimshopaka_bala",
        "yogas",
        "argala",
        "upagrahas",
        "special_points",
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


def _compatibility_relevant_condition_keys(packet: dict[str, Any]) -> set[str]:
    context = packet.get("context") if isinstance(packet.get("context"), dict) else {}
    compatibility = context.get("compatibility") if isinstance(context.get("compatibility"), dict) else {}
    analysis = compatibility.get("analysis") if isinstance(compatibility.get("analysis"), dict) else {}
    keys = {
        "compatibility",
        "ashtakuta",
        "vivaha",
        "lagna_and_body",
        "moon_mind_and_dasha_seed",
        "bhava_topics",
        "graha_placements",
        "vimshottari",
        "vaishnava_remedies",
        "seventh_house",
        "shukra_mangala",
        "guru_shukra",
        "dasha_context",
    }
    for perspective in analysis.get("perspectives", []) or []:
        if not isinstance(perspective, dict):
            continue
        key = str(perspective.get("key") or "").strip()
        if key:
            keys.add(key)
    for request in packet.get("citation_requests", []) or []:
        if isinstance(request, dict) and request.get("key"):
            keys.add(str(request["key"]))
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
        "source_anchor": _compact_source_anchor(item.get("source_anchor")),
        "matched_terms": item.get("matched_terms", []),
        "snippet": str(item.get("snippet") or "")[:220],
    }


def _compact_source_anchor(value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    compact = _compact_source_anchors([value])
    return compact[0] if compact else {}


def _compact_source_traces(payload: object, relevant_keys: set[str]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {"traces": []}
    traces = []
    for trace in payload.get("traces", []) or []:
        if not isinstance(trace, dict):
            continue
        condition_key = str(trace.get("condition_key") or "")
        if condition_key not in relevant_keys:
            continue
        source = trace.get("source") if isinstance(trace.get("source"), dict) else {}
        traces.append(
            {
                "condition_key": condition_key,
                "condition_title": trace.get("condition_title"),
                "condition_kind": trace.get("condition_kind"),
                "trigger": trace.get("trigger", {}),
                "work_title": source.get("work_title"),
                "reference": source.get("reference"),
                "chapter": source.get("chapter"),
                "verse": source.get("verse"),
                "reference_status": source.get("reference_status"),
                "public_quote_policy": source.get("public_quote_policy"),
                "source_status": trace.get("source_status"),
                "source_anchor": _compact_source_anchor(source.get("source_anchor")),
                "fragment": str(source.get("fragment") or "")[:240],
                "interpretation_hint": str(trace.get("interpretation_hint") or "")[:240],
            }
        )
    return {
        "schema_version": payload.get("schema_version"),
        "summary": {
            "traces_in_prompt": len(traces),
            "approved_traces_in_prompt": sum(1 for trace in traces if trace.get("source_status") == "approved"),
        },
        "traces": traces[:80],
    }


def _source_policy(private_research_mode: bool) -> str:
    return "private_shastra_research_first" if private_research_mode else "shastra_evidence_first"


def _has_full_report_coverage(output: dict[str, Any]) -> bool:
    sections = output.get("sections")
    return isinstance(sections, list) and len(sections) >= MIN_FULL_REPORT_SECTIONS


def _has_compatibility_report_coverage(output: dict[str, Any]) -> bool:
    sections = output.get("sections")
    return isinstance(sections, list) and len(sections) >= MIN_COMPATIBILITY_REPORT_SECTIONS


def _coverage_status(output: dict[str, Any], private_research_mode: bool) -> str:
    if not private_research_mode:
        return "draft_generation"
    return "full_generation" if _has_full_report_coverage(output) else "incomplete_generation"


def _review_status(private_research_mode: bool, output: dict[str, Any] | None = None) -> str:
    if not private_research_mode:
        return "draft"
    if output is not None and not _has_full_report_coverage(output):
        return "private_partial"
    return "private_final"


def _compatibility_coverage_status(output: dict[str, Any], private_research_mode: bool) -> str:
    if not private_research_mode:
        return "draft_generation"
    return "full_generation" if _has_compatibility_report_coverage(output) else "incomplete_generation"


def _compatibility_review_status(private_research_mode: bool, output: dict[str, Any] | None = None) -> str:
    if not private_research_mode:
        return "draft"
    if output is not None and not _has_compatibility_report_coverage(output):
        return "private_partial"
    return "private_final"


def configured_analysis_runner(prompt: str) -> dict[str, Any] | str:
    return codex_exec_runner(prompt)


def _analysis_provider_metadata(codex_runner: CodexRunner | None) -> tuple[str, str]:
    return "codex_cli", "codex_exec"


def codex_exec_runner(prompt: str) -> str:
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = Path(tmp_dir) / "codex-last-message.json"
        command = [
            "codex",
            "exec",
            "--skip-git-repo-check",
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
