import json
from datetime import date, time, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition
from apps.calculations.primitives import zodiac_placement
from apps.charts.models import BirthProfile, Place
from apps.reports.models import GeneratedAnalysisDraft, GeneratedAnalysisJob


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


def _codex_api_place() -> Place:
    return Place.objects.create(
        name="Vrindavan",
        country_code="IN",
        latitude="27.565000",
        longitude="77.659000",
        timezone_name="Asia/Kolkata",
    )


def _codex_api_self_profile(user) -> BirthProfile:
    return BirthProfile.objects.create(
        user=user,
        display_name="My chart",
        birth_date=date(2000, 1, 1),
        birth_time=time(15, 30),
        birth_time_accuracy=BirthProfile.TimeAccuracy.EXACT,
        place=_codex_api_place(),
        timezone_name="Asia/Kolkata",
        is_self_profile=True,
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

    assert result["review_status"] == "private_partial"
    assert result["source_policy"] == "private_shastra_research_first"
    assert result["kind"] == "birth_chart_codex_cli"
    assert "shastra_evidence" in captured["prompt"]
    assert "PRIVATE RESEARCH MODE" in captured["prompt"]
    assert "body пиши как понятный текст для человека" in captured["prompt"]
    assert "техническую цепочку условие -> источник -> вывод клади только в source_traces" in captured["prompt"]
    record = GeneratedAnalysisDraft.objects.get()
    assert record.provider == "codex_cli"
    assert record.source_policy == "private_shastra_research_first"
    assert record.review_status == "private_partial"
    assert record.output_json["review_status"] == "private_partial"
    assert "prompt_markdown" not in record.packet_snapshot


@pytest.mark.django_db
@override_settings(CODEX_ANALYSIS_PROVIDER="openai", OPENAI_MODEL="gpt-test")
def test_generate_birth_chart_codex_cli_analysis_ignores_openai_provider_setting(monkeypatch):
    from apps.reports import codex_cli_generation

    sections = [
        {"title": f"Section {index}", "body": "body", "citation_titles": [], "review_notes": []}
        for index in range(codex_cli_generation.MIN_FULL_REPORT_SECTIONS)
    ]
    monkeypatch.setattr(
        codex_cli_generation,
        "codex_exec_runner",
        lambda prompt: {"sections": sections},
    )

    result = codex_cli_generation.generate_birth_chart_codex_cli_analysis(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "timezone": "Asia/Kolkata",
            "latitude": 27.583,
            "longitude": 77.7,
        },
        provider=CliProvider(),
        refresh_evidence=False,
    )

    record = GeneratedAnalysisDraft.objects.get(id=result["id"])
    assert result["review_status"] == "private_final"
    assert record.provider == "codex_cli"
    assert record.model == "codex_exec"


@pytest.mark.django_db
def test_generate_birth_chart_codex_cli_analysis_public_mode_stays_draft():
    from apps.reports.codex_cli_generation import generate_birth_chart_codex_cli_analysis

    result = generate_birth_chart_codex_cli_analysis(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=CliProvider(),
        codex_runner=lambda prompt: '{"sections":[]}',
        refresh_evidence=False,
        private_research_mode=False,
    )

    assert result["review_status"] == "draft"
    assert result["source_policy"] == "shastra_evidence_first"
    assert GeneratedAnalysisDraft.objects.get().review_status == "draft"


