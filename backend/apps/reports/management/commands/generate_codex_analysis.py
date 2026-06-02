from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.interpretations.engine import public_interpretation_sections_for_chart
from apps.sources.citations import combined_citation_search, local_research_corpus_search

from ...codex_cli_generation import generate_birth_chart_codex_cli_analysis


class Command(BaseCommand):
    help = "Generate a birth-chart analysis draft through Codex CLI using matched shastra evidence."

    def add_arguments(self, parser):
        parser.add_argument("--birth-date", required=True)
        parser.add_argument("--birth-time", required=True)
        parser.add_argument("--place-name", required=True)
        parser.add_argument("--timezone")
        parser.add_argument("--latitude")
        parser.add_argument("--longitude")
        parser.add_argument("--as-of-date")
        parser.add_argument("--output")
        parser.add_argument("--skip-evidence-refresh", action="store_true")

    def handle(self, *args, **options):
        result = generate_birth_chart_codex_cli_analysis(
            _birth_data(options),
            citation_search=_vl_citation_search,
            research_search=local_research_corpus_search,
            interpretation_provider=public_interpretation_sections_for_chart,
            refresh_evidence=not bool(options["skip_evidence_refresh"]),
        )
        if options.get("output"):
            output_path = Path(options["output"])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(
            self.style.SUCCESS(
                f"Generated Codex CLI analysis draft #{result['id']} with {len(result.get('sections', []))} sections."
            )
        )


def _birth_data(options: dict[str, Any]) -> dict[str, Any]:
    data = {
        "birth_date": options["birth_date"],
        "birth_time": options["birth_time"],
        "place_name": options["place_name"],
    }
    for key in ("timezone", "latitude", "longitude", "as_of_date"):
        if options.get(key) not in {None, ""}:
            data[key] = options[key]
    return data


def _vl_citation_search(query: str) -> list[dict[str, object]]:
    return combined_citation_search(
        settings.VL_DATABASE_URL,
        query,
        limit=3,
        public_base_url=settings.VL_PUBLIC_BASE_URL,
    )
