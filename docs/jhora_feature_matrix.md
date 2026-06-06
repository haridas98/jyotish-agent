# JHora Feature Matrix

| Area | MVP | Phase | Notes |
| --- | --- | --- | --- |
| Birth data input | yes | MVP | Date, time, place, timezone, accuracy flag. |
| Rashi chart D1 | yes | MVP | Must match configured ayanamsa. |
| Navamsa D9 | yes | MVP | Now part of the shodasha varga payload. |
| Nakshatra and pada | yes | MVP | Boundary cases flagged. |
| Panchanga basics | jhora-matched | MVP | Tithi, vara, nakshatra, yoga, karana; Sterlitamak JHora fixture now matches 4/4 checked panchanga names after alias normalization. |
| Vimshottari dasha | yes | MVP | First dasha system. |
| Extra dasha systems | partial | Phase 3 | Yogini dasha baseline is calculated; Ashtottari sequence is exposed as audit metadata until applicability/start-rule review. |
| D1-D60 | jhora-matched | Phase 2 | Varga engine, selector and compact D1/D9/D10/D30/D3/D60 snapshot are implemented; Sterlitamak captured JHora ASCII charts now check 300 placements with 300 matches, including D2 Uma-Shambhu, D20 movable/fixed/dual starts and D27 elemental starts. More fixtures still required before broad authority claim. |
| Yogas | partial+jhora | Phase 2 | 100+ yoga formulas are catalogued/detected; Sterlitamak JHora `Other strengths` active yogas now match 13/13. Full formula-to-shastra mappings still need review before final prose. |
| Avasthas | partial+ | Phase 2 | Degree/sign avasthas are calculated; remaining avastha families need source review and fixtures. |
| Vimshopaka bala | jhora-matched | Phase 2 | BPHS Varga Viswa weights are implemented for shadvarga/saptavarga/dashavarga/shodasha. Sterlitamak JHora comparison is now 36/36 exact matches with max delta 0.01 after applying the JHora-matched Rahu/Ketu dignity profile. |
| Shadbala | calculated/profile-divergence | Phase 2 | Six groups are calculated: Sthana, Dig, Kala, Chesta, Drik, Naisargika. The engine now uses real house cusps for Dig Bala when available, BPHS Drishti Pinda, sunrise-to-sunrise Dina/Hora/Ahargana, ephemeris declination/Kranti for Ayana Bala, and mean/true/Seeghrocha Chesta. Swiss/JPL providers derive the five starry planets' Chesta inputs from drik orbital elements, so speed fallback is no longer used when those inputs are available. JHora totals still differ 0/7 because the current export exposes totals only, so this is tracked as JHora-profile divergence rather than missing core math. |
| Ashtakavarga | jhora-matched | Phase 2 | BAV/SAV bindu tables exposed with 337 SAV total; Sterlitamak JHora fixture checks 84 cells with 84 matches. |
| Argala | partial+ | Phase 2 | Primary and secondary Lagna argala pairs are calculated with obstruction/net-effect rows; tradition/JHora fixture audit remains. |
| Special points | core+jhora | Phase 2 | Gulika/Maandi, solar upagrahas, Indu Lagna and Bhava/Hora/Ghati Lagna match the Sterlitamak JHora fixture after one recorded time-lagna profile correction. Current fixture: 11/11 checked matches; broader optional JHora special-point catalog remains separate. |
| Transits | partial | Phase 2 | `/api/calculations/transits` compares current/as-of grahas to natal Lagna and Moon. |
| Annual charts | baseline/audit | Phase 3 | `/api/calculations/tithi-pravesha` and UI tab calculate the annual same solar-lunar-angle return; Tajaka wrapper exposes Muntha and open annual-chart items. |
| Compatibility | partial+ | Phase 3 | `/api/calculations/compatibility` exposes 8/8 ashtakuta plus multi-factor chart analysis: Lagna, Moon, seventh house, Shukra/Mangala, Guru/Shukra and dasha context. Final counsel still needs citations and senior review. |
| Muhurta | partial+ | Phase 3 | `/api/calculations/muhurta` ranks date candidates by purpose profile, panchanga rules, Vaishnava priority, and sunrise-based Rahu/Yamaganda/Gulika avoidance. |
| Prashna | baseline/audit | Phase 3 | `/api/calculations/prashna` builds a horary chart with Lagna, Moon and panchanga anchors; judgement rules remain source-gated. |
| Mundane/event charts | baseline/audit | Phase 3 | `/api/calculations/mundane` builds an event chart with angular houses and slow-planet anchors; event-type rules remain source-gated. |
| Compact JHora-like workspace | partial | Phase 2 | First pass implemented: dense tabs, compact rows, multi-varga snapshot, less vertical whitespace. More JHora screens still need capture. |
| Dual calculation view | partial+ | Phase 2 | Backend endpoint and frontend compact panel show primary calculation, JHora-profile reproduction, settings diff, graha/varga/dasha/shadbala deltas, and authority decision. It still needs real JHora export fixtures. |
| JHora screenshot inventory | partial | Phase 2 | Main JHora window captured locally; remaining tabs/screens still need systematic capture. |
| Parashara Light witness inventory | live-manual-diff-ready | Phase 2 | PL7 UI metadata/screenshot capture and verification-packet command exist for the running `PL7.exe` session. Packet reports now accept `manual_witness_values`, compare copied/manual PL values against our chart fields, generate an editable Lagna/graha witness template from a packet, and read an external manual-values JSON in the Accuracy tab without rebuilding the packet. Qt panes expose mostly generic `QWidget`, so PL artifacts remain draft metadata/screenshot/manual-export witnesses until copyable tables are identified. |
| Authoritative JHora fixtures | packet-ready | Phase 2 | Capture-packet command exists and Sterlitamak 1998 packet is generated locally; fixture becomes `jhora_verified` only after real export/screens/settings/reviewer are attached. |
| Reports | partial | MVP | Citation-first, no free hallucination. |
