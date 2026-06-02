from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import Any

from apps.sources.models import ReviewStatus, SourceWork

CATALOG_WORK_SLUG = "classical-yoga-research-catalog"

BASE_SOURCE_PRIORITY = ["Brhat Jataka", "Phaladipika", "Jataka Parijata", "Saravali"]
NABHASA_SOURCE_PRIORITY = ["Brhat Jataka", "BPHS with caution", "Saravali"]
RAJA_SOURCE_PRIORITY = ["Phaladipika", "Jataka Parijata", "Sarvartha Cintamani"]
VAISHNAVA_GUARD = (
    "Explain as karma and service context only; no fatalistic promise, no independent "
    "graha or demigod worship, and no public claim without citations."
)


def yoga_registry() -> list[dict[str, Any]]:
    yogas: list[dict[str, Any]] = []
    yogas.extend(
        _many(
            "panca_mahapurusha",
            "uncommon",
            ["Brhat Jataka", "BPHS with caution", "Phaladipika"],
            [
                ("ruchaka_mahapurusha", "Ruchaka Mahapurusha"),
                ("bhadra_mahapurusha", "Bhadra Mahapurusha"),
                ("hamsa_mahapurusha", "Hamsa Mahapurusha"),
                ("malavya_mahapurusha", "Malavya Mahapurusha"),
                ("shasha_mahapurusha", "Shasha Mahapurusha"),
            ],
            "Kendra strength of a qualifying graha in own or exaltation sign.",
            "signature_ready",
        )
    )
    yogas.extend(
        _many(
            "lunar_yoga",
            "common",
            ["Brhat Jataka", "Phaladipika"],
            [
                ("sunapha", "Sunapha"),
                ("anapha", "Anapha"),
                ("durudhara", "Durudhara"),
                ("kemadruma", "Kemadruma"),
                ("gaja_kesari", "Gaja Kesari"),
                ("chandra_mangala", "Chandra Mangala"),
            ],
            "Moon-centered combinations; strength and cancellation require full audit.",
            "partial_signature_ready",
        )
    )
    yogas.extend(
        _many(
            "solar_yoga",
            "common",
            ["Brhat Jataka", "Phaladipika"],
            [
                ("veshi", "Veshi"),
                ("voshi", "Voshi"),
                ("ubhayachari", "Ubhayachari"),
                ("budha_aditya", "Budha Aditya"),
            ],
            "Sun-centered combinations; combustion and dignity must be reviewed.",
            "partial_signature_ready",
        )
    )
    yogas.extend(
        _many(
            "raja_yoga",
            "uncommon",
            RAJA_SOURCE_PRIORITY,
            [
                ("dharma_karmadhipati_raja", "Dharma Karmadhipati Raja"),
                ("kendra_trikona_raja", "Kendra Trikona Raja"),
                ("lagna_lord_kendra_trikona_raja", "Lagna Lord Kendra/Trikona Raja"),
                ("raja_sambandha", "Raja Sambandha"),
                ("maharaja", "Maharaja"),
                ("sri_natha", "Sri Natha"),
                ("lakshmi", "Lakshmi"),
                ("saraswati", "Saraswati"),
                ("kalanidhi", "Kalanidhi"),
                ("bheri", "Bheri"),
                ("chamara", "Chamara"),
                ("kahala", "Kahala"),
                ("parvata", "Parvata"),
                ("sankha", "Sankha"),
            ],
            "Authority, support, learning, and rise combinations; public claims need exact rule.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "viparita_raja_yoga",
            "rare",
            RAJA_SOURCE_PRIORITY,
            [
                ("viparita_harsha", "Harsha Viparita Raja"),
                ("viparita_sarala", "Sarala Viparita Raja"),
                ("viparita_vimala", "Vimala Viparita Raja"),
                ("dusthana_lord_exchange_viparita", "Dusthana Lord Exchange Viparita"),
            ],
            "Difficult-house lordship patterns; interpret with humility and lived context.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "dhana_yoga",
            "uncommon",
            ["Phaladipika", "Saravali", "Sarvartha Cintamani"],
            [
                ("dhana_lagna_lord_second_eleventh", "Dhana Lagna/2nd/11th Link"),
                ("dwi_dhana", "Dwi Dhana"),
                ("bahu_dhana", "Bahu Dhana"),
                ("vasumati", "Vasumati"),
                ("indra", "Indra"),
                ("chandra_guru_dhana", "Chandra Guru Dhana"),
                ("dhana_from_arudha", "Dhana from Arudha"),
                ("labha_lord_strength", "Labha Lord Strength"),
                ("second_lord_eleventh_lord_link", "Second/Eleventh Lord Link"),
                ("lakshmi_dhana", "Lakshmi Dhana"),
            ],
            "Resource combinations; no financial advice or guarantee.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "arishta_and_bhanga",
            "uncommon",
            ["Brhat Jataka", "Phaladipika", "Jataka Parijata"],
            [
                ("balarishta", "Balarishta"),
                ("arishta_bhanga", "Arishta Bhanga"),
                ("daridra", "Daridra"),
                ("grahana", "Grahana"),
                ("shakata", "Shakata"),
                ("neecha_bhanga_raja", "Neecha Bhanga Raja"),
                ("mangala_dosha", "Mangala Dosha"),
                ("pitru_dosha_research", "Pitru Dosha Research"),
                ("kala_sarpa_contested", "Kala Sarpa Contested"),
                ("visha", "Visha"),
            ],
            "Difficult combinations; must be softened through Vaishnava remedy policy.",
            "catalog_only",
        )
    )
    yogas.extend(_nabhasa_yogas())
    yogas.extend(
        _many(
            "sannyasa_and_tapas",
            "rare",
            ["Brhat Jataka", "Phaladipika", "Prasna Marga"],
            [
                ("pravrajya", "Pravrajya"),
                ("sannyasa", "Sannyasa"),
                ("tapasvi", "Tapasvi"),
                ("brahma", "Brahma"),
                ("maha_bhagya", "Maha Bhagya"),
                ("bhagya", "Bhagya"),
            ],
            "Renunciation and austerity indications; align with guru, sadhu, and shastra.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "rare_named_yoga",
            "rare",
            BASE_SOURCE_PRIORITY,
            [
                ("mridanga", "Mridanga"),
                ("naga", "Naga"),
                ("garuda", "Garuda"),
                ("go", "Go"),
                ("vidyut", "Vidyut"),
                ("pushkala", "Pushkala"),
                ("amala", "Amala"),
                ("adhama", "Adhama"),
                ("subha_vesi", "Subha Vesi"),
                ("asubha_vesi", "Asubha Vesi"),
                ("adrogate_raja_research", "Adrogate Raja Research"),
                ("kesari_variant", "Kesari Variant"),
                ("rajju_variant", "Rajju Variant"),
                ("parijata", "Parijata"),
                ("vasishta", "Vasishta"),
            ],
            "Named rare yoga family; each requires exact textual mapping before publication.",
            "catalog_only",
        )
    )
    return [_with_common_policy(yoga, index) for index, yoga in enumerate(yogas, start=1)]


