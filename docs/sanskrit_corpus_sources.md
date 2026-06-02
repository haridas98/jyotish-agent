# Sanskrit Corpus Sources

The local Sanskrit research corpus is kept outside git in `.private_corpus/`.
Current Sanskrit source format is SanskritDocuments ITX/ITRANS.

Source index: <https://sanskritdocuments.org/sanskrit/sociology_astrology/>

Imported manifest:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py import_private_corpus ..\.private_corpus\jyotish-sanskrit-manifest.json
.\.venv\Scripts\python manage.py segment_private_corpus --max-chars 1800
.\.venv\Scripts\python manage.py build_shastra_evidence --limit-per-condition 7 --min-score 8
```

## Imported ITX Texts

| Work | Local slug | Source |
| --- | --- | --- |
| Chamatkara Chintamani | `chamatkara-chintamani-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/chamatkarachintamani.itx> |
| Jataka Parijata | `jataka-parijata-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/jAtakapArijAtaH.itx> |
| Daivajna Vallabha | `daivajna-vallabha-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/daivaGYavallabha.itx> |
| Phaladipika | `phaladipika-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/phaladIpika.itx> |
| Brhat Jataka | `brhat-jataka-sanskrit-itx` | <https://sanskritdocuments.org/doc_z_misc_sociology_astrology/brihajjAtakam.itx> |
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

## Status

These texts are imported as `research_only`.
They can be used for internal matching and cross-checking, but public quotation remains blocked until a passage is reviewed and approved.
