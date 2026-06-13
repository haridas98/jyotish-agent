from pathlib import Path

import pytest
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient

from apps.calculations.ephemeris import BodyPosition
from apps.calculations.primitives import zodiac_placement
from apps.interpretations.models import ShastraConditionEvidence
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


class AnalysisProvider:
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
def test_build_analysis_packet_contains_codex_ready_prompt_policy_and_citations():
    try:
        from apps.reports.analysis_packet import build_analysis_packet
    except ModuleNotFoundError:
        pytest.fail("analysis packet service is not implemented yet")

    packet = build_analysis_packet(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
            "as_of_date": "2026-06-02",
        },
        provider=AnalysisProvider(),
        citation_search=lambda query: [
            {
                "title": "Bhagavad-gita 9.22",
                "work_title": "Bhagavad-gita As It Is",
                "body": "Krishna protects His devotee.",
                "public_url": "http://127.0.0.1:3100/bhagavad-gita/9/22",
            }
        ],
        interpretation_provider=lambda chart: [
            {
                "key": "interpretation:test",
                "title": "Test interpretation",
                "body": "Use service to Krishna as the framing.",
                "review_status": "approved",
                "calculation_only": False,
                "citations": [
                    {
                        "title": "Srimad-Bhagavatam 1.2.6",
                        "work_title": "Srimad-Bhagavatam",
                        "snippet": "Pure devotional service is supreme dharma.",
                        "public_url": "http://127.0.0.1:3100/srimad-bhagavatam/1/2/6",
                    }
                ],
            }
        ],
        research_search=lambda query: [
            {
                "title": "private full text chunk 0001",
                "work_title": "Phaladipika",
                "body": "Research-only yoga wording from private OCR.",
                "review_status": "research_only",
                "is_public_citation": False,
                "public_quote_policy": "blocked_until_approved",
            }
        ],
    )

    assert packet["schema_version"] == "jyotish-analysis-packet-v1"
    assert packet["shastra_coverage"]["schema_version"] == "jyotish-source-coverage-v1"
    assert packet["shastra_condition_matrix"]["schema_version"] == "jyotish-shastra-condition-matrix-v1"
    assert packet["shastra_evidence"]["schema_version"] == "jyotish-shastra-evidence-v1"
    assert packet["shastra_source_traces"]["schema_version"] == "jyotish-shastra-source-traces-v1"
    assert packet["status"] == "ready_for_generation"
    assert packet["generator_policy"]["language"] == "ru"
    assert packet["generator_policy"]["forbidden_outputs"][0] == "independent_demigod_worship"
    assert "compare_multiple_translation_variants" in packet["generator_policy"]["required_behaviors"]
    assert "public_quotation_from_unreviewed_translation" in packet["generator_policy"]["forbidden_outputs"]
    assert packet["report"]["source_policy"] == "citation_first"
    assert packet["context"]["birth"]["date"] == "2000-01-01"
    assert packet["context"]["explanation_schedule"][0]["key"] == "calculation_audit"
    assert packet["context"]["explanation_schedule"][-1]["key"] == "source_review_notes"
    assert packet["context"]["yoga_catalog_overview"]["total_yogas"] >= 90
    assert packet["context"]["yoga_catalog_overview"]["anchor_coverage"]["exact_verse_verified"] >= 70
    assert packet["context"]["jhora_parity_suite"]["case_count"] >= 20
    assert packet["context"]["workflow_interpretation_library"]["transits"]["required_factors"]
    assert "nabhasa_akriti" in packet["context"]["yoga_catalog_overview"]["categories"]
    yoga_map = packet["context"]["detected_yoga_source_map"]
    assert yoga_map
    assert all(row["citation_policy"] == "required_for_public_interpretation" for row in yoga_map)
    assert any(row["source_mapping_status"] == "mapped_research_only" for row in yoga_map)
    assert any(row["source_anchors"] for row in yoga_map)
    assert all(row["explanation_plan"]["client_text_sequence"] for row in yoga_map)
    citation_requests = packet["citation_requests"]
    assert citation_requests
    assert any(request["kind"] == "detected_yoga" for request in citation_requests)
    assert all(request["required_for_public_text"] for request in citation_requests)
    assert packet["context"]["chart_facts"]["grahas"]["Chandra"]["house"] == 2
    assert {citation["title"] for citation in packet["citations"]} == {
        "Srimad-Bhagavatam 1.2.6",
        "Bhagavad-gita 9.22",
    }
    assert packet["research_context"]["status"] == "private_research_not_public_citation"
    assert packet["research_context"]["items"][0]["work_title"] == "Phaladipika"
    assert packet["research_context"]["items"][0]["is_public_citation"] is False
    assert "OUTPUT JSON schema" in packet["prompt_markdown"]
    assert "explanation_schedule" in packet["prompt_markdown"]
    assert "detected_yoga_source_map" in packet["prompt_markdown"]
    assert "source_anchors" in packet["prompt_markdown"]
    assert "workflow_interpretation_library" in packet["prompt_markdown"]
    assert "jhora_parity_suite" in packet["prompt_markdown"]
    assert "citation_requests" in packet["prompt_markdown"]
    assert "research_context" in packet["prompt_markdown"]
    assert "shastra_coverage" in packet["prompt_markdown"]
    assert "shastra_condition_matrix" in packet["prompt_markdown"]
    assert "shastra_evidence" in packet["prompt_markdown"]
    assert "shastra_source_traces" in packet["prompt_markdown"]
    assert "compare_multiple_translation_variants" in packet["prompt_markdown"]
    assert "cite_exact_edition_translator_and_reference" in packet["prompt_markdown"]
    assert "flag_translation_conflicts" in packet["prompt_markdown"]
    assert "не выдумывай цитаты" in packet["prompt_markdown"]
    assert "independent demigod" in packet["prompt_markdown"]


