import pytest
from django.core.management import call_command

from apps.interpretations.models import ShastraConditionEvidence
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


@pytest.mark.django_db
def test_build_shastra_evidence_command_matches_requested_condition():
    work = SourceWork.objects.create(
        slug="phaladipika-subrahmanya-sastri-private",
        title="Phaladipika",
        source_class=SourceWork.SourceClass.JYOTISH_SHASTRA,
        review_status=ReviewStatus.RESEARCH_ONLY,
    )
    SourcePassage.objects.create(
        work=work,
        reference="candidate passage 0001",
        body="Adhyaya 6. Sloka 16. Gaja Kesari Yoga source wording.",
        review_status=ReviewStatus.RESEARCH_ONLY,
        metadata={"import_kind": "candidate_shastra_passage"},
    )

    call_command(
        "build_shastra_evidence",
        "--condition-key",
        "gaja_kesari",
        "--limit-per-condition",
        "2",
    )

    assert ShastraConditionEvidence.objects.filter(condition_key="gaja_kesari").count() == 1
