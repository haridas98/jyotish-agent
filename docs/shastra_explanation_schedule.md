# Shastra Explanation Schedule

The service now has an ordered explanation schedule in `apps.interpretations.shastra_catalog`.

Source policy:

- Prabhupada and Gaudiya sources frame purpose, remedies, and siddhanta.
- Shyamasundara Dasa's bibliography is used as a teacher-reference map.
- Brhat Jataka, Jataka Parijata, Phaladipika, Saravali, and Sarvartha Cintamani are the primary natal classics.
- BPHS is useful but marked `use_with_caution` until every rule is cross-checked against older sources and JHora parity.
- Public interpretation text requires citations; research-only anchors are not enough for public release.

Current ordered sections:

1. calculation audit;
2. lagna and body;
3. graha placements;
4. moon, mind, nakshatra, and dasha seed;
5. sun, dharma, and authority;
6. bhava topics;
7. vargas D1-D60;
8. vimshottari timeline;
9. avasthas, shadbala, vimshopaka;
10. ashtakavarga;
11. yogas, argala, upagrahas, special points;
12. panchanga and muhurta seed;
13. transits;
14. compatibility;
15. muhurta;
16. Vaishnava remedies;
17. source review notes.

Seed command:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py seed_shastra_catalog
```

External teacher references:

- https://shyamasundaradasa.com/jyotish/study/books.html
- https://shyamasundaradasa.com/jyotish/resources/articles/bphs.html
- https://shyamasundaradasa.com/jyotish/services/explanation_services/remedial.html
