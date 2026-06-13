# Product Scope

## Mission

Build a web jyotish service that calculates charts accurately and explains results through traceable jyotish sources, Srila Prabhupada's teachings, and Gaudiya Vaishnava siddhanta.

## MVP

- User registration and login.
- Birth profile storage.
- Place, timezone, and coordinate input.
- D1 chart.
- D9 chart and shodasha varga payload D1-D60 with audit status.
- Rashi, nakshatra, and pada.
- Panchanga basics.
- Vimshottari dasha baseline.
- Transit, muhurta, and multi-factor compatibility API baselines.
- Report sections with citations.
- Codex-ready natal and compatibility analysis packet generation for reviewed draft interpretation.
- Ordered shastra explanation schedule and research-only authority catalog seed.
- Research-only broad yoga catalog seed, including rare Nabhasa and named yogas.
- Read-only integration with the VL database.
- Seeded foundational Vaishnava interpretation rules with approved citation anchors.
- Accuracy comparison harness against Jagannatha Hora exports.
- Working chart workspace: active chart on the left, current calculation table on the right, and no duplicate chart-style switcher outside calculation settings.
- Tap/click explanations for core jyotish terms and numbers where practical, including houses, shadbala, combustion, varga names, panchanga terms, and dasha terms.
- Calculation table should prioritize what an astrologer checks first: graha, longitude, rashi, nakshatra/pada, dignity, retrograde marker, combustion, navamsa, and visible explanations for every symbol.
- Saved personal AI review history, saved compatibility review history, and review dialogue history.
- Current-day review workflow based on transits, panchanga, dasha context, and the user's saved birth chart.

## Later Phases

- Full dasha catalog.
- Full yoga catalog with citations.
- Shadbala and ashtakavarga.
- Full transit engine.
- Annual charts.
- Full compatibility with reviewed shastra citations and senior Vaishnava review.
- Full muhurta workflow.
- Prashna.
- PDF export.
- Admin review workflow for rules and citations.
- Two product modes before public launch: professional workspace for astrologers and simplified guided mode for non-astrologers.
- Guided learning layer for non-astrologers: tap terms, houses, vargas, dashas, and calculation labels to open short explanations without leaving the current screen.
- Registration onboarding with basic birth data first, optional birth time completion later, and one free AI review only for the user's own chart.
- Paid AI review for other saved charts while still allowing users to save and view non-paid charts.
- Relationship analysis beyond marriage compatibility: father, mother, sibling, boss, subordinate, enemy, teacher, friend, and custom roles.
- Relationship-aware context: interaction reports should open both charts and emphasize the houses, vargas, and factors relevant to the selected role.
- Account linking with consent: if a saved chart belongs to another registered user, linking should require an explicit request/approval and privacy controls.
- Full modern product redesign after the current functional pass: one stable information architecture across desktop web, mobile web, Telegram, and future native mobile apps.
- Mobile UX reference study before redesign: Divya Chakshu, Ishtaphala, JyotishUp, JHora, Vedic-horo, plus non-jyotish modern productivity apps for navigation, bottom sheets, dense tables, guided onboarding, and explanation popovers.
- Stable app shell: the same core navigation must stay available on charts, compatibility, interactions, reports, and history pages; switching pages must not make menu sections disappear.
- No hydration flash: never show a wrong empty chart or default birth data while saved local/API state is still loading.
- Contextual explanation layer like Vedic-horo: tap a graha, house number, rashi, nakshatra, dignity, combustion marker, shadbala label, or varga name to open a short explanation and an option to ask AI about that exact object.
- Guided learning mode: AI-led walkthrough for beginners explaining houses, signs, nakshatras, vargas, graha aspects, dignity, combustion, shadbala, dashas, and how the values are calculated.
- Area-question workflow: user can point at a chart/table area and ask "what is this?", "why is this important?", or "how is this calculated?", with the answer grounded in the current chart and available source policy.

## Out Of Scope For MVP

- Medical diagnosis.
- Financial or legal advice.
- Fatalistic guarantees.
- Unreviewed remedial prescriptions.
- Public display of unverified shastra imports.