@pytest.mark.django_db
def test_build_compatibility_analysis_packet_contains_two_chart_context_and_perspective_requests():
    try:
        from apps.reports.analysis_packet import build_compatibility_analysis_packet
    except ImportError:
        pytest.fail("compatibility analysis packet service is not implemented yet")

    packet = build_compatibility_analysis_packet(
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
        provider=AnalysisProvider(),
        citation_search=lambda query: [
            {
                "title": "Vivaha source anchor",
                "work_title": "Muhurta Chintamani",
                "body": "Marriage compatibility requires more than one factor.",
                "public_url": "http://127.0.0.1:3100/vivaha/source",
            }
        ],
    )

    assert packet["schema_version"] == "jyotish-compatibility-analysis-packet-v1"
    assert packet["shastra_coverage"]["schema_version"] == "jyotish-source-coverage-v1"
    assert packet["shastra_condition_matrix"]["schema_version"] == "jyotish-shastra-condition-matrix-v1"
    assert packet["shastra_evidence"]["schema_version"] == "jyotish-shastra-evidence-v1"
    assert packet["status"] == "needs_citation_review"
    assert packet["generator_policy"]["required_behaviors"][0] == "compare_both_charts_from_multiple_angles"
    assert "compare_multiple_translation_variants" in packet["generator_policy"]["required_behaviors"]
    assert packet["context"]["compatibility"]["coverage"]["system"] == "ashtakuta_plus_chart_analysis"
    assert packet["context"]["person_a"]["chart"]["birth"]["date"] == "2000-01-01"
    assert packet["context"]["person_b"]["chart"]["birth"]["date"] == "2001-02-03"
    assert packet["context"]["compatibility"]["analysis"]["perspectives"]
    assert packet["context"]["compatibility"]["interpretation_plan"]["kind"] == "compatibility"
    assert packet["context"]["jhora_parity_suite"]["case_count"] >= 20
    assert any(request["kind"] == "compatibility_perspective" for request in packet["citation_requests"])
    assert all(request["required_for_public_text"] for request in packet["citation_requests"])
    assert packet["citations"][0]["title"] == "Vivaha source anchor"
    assert "compatibility" in packet["prompt_markdown"]
    assert "person_a" in packet["prompt_markdown"]
    assert "person_b" in packet["prompt_markdown"]
    assert "compare_multiple_translation_variants" in packet["prompt_markdown"]
    assert "independent demigod" in packet["prompt_markdown"]


