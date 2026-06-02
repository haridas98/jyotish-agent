from __future__ import annotations

from copy import deepcopy
from typing import Any

from apps.sources.models import ReviewStatus, SourceWork

SHYAMASUNDARA_BOOKS_URL = "https://shyamasundaradasa.com/jyotish/study/books.html"
SHYAMASUNDARA_BPHS_URL = "https://shyamasundaradasa.com/jyotish/resources/articles/bphs.html"
SHYAMASUNDARA_REMEDIES_URL = (
    "https://shyamasundaradasa.com/jyotish/services/explanation_services/remedial.html"
)


EXPLANATION_SCHEDULE: list[dict[str, Any]] = [
    {
        "key": "calculation_audit",
        "title_ru": "Проверка исходных данных и расчета",
        "depends_on": ["birth", "place", "settings", "calculation_version"],
        "source_priority": ["calculation_engine", "jhora_parity_policy"],
        "implementation_status": "active",
    },
    {
        "key": "lagna_and_body",
        "title_ru": "Лагна, тело, темперамент и практический контекст жизни",
        "depends_on": ["ascendant", "houses"],
        "source_priority": ["Brhat Jataka", "Saravali", "Jataka Parijata", "Prabhupada"],
        "implementation_status": "seeded_foundation",
    },
    {
        "key": "graha_placements",
        "title_ru": "Планеты по знакам, домам, управлению и достоинству",
        "depends_on": ["grahas", "chart_facts.detailed_positions"],
        "source_priority": ["Brhat Jataka", "Phaladipika", "Sarvartha Cintamani"],
        "implementation_status": "active_draft",
    },
    {
        "key": "moon_mind_and_dasha_seed",
        "title_ru": "Луна, ум, накшатра и старт Вимшоттари",
        "depends_on": ["grahas.Chandra", "dashas.vimshottari"],
        "source_priority": ["Phaladipika", "Jataka Parijata", "Prabhupada"],
        "implementation_status": "seeded_foundation",
    },
    {
        "key": "sun_dharma_and_authority",
        "title_ru": "Солнце, дхарма, ответственность и власть",
        "depends_on": ["grahas.Surya"],
        "source_priority": ["Brhat Jataka", "Saravali", "Bhagavad-gita As It Is"],
        "implementation_status": "planned_rules",
    },
    {
        "key": "bhava_topics",
        "title_ru": "Дома карты: темы жизни и связи управителей",
        "depends_on": ["houses", "chart_facts.grahas.ruled_houses"],
        "source_priority": ["Brhat Jataka", "Saravali", "Sarvartha Cintamani"],
        "implementation_status": "planned_rules",
    },
    {
        "key": "d1_d60_vargas",
        "title_ru": "Варги D1-D60 и приоритеты подтверждения",
        "depends_on": ["vargas"],
        "source_priority": ["BPHS with caution", "Hora Sara", "Splendour of Vargas"],
        "implementation_status": "calculated_needs_text_rules",
    },
    {
        "key": "vimshottari_timeline",
        "title_ru": "Вимшоттари: махадаша, антардаша и жизненные периоды",
        "depends_on": ["dashas.vimshottari", "person_summary.dasha"],
        "source_priority": ["Phaladipika", "Jataka Parijata", "Laghu Parashari"],
        "implementation_status": "active_draft",
    },
    {
        "key": "avasthas_shadbala_vimshopaka",
        "title_ru": "Авастхи, Шадбала и Вимшопака бала",
        "depends_on": ["classical.avasthas", "classical.shadbala", "vargas"],
        "source_priority": ["Graha and Bhava Balas", "Shadbala Rahasyam", "BPHS with caution"],
        "implementation_status": "needs_jhora_audit",
    },
    {
        "key": "ashtakavarga",
        "title_ru": "Аштакаварга и сила транзитных/домовых тем",
        "depends_on": ["classical.ashtakavarga"],
        "source_priority": ["Ashtakavarga by C.S. Patel", "BPHS with caution"],
        "implementation_status": "needs_jhora_audit",
    },
    {
        "key": "yogas_argala_special_points",
        "title_ru": "Йоги, аргала, упаграхи и специальные точки",
        "depends_on": ["classical.yogas", "classical.special_points"],
        "source_priority": ["Jataka Parijata", "Phaladipika", "Jaimini Sutras"],
        "implementation_status": "partial_draft",
    },
    {
        "key": "panchanga_and_muhurta_seed",
        "title_ru": "Панчанга и первичная оценка времени",
        "depends_on": ["panchanga", "solar_day"],
        "source_priority": ["Kalaprakasika", "Muhurta Chintamani", "Brhat Samhita"],
        "implementation_status": "active_draft",
    },
    {
        "key": "transits",
        "title_ru": "Транзиты и текущая динамика",
        "depends_on": ["transits", "as_of_date"],
        "source_priority": ["Gochar Phaladeepika", "What the Stars Foretell"],
        "implementation_status": "planned_engine",
    },
    {
        "key": "compatibility",
        "title_ru": "Совместимость и аштакута",
        "depends_on": ["compatibility"],
        "source_priority": ["classical_matchmaking_texts", "teacher_review"],
        "implementation_status": "baseline_api",
    },
    {
        "key": "muhurta",
        "title_ru": "Мухурта для выбора времени",
        "depends_on": ["muhurta", "panchanga", "solar_day"],
        "source_priority": ["Kalaprakasika", "Muhurta Chintamani", "Prasna Marga"],
        "implementation_status": "baseline_api",
    },
    {
        "key": "vaishnava_remedies",
        "title_ru": "Вайшнавская рамка рекомендаций и remedial policy",
        "depends_on": ["sections.devotional_guidance", "remedy_policy"],
        "source_priority": ["Bhagavad-gita As It Is", "Srimad-Bhagavatam", "Caitanya-caritamrta"],
        "implementation_status": "seeded_foundation",
    },
    {
        "key": "source_review_notes",
        "title_ru": "Что проверено, что остается draft/research-only",
        "depends_on": ["citations", "review_status"],
        "source_priority": ["source_policy", "human_review"],
        "implementation_status": "active",
    },
]