@pytest.mark.django_db
def test_generate_birth_chart_codex_cli_analysis_retries_short_private_report_and_marks_partial_if_still_short():
    from apps.reports.codex_cli_generation import generate_birth_chart_codex_cli_analysis

    prompts = []

    def short_runner(prompt: str) -> str:
        prompts.append(prompt)
        return json.dumps(
            {
                "language": "ru",
                "sections": [
                    {
                        "title": "Коротко",
                        "body": "Недостаточно для полной карты.",
                        "citation_titles": [],
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
        codex_runner=short_runner,
        refresh_evidence=False,
    )

    assert len(prompts) == 2
    assert "FULL REPORT CONTRACT" in prompts[0]
    assert "minimum 22 sections" in prompts[0]
    assert "EXPAND INCOMPLETE REPORT" in prompts[1]
    assert result["review_status"] == "private_partial"
    assert result["coverage_status"] == "incomplete_generation"


@pytest.mark.django_db
def test_generate_birth_chart_codex_cli_analysis_reuses_cached_full_private_report(monkeypatch):
    from apps.reports import codex_cli_generation

    data = {"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"}
    sections = [
        {"title": f"section {index}", "body": "body", "source_traces": []}
        for index in range(codex_cli_generation.MIN_FULL_REPORT_SECTIONS)
    ]
    record = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot=data,
        output_json={"review_status": "private_final", "sections": sections},
    )

    def fail_runner(prompt: str) -> str:
        raise AssertionError("Codex CLI should not run when a full cached report exists")

    monkeypatch.setattr(codex_cli_generation, "codex_exec_runner", fail_runner)

    result = codex_cli_generation.generate_birth_chart_codex_cli_analysis(data, refresh_evidence=False)

    assert result["id"] == record.id
    assert result["review_status"] == "private_final"
    assert result["coverage_status"] == "full_generation"
    assert len(result["sections"]) == codex_cli_generation.MIN_FULL_REPORT_SECTIONS


@pytest.mark.django_db
def test_generate_birth_chart_codex_cli_analysis_skips_incomplete_cached_report(monkeypatch):
    from apps.reports import codex_cli_generation

    data = {"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"}
    full_sections = [
        {"title": f"section {index}", "body": "body", "source_traces": []}
        for index in range(codex_cli_generation.MIN_FULL_REPORT_SECTIONS)
    ]
    full_record = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot=data,
        output_json={"review_status": "private_final", "sections": full_sections},
    )
    GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot=data,
        output_json={"review_status": "private_final", "sections": [{"title": "short", "body": "body"}]},
    )

    def fail_runner(prompt: str) -> str:
        raise AssertionError("Codex CLI should not run when an older full cached report exists")

    monkeypatch.setattr(codex_cli_generation, "codex_exec_runner", fail_runner)

    result = codex_cli_generation.generate_birth_chart_codex_cli_analysis(data, refresh_evidence=False)

    assert result["id"] == full_record.id
    assert result["coverage_status"] == "full_generation"
    assert len(result["sections"]) == codex_cli_generation.MIN_FULL_REPORT_SECTIONS


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
            "detected_yoga_source_map": [
                {
                    "key": "gaja_kesari",
                    "formula": {"description": "Guru is in a kendra from Chandra."},
                    "source_anchor_status": "exact_verse_verified",
                    "source_anchors": [
                        {
                            "condition_key": "gaja_kesari",
                            "work_title": "Brhat Parashara Hora Shastra",
                            "reference": "Chapter 36, Verses 3-4",
                            "reference_status": "exact_verse_verified",
                            "source_url": "https://example.test/bphs/gaja",
                            "condition_formula": "Jupiter in kendra from Moon.",
                            "source_summary": "Gaja Kesari source summary.",
                            "interpretation_hint": "Protective intelligence.",
                        }
                    ],
                }
            ],
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
    assert len(prompt) < 36000