def yoga_catalog_overview() -> dict[str, Any]:
    yogas = yoga_registry()
    categories = Counter(str(yoga["category"]) for yoga in yogas)
    return {
        "status": "research_catalog_started",
        "total_yogas": len(yogas),
        "rare_yogas": sum(1 for yoga in yogas if yoga["rarity"] == "rare"),
        "categories": dict(sorted(categories.items())),
        "citation_policy": "required_for_public_interpretation",
        "public_release_policy": "catalog entries are research-only until source passages are approved",
    }


def yoga_catalog_import_payload() -> dict[str, Any]:
    return {
        "works": [
            {
                "slug": CATALOG_WORK_SLUG,
                "title": "Classical Yoga Research Catalog",
                "source_class": SourceWork.SourceClass.RESEARCH_ONLY,
                "review_status": ReviewStatus.RESEARCH_ONLY,
                "metadata": {
                    "seed": "yoga_catalog",
                    "source_role": "yoga_catalog_index",
                    "public_quote_status": "summary_anchor_only",
                },
            }
        ],
        "passages": [_passage_for_yoga(yoga) for yoga in yoga_registry()],
        "rules": [],
    }


def _nabhasa_yogas() -> list[dict[str, Any]]:
    yogas: list[dict[str, Any]] = []
    yogas.extend(
        _many(
            "nabhasa_ashraya",
            "rare",
            NABHASA_SOURCE_PRIORITY,
            [
                ("rajju_nabhasa", "Rajju Nabhasa"),
                ("musala_nabhasa", "Musala Nabhasa"),
                ("nala_nabhasa", "Nala Nabhasa"),
            ],
            "Nabhasa Ashraya sky-pattern family.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "nabhasa_dala",
            "rare",
            NABHASA_SOURCE_PRIORITY,
            [
                ("mala_nabhasa", "Mala Nabhasa"),
                ("sarpa_nabhasa", "Sarpa Nabhasa"),
            ],
            "Nabhasa Dala sky-pattern family.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "nabhasa_akriti",
            "rare",
            NABHASA_SOURCE_PRIORITY,
            [
                ("gada_nabhasa", "Gada Nabhasa"),
                ("shakata_nabhasa", "Shakata Nabhasa"),
                ("vihaga_nabhasa", "Vihaga Nabhasa"),
                ("shringataka_nabhasa", "Shringataka Nabhasa"),
                ("hala_nabhasa", "Hala Nabhasa"),
                ("vajra_nabhasa", "Vajra Nabhasa"),
                ("yava_nabhasa", "Yava Nabhasa"),
                ("kamala_nabhasa", "Kamala Nabhasa"),
                ("vapi_nabhasa", "Vapi Nabhasa"),
                ("yupa_nabhasa", "Yupa Nabhasa"),
                ("ishu_nabhasa", "Ishu/Shara Nabhasa"),
                ("shakti_nabhasa", "Shakti Nabhasa"),
                ("danda_nabhasa", "Danda Nabhasa"),
                ("nauka_nabhasa", "Nauka Nabhasa"),
                ("kuta_nabhasa", "Kuta Nabhasa"),
                ("chhatra_nabhasa", "Chhatra Nabhasa"),
                ("chapa_nabhasa", "Chapa/Dhanusha Nabhasa"),
                ("ardha_chandra_nabhasa", "Ardha Chandra Nabhasa"),
                ("chakra_nabhasa", "Chakra Nabhasa"),
                ("samudra_nabhasa", "Samudra Nabhasa"),
            ],
            "Nabhasa Akriti sky-pattern family.",
            "catalog_only",
        )
    )
    yogas.extend(
        _many(
            "nabhasa_sankhya",
            "rare",
            NABHASA_SOURCE_PRIORITY,
            [
                ("gola_nabhasa", "Gola Nabhasa"),
                ("yuga_nabhasa", "Yuga Nabhasa"),
                ("shula_nabhasa", "Shula Nabhasa"),
                ("kedara_nabhasa", "Kedara Nabhasa"),
                ("pasha_nabhasa", "Pasha Nabhasa"),
                ("dama_nabhasa", "Dama/Damini Nabhasa"),
                ("vina_nabhasa_variant", "Vina Nabhasa Variant"),
            ],
            "Nabhasa Sankhya sky-pattern family; variant names require source audit.",
            "catalog_only",
        )
    )
    return yogas


