# Shastra Calculation Audit

## Rule

Calculations are not treated as final just because JHora or another service agrees. The order is:

1. older shastra and reviewed parampara instruction;
2. astronomical correctness: ephemeris, timezone, coordinates, ayanamsa, node type;
3. JHora and external services as black-box witnesses;
4. internal regression fixtures.

Shyamasundara Dasa's BPHS caution is now encoded in `shastra_audit.bphs_policy`: modern BPHS is useful, but not accepted blindly where older sources disagree.

## Current Public Interpretation Gate

`shastra_audit.items[*].can_generate_client_interpretation` controls whether a layer may be used directly in a client-facing reading.

Currently allowed:

- rashi, nakshatra, pada, navamsa;
- panchanga core math: Sterlitamak JHora fixture matched 4/4 checked tithi/vara/yoga/karana names after alias normalization;
- ashtakavarga BAV/SAV facts for personal reading: Sterlitamak JHora fixture matched 84/84 checked Sun-through-Saturn cells;
- checked special/upagraha points for personal reading: Sterlitamak JHora fixture matched 11/11 implemented core points, including Bhava/Hora/Ghati Lagna with a recorded time-lagna profile correction.
- vimshopaka bala facts for personal reading: BPHS Varga Viswa weighted calculation matched the Sterlitamak JHora fixture 36/36 with max delta 0.01.
- shadbala component facts for personal reading: source-backed components are calculated; include a note that JHora total parity is still a profile divergence.

Currently blocked for final interpretation:

- D2-D60 vargas: calculated; Sterlitamak captured JHora ASCII charts matched 300/300 placements, broader text-rule review open;
- Vimshottari: calculated, interpretation rule review open;
- avasthas: calculated, text-rule review open;
- ashtakavarga prose: exact verse mapping and Lagna Ashtakavarga row still pending;
- yogas: detected conditions only, exact citations/cancellations pending;
- argala and the broader optional JHora special-point catalog: source/tradition audit open;
- upagrahas beyond the checked Sterlitamak core set: broader JHora catalog audit open;
- compatibility: multi-factor chart analysis is calculated, but not final marriage counsel without exact citations and senior review;
- transits and muhurta: API/baseline only, not final counsel.

## Source Anchors

- Shyamasundara Dasa reading list: `https://shyamasundaradasa.com/jyotish/study/books.html`
- Shyamasundara Dasa BPHS authenticity caution: `https://shyamasundaradasa.com/jyotish/resources/articles/bphs.html`
- Brhat Jataka, chapter IX: primary Ashtakavarga anchor.
- Kalaprakasika and Muhurta Chintamani: muhurta anchors.
- Graha and Bhava Balas, Shadbala Rahasyam, BPHS/Santhanam Ch.27 and Uttara Kalamrita section 4: shadbala anchors, including declination/Kranti for Ayana Bala.