def test_render_codex_cli_analysis_prompt_private_mode_uses_research_traces():
    from apps.reports.codex_cli_generation import render_codex_cli_analysis_prompt

    packet = {
        "schema_version": "jyotish-analysis-packet-v1",
        "context": {
            "birth": {"date": "2000-01-01"},
            "place": {"label": "Vrindavan"},
            "chart_facts": {},
            "person_summary": {},
            "detected_yoga_source_map": [
                {
                    "key": "gaja_kesari",
                    "source_anchor_status": "exact_verse_verified",
                    "source_anchors": [
                        {
                            "condition_key": "gaja_kesari",
                            "work_title": "Brhat Parashara Hora Shastra",
                            "reference": "Chapter 36, Verses 3-4",
                            "reference_status": "exact_verse_verified",
                            "source_url": "https://example.test/bphs/gaja",
                            "condition_formula": "Jupiter in kendra from Moon.",
                            "source_summary": "Gaja Kesari source summary.",
                            "interpretation_hint": "Protective intelligence.",
                        }
                    ],
                }
            ],
        },
        "approved_shastra_citations": {"summary": {"approved_evidence_items": 0}, "items": []},
        "shastra_evidence": {
            "conditions": [
                {
                    "condition_key": "gaja_kesari",
                    "condition_title": "Gaja Kesari",
                    "evidence": [
                        {
                            "snippet": "Adhyaya 6. Sloka 16. Gaja Kesari yoga wording.",
                            "work_title": "Phaladipika",
                            "inferred_reference": "Adhyaya 6, Sloka 16",
                            "reference_status": "inferred_needs_review",
                            "review_status": "research_only",
                            "public_quote_policy": "blocked_until_approved",
                        }
                    ],
                }
            ]
        },
        "shastra_source_traces": {
            "traces": [
                {
                    "condition_key": "gaja_kesari",
                    "condition_title": "Gaja Kesari",
                    "condition_kind": "yoga_condition",
                    "trigger": {"kind": "yoga"},
                    "source": {
                        "work_title": "Phaladipika",
                        "reference": "Adhyaya 6, Sloka 16",
                        "chapter": "Adhyaya 6",
                        "verse": "Sloka 16",
                        "reference_status": "inferred_needs_review",
                        "public_quote_policy": "blocked_until_approved",
                        "fragment": "Gaja Kesari yoga wording.",
                    },
                    "source_status": "inferred_needs_review",
                    "interpretation_hint": "Jupiter in kendra from Moon.",
                }
            ]
        },
        "citations": [],
    }

    prompt = render_codex_cli_analysis_prompt(packet, private_research_mode=True)

    assert "PRIVATE RESEARCH MODE" in prompt
    assert "research-only фрагменты можно использовать" in prompt
    assert '"source_traces"' in prompt
    assert '"source_anchors"' in prompt
    assert "Chapter 36, Verses 3-4" in prompt
    assert "Adhyaya 6, Sloka 16" in prompt
    assert "Gaja Kesari yoga wording" in prompt
    assert "Jupiter in kendra from Moon" in prompt