def shastra_authority_catalog() -> dict[str, Any]:
    return {
        "works": [
            _work(
                "shyamasundara-reading-list",
                "Shyamasundara Dasa Recommended Reading List",
                SourceWork.SourceClass.TEACHER_REFERENCE,
                SHYAMASUNDARA_BOOKS_URL,
                authority_tier="teacher_bibliography",
            ),
            _work(
                "shyamasundara-bphs-authenticity",
                "Shyamasundara Dasa: On the Authenticity of the Brhat Parasara Hora Sastra",
                SourceWork.SourceClass.TEACHER_REFERENCE,
                SHYAMASUNDARA_BPHS_URL,
                authority_tier="teacher_methodology",
            ),
            _work(
                "shyamasundara-remedial-measures",
                "Shyamasundara Dasa: Jyotish Remedial Measures",
                SourceWork.SourceClass.TEACHER_REFERENCE,
                SHYAMASUNDARA_REMEDIES_URL,
                authority_tier="teacher_methodology",
            ),
            _work(
                "bhagavad-gita-as-it-is",
                "Bhagavad-gita As It Is",
                SourceWork.SourceClass.CANONICAL_PRABHUPADA,
                "",
                authority_tier="gaudiya_foundation",
                review_status=ReviewStatus.APPROVED,
            ),
            _work(
                "srimad-bhagavatam-prabhupada",
                "Srimad-Bhagavatam",
                SourceWork.SourceClass.CANONICAL_PRABHUPADA,
                "",
                authority_tier="gaudiya_foundation",
                review_status=ReviewStatus.APPROVED,
            ),
            _work(
                "caitanya-caritamrta-prabhupada",
                "Sri Caitanya-caritamrta",
                SourceWork.SourceClass.CANONICAL_PRABHUPADA,
                "",
                authority_tier="gaudiya_foundation",
                review_status=ReviewStatus.APPROVED,
            ),
            _work(
                "brhat-jataka",
                "Brhat Jataka",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "https://archive.org/details/brihatjataka00varaiala",
                authority_tier="primary_classic",
                access_policy="public_domain_scan",
                edition_note="N. Chidambaram Aiyar English translation, 1905 scan.",
            ),
            _work(
                "jataka-parijata",
                "Jataka Parijata",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "https://elibraryofyoga.com/items/5586d137-1723-4564-81b3-84a5db5f2945",
                authority_tier="primary_classic",
                access_policy="copyright_review_required",
            ),
            _work(
                "phaladipika",
                "Phaladipika",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "https://openlibrary.org/works/OL1038542W/Mantreswara%27s_phaladeepika",
                authority_tier="primary_classic",
                access_policy="copyright_review_required",
            ),
            _work(
                "phaladipika-subrahmanya-sastri",
                "Phaladipika - V. Subrahmanya Sastri translation",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "https://openlibrary.org/works/OL1038542W/Mantreswara%27s_phaladeepika",
                authority_tier="primary_classic_translation_variant",
                access_policy="copyright_review_required",
                translation_variant="V. Subrahmanya Sastri",
                bibliographic_publication_year="1937",
                user_claimed_publication_year="1932",
                rights_status="rights_review_required",
                use_policy="private_research_only_until_approved",
            ),
            _work(
                "saravali",
                "Saravali",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "https://www.rarebooksocietyofindia.org/postDetail.php?id=196174216674_10153565781516675",
                authority_tier="primary_classic",
                access_policy="copyright_review_required",
            ),
            _work(
                "sarvartha-cintamani",
                "Sarvartha Cintamani",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="primary_classic",
            ),
            _work(
                "brhat-parashara-hora-shastra",
                "Brhat Parasara Hora Sastra",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="conditional_classic",
                authority_note="use_with_caution",
            ),
            _work(
                "prasna-marga",
                "Prasna Marga",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="primary_prasna",
            ),
            _work(
                "hora-sara",
                "Hora Sara",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="supporting_classic",
            ),
            _work(
                "jaimini-sutras",
                "Jaimini Sutras",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="jaimini_classic",
            ),
            _work(
                "brhat-samhita",
                "Brhat Samhita",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="samhita_classic",
            ),
            _work(
                "kalaprakasika",
                "Kalaprakasika",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="muhurta_classic",
            ),
            _work(
                "muhurta-chintamani",
                "Muhurta Chintamani",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="muhurta_classic",
            ),
            _work(
                "surya-siddhanta",
                "Surya Siddhanta",
                SourceWork.SourceClass.JYOTISH_SHASTRA,
                "",
                authority_tier="siddhanta",
            ),
        ],
        "passages": [
            _passage(
                "shyamasundara-reading-list",
                "Shyamasundara recommended reading list",
                "Bibliography anchor: big five natal classics, Prasna Marga, muhurta texts, calculation texts, and Prabhupada works require review before public quotation.",
                SHYAMASUNDARA_BOOKS_URL,
                source_role="bibliography_anchor",
            ),
            _passage(
                "shyamasundara-bphs-authenticity",
                "BPHS authenticity caution",
                "Methodology anchor: use modern BPHS with caution and cross-check against older classical authorities and commentaries.",
                SHYAMASUNDARA_BPHS_URL,
                source_role="methodology_anchor",
            ),
            _passage(
                "shyamasundara-remedial-measures",
                "Vaishnava remedial congruence",
                "Remedial anchor: recommendations must remain congruent with Vaishnava siddhanta and should not become commercialized gem or yajna selling.",
                SHYAMASUNDARA_REMEDIES_URL,
                source_role="remedy_policy_anchor",
            ),
        ],
        "rules": [],
    }


