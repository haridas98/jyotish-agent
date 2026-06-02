import json

import pytest
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition
from apps.calculations.primitives import zodiac_placement
from apps.reports.models import GeneratedAnalysisDraft


class CliProvider:
    def planet_positions(self, moment, bodies, settings):
        return {
            "Surya": BodyPosition(
                body="Surya",
                longitude=120.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(120.0),
            ),
            "Chandra": BodyPosition(
                body="Chandra",
                longitude=132.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=1.0,
                placement=zodiac_placement(132.0),
            ),
            "Shani": BodyPosition(
                body="Shani",
                longitude=280.0,
                latitude=0.0,
                distance_au=1.0,
                speed_longitude=0.1,
                placement=zodiac_placement(280.0),
            ),
        }

    def ascendant_position(self, moment, latitude, longitude, settings):
        return BodyPosition(
            body="Lagna",
            longitude=90.0,
            latitude=None,
            distance_au=None,
            speed_longitude=None,
            placement=zodiac_placement(90.0),
        )


@pytest.mark.django_db
def test_generate_birth_chart_codex_cli_analysis_sends_evidence_prompt_and_saves_draft():
    from apps.reports.codex_cli_generation import generate_birth_chart_codex_cli_analysis

    captured = {}

    def fake_runner(prompt: str) -> str:
        captured["prompt"] = prompt
        return json.dumps(
            {
                "review_status": "approved",
                "language": "ru",
                "sections": [
                    {
                        "title": "Карта",
                        "body": "Черновик по карте.",
                        "citation_titles": [],
                        "review_notes": [],
                    }
                ],
            }
        )

    result = generate_birth_chart_codex_cli_analysis(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=CliProvider(),
        codex_runner=fake_runner,
        refresh_evidence=False,
    )

    assert result["review_status"] == "draft"
    assert result["source_policy"] == "shastra_evidence_first"
    assert result["kind"] == "birth_chart_codex_cli"
    assert "shastra_evidence" in captured["prompt"]
    assert "условие -> фрагмент -> ссылка -> интерпретация" in captured["prompt"]
    record = GeneratedAnalysisDraft.objects.get()
    assert record.provider == "codex_cli"
    assert record.output_json["review_status"] == "draft"
    assert "prompt_markdown" not in record.packet_snapshot


def test_codex_exec_runner_uses_utf8_for_unicode_prompt(monkeypatch, tmp_path):
    from apps.reports.codex_cli_generation import codex_exec_runner

    class Completed:
        returncode = 0
        stdout = '{"sections":[]}'
        stderr = ""

    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return Completed()

    monkeypatch.setattr("apps.reports.codex_cli_generation.subprocess.run", fake_run)
    monkeypatch.setattr("apps.reports.codex_cli_generation.tempfile.TemporaryDirectory", lambda: _Tmp(tmp_path))

    result = codex_exec_runner("текст £")

    assert result == '{"sections":[]}'
    assert captured["kwargs"]["encoding"] == "utf-8"
    assert captured["kwargs"]["errors"] == "replace"
    assert "--ask-for-approval" not in captured["command"]


def test_render_codex_cli_analysis_prompt_compacts_large_evidence_payload():
    from apps.reports.codex_cli_generation import render_codex_cli_analysis_prompt

    packet = {
        "schema_version": "jyotish-analysis-packet-v1",
        "context": {
            "birth": {"date": "2000-01-01"},
            "place": {"label": "Vrindavan"},
            "chart_facts": {},
            "person_summary": {},
            "detected_yoga_source_map": [{"key": "gaja_kesari"}],
        },
        "shastra_evidence": {
            "conditions": [
                {
                    "condition_key": "gaja_kesari",
                    "evidence": [{"snippet": "Gaja " + ("x" * 2000), "inferred_reference": "Sloka 16"}],
                },
                {
                    "condition_key": "irrelevant",
                    "evidence": [{"snippet": "SHOULD_NOT_BE_INCLUDED", "inferred_reference": "Sloka 1"}],
                },
            ]
        },
        "citations": [],
        "research_context": {"items": [{"body": "not for cli"}]},
    }

    prompt = render_codex_cli_analysis_prompt(packet)

    assert "gaja_kesari" in prompt
    assert "SHOULD_NOT_BE_INCLUDED" not in prompt
    assert len(prompt) < 12000