def test_render_codex_cli_analysis_prompt_requires_human_readable_body():
    from apps.reports.codex_cli_generation import render_codex_cli_analysis_prompt

    packet = {
        "schema_version": "jyotish-analysis-packet-v1",
        "context": {
            "birth": {"date": "2000-01-01"},
            "place": {"label": "Vrindavan"},
            "chart_facts": {},
            "person_summary": {},
            "detected_yoga_source_map": [],
        },
        "shastra_evidence": {"conditions": []},
        "citations": [],
    }

    prompt = render_codex_cli_analysis_prompt(packet)

    assert '"review_status": "private_final"' in prompt
    assert "FULL REPORT CONTRACT" in prompt
    assert "minimum 22 sections" in prompt
    assert "career_and_work" in prompt
    assert "marriage_and_relationships" in prompt
    assert "body пиши как понятный текст для человека" in prompt
    assert "не начинай body словами Условие" in prompt
    assert '"key_points"' in prompt
    assert '"practical_steps"' in prompt


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
                    "formula": {"description": "Mangala in kendra in own or exaltation sign."},
                    "source_anchor_status": "exact_verse_verified",
                    "source_anchors": [
                        {
                            "work_title": "Brhat Jataka",
                            "reference": "Chapter 1",
                            "reference_status": "exact_verse_verified",
                            "source_summary": "Ruchaka source summary.",
                            "interpretation_hint": "Judge strength.",
                        }
                    ],
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

    assert compact["full_report_blueprint"][0]["key"] == "birth_context_and_method"
    assert len(compact["full_report_blueprint"]) >= 22
    assert "chart_layers" in compact
    assert "verbose outline should not enter prompt" not in rendered
    assert "verbose guard should not enter prompt" not in rendered
    assert "detailed_positions" not in rendered
    assert "M" * 400 not in rendered
    assert "Ruchaka source summary" in rendered
    assert "Mangala in kendra" in rendered


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
def test_generate_compatibility_codex_cli_analysis_saves_full_private_report():
    from apps.reports import codex_cli_generation

    captured = {}
    sections = [
        {
            "title": f"Раздел {index}",
            "body": "Полный разбор совместимости двух карт.",
            "citation_titles": [],
            "source_traces": [],
        }
        for index in range(codex_cli_generation.MIN_COMPATIBILITY_REPORT_SECTIONS)
    ]

    def fake_runner(prompt: str) -> str:
        captured["prompt"] = prompt
        return json.dumps({"language": "ru", "sections": sections})

    result = codex_cli_generation.generate_compatibility_codex_cli_analysis(
        {
            "person_a": {
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
            },
            "person_b": {
                "birth_date": "2001-02-03",
                "birth_time": "09:10",
                "place_name": "Mayapur",
            },
        },
        provider=CliProvider(),
        codex_runner=fake_runner,
        refresh_evidence=False,
    )

    assert result["kind"] == "compatibility_codex_cli"
    assert result["review_status"] == "private_final"
    assert result["coverage_status"] == "full_generation"
    assert "Ashtakuta is only one supporting metric" in captured["prompt"]
    assert "compatibility_report_blueprint" in captured["prompt"]
    record = GeneratedAnalysisDraft.objects.get(kind="compatibility_codex_cli")
    assert record.provider == "codex_cli"
    assert record.review_status == "private_final"
    assert "prompt_markdown" not in record.packet_snapshot


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_compatibility_codex_analysis_api_returns_saved_draft(monkeypatch):
    user = get_user_model().objects.create_user(username="compat-generate-owner", password="strong-pass-108")
    captured = {}

    def fake_generate(data, citation_search=None, research_search=None, refresh_evidence=True, user=None):
        captured["refresh_evidence"] = refresh_evidence
        return {
            "id": 44,
            "kind": "compatibility_codex_cli",
            "review_status": "private_final",
            "source_policy": "private_shastra_research_first",
            "sections": [{"title": "Совместимость", "body": "Полный разбор.", "citation_titles": []}],
        }

    monkeypatch.setattr("apps.reports.views.generate_compatibility_codex_cli_analysis", fake_generate)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/compatibility/codex-analysis",
        {
            "person_a": {
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
            },
            "person_b": {
                "birth_date": "2001-02-03",
                "birth_time": "09:10",
                "place_name": "Mayapur",
            },
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "compatibility_codex_cli"
    assert captured["refresh_evidence"] is False


@pytest.mark.django_db
def test_compatibility_codex_analysis_api_requires_authentication():
    response = APIClient().post(
        "/api/reports/compatibility/codex-analysis",
        {
            "person_a": {"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
            "person_b": {"birth_date": "2001-02-03", "birth_time": "09:10", "place_name": "Mayapur"},
        },
        format="json",
    )

    assert response.status_code in {401, 403}


@pytest.mark.django_db
def test_ask_compatibility_codex_analysis_uses_saved_pair_report_and_saves_answer():
    from apps.reports.codex_cli_generation import ask_compatibility_codex_cli_analysis

    report = GeneratedAnalysisDraft.objects.create(
        kind="compatibility_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot={
            "person_a": {"birth_date": "2000-01-01"},
            "person_b": {"birth_date": "2001-02-03"},
        },
        packet_snapshot={
            "schema_version": "jyotish-compatibility-analysis-packet-v1",
            "context": {
                "compatibility": {
                    "score": {"total": 22, "max": 36},
                    "analysis": {"perspectives": [{"key": "seventh_house", "status": "mixed"}]},
                }
            },
        },
        output_json={
            "sections": [
                {
                    "title": "7 дом",
                    "body": "Есть смешанный показатель по браку, требуется зрелое общение.",
                    "source_traces": [
                        {
                            "condition_key": "seventh_house",
                            "work_title": "Vivaha source",
                            "reference": "1.1",
                            "source_status": "research_only",
                            "short_excerpt": "marriage factor",
                            "interpretation": "смотреть 7 дом",
                        }
                    ],
                }
            ]
        },
    )
    prompts = []

    def fake_runner(prompt: str) -> str:
        prompts.append(prompt)
        return json.dumps(
            {
                "answer": "По совместимости главный фокус: спокойно проверить 7 дом и даши, не делать вывод только по ашта-куте.",
                "source_traces": [{"condition_key": "seventh_house", "work_title": "Vivaha source", "reference": "1.1"}],
            }
        )

    result = ask_compatibility_codex_cli_analysis(
        analysis_id=report.id,
        question="Стоит ли рассматривать брак?",
        codex_runner=fake_runner,
    )

    assert result["kind"] == "compatibility_codex_cli_chat"
    assert result["analysis_id"] == report.id
    assert "ашта-куте" in result["answer"]
    assert "Стоит ли рассматривать брак?" in prompts[0]
    assert "SAVED COMPATIBILITY ANALYSIS JSON" in prompts[0]
    assert "seventh_house" in prompts[0]
    chat = GeneratedAnalysisDraft.objects.get(kind="compatibility_codex_cli_chat")
    assert chat.input_snapshot["analysis_id"] == report.id
    assert chat.output_json["answer"] == result["answer"]


@pytest.mark.django_db
def test_compatibility_codex_analysis_chat_api_returns_answer(monkeypatch):
    user = get_user_model().objects.create_user(username="compat-chat-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="compatibility_codex_cli",
        review_status="private_final",
        input_snapshot={"person_a": {}, "person_b": {}},
        output_json={"sections": [{"title": "Совместимость", "body": "Есть данные."}]},
    )

    monkeypatch.setattr(
        "apps.reports.views.ask_compatibility_codex_cli_analysis",
        lambda analysis_id, question, history=None, user=None: {
            "kind": "compatibility_codex_cli_chat",
            "analysis_id": analysis_id,
            "question": question,
            "answer": "Ответ по совместимости.",
            "history_used": len(history or []),
            "source_traces": [],
        },
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/compatibility/codex-analysis/chat",
        {"analysis_id": report.id, "question": "Что по браку?", "history": [{"role": "user", "content": "Привет"}]},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "compatibility_codex_cli_chat"
    assert response.data["analysis_id"] == report.id
    assert response.data["history_used"] == 1


@pytest.mark.django_db
def test_compatibility_codex_analysis_chat_api_rejects_duplicate_running_answer(monkeypatch):
    user = get_user_model().objects.create_user(username="compat-chat-lock-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="compatibility_codex_cli",
        review_status="private_final",
        input_snapshot={"person_a": {}, "person_b": {}},
        output_json={"sections": [{"title": "Compatibility", "body": "Saved body."}]},
    )
    cache.clear()
    monkeypatch.setattr("apps.reports.views.cache.add", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        "apps.reports.views.ask_compatibility_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("compatibility chat must not run while lock is active"),
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/compatibility/codex-analysis/chat",
        {"analysis_id": report.id, "question": "What about marriage?"},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["error"] == "analysis_chat_in_progress"


@pytest.mark.django_db
def test_compatibility_codex_analysis_chat_rejects_other_users_report(monkeypatch):
    owner = get_user_model().objects.create_user(username="compat-direct-owner", password="strong-pass-108")
    viewer = get_user_model().objects.create_user(username="compat-direct-viewer", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=owner,
        kind="compatibility_codex_cli",
        review_status="private_final",
        input_snapshot={"person_a": {}, "person_b": {}},
        output_json={"sections": [{"title": "Private pair", "body": "Owner only."}]},
    )
    monkeypatch.setattr(
        "apps.reports.views.ask_compatibility_codex_cli_analysis",
        lambda **kwargs: {"answer": "Should not run"},
    )
    client = APIClient()
    client.force_authenticate(user=viewer)

    response = client.post(
        "/api/reports/compatibility/codex-analysis/chat",
        {"analysis_id": report.id, "question": "Read it?"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_codex_analysis_api_returns_saved_draft(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-generate-owner", password="strong-pass-108")
    profile = _codex_api_self_profile(user)
    captured = {}

    def fake_generate(
        data,
        citation_search=None,
        research_search=None,
        interpretation_provider=None,
        refresh_evidence=True,
        force_regenerate=False,
        user=None,
    ):
        captured["refresh_evidence"] = refresh_evidence
        captured["force_regenerate"] = force_regenerate
        return {
            "id": 12,
            "kind": "birth_chart_codex_cli",
            "review_status": "draft",
            "source_policy": "shastra_evidence_first",
            "sections": [{"title": "Codex", "body": "Draft.", "evidence_references": []}],
        }

    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
            lambda data, citation_search=None, research_search=None, interpretation_provider=None, force_regenerate=False, user=None: {
            "id": 12,
            "kind": "birth_chart_codex_cli",
            "review_status": "draft",
            "source_policy": "shastra_evidence_first",
            "sections": [{"title": "Карта", "body": "Черновик.", "evidence_references": []}],
        },
    )

    monkeypatch.setattr("apps.reports.views.generate_birth_chart_codex_cli_analysis", fake_generate)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
            {
                "profile_id": profile.id,
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["kind"] == "birth_chart_codex_cli"
    assert captured["refresh_evidence"] is False
    assert captured["force_regenerate"] is False
    job = GeneratedAnalysisJob.objects.get(user=user, kind="birth_chart_codex_cli")
    assert job.status == GeneratedAnalysisJob.Status.COMPLETE
    assert job.input_summary == {
        "birth_date": "2000-01-01",
        "birth_time": "15:30",
        "place_name": "Vrindavan",
        "profile_id": profile.id,
    }


@pytest.mark.django_db
def test_generation_job_api_is_scoped_to_authenticated_user():
    owner = get_user_model().objects.create_user(username="job-owner", password="strong-pass-108")
    other = get_user_model().objects.create_user(username="job-other", password="strong-pass-108")
    own_job = GeneratedAnalysisJob.objects.create(
        user=owner,
        kind="birth_chart_codex_cli",
        status=GeneratedAnalysisJob.Status.RUNNING,
        input_summary={"birth_date": "2000-01-01"},
        request_snapshot={"birth_date": "2000-01-01", "large": "hidden"},
    )
    other_job = GeneratedAnalysisJob.objects.create(
        user=other,
        kind="birth_chart_codex_cli",
        status=GeneratedAnalysisJob.Status.COMPLETE,
        input_summary={"birth_date": "2001-01-01"},
        request_snapshot={"birth_date": "2001-01-01"},
    )

    client = APIClient()
    client.force_authenticate(user=owner)
    list_response = client.get("/api/reports/generation-jobs", {"kind": "birth_chart_codex_cli"})
    detail_response = client.get(f"/api/reports/generation-jobs/{own_job.id}")
    other_detail_response = client.get(f"/api/reports/generation-jobs/{other_job.id}")

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.data["jobs"]] == [own_job.id]
    assert "request_snapshot" not in list_response.data["jobs"][0]
    assert detail_response.status_code == 200
    assert detail_response.data["job"]["status"] == "running"
    assert other_detail_response.status_code == 404


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="", CODEX_GENERATION_QUEUE_ENABLED=True)
def test_birth_codex_analysis_api_queues_generation_when_queue_enabled(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-queue-owner", password="strong-pass-108")
    profile = _codex_api_self_profile(user)
    cache.clear()

    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("queued API response must not run Codex inline"),
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "profile_id": profile.id,
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 202
    assert response.data["queued"] is True
    assert response.data["job"]["status"] == GeneratedAnalysisJob.Status.QUEUED
    job = GeneratedAnalysisJob.objects.get(user=user, kind="birth_chart_codex_cli")
    assert job.status == GeneratedAnalysisJob.Status.QUEUED
    assert job.started_at is None


@pytest.mark.django_db
def test_process_generation_jobs_completes_queued_birth_job(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-worker-owner", password="strong-pass-108")
    job = GeneratedAnalysisJob.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        status=GeneratedAnalysisJob.Status.QUEUED,
        request_snapshot={"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
    )

    def fake_generate(data, **kwargs):
        draft = GeneratedAnalysisDraft.objects.create(
            user=user,
            kind="birth_chart_codex_cli",
            review_status="private_final",
            source_policy="private_shastra_research_first",
            provider="codex_cli",
            model="test",
            input_snapshot=data,
            packet_snapshot={},
            output_json={"sections": [{"title": "Ready", "body": "Done."}]},
            prompt_markdown="",
        )
        return {"id": draft.id, "kind": "birth_chart_codex_cli", "sections": [{"title": "Ready", "body": "Done."}]}

    monkeypatch.setattr(
        "apps.reports.management.commands.process_generation_jobs.generate_birth_chart_codex_cli_analysis",
        fake_generate,
    )

    call_command("process_generation_jobs", limit=1, skip_evidence_refresh=True)

    job.refresh_from_db()
    assert job.status == GeneratedAnalysisJob.Status.COMPLETE
    assert job.started_at is not None
    assert job.completed_at is not None
    assert job.analysis_id is not None


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_codex_analysis_api_can_force_regenerate(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-force-owner", password="strong-pass-108")
    profile = _codex_api_self_profile(user)
    captured = {}

    def fake_generate(
        data,
        citation_search=None,
        research_search=None,
        interpretation_provider=None,
        refresh_evidence=True,
        force_regenerate=False,
        user=None,
    ):
        captured["data"] = data
        captured["force_regenerate"] = force_regenerate
        return {
            "id": 22,
            "kind": "birth_chart_codex_cli",
            "review_status": "private_final",
            "source_policy": "private_shastra_research_first",
            "sections": [{"title": "Codex", "body": "Fresh draft.", "evidence_references": []}],
        }

    monkeypatch.setattr("apps.reports.views.generate_birth_chart_codex_cli_analysis", fake_generate)

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
            {
                "profile_id": profile.id,
                "birth_date": "2000-01-01",
                "birth_time": "15:30",
                "place_name": "Vrindavan",
            "force_regenerate": True,
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["id"] == 22
    assert captured["force_regenerate"] is True
    assert "force_regenerate" not in captured["data"]


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_birth_codex_analysis_api_rejects_duplicate_running_generation(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-lock-owner", password="strong-pass-108")
    profile = _codex_api_self_profile(user)
    cache.clear()

    monkeypatch.setattr("apps.reports.views.cache.add", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("generator must not run while lock is active"),
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "profile_id": profile.id,
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.data["error"] == "analysis_generation_in_progress"


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="", CODEX_MAX_RUNNING_GENERATIONS_PER_USER=1)
def test_birth_codex_analysis_api_rejects_second_running_user_generation(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-user-limit", password="strong-pass-108")
    profile = _codex_api_self_profile(user)
    GeneratedAnalysisJob.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        status=GeneratedAnalysisJob.Status.RUNNING,
        started_at=timezone.now(),
        input_summary={"birth_date": "1999-01-01"},
    )
    cache.clear()

    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("generator must not run when user limit is reached"),
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "profile_id": profile.id,
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 429
    assert response.data["error"] == "analysis_user_generation_limit"
    assert response.data["running_count"] == 1


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="", CODEX_MAX_RUNNING_GENERATIONS_PER_USER=1, CODEX_RUNNING_GENERATION_STALE_SECONDS=300)
def test_birth_codex_analysis_api_ignores_stale_running_user_generation(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-stale-limit", password="strong-pass-108")
    profile = _codex_api_self_profile(user)
    GeneratedAnalysisJob.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        status=GeneratedAnalysisJob.Status.RUNNING,
        started_at=timezone.now() - timedelta(minutes=10),
        input_summary={"birth_date": "1999-01-01"},
    )
    cache.clear()

    monkeypatch.setattr(
        "apps.reports.views.generate_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: {
            "id": 333,
            "kind": "birth_chart_codex_cli",
            "review_status": "private_final",
            "source_policy": "private_shastra_research_first",
            "sections": [{"title": "Fresh", "body": "Allowed."}],
        },
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis",
        {
            "profile_id": profile.id,
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["id"] == 333


@pytest.mark.django_db
def test_compatibility_codex_analysis_api_rejects_duplicate_running_generation(monkeypatch):
    user = get_user_model().objects.create_user(username="compat-lock-owner", password="strong-pass-108")
    cache.clear()

    monkeypatch.setattr("apps.reports.views.cache.add", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        "apps.reports.views.generate_compatibility_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("compatibility generator must not run while lock is active"),
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/compatibility/codex-analysis",
        {
            "person_a": {"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
            "person_b": {"birth_date": "2001-02-03", "birth_time": "09:10", "place_name": "Mayapur"},
        },
        format="json",
    )

    assert response.status_code == 409
    assert response.data["error"] == "analysis_generation_in_progress"


@pytest.mark.django_db
def test_ask_birth_codex_analysis_uses_saved_report_and_saves_answer():
    from apps.reports.codex_cli_generation import ask_birth_chart_codex_cli_analysis

    report = GeneratedAnalysisDraft.objects.create(
        kind="birth_chart_codex_cli",
        review_status="private_final",
        source_policy="private_shastra_research_first",
        provider="codex_cli",
        model="codex_exec",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={
            "sections": [
                {
                    "title": "Карьера",
                    "body": "Десятый дом силён.",
                    "source_traces": [
                        {
                            "condition_key": "career_and_work",
                            "work_title": "BPHS",
                            "reference": "10.1",
                            "source_status": "research_only",
                            "short_excerpt": "karma bhava",
                            "interpretation": "смотреть 10 дом",
                        }
                    ],
                }
            ]
        },
    )
    prompts = []

    def fake_runner(prompt: str) -> str:
        prompts.append(prompt)
        return json.dumps(
            {
                "answer": "По карьере главный акцент на дисциплине и служении.",
                "evidence_references": ["BPHS 10.1"],
                "source_traces": [{"condition_key": "career_and_work", "work_title": "BPHS", "reference": "10.1"}],
            }
        )

    result = ask_birth_chart_codex_cli_analysis(
        analysis_id=report.id,
        question="Что по карьере?",
        codex_runner=fake_runner,
    )

    assert result["kind"] == "birth_chart_codex_cli_chat"
    assert result["analysis_id"] == report.id
    assert "дисциплине" in result["answer"]
    assert "Что по карьере?" in prompts[0]
    assert "Десятый дом силён" in prompts[0]
    chat = GeneratedAnalysisDraft.objects.get(kind="birth_chart_codex_cli_chat")
    assert chat.input_snapshot["analysis_id"] == report.id
    assert chat.output_json["answer"] == result["answer"]


@pytest.mark.django_db
def test_birth_codex_analysis_chat_api_returns_answer(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-chat-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Карта", "body": "Есть данные."}]},
    )

    monkeypatch.setattr(
        "apps.reports.views.ask_birth_chart_codex_cli_analysis",
        lambda analysis_id, question, history=None, user=None: {
            "kind": "birth_chart_codex_cli_chat",
            "analysis_id": analysis_id,
            "question": question,
            "answer": "Ответ по карте.",
            "history_used": len(history or []),
            "source_traces": [],
        },
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis/chat",
        {"analysis_id": report.id, "question": "Что с браком?", "history": [{"role": "user", "content": "Привет"}]},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["answer"] == "Ответ по карте."
    assert response.data["analysis_id"] == report.id
    assert response.data["history_used"] == 1


@pytest.mark.django_db
def test_birth_codex_analysis_chat_api_rejects_duplicate_running_answer(monkeypatch):
    user = get_user_model().objects.create_user(username="birth-chat-lock-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Chart", "body": "Saved body."}]},
    )
    cache.clear()
    monkeypatch.setattr("apps.reports.views.cache.add", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        "apps.reports.views.ask_birth_chart_codex_cli_analysis",
        lambda *args, **kwargs: pytest.fail("chat generator must not run while lock is active"),
    )

    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis/chat",
        {"analysis_id": report.id, "question": "What about marriage?"},
        format="json",
    )

    assert response.status_code == 409
    assert response.data["error"] == "analysis_chat_in_progress"


@pytest.mark.django_db
def test_birth_codex_analysis_chat_api_requires_question():
    user = get_user_model().objects.create_user(username="birth-chat-question-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=user,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Private", "body": "Owner only."}]},
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/reports/birth-chart/codex-analysis/chat",
        {"analysis_id": report.id, "question": ""},
        format="json",
    )

    assert response.status_code == 400
    assert "question" in response.data["error"]


@pytest.mark.django_db
def test_saved_analysis_chat_requires_authentication():
    owner = get_user_model().objects.create_user(username="saved-chat-owner", password="strong-pass-108")
    report = GeneratedAnalysisDraft.objects.create(
        user=owner,
        kind="birth_chart_codex_cli",
        review_status="private_final",
        input_snapshot={"birth_date": "2000-01-01"},
        output_json={"sections": [{"title": "Private", "body": "Owner only."}]},
    )

    response = APIClient().post(
        "/api/reports/birth-chart/codex-analysis/chat",
        {"analysis_id": report.id, "question": "Read it?"},
        format="json",
    )

    assert response.status_code in {401, 403}


class _Tmp:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        return str(self.path)

    def __exit__(self, exc_type, exc, tb):
        return False
