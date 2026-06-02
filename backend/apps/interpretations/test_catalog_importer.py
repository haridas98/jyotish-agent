import pytest

from apps.interpretations.engine import public_interpretation_sections_for_chart
from apps.interpretations.models import InterpretationBlock, InterpretationRule
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork


@pytest.mark.django_db
def test_import_interpretation_catalog_creates_idempotent_rules_sources_and_blocks():
    try:
        from apps.interpretations.catalog_importer import import_interpretation_catalog
    except ModuleNotFoundError:
        pytest.fail("catalog importer is not implemented yet")

    catalog = {
        "works": [
            {
                "slug": "brihat-parashara-hora-shastra",
                "title": "Brihat Parashara Hora Shastra",
                "source_class": "jyotish_shastra",
                "author": "Parashara Muni",
                "source_url": "https://example.test/bphs",
                "review_status": "approved",
            }
        ],
        "passages": [
            {
                "work_slug": "brihat-parashara-hora-shastra",
                "reference": "BPHS Lagna 1",
                "body": "Lagna is a primary chart factor.",
                "language_code": "en",
                "review_status": "approved",
                "public_url": "https://example.test/bphs/lagna-1",
            }
        ],
        "rules": [
            {
                "slug": "bphs-lagna-public-context",
                "title": "Lagna public context",
                "condition": {"all": [{"path": "ascendant.body", "equals": "Lagna"}]},
                "priority": 40,
                "review_status": "approved",
                "passage_refs": [
                    {
                        "work_slug": "brihat-parashara-hora-shastra",
                        "reference": "BPHS Lagna 1",
                        "language_code": "en",
                    }
                ],
                "blocks": [
                    {
                        "section": "lagna",
                        "title": "Лагна и контекст",
                        "body": "Лагна используется как технический фактор, но рекомендации остаются Кришна-центричными.",
                        "language_code": "ru",
                        "review_status": "approved",
                    }
                ],
            }
        ],
    }

    first = import_interpretation_catalog(catalog)
    second = import_interpretation_catalog(catalog)

    assert first["works"] == 1
    assert second["works"] == 1
    assert SourceWork.objects.count() == 1
    assert SourcePassage.objects.count() == 1
    assert InterpretationRule.objects.count() == 1
    assert InterpretationBlock.objects.count() == 1
    assert SourceWork.objects.get().review_status == ReviewStatus.APPROVED

    sections = public_interpretation_sections_for_chart({"ascendant": {"body": "Lagna"}})

    assert sections[0]["key"] == "interpretation:bphs-lagna-public-context"
    assert sections[0]["citations"][0]["title"] == "BPHS Lagna 1"
    assert "Кришна" in sections[0]["body"]


@pytest.mark.django_db
def test_import_interpretation_catalog_rejects_unknown_passage_reference():
    try:
        from apps.interpretations.catalog_importer import import_interpretation_catalog
    except ModuleNotFoundError:
        pytest.fail("catalog importer is not implemented yet")

    with pytest.raises(ValueError, match="Unknown passage reference"):
        import_interpretation_catalog(
            {
                "works": [],
                "passages": [],
                "rules": [
                    {
                        "slug": "bad-rule",
                        "title": "Bad",
                        "condition": {"all": [{"path": "ascendant.body", "equals": "Lagna"}]},
                        "passage_refs": [{"work_slug": "missing", "reference": "Missing"}],
                        "blocks": [],
                    }
                ],
            }
        )
