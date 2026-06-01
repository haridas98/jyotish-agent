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
| Shadbala | no | Phase 2 | Status exposed as pending until the sixfold formula pipeline is reviewed. |
| Ashtakavarga | no | Phase 2 | Status exposed as pending until BAV/SAV rule tables are fixture-tested. |
| Argala | partial | Phase 2 | Primary Lagna argala 2/4/11 with obstruction 12/10/3. |
| Special points | partial | Phase 2 | Arabic lots of fortune calculated; upagrahas and Vedic points pending fixture audit. |
| Transits | no | Phase 2 | API status placeholder; reuse calculation engine next. |
| Annual charts | no | Phase 3 | After core parity. |
| Compatibility | no | Phase 3 | Requires ethical wording. |
| Muhurta | no | Phase 3 | Separate policy review. |
| Prashna | no | Phase 3 | Separate input model. |
| Reports | partial | MVP | Citation-first, no free hallucination. |
