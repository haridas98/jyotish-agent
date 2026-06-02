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
- panchanga core math.

Currently blocked for final interpretation:

- D2-D60 vargas: calculated, text-rule review open;
- Vimshottari: calculated, interpretation rule review open;
- avasthas: calculated, text-rule review open;
- ashtakavarga: Brhat Jataka based, JHora/service diff open;
- shadbala: partial only, not full shadbala;
- vimshopaka: temporary proxy;
- yogas: detected conditions only, exact citations/cancellations pending;
- argala, upagrahas, special points: partial/source audit open;
- transits, compatibility, muhurta: API/baseline only, not final counsel.

## Source Anchors

- Shyamasundara Dasa reading list: `https://shyamasundaradasa.com/jyotish/study/books.html`
- Shyamasundara Dasa BPHS authenticity caution: `https://shyamasundaradasa.com/jyotish/resources/articles/bphs.html`
- Brhat Jataka, chapter IX: primary Ashtakavarga anchor.
- Kalaprakasika and Muhurta Chintamani: muhurta anchors.
- Graha and Bhava Balas and Shadbala Rahasyam: shadbala anchors.