def _many(
    category: str,
    rarity: str,
    source_priority: list[str],
    pairs: list[tuple[str, str]],
    definition_scope: str,
    detection_status: str,
) -> list[dict[str, Any]]:
    return [
        {
            "key": key,
            "name": name,
            "category": category,
            "rarity": rarity,
            "source_priority": source_priority,
            "definition_scope": definition_scope,
            "detection_status": detection_status,
        }
        for key, name in pairs
    ]


def _with_common_policy(yoga: dict[str, Any], order: int) -> dict[str, Any]:
    item = deepcopy(yoga)
    item["order"] = order
    item["citation_policy"] = "required_for_public_interpretation"
    item["review_status"] = ReviewStatus.RESEARCH_ONLY
    item["vaishnava_guard"] = VAISHNAVA_GUARD
    item["public_explanation_outline"] = (
        "Name the yoga only as a researched classical indicator, explain the required "
        "formation, cite approved shastra passages, and frame practical guidance through "
        "Krishna-centered responsibility and service."
    )
    return item


def _passage_for_yoga(yoga: dict[str, Any]) -> dict[str, Any]:
    return {
        "work_slug": CATALOG_WORK_SLUG,
        "reference": f"Yoga catalog: {yoga['name']}",
        "body": (
            f"{yoga['name']} ({yoga['category']}): {yoga['definition_scope']} "
            "This is a research-only catalog anchor, not a public shastra quotation."
        ),
        "language_code": "en",
        "review_status": ReviewStatus.RESEARCH_ONLY,
        "metadata": {
            "seed": "yoga_catalog",
            "source_role": "yoga_research_anchor",
            "public_quote_status": "summary_anchor_only",
            "yoga_key": yoga["key"],
            "category": yoga["category"],
            "rarity": yoga["rarity"],
            "source_priority": yoga["source_priority"],
            "detection_status": yoga["detection_status"],
            "citation_policy": yoga["citation_policy"],
            "vaishnava_guard": yoga["vaishnava_guard"],
        },
    }