def test_compact_codex_packet_removes_verbose_catalog_fields_and_shortens_snippets():
    from apps.reports.codex_cli_generation import _compact_packet_for_codex_cli

    packet = {
        "context": {
            "detected_yoga_source_map": [
                {
                    "key": "ruchaka_mahapurusha",
                    "catalog_key": "ruchaka_mahapurusha",
                    "name": "Ruchaka Mahapurusha",
                    "detected_status": "calculated_needs_citation",
                    "public_explanation_outline": "verbose outline should not enter prompt",
                    "vaishnava_guard": "verbose guard should not enter prompt",
                    "bodies": ["Mangala"],
                }
            ],
            "person_summary": {
                "core_factors": [{"label": "Lagna", "value": "Karka"}],
                "detailed_positions": [{"body": "Surya", "sign_degrees_dms": "long detail"}],
            },
        },
        "shastra_evidence": {
            "conditions": [
                {
                    "condition_key": "ruchaka_mahapurusha",
                    "evidence": [
                        {
                            "snippet": "M" * 1000,
                            "work_title": "Phaladipika",
                            "inferred_reference": "Sloka 1",
                        }
                    ],
                }
            ]
        },
    }

    compact = _compact_packet_for_codex_cli(packet)
    rendered = json.dumps(compact, ensure_ascii=False)

    assert "verbose outline should not enter prompt" not in rendered
    assert "verbose guard should not enter prompt" not in rendered
    assert "detailed_positions" not in rendered
    assert "M" * 400 not in rendered


@pytest.mark.django_db
def test_generate_codex_analysis_command_writes_output(monkeypatch, tmp_path):
    output_path = tmp_path / "analysis.json"

    def fake_generate(data, **kwargs):
        assert data["birth_date"] == "2000-01-01"
        assert kwargs["refresh_evidence"] is False
        return {
            "id": 9,
            "kind": "birth_chart_codex_cli",
            "review_status": "draft",
            "source_policy": "shastra_evidence_first",
            "sections": [{"title": "Карта", "body": "Черновик."}],
        }

    monkeypatch.setattr(
        "apps.reports.management.commands.generate_codex_analysis.generate_birth_chart_codex_cli_analysis",
        fake_generate,
    )

    call_command(
        "generate_codex_analysis",
        "--birth-date",
        "2000-01-01",
        "--birth-time",
        "15:30",
        "--place-name",
        "Vrindavan",
        "--skip-evidence-refresh",
        "--output",
        str(output_path),
    )

    assert '"kind": "birth_chart_codex_cli"' in output_path.read_text(encoding="utf-8")


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_codex_analysis_api_returns_saved_draft(monkeypatch):
    captured = {}

    def fake_generate(
        data,
        citation_search=None,
        research_search=None,
        interpretation_provider=None,
        refresh_evidence=True,
    ):
        captured["refresh_evidence"] = refresh_evidence
        return {
            "id": 12,
            "kind": "birth_chart_codex_cli",
            "review_status": "draft",
            "source_policy": "shastra_evidence_first",
            "sections": [{"title": "Codex", "body": "Draft.", "evidence_references": []}],
        }

    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda data, citation_search=None, research_search=None, interpretation_provider=None: {
            "id": 12,
            "kind": "birth_chart_codex_cli",
            "review_status": "draft",
            "source_policy": "shastra_evidence_first",
            "sections": [{"title": "Карта", "body": "Черновик.", "evidence_references": []}],
        },
    )

    monkeypatch.setattr("apps.reports.views.generate_birth_chart_codex_cli_analysis", fake_generate)

    response = APIClient().post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "birth_chart_codex_cli"
    assert captured["refresh_evidence"] is False


class _Tmp:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return str(self.path)

    def __exit__(self, exc_type, exc, tb):
        return False
