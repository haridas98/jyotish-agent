import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.interpretations.evidence_matcher import (
    approve_shastra_condition_evidence,
    build_shastra_evidence,
    shastra_evidence_payload,
    shastra_source_trace_payload,
)
from apps.interpretations.models import ShastraConditionEvidence
from apps.interpretations.yoga_catalog import yoga_registry
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


@pytest.mark.django_db
def test_build_shastra_evidence_links_condition_to_specific_candidate_passage_and_reference():
    work = SourceWork.objects.create(
        slug="phaladipika-subrahmanya-sastri-private",
        title="Phaladipika",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="candidate passage 0001",
        body=(
            "Adhyaya 6. Sloka 16. The person born in the Gaja Kesari Yoga "
            "will be respected, eloquent and able to overcome enemies."
        ),
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={
            "import_kind": "candidate_shastra_passage",
            "public_quote_policy": "blocked_until_approved",
        },
    )

    result = build_shastra_evidence(condition_keys=["gaja_kesari"], limit_per_condition=3)

    assert result["summary"]["conditions_processed"] == 1
    evidence = ShastraConditionEvidence.objects.get(condition_key="gaja_kesari")
    assert evidence.passage == passage
    assert evidence.inferred_reference == "Adhyaya 6, Sloka 16"
    assert evidence.reference_status == "inferred_needs_review"
    assert evidence.public_quote_policy == "blocked_until_approved"
    assert evidence.score > 0


@pytest.mark.django_db
def test_build_shastra_evidence_adds_catalog_anchor_for_every_yoga_without_exact_match():
    from django.core.management import call_command

    call_command("seed_yoga_catalog")

    build_shastra_evidence(condition_keys=["gaja_kesari", "pravrajya"], limit_per_condition=1, min_score=999)

    yoga_keys = {"gaja_kesari", "pravrajya"}
    rows = ShastraConditionEvidence.objects.filter(condition_key__in=yoga_keys).select_related("passage", "passage__work")

    assert {row.condition_key for row in rows} == yoga_keys
    assert all(row.passage.work.slug == "classical-yoga-research-catalog" for row in rows)
    by_key = {row.condition_key: row for row in rows}
    assert by_key["gaja_kesari"].reference_status == "exact_verse_verified"
    assert by_key["gaja_kesari"].inferred_reference == "Chapter 36, Verses 3-4"
    assert by_key["gaja_kesari"].metadata["matcher"] == "curated_yoga_source_anchor_v1"
    assert by_key["gaja_kesari"].metadata["source_anchor"]["work_title"] == "Brhat Parashara Hora Shastra"
    assert by_key["gaja_kesari"].metadata["exact_source_required"] is False
    assert by_key["pravrajya"].reference_status == "exact_verse_verified"
    assert by_key["pravrajya"].inferred_reference == "Chapter XV, Verses 1-4"
    assert by_key["pravrajya"].metadata["matcher"] == "curated_yoga_source_anchor_v1"
    assert by_key["pravrajya"].metadata["source_anchor"]["work_title"] == "Brihat Jataka"
    assert by_key["pravrajya"].metadata["exact_source_required"] is False


@pytest.mark.django_db
def test_build_shastra_evidence_can_cover_all_yoga_catalog_keys_with_source_links():
    from django.core.management import call_command

    call_command("seed_yoga_catalog")
    keys = [row["key"] for row in yoga_registry()]

    build_shastra_evidence(condition_keys=keys, limit_per_condition=1, min_score=999)

    linked_keys = set(ShastraConditionEvidence.objects.filter(condition_key__in=keys).values_list("condition_key", flat=True))
    assert linked_keys == set(keys)
    assert not ShastraConditionEvidence.objects.filter(
        condition_key__in=keys,
        metadata__source_anchor={},
    ).exists()


@pytest.mark.django_db
def test_shastra_evidence_payload_returns_condition_passage_reference_and_prompt_rules():
    work = SourceWork.objects.create(
        slug="brhat-jataka-aiyar-1905-private",
        title="Brhat Jataka",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="candidate passage 0042",
        body="Chapter XIII. Stanza 4. Sunapha yoga source wording.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "candidate_shastra_passage"},
    )
    ShastraConditionEvidence.objects.create(
        condition_key="sunapha",
        condition_kind="yoga_condition",
        condition_title="Sunapha",
        passage=passage,
        score=31,
        inferred_reference="Chapter XIII, Stanza 4",
        reference_status="inferred_needs_review",
        public_quote_policy="blocked_until_approved",
    )

    payload = shastra_evidence_payload(condition_keys=["sunapha"])

    assert payload["schema_version"] == "jyotish-shastra-evidence-v1"
    row = payload["conditions"][0]
    assert row["condition_key"] == "sunapha"
    assert row["evidence"][0]["work_title"] == "Brhat Jataka"
    assert row["evidence"][0]["inferred_reference"] == "Chapter XIII, Stanza 4"
    assert row["evidence"][0]["reference_status"] == "inferred_needs_review"
    assert "do not quote research-only passages publicly" in payload["prompt_rules"][0]