def explanation_schedule() -> list[dict[str, Any]]:
    return [
        {**deepcopy(section), "citation_policy": "required_for_public_text"}
        for section in EXPLANATION_SCHEDULE
    ]


def _work(
    slug: str,
    title: str,
    source_class: str,
    source_url: str,
    *,
    authority_tier: str,
    review_status: str = ReviewStatus.RESEARCH_ONLY,
    authority_note: str = "",
    **metadata_items: str,
) -> dict[str, Any]:
    metadata = {
        "seed": "shastra_authority_catalog",
        "authority_tier": authority_tier,
    }
    if authority_note:
        metadata["authority_note"] = authority_note
    metadata.update({key: value for key, value in metadata_items.items() if value})
    return {
        "slug": slug,
        "title": title,
        "source_class": source_class,
        "source_url": source_url,
        "review_status": review_status,
        "metadata": metadata,
    }


def _passage(
    work_slug: str,
    reference: str,
    body: str,
    public_url: str,
    *,
    source_role: str,
) -> dict[str, Any]:
    return {
        "work_slug": work_slug,
        "reference": reference,
        "body": body,
        "language_code": "en",
        "review_status": ReviewStatus.RESEARCH_ONLY,
        "public_url": public_url,
        "metadata": {
            "seed": "shastra_authority_catalog",
            "source_role": source_role,
            "public_quote_status": "summary_anchor_only",
        },
    }
