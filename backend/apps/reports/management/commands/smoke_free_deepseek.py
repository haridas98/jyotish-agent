from __future__ import annotations

import json
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.reports import deepseek_generation
from apps.reports.draft_generation import DraftGenerationUnavailable


DEFAULT_PROMPT = (
    'Return only valid JSON: {"language":"ru","sections":[{"title":"Smoke","body":"ok","citation_titles":[]}]}'
)


class Command(BaseCommand):
    help = "Run a minimal FreeDeepseekAPI smoke check and print a JSON status payload."

    def add_arguments(self, parser):
        parser.add_argument("--prompt", default=DEFAULT_PROMPT)

    def handle(self, *args, **options):
        try:
            raw_output = deepseek_generation.free_deepseek_chat_client()(options["prompt"])
            normalized = deepseek_generation._normalize_deepseek_output(raw_output)
        except DraftGenerationUnavailable as exc:
            raise CommandError(f"DeepSeek smoke failed: {exc}") from exc

        sections = normalized.get("sections")
        if not isinstance(sections, list):
            sections = []
        payload = {
            "status": "ok",
            "provider": "free_deepseek",
            "model": settings.FREE_DEEPSEEK_MODEL,
            "section_count": len(sections),
            "message_excerpt": _message_excerpt(raw_output, sections),
        }
        self.stdout.write(json.dumps(payload, ensure_ascii=False))


def _message_excerpt(raw_output: Any, sections: list[Any]) -> str:
    for section in sections:
        if isinstance(section, dict) and isinstance(section.get("body"), str):
            return section["body"][:240]
    if isinstance(raw_output, str):
        return raw_output[:240]
    return ""
