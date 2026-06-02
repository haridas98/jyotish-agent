import pytest
from django.core.management import CommandError, call_command

from apps.interpretations.engine import public_interpretation_sections_for_chart
from apps.interpretations.models import InterpretationBlock, InterpretationRule
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


@pytest.mark.django_db
def test_seed_vaishnava_interpretations_creates_idempotent_public_rules():
    try:
        call_command("seed_vaishnava_interpretations")
    except CommandError:
        pytest.fail("seed_vaishnava_interpretations command is not implemented yet")

    first_counts = {
        "works": SourceWork.objects.count(),
        "passages": SourcePassage.objects.count(),
        "rules": InterpretationRule.objects.count(),
        "blocks": InterpretationBlock.objects.count(),
    }

    call_command("seed_vaishnava_interpretations")

    assert {
        "works": SourceWork.objects.count(),
        "passages": SourcePassage.objects.count(),
        "rules": InterpretationRule.objects.count(),
        "blocks": InterpretationBlock.objects.count(),
    } == first_counts
    assert SourceWork.objects.get(slug="bhagavad-gita-as-it-is").review_status == ReviewStatus.APPROVED

    sections = public_interpretation_sections_for_chart(
        {
            "ascendant": {"body": "Lagna", "rashi": "Karka", "rashi_index": 3},
            "grahas": [
                {"body": "Chandra", "rashi": "Vrishabha", "rashi_index": 1},
                {"body": "Shani", "rashi": "Makara", "rashi_index": 9},
            ],
        }
    )
    keys = {section["key"] for section in sections}

    assert "interpretation:foundation-lagna-devotional-service" in keys
    assert "interpretation:foundation-moon-krishna-shelter" in keys
    assert "interpretation:foundation-shani-devotional-discipline" in keys
    assert all(section["review_status"] == ReviewStatus.APPROVED for section in sections)
    assert all(section["citations"] for section in sections)
    assert "Worship Shani" not in " ".join(section["body"] for section in sections)
    assert "Кришн" in " ".join(section["body"] for section in sections)
