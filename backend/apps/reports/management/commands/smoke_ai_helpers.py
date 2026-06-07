from __future__ import annotations

import json
from typing import Any, Callable

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.reports import deepseek_generation, nemotron_generation, qwen_generation
from apps.reports.draft_generation import DraftGenerationUnavailable, _normalize_llm_output


DEFAULT_PROMPT = (
    'Return only valid JSON: {"language":"ru","sections":[{"title":"Smoke","body":"ok","citation_titles":[]}]}'
)
DEFAULT_PROVIDERS = "qwen,free_deepseek,nemotron"

ProviderRunner = Callable[[str], str | dict[str, Any]]


class Command(BaseCommand):
    help = "Run minimal smoke checks for AI helper providers."

    def add_arguments(self, parser):
        parser.add_argument("--prompt", default=DEFAULT_PROMPT)
        parser.add_argument(
            "--providers",
            default=DEFAULT_PROVIDERS,
            help="Comma-separated provider keys: qwen,free_deepseek,nemotron.",
        )
        parser.add_argument("--continue-on-error", action="store_true")

    def handle(self, *args, **options):
        provider_keys = _provider_keys(options["providers"])
        results = [_smoke_provider(key, str(options["prompt"])) for key in provider_keys]
        payload = {
            "status": "ok" if all(result["status"] == "ok" for result in results) else "failed",
            "results": results,
        }
        self.stdout.write(json.dumps(payload, ensure_ascii=False))
        if payload["status"] != "ok" and not options["continue_on_error"]:
            failed = ", ".join(result["provider"] for result in results if result["status"] != "ok")
            raise CommandError(f"AI helper smoke failed: {failed}")


def _provider_keys(value: str) -> list[str]:
    keys = [item.strip() for item in value.split(",") if item.strip()]
    if not keys:
        raise CommandError("At least one provider is required")
    unknown = [key for key in keys if key not in {"qwen", "free_deepseek", "nemotron"}]
    if unknown:
        raise CommandError(f"Unknown AI helper provider(s): {', '.join(unknown)}")
    return keys


def _smoke_provider(provider: str, prompt: str) -> dict[str, Any]:
    try:
        raw_output = _runner(provider)(prompt)
        normalized = _normalize_llm_output(raw_output)
        sections = normalized.get("sections") if isinstance(normalized.get("sections"), list) else []
        return {
            "status": "ok",
            "provider": provider,
            "model": _model(provider),
            "section_count": len(sections),
            "message_excerpt": _message_excerpt(raw_output, sections),
        }
    except DraftGenerationUnavailable as exc:
        return {
            "status": "failed",
            "provider": provider,
            "model": _model(provider),
            "error": str(exc),
            "setup_hint": _setup_hint(provider),
        }


def _runner(provider: str) -> ProviderRunner:
    if provider == "qwen":
        return qwen_generation.qwen_chat_completions_client()
    if provider == "free_deepseek":
        return deepseek_generation.free_deepseek_chat_client()
    if provider == "nemotron":
        return nemotron_generation.nemotron_chat_completions_client()
    raise CommandError(f"Unknown AI helper provider: {provider}")


def _model(provider: str) -> str:
    if provider == "qwen":
        return settings.QWEN_MODEL
    if provider == "free_deepseek":
        return settings.FREE_DEEPSEEK_MODEL
    if provider == "nemotron":
        return settings.NEMOTRON_MODEL
    return ""


def _setup_hint(provider: str) -> str:
    if provider == "qwen":
        return "Run FreeQwenApi and set QWEN_API_BASE_URL/QWEN_MODEL in backend .env."
    if provider == "free_deepseek":
        return "Run FreeDeepseekAPI and set FREE_DEEPSEEK_API_BASE_URL/FREE_DEEPSEEK_MODEL in backend .env."
    if provider == "nemotron":
        return "Set OPENROUTER_API_KEY and NEMOTRON_MODEL in backend .env."
    return ""


def _message_excerpt(raw_output: Any, sections: list[Any]) -> str:
    for section in sections:
        if isinstance(section, dict) and isinstance(section.get("body"), str):
            return section["body"][:240]
    if isinstance(raw_output, str):
        return raw_output[:240]
    return ""