@pytest.mark.django_db
def test_analysis_packet_includes_persisted_shastra_evidence():
    try:
        from apps.reports.analysis_packet import build_analysis_packet
    except ModuleNotFoundError:
        pytest.fail("analysis packet service is not implemented yet")

    work = SourceWork.objects.create(
        slug="phaladipika-subrahmanya-sastri-private",
        title="Phaladipika",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="candidate passage 0001",
        body="Adhyaya 6. Sloka 16. Gaja Kesari Yoga source wording.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "candidate_shastra_passage"},
    )
    ShastraConditionEvidence.objects.create(
        condition_key="gaja_kesari",
        condition_kind="yoga_condition",
        condition_title="Gaja Kesari",
        passage=passage,
        score=42,
        inferred_reference="Adhyaya 6, Sloka 16",
        reference_status="inferred_needs_review",
    )

    packet = build_analysis_packet(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=AnalysisProvider(),
    )

    gaja = next(
        row for row in packet["shastra_evidence"]["conditions"] if row["condition_key"] == "gaja_kesari"
    )
    assert gaja["evidence"][0]["inferred_reference"] == "Adhyaya 6, Sloka 16"
    assert gaja["evidence"][0]["work_title"] == "Phaladipika"
    traces = packet["shastra_source_traces"]["traces"]
    assert any(trace["condition_key"] == "gaja_kesari" for trace in traces)


