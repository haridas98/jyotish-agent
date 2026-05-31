import pytest

from apps.interpretations.engine import public_interpretation_sections_for_chart
from apps.interpretations.models import InterpretationBlock, InterpretationRule
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork, VLCitationLink


@pytest.mark.django_db
def test_public_interpretation_sections_require_approved_rule_block_and_citation():
    passage = _approved_passage()
    rule = InterpretationRule.objects.create(
        slug="kanya-lagna-service",
        title="Kanya Lagna Service",
        condition={"all": [{"path": "ascendant.rashi", "equals": "Kanya"}]},
        review_status=ReviewStatus.APPROVED,
    )
    rule.passages.add(passage)
    InterpretationBlock.objects.create(
        rule=rule,
        section="spiritual_practice",
        title="Service Orientation",
        body="Kanya lagna indications should be framed as practical service and sadhana.",
        review_status=ReviewStatus.APPROVED,
    )

    sections = public_interpretation_sections_for_chart({"ascendant": {"rashi": "Kanya"}})

    assert len(sections) == 1
    assert sections[0]["key"] == "interpretation:kanya-lagna-service"
    assert sections[0]["title"] == "Service Orientation"
    assert sections[0]["review_status"] == "approved"
    assert sections[0]["citations"][0]["title"] == "Bhagavad-gita 9.22"
    assert sections[0]["citations"][0]["public_url"] == "http://127.0.0.1:3001/bg/9/22"


@pytest.mark.django_db
def test_public_interpretation_sections_skip_uncited_or_unapproved_rules():
    uncited_rule = InterpretationRule.objects.create(
        slug="uncited-kanya",
        title="Uncited Kanya",
        condition={"all": [{"path": "ascendant.rashi", "equals": "Kanya"}]},
        review_status=ReviewStatus.APPROVED,
    )
    InterpretationBlock.objects.create(
        rule=uncited_rule,
        section="spiritual_practice",
        title="Uncited",
        body="This must not appear publicly without a citation.",
        review_status=ReviewStatus.APPROVED,
    )
    draft_rule = InterpretationRule.objects.create(
        slug="draft-kanya",
        title="Draft Kanya",
        condition={"all": [{"path": "ascendant.rashi", "equals": "Kanya"}]},
        review_status=ReviewStatus.DRAFT,
    )
    draft_rule.passages.add(_approved_passage(slug="bg-18-66", reference="Bhagavad-gita 18.66"))
    InterpretationBlock.objects.create(
        rule=draft_rule,
        section="spiritual_practice",
        title="Draft",
        body="Draft rules must stay out of public reports.",
        review_status=ReviewStatus.APPROVED,
    )

    sections = public_interpretation_sections_for_chart({"ascendant": {"rashi": "Kanya"}})

    assert sections == []


@pytest.mark.django_db
def test_public_interpretation_sections_match_collection_condition():
    passage = _approved_passage()
    rule = InterpretationRule.objects.create(
        slug="moon-vrishabha",
        title="Moon in Vrishabha",
        condition={
            "all": [
                {
                    "collection": "grahas",
                    "where": {"body": "Chandra", "rashi": "Vrishabha"},
                }
            ]
        },
        review_status=ReviewStatus.APPROVED,
    )
    rule.passages.add(passage)
    InterpretationBlock.objects.create(
        rule=rule,
        section="mind",
        title="Steady Mind",
        body="Moon in Vrishabha can be discussed only with reviewed source support.",
        review_status=ReviewStatus.APPROVED,
    )

    sections = public_interpretation_sections_for_chart(
        {"grahas": [{"body": "Chandra", "rashi": "Vrishabha"}]}
    )

    assert [section["key"] for section in sections] == ["interpretation:moon-vrishabha"]


def _approved_passage(slug="bg-9-22", reference="Bhagavad-gita 9.22"):
    work = SourceWork.objects.create(
        slug=slug,
        title="Bhagavad-gita As It Is",
        source_class=SourceWork.SourceClass.CANONICAL_PRABHUPADA,
        author="A. C. Bhaktivedanta Swami Prabhupada",
        review_status=ReviewStatus.APPROVED,
    )
    passage = SourcePassage.objects.create(
        work=work,
        reference=reference,
        body="Krishna protects His devotee.",
        review_status=ReviewStatus.APPROVED,
    )
    VLCitationLink.objects.create(
        passage=passage,
        vl_work_id=1,
        vl_text_unit_id=922,
        public_url=f"http://127.0.0.1:3001/{slug.replace('-', '/')}",
    )
    return passage
