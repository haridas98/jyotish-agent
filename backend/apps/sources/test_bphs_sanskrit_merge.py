from apps.sources.bphs_sanskrit_merge import (
    load_bphs_sanskrit_chapters,
    merge_sanskrit_into_english,
)


def test_load_bphs_sanskrit_chapters_transliterates_devanagari(tmp_path):
    root = tmp_path / "witnesses" / "sanskritdocuments" / "bphs"
    root.mkdir(parents=True)
    (root / "par0110.itx").write_text(
        "\\section{sR^iShTikramakathanAdhyAyaH || 1||}\n"
        "athaikadA munishreShThaM trikalaj~naM parAsharam |\n"
        "paprachChopetya maitreyaH praNipatya kR^itA~njaliH || 1||\n",
        encoding="utf-8",
    )

    chapters = load_bphs_sanskrit_chapters(tmp_path / "witnesses")

    assert chapters[1].title_itrans == "sR^iShTikramakathanAdhyAyaH || 1||"
    assert "अथैकदा" in chapters[1].body_devanagari
    assert "त्रिकलज्ञं" in chapters[1].body_devanagari


def test_load_bphs_sanskrit_chapters_reads_plain_chapter_markers(tmp_path):
    root = tmp_path / "witnesses" / "sanskritdocuments" / "bphs"
    root.mkdir(parents=True)
    (root / "par2130.itx").write_text(
        "\\medskip\\hrule\\medskip\n"
        "           atha karmabhAvaphalAdhyAyaH || 21||\n"
        "\\smallskip\n"
        "karmabhAvaphalaM chA.atha kathayAmi tavAgrataH |\n"
        "\\medskip\\hrule\\medskip\n"
        "           atha dashAphalAdyAyaH || 47||\n"
        "shrutAshcha bahudhA bhedA dashAnAM cha mayA mune |\n"
        "\\medskip\\hrule\\medskip\n"
        "        atha lAbhabhAvaphalAdhyAyaH || 22||\n"
        "lAbhabhAvaphala~nchAtha kathayAmi dvijottama |\n",
        encoding="utf-8",
    )

    chapters = load_bphs_sanskrit_chapters(tmp_path / "witnesses")

    assert sorted(chapters) == [21, 22, 47]
    assert chapters[21].title_itrans == "atha karmabhAvaphalAdhyAyaH || 21||"
    assert chapters[47].title_itrans == "atha dashAphalAdyAyaH || 47||"
    assert "कर्मभावफलं" in chapters[21].body_devanagari


def test_merge_sanskrit_into_english_inserts_before_chapter_heading(tmp_path):
    root = tmp_path / "witnesses" / "sanskritdocuments" / "bphs"
    root.mkdir(parents=True)
    (root / "par0110.itx").write_text(
        "\\section{sR^iShTikramakathanAdhyAyaH || 1||}\n"
        "athaikadA munishreShThaM trikalaj~naM parAsharam |\n",
        encoding="utf-8",
    )
    chapters = load_bphs_sanskrit_chapters(tmp_path / "witnesses")

    merged, inserted = merge_sanskrit_into_english(
        "Preface mentions Chapter 1 and Chapter 2.\n\nChapter 1. The Creation\nEnglish text.",
        chapters,
    )

    assert inserted == {1}
    assert merged.index("=== Sanskrit Witness Chapter 1 ===") < merged.index("Chapter 1. The Creation")
    assert "Preface mentions Chapter 1 and Chapter 2." in merged


def test_merge_sanskrit_into_english_accepts_colon_and_bare_chapter_headings(tmp_path):
    root = tmp_path / "witnesses" / "sanskritdocuments" / "bphs"
    root.mkdir(parents=True)
    (root / "par5160.itx").write_text(
        "atha antardashAphalAdhyAyaH || 52||\n"
        "raverdashAphalaM vakShye |\n"
        "atha ketvantardashAphalAdhyAyaH || 59||\n"
        "ketordashAphalaM vakShye |\n",
        encoding="utf-8",
    )
    chapters = load_bphs_sanskrit_chapters(tmp_path / "witnesses")

    merged, inserted = merge_sanskrit_into_english(
        "Chapter 52: Effects of the Antardasha of Sun\nEnglish.\n\nChapter 59\nEnglish.",
        chapters,
    )

    assert inserted == {52, 59}
    assert "=== Sanskrit Witness Chapter 52 ===" in merged
    assert "=== Sanskrit Witness Chapter 59 ===" in merged