@pytest.mark.django_db
def test_analysis_packet_exposes_approved_shastra_citations_separately():
    try:
        from apps.reports.analysis_packet import build_analysis_packet
    except ModuleNotFoundError:
        pytest.fail("analysis packet service is not implemented yet")

    work = SourceWork.objects.create(
        slug="phaladipika-subrahmanya-sastri-private",
        title="Phaladipika",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="Adhyaya 6, Sloka 16",
        body="Gaja Kesari Yoga source wording.",
        review_status=ReviewStatus.APPROVED,
        metadata={"import_kind": "candidate_shastra_passage", "public_quote_policy": "approved_public_quote"},
    )
    ShastraConditionEvidence.objects.create(
        condition_key="gaja_kesari",
        condition_kind="yoga_condition",
        condition_title="Gaja Kesari",
        passage=passage,
        score=42,
        inferred_reference="Adhyaya 6, Sloka 16",
        reference_status="approved",
        public_quote_policy="approved_public_quote",
        review_status=ReviewStatus.APPROVED,
        metadata={
            "approved_reference": "Adhyaya 6, Sloka 16",
            "approved_excerpt": "Gaja Kesari Yoga source wording.",
            "reviewer": "source-review",
        },
    )

    packet = build_analysis_packet(
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        provider=AnalysisProvider(),
    )

    approved = packet["approved_shastra_citations"]
    assert approved["summary"]["approved_evidence_items"] == 1
    assert approved["items"][0]["condition_key"] == "gaja_kesari"
    assert approved["items"][0]["reference"] == "Adhyaya 6, Sloka 16"
    assert approved["items"][0]["excerpt"] == "Gaja Kesari Yoga source wording."
    assert "approved_shastra_citations" in packet["prompt_markdown"]


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_analysis_packet_api_returns_packet(monkeypatch):
    captured = {}

    def fake_build_analysis_packet(
        data,
        citation_search=None,
        research_search=None,
        interpretation_provider=None,
        include_prompt=True,
    ):
        captured["include_prompt"] = include_prompt
        return {
            "schema_version": "jyotish-analysis-packet-v1",
            "status": "ready_for_generation",
            "prompt_markdown": "prompt",
        }

    monkeypatch.setattr(
        "apps.reports.views.build_analysis_packet",
        fake_build_analysis_packet,
    )

    response = APIClient().post(
        "/api/reports/birth-chart/analysis-packet",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["schema_version"] == "jyotish-analysis-packet-v1"
    assert "prompt_markdown" not in response.data
    assert captured["include_prompt"] is False


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_analysis_packet_api_can_include_prompt_when_requested(monkeypatch):
    captured = {}

    def fake_build_analysis_packet(
        data,
        citation_search=None,
        research_search=None,
        interpretation_provider=None,
        include_prompt=True,
    ):
        captured["include_prompt"] = include_prompt
        return {
            "schema_version": "jyotish-analysis-packet-v1",
            "status": "ready_for_generation",
            "prompt_markdown": "prompt",
        }

    monkeypatch.setattr(
        "apps.reports.views.build_analysis_packet",
        fake_build_analysis_packet,
    )

    response = APIClient().post(
        "/api/reports/birth-chart/analysis-packet?include_prompt=1",
        {
            "birth_date": "2000-01-01",
            "birth_time": "15:30",
            "place_name": "Vrindavan",
        },
        format="json",
    )

    assert response.status_code == 200
    assert response.data["prompt_markdown"] == "prompt"
    assert captured["include_prompt"] is True


@pytest.mark.django_db
@override_settings(VL_DATABASE_URL="")
def test_compatibility_analysis_packet_api_returns_packet(monkeypatch):
    monkeypatch.setattr(
        "apps.reports.views.build_compatibility_analysis_packet",
        lambda data, citation_search=None, research_search=None: {
            "schema_version": "jyotish-compatibility-analysis-packet-v1",
            "status": "needs_citation_review",
            "prompt_markdown": "prompt",
        },
    )

    response = APIClient().post(
        "/api/reports/compatibility/analysis-packet",
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
    assert response.data["schema_version"] == "jyotish-compatibility-analysis-packet-v1"


def test_compatibility_analysis_packet_keeps_relationship_context(monkeypatch):
    from apps.reports import analysis_packet

    monkeypatch.setattr(
        analysis_packet,
        "build_birth_chart",
        lambda data, provider=None: {
            "birth": data,
            "calculation_version": "test",
            "grahas": [],
            "houses": [],
            "vargas": {},
        },
    )
    monkeypatch.setattr(
        analysis_packet,
        "build_compatibility_report",
        lambda data, provider=None: {
            "analysis": {"perspectives": [], "source_anchors": []},
            "coverage": {},
            "score": {},
            "assessment": {},
        },
    )
    monkeypatch.setattr(analysis_packet, "source_inventory_payload", lambda: {"summary": {}})
    monkeypatch.setattr(analysis_packet, "source_coverage_matrix", lambda: {"summary": {}})
    monkeypatch.setattr(analysis_packet, "shastra_condition_matrix", lambda: {"summary": {}})
    monkeypatch.setattr(analysis_packet, "shastra_evidence_payload", lambda: {})
    monkeypatch.setattr(analysis_packet, "shastra_source_trace_payload", lambda: {})
    monkeypatch.setattr(analysis_packet, "jhora_parity_suite_manifest", lambda: {})

    packet = analysis_packet.build_compatibility_analysis_packet(
        {
            "person_a": {"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
            "person_b": {"birth_date": "2001-02-03", "birth_time": "09:10", "place_name": "Mayapur"},
            "relationship_context": {
                "role": "father",
                "label": "Отец",
                "focus_houses": [1, 9, 10, 4],
                "focus_vargas": ["D1", "D9", "D12", "D60"],
                "prompt_hint": "читать как связь с отцом",
                "consent_policy": "requires request before mutual user link",
            },
        },
        citation_search=lambda query: [],
        research_search=lambda query, limit=6: [],
    )

    assert packet["context"]["relationship_context"]["role"] == "father"
    assert packet["context"]["relationship_context"]["focus_houses"] == [1, 9, 10, 4]
    assert packet["context"]["interaction_focus"]["role"] == "father"
    assert packet["context"]["interaction_focus"]["houses"] == [1, 9, 10, 4]
    assert packet["context"]["interaction_focus"]["vargas"] == ["D1", "D9", "D12", "D60"]
    assert "show both charts before interpretation" in packet["context"]["interaction_focus"]["reading_contract"]
    assert "honor_relationship_role_interaction_focus" in packet["generator_policy"]["required_behaviors"]
    assert "relationship_context" in packet["prompt_markdown"]


def test_compatibility_analysis_packet_derives_role_focus_when_only_role_is_sent(monkeypatch):
    from apps.reports import analysis_packet

    monkeypatch.setattr(
        analysis_packet,
        "build_birth_chart",
        lambda data, provider=None: {
            "birth": data,
            "calculation_version": "test",
            "grahas": [],
            "houses": [],
            "vargas": {},
        },
    )
    monkeypatch.setattr(
        analysis_packet,
        "build_compatibility_report",
        lambda data, provider=None: {
            "analysis": {"perspectives": [], "source_anchors": []},
            "coverage": {},
            "score": {},
            "assessment": {},
        },
    )
    monkeypatch.setattr(analysis_packet, "source_inventory_payload", lambda: {"summary": {}})
    monkeypatch.setattr(analysis_packet, "source_coverage_matrix", lambda: {"summary": {}})
    monkeypatch.setattr(analysis_packet, "shastra_condition_matrix", lambda: {"summary": {}})
    monkeypatch.setattr(analysis_packet, "shastra_evidence_payload", lambda: {})
    monkeypatch.setattr(analysis_packet, "shastra_source_trace_payload", lambda: {})
    monkeypatch.setattr(analysis_packet, "jhora_parity_suite_manifest", lambda: {})

    packet = analysis_packet.build_compatibility_analysis_packet(
        {
            "person_a": {"birth_date": "2000-01-01", "birth_time": "15:30", "place_name": "Vrindavan"},
            "person_b": {"birth_date": "2001-02-03", "birth_time": "09:10", "place_name": "Mayapur"},
            "relationship_context": {"role": "boss"},
        },
        citation_search=lambda query: [],
        research_search=lambda query, limit=6: [],
    )

    assert packet["context"]["relationship_context"]["role"] == "boss"
    assert packet["context"]["relationship_context"]["focus_houses"] == [1, 10, 6, 9]
    assert packet["context"]["interaction_focus"]["vargas"] == ["D1", "D10", "D9"]
    assert "Surya" in packet["context"]["interaction_focus"]["grahas"]


def test_build_analysis_packet_command_writes_json_and_prompt(monkeypatch, tmp_path):
    json_path = tmp_path / "packet.json"
    prompt_path = tmp_path / "packet.prompt.md"
    citation_requests_path = tmp_path / "citation-requests.json"

    monkeypatch.setattr(
        "apps.reports.management.commands.build_analysis_packet.build_analysis_packet",
        lambda data, citation_search=None, research_search=None, interpretation_provider=None: {
            "schema_version": "jyotish-analysis-packet-v1",
            "status": "ready_for_generation",
            "citation_requests": [{"key": "gaja_kesari", "kind": "detected_yoga"}],
            "prompt_markdown": "# Prompt\nUse packet.",
        },
    )

    call_command(
        "build_analysis_packet",
        "--birth-date",
        "2000-01-01",
        "--birth-time",
        "15:30",
        "--place-name",
        "Vrindavan",
        "--output",
        str(json_path),
        "--prompt-output",
        str(prompt_path),
        "--citation-requests-output",
        str(citation_requests_path),
    )

    assert '"schema_version": "jyotish-analysis-packet-v1"' in Path(json_path).read_text(encoding="utf-8")
    assert Path(prompt_path).read_text(encoding="utf-8") == "# Prompt\nUse packet."
    assert '"gaja_kesari"' in Path(citation_requests_path).read_text(encoding="utf-8")
