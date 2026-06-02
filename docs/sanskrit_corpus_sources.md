# Sanskrit Corpus Sources

The local Sanskrit research corpus is kept outside git in `.private_corpus/`.
Current inputs are SanskritDocuments ITX/ITRANS and GRETIL plain text transformations.

Primary indexes:

- SanskritDocuments Jyotisha: <https://sanskritdocuments.org/sanskrit/sociology_astrology/>
- GRETIL Jyotisha/astronomy/math: <https://gretil.sub.uni-goettingen.de/gretil.html#Jyot>

Imported manifest:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py import_private_corpus ..\.private_corpus\jyotish-sanskrit-manifest.json
.\.venv\Scripts\python manage.py import_private_corpus ..\.private_corpus\jyotish-archive-ocr-manifest.json
.\.venv\Scripts\python manage.py segment_private_corpus --max-chars 1800
.\.venv\Scripts\python manage.py build_shastra_evidence --limit-per-condition 10 --min-score 8
```

## SanskritDocuments ITX

| Work | Local slug | Source |
| --- | --- | --- |
| Archa Jyotisha | `archa-jyotisha-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/aarchajyotiSha.itx> |
| Kautiliya Arthashastra | `kautiliya-arthashastra-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/artha.itx> |
| Chamatkara Chintamani | `chamatkara-chintamani-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/chamatkarachintamani.itx> |
| Jataka Parijata | `jataka-parijata-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/jAtakapArijAtaH.itx> |
| Daivajna Vallabha | `daivajna-vallabha-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/daivaGYavallabha.itx> |
| Phaladipika | `phaladipika-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/phaladIpika.itx> |
| Brhat Jataka | `brhat-jataka-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/brihajjAtakam.itx> |
| Hora Shastra English meaning 34-45 | `hora-shastra-english-itx-34-45` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/horaashaastraEng34-45.itx> |
| Manusmriti | `manusmriti-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/manu.itx> |
| Yajusha Jyotisha | `yajusha-jyotisha-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/yaajuShajyotiSha.itx> |
| BPHS 1-10 | `brhat-parashara-hora-shastra-sanskrit-itx-01-10` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par0110.itx> |
| BPHS 11-20 | `brhat-parashara-hora-shastra-sanskrit-itx-11-20` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par1120.itx> |
| BPHS 21-30 | `brhat-parashara-hora-shastra-sanskrit-itx-21-30` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par2130.itx> |
| BPHS 31-40 | `brhat-parashara-hora-shastra-sanskrit-itx-31-40` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par3140.itx> |
| BPHS 41-45 | `brhat-parashara-hora-shastra-sanskrit-itx-41-45` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par4145.itx> |
| BPHS 46-50 | `brhat-parashara-hora-shastra-sanskrit-itx-46-50` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par4650.itx> |
| BPHS 51-60 | `brhat-parashara-hora-shastra-sanskrit-itx-51-60` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par5160.itx> |
| BPHS 61-70 | `brhat-parashara-hora-shastra-sanskrit-itx-61-70` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par6170.itx> |
| BPHS 71-80 | `brhat-parashara-hora-shastra-sanskrit-itx-71-80` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par7180.itx> |
| BPHS 81-90 | `brhat-parashara-hora-shastra-sanskrit-itx-81-90` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par8190.itx> |
| BPHS 91-97 | `brhat-parashara-hora-shastra-sanskrit-itx-91-97` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/par9197.itx> |
| Brhat Samhita | `brhat-samhita-varahamihira-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/varbrhs.itx> |
| Brhat Samhita alternate ITX | `brhat-samhita-sanskrit-itx-alt` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/bRRihatsaMhitA.itx> |
| Bhrigu Sutram | `bhrigu-sutram-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/bhrigusUtram.itx> |
| Vriddha Yavana Jataka | `vriddha-yavana-jataka-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/vriddhayavanajataka1.itx> |
| Laghu Jataka | `laghu-jataka-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/laghujAtaka.itx> |
| Shatpanchashika | `shatpanchashika-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/ShaTpanchAshikA.itx> |

## GRETIL Plain Text

| Work | Local slug | Source |
| --- | --- | --- |
| Aryabhatiya | `aryabhatiya-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_AryabhaTa-AryabhaTIya.txt> |
| Aryabhatiya with commentary | `aryabhatiya-commentary-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_AryabhaTa-AryabhaTIya-comm.txt> |
| Bijaganita | `bijaganita-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_bhAskara-bIjagaNita.txt> |
| Lilavati | `lilavati-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_bhAskara-lIlAvatI.txt> |
| Brahmasphutasiddhanta | `brahmasphutasiddhanta-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_brahmagupta-brAhmasphuTasiddhAnta.txt> |
| Rgveda Vedanga Jyotisha | `rgveda-vedanga-jyotisha-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_lagadha-RgvedavedAGgajyotiSa.txt> |
| Surya Siddhanta | `surya-siddhanta-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_sUryasiddhAnta.txt> |
| Brhat Jataka | `brhat-jataka-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_varAhamihira-bRhajjAtaka.txt> |
| Brhat Samhita | `brhat-samhita-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_varAhamihira-bRhatsaMhitA.txt> |
| Tikanika Yatra | `tikanika-yatra-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_varAhamihira-tikanikayAtra.txt> |
| Vivaha Patala | `vivaha-patala-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_varAhamihira-vivAhapaTala.txt> |
| Yogayatra, Jha edition | `yogayatra-jha-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_varAhamihira-yogayAtrA-edjha.txt> |
| Yogayatra, Pingree edition | `yogayatra-pingree-gretil` | <https://gretil.sub.uni-goettingen.de/gretil/corpustei/transformations/plaintext/sa_varAhamihira-yogayAtrA-edpingree.txt> |

## Internet Archive OCR Layer

These are raw OCR texts from scans or text PDFs. They are useful for search and comparison, but must be manually checked before any citation.

| Work | Local slug | Source |
| --- | --- | --- |
| Saravali | `saravali-dli-csl-7888-archive-ocr` | <https://archive.org/details/dli.csl.7888> |
| Saravali Devanagari Jyotisha | `saravali-devanagari-jyotisha-archive-ocr` | <https://archive.org/details/SaravaliKalyanVerma834GhaAlm4Shlf4DevanagariJyothisha> |
| Saravali | `saravali-vsub-archive-ocr` | <https://archive.org/details/ksu.h1308.saravali0000vsub> |
| Sarvartha Chintamani | `sarvartha-chintamani-row-1899-archive-ocr` | <https://archive.org/details/Astrology_Books_by_B_Suryanarayana_Row> |
| Jataka Chandrika / Laghu Parashari | `jataka-chandrika-row-1900-archive-ocr` | <https://archive.org/details/Astrology_Books_by_B_Suryanarayana_Row> |
| Jaimini Sutras | `jaimini-sutras-row-1955-archive-ocr` | <https://archive.org/details/Astrology_Books_by_B_Suryanarayana_Row> |
| Jaimini Sutras | `jaimini-sutras-dli-archive-ocr` | <https://archive.org/details/in.ernet.dli.2015.486584> |
| Muhurta Chintamani | `muhurta-chintamani-kedar-datt-joshi-archive-ocr` | <https://archive.org/details/muhurta-chintamani-kedar-datt-joshi> |
| Hora Sara | `hora-sara-santhanam-archive-ocr` | <https://archive.org/details/HoraSaraRSanthanamEng> |
| Laghu Parashari | `laghu-parashari-op-verma-archive-ocr` | <https://archive.org/details/LaghuParashariOPVerma> |
| Uttara Kalamrita | `uttara-kalamrita-subrahmanya-sastri-archive-ocr` | <https://archive.org/details/uttkalamrita-kalidas-ps-sastri> |
| Bhavartha Ratnakara | `bhavartha-ratnakara-bv-raman-archive-ocr` | <https://archive.org/details/BhavarthaRatnakaraByBVRaman> |
| Prasna Marga Vol. 1 | `prasna-marga-vol-1-bv-raman-archive-ocr` | <https://archive.org/details/PrasnaMargaBVR> |
| Prasna Marga Vol. 2 | `prasna-marga-vol-2-bv-raman-archive-ocr` | <https://archive.org/details/PrasnaMargaBVR> |
| Prasna Tantra | `prasna-tantra-bv-raman-archive-ocr` | <https://archive.org/details/UJrg_prasna-tantra-by-b.-v.-raman-raman-publication> |
| Muhurtha or Electional Astrology | `muhurtha-electional-astrology-bv-raman-archive-ocr` | <https://archive.org/details/in.ernet.dli.2015.128092> |
| Vedanga Jyotisha | `vedanga-jyotisha-archive-ocr` | <https://archive.org/details/VedangaJyotisa> |
| Brahmasphutasiddhanta Vol. 1 | `brahmasphutasiddhanta-vol-1-archive-ocr` | <https://archive.org/details/Brahmasphutasiddhanta_Vol_1> |

## Status

All imported texts are `research_only`.
They can be used for internal matching and cross-checking, but public quotation remains blocked until a passage is reviewed and approved.

Still missing as clean open Sanskrit e-texts after this pass: Saravali, Sarvartha Chintamani, Muhurta Chintamani, Hora Sara, Jaimini Upadesa Sutra and Prasna Marga. They are now present in the Archive OCR layer where available, but that OCR is not citation-grade.
