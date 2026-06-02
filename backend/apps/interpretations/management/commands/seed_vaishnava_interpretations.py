from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.interpretations.models import InterpretationBlock, InterpretationRule
from apps.sources.models import ReviewStatus, SourcePassage, SourceWork, VLCitationLink

VL_BASE_URL = "http://127.0.0.1:3100"

WORKS = [
    {
        "slug": "bhagavad-gita-as-it-is",
        "title": "Bhagavad-gita As It Is",
        "source_class": SourceWork.SourceClass.CANONICAL_PRABHUPADA,
        "author": "A. C. Bhaktivedanta Swami Prabhupada",
        "source_url": f"{VL_BASE_URL}/bhagavad-gita",
    },
    {
        "slug": "srimad-bhagavatam-prabhupada",
        "title": "Srimad-Bhagavatam",
        "source_class": SourceWork.SourceClass.CANONICAL_PRABHUPADA,
        "author": "A. C. Bhaktivedanta Swami Prabhupada",
        "source_url": f"{VL_BASE_URL}/srimad-bhagavatam",
    },
]

PASSAGES = [
    {
        "work_slug": "bhagavad-gita-as-it-is",
        "reference": "Bhagavad-gita 9.22",
        "body": "Указатель к наставлению Шрилы Прабхупады о защите и поддержке преданных Кришной.",
        "public_url": f"{VL_BASE_URL}/bhagavad-gita/9/22",
    },
    {
        "work_slug": "bhagavad-gita-as-it-is",
        "reference": "Bhagavad-gita 18.66",
        "body": "Указатель к наставлению Шрилы Прабхупады о принятии Кришны как высшего прибежища.",
        "public_url": f"{VL_BASE_URL}/bhagavad-gita/18/66",
    },
    {
        "work_slug": "srimad-bhagavatam-prabhupada",
        "reference": "Srimad-Bhagavatam 1.2.6",
        "body": "Указатель к определению чистого преданного служения как высшей дхармы души.",
        "public_url": f"{VL_BASE_URL}/srimad-bhagavatam/1/2/6",
    },
]

RULES = [
    {
        "slug": "foundation-lagna-devotional-service",
        "title": "Lagna as devotional service context",
        "condition": {"all": [{"path": "ascendant.body", "equals": "Lagna"}]},
        "priority": 10,
        "references": ["Srimad-Bhagavatam 1.2.6"],
        "block": {
            "section": "spiritual_foundation",
            "title": "Духовная опора карты",
            "body": (
                "Лагна показывает практический контекст жизни и служения, но не является независимым "
                "прибежищем. В публичном разборе её следует читать через вопрос: как тело, обязанности "
                "и обстоятельства можно занять в устойчивом служении Кришне."
            ),
        },
    },
    {
        "slug": "foundation-moon-krishna-shelter",
        "title": "Moon as Krishna shelter context",
        "condition": {"all": [{"collection": "grahas", "where": {"body": "Chandra"}}]},
        "priority": 20,
        "references": ["Bhagavad-gita 9.22"],
        "block": {
            "section": "mind",
            "title": "Ум и прибежище",
            "body": (
                "Положение Луны используется для оценки ума, привычек и эмоциональной реакции. "
                "Практическая рекомендация в гаудия-вайшнавской рамке: укреплять ум через шраванам, "
                "киртанам, повторение Харе Кришна и регулярное общение с преданными."
            ),
        },
    },
    {
        "slug": "foundation-shani-devotional-discipline",
        "title": "Saturn as devotional discipline context",
        "condition": {"all": [{"collection": "grahas", "where": {"body": "Shani"}}]},
        "priority": 30,
        "references": ["Bhagavad-gita 18.66"],
        "block": {
            "section": "remedial_policy",
            "title": "Дисциплина без независимого поклонения грахам",
            "body": (
                "Шани и другие грахи не должны становиться самостоятельным объектом поклонения в отчёте. "
                "Если расчёт указывает на напряжение, публичная рекомендация переводится в дисциплину "
                "садханы, ответственность, служение вайшнавам и принятие прибежища у Кришны."
            ),
        },
    },
]


class Command(BaseCommand):
    help = "Seed foundational Gaudiya Vaishnava interpretation rules and Prabhupada citation anchors."

    @transaction.atomic
    def handle(self, *args, **options):
        works = self._seed_works()
        passages = self._seed_passages(works)
        self._seed_rules(passages)
        self.stdout.write(self.style.SUCCESS("Seeded Vaishnava interpretation rules."))

    def _seed_works(self) -> dict[str, SourceWork]:
        works = {}
        for item in WORKS:
            work, _created = SourceWork.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "source_class": item["source_class"],
                    "author": item["author"],
                    "source_url": item["source_url"],
                    "review_status": ReviewStatus.APPROVED,
                    "metadata": {"seed": "vaishnava_foundation"},
                },
            )
            works[item["slug"]] = work
        return works

    def _seed_passages(self, works: dict[str, SourceWork]) -> dict[str, SourcePassage]:
        passages = {}
        for item in PASSAGES:
            passage, _created = SourcePassage.objects.update_or_create(
                work=works[item["work_slug"]],
                reference=item["reference"],
                language_code="ru",
                defaults={
                    "body": item["body"],
                    "review_status": ReviewStatus.APPROVED,
                    "metadata": {"seed": "vaishnava_foundation", "body_kind": "summary_anchor"},
                },
            )
            VLCitationLink.objects.get_or_create(
                passage=passage,
                public_url=item["public_url"],
                defaults={"metadata": {"seed": "vaishnava_foundation"}},
            )
            passages[item["reference"]] = passage
        return passages

    def _seed_rules(self, passages: dict[str, SourcePassage]) -> None:
        for item in RULES:
            rule, _created = InterpretationRule.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "condition": item["condition"],
                    "priority": item["priority"],
                    "review_status": ReviewStatus.APPROVED,
                    "metadata": {"seed": "vaishnava_foundation"},
                },
            )
            rule.passages.set([passages[reference] for reference in item["references"]])
            block = item["block"]
            InterpretationBlock.objects.update_or_create(
                rule=rule,
                section=block["section"],
                title=block["title"],
                defaults={
                    "body": block["body"],
                    "language_code": "ru",
                    "review_status": ReviewStatus.APPROVED,
                    "metadata": {"seed": "vaishnava_foundation"},
                },
            )
