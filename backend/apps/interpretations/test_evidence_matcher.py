import pytest
from rest_framework.test import APIClient

from apps.interpretations.evidence_matcher import (
    build_shastra_evidence,
    shastra_evidence_payload,
)
from apps.interpretations.models import ShastraConditionEvidence
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
def test_shastra_evidence_api_returns_payload():
    response = APIClient().get("/api/reports/shastra-evidence")

    assert response.status_code == 200
    assert response.json()["schema_version"] == "jyotish-shastra-evidence-v1"
