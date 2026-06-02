# JHora Feature Matrix

| Area | MVP | Phase | Notes |
| --- | --- | --- | --- |
| Birth data input | yes | MVP | Date, time, place, timezone, accuracy flag. |
| Rashi chart D1 | yes | MVP | Must match configured ayanamsa. |
| Navamsa D9 | yes | MVP | Now part of the shodasha varga payload. |
| Nakshatra and pada | yes | MVP | Boundary cases flagged. |
| Panchanga basics | yes | MVP | Tithi, vara, nakshatra, yoga, karana. |
| Vimshottari dasha | yes | MVP | First dasha system. |
| D1-D60 | partial | Phase 2 | Shodasha varga engine and UI selector are implemented; JHora fixtures still required before authority claim. |
| Yogas | partial | Phase 2 | Simple signatures only: Gaja Kesari, Budha Aditya, Chandra Mangala. Interpretations require citations. |
| Avasthas | partial | Phase 2 | Baladi avastha calculated; other avasthas pending source review. |
| Vimshopaka bala | draft | Phase 2 | Temporary varga own/exaltation support count; not final bala. |
| Shadbala | draft | Phase 2 | Naisargika, uccha, and whole-sign dig bala exposed; remaining components pending audit. |
| Ashtakavarga | draft | Phase 2 | BAV/SAV bindu tables exposed with 337 SAV total; JHora fixtures still required. |
| Argala | partial | Phase 2 | Primary Lagna argala 2/4/11 with obstruction 12/10/3. |
| Special points | partial | Phase 2 | Arabic lots plus Gulika/Mandi draft segment timing; Vedic points pending fixture audit. |
| Transits | partial | Phase 2 | `/api/calculations/transits` compares current/as-of grahas to natal Lagna and Moon. |
| Annual charts | no | Phase 3 | After core parity. |
| Compatibility | partial | Phase 3 | `/api/calculations/compatibility` exposes 8-kuta baseline with Vaishnava caution text. |
| Muhurta | partial | Phase 3 | `/api/calculations/muhurta` ranks date candidates by panchanga rules and Vaishnava priority. |
| Prashna | no | Phase 3 | Separate input model. |
| Reports | partial | MVP | Citation-first, no free hallucination. |