@pytest.mark.django_db
def test_shastra_source_trace_payload_links_condition_fragment_reference_and_status():
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
        public_quote_policy="blocked_until_approved",
        metadata={"condition_summary": "Jupiter in kendra from Moon."},
    )

    payload = shastra_source_trace_payload(condition_keys=["gaja_kesari"])

    assert payload["schema_version"] == "jyotish-shastra-source-traces-v1"
    trace = payload["traces"][0]
    assert trace["condition_key"] == "gaja_kesari"
    assert trace["trigger"]["kind"] == "yoga"
    assert trace["source"]["work_title"] == "Phaladipika"
    assert trace["source"]["chapter"] == "Adhyaya 6"
    assert trace["source"]["verse"] == "Sloka 16"
    assert trace["source_status"] == "inferred_needs_review"
    assert trace["interpretation_hint"] == "Jupiter in kendra from Moon."


@pytest.mark.django_db
def test_shastra_source_trace_payload_uses_curated_yoga_anchor_metadata():
    from django.core.management import call_command

    call_command("seed_yoga_catalog")
    build_shastra_evidence(condition_keys=["gaja_kesari"], limit_per_condition=1, min_score=999)

    payload = shastra_source_trace_payload(condition_keys=["gaja_kesari"])

    trace = payload["traces"][0]
    assert trace["source"]["work_title"] == "Brhat Parashara Hora Shastra"
    assert trace["source"]["reference"] == "Chapter 36, Verses 3-4"
    assert trace["source"]["source_anchor"]["reference_status"] == "exact_verse_verified"
    assert trace["source_status"] == "curated_research_anchor"
    assert "protective intelligence" in trace["interpretation_hint"]


@pytest.mark.django_db
def test_shastra_evidence_api_returns_payload():
    response = APIClient().get("/api/reports/shastra-evidence")

    assert response.status_code == 200
    assert response.json()["schema_version"] == "jyotish-shastra-evidence-v1"


@pytest.mark.django_db
def test_approve_shastra_condition_evidence_promotes_exact_public_citation():
    work = SourceWork.objects.create(
        slug="phaladipika-subrahmanya-sastri-private",
        title="Phaladipika",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"rights_status": "public_domain_reviewed"},
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="candidate passage 0001",
        body="Adhyaya 6. Sloka 16. Gaja Kesari Yoga source wording.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "candidate_shastra_passage"},
    )
    evidence = ShastraConditionEvidence.objects.create(
        condition_key="gaja_kesari",
        condition_kind="yoga_condition",
        condition_title="Gaja Kesari",
        passage=passage,
        score=42,
        inferred_reference="Adhyaya 6, Sloka 16",
        reference_status="inferred_needs_review",
        public_quote_policy="blocked_until_approved",
    )

    approved = approve_shastra_condition_evidence(
        evidence.id,
        exact_reference="Adhyaya 6, Sloka 16",
        approved_excerpt="Gaja Kesari Yoga source wording.",
        reviewer="source-review",
        notes="Checked against imported edition.",
    )

    evidence.refresh_from_db()
    passage.refresh_from_db()
    assert approved["review_status"] == ReviewStatus.APPROVED
    assert evidence.review_status == ReviewStatus.APPROVED
    assert evidence.reference_status == "approved"
    assert evidence.public_quote_policy == "approved_public_quote"
    assert evidence.metadata["approved_reference"] == "Adhyaya 6, Sloka 16"
    assert evidence.metadata["approved_excerpt"] == "Gaja Kesari Yoga source wording."
    assert evidence.metadata["reviewer"] == "source-review"
    assert passage.review_status == ReviewStatus.APPROVED
    assert passage.reference == "Adhyaya 6, Sloka 16"

    payload = shastra_evidence_payload(condition_keys=["gaja_kesari"])
    row = payload["conditions"][0]
    assert row["public_release_policy"] == "approved"
    assert row["approved_citations"][0]["reference"] == "Adhyaya 6, Sloka 16"
    assert row["approved_citations"][0]["excerpt"] == "Gaja Kesari Yoga source wording."
    assert payload["summary"]["approved_conditions"] == 1
    assert payload["summary"]["approved_evidence_items"] == 1


@pytest.mark.django_db
def test_shastra_evidence_approve_api_returns_updated_payload():
    work = SourceWork.objects.create(
        slug="brhat-jataka-aiyar-1905-private",
        title="Brhat Jataka",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"rights_status": "public_domain_reviewed"},
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference="candidate passage 0042",
        body="Chapter XIII. Stanza 4. Sunapha yoga source wording.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "candidate_shastra_passage"},
    )
    evidence = ShastraConditionEvidence.objects.create(
        condition_key="sunapha",
        condition_kind="yoga_condition",
        condition_title="Sunapha",
        passage=passage,
        score=31,
        inferred_reference="Chapter XIII, Stanza 4",
        reference_status="inferred_needs_review",
        public_quote_policy="blocked_until_approved",
    )

    client = APIClient()
    client.force_authenticate(
        get_user_model().objects.create_user(username="review-admin", password="strong-pass", is_staff=True)
    )
    response = client.post(
        f"/api/reports/shastra-evidence/{evidence.id}/approve",
        {
            "exact_reference": "Chapter XIII, Stanza 4",
            "approved_excerpt": "Sunapha yoga source wording.",
            "reviewer": "source-review",
        },
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["review_status"] == ReviewStatus.APPROVED
    assert data["reference_status"] == "approved"
    assert data["condition_key"] == "sunapha"


@pytest.mark.django_db
def test_shastra_evidence_approve_api_rejects_anonymous_user():
    response = APIClient().post(
        "/api/reports/shastra-evidence/1/approve",
        {
            "exact_reference": "Chapter XIII, Stanza 4",
            "approved_excerpt": "Sunapha yoga source wording.",
        },
        format="json",
    )

    assert response.status_code in {401, 403}
