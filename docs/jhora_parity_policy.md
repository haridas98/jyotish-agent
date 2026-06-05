# Jagannatha Hora Parity Policy

## What Parity Means

Jagannatha Hora is a functional and numerical reference. Parity means the service can reproduce comparable outputs when the same settings are used:

- ayanamsa;
- house system;
- true or mean nodes;
- timezone and DST handling;
- coordinates;
- sunrise method;
- calculation date and ephemeris.

## Cross-Service Rule

JHora is not the final authority. When JHora, VedicHoro, Vedaansh, AstroSutra or another service disagrees, the disagreement is recorded as evidence. The formula changes only when supported by shastra, a documented parampara decision, or a verified settings/profile mismatch.

See `docs/calculation_authority.md`.

## Dual Calculation View

The product shows two calculation tracks:

- Jyotish Agent primary calculation;
- JHora-profile reproduction with the intended JHora settings;
- exact delta by graha, lagna, nakshatra, varga, dasha and bala component;
- settings diff;
- short explanation of the authority decision.

Important: `jhora_profile_calculation` is currently our engine running with a JHora-like settings profile. It is not a literal JHora export and must not be treated as verified parity until the same chart is captured from JHora with recorded settings, version, timezone/DST handling and screenshots/export.

The purpose is trust and auditability. A JHora match is evidence that settings and formulas align; a JHora mismatch is not automatically an error if the timezone, DST, ephemeris, ayanamsa, node model or shastra formula differs.

## What Is Not Allowed

- Decompiling JHora.
- Copying proprietary data tables.
- Copying UI assets or reports.
- Treating JHora as the only authority when settings differ.

## Accuracy Review

Every comparison run must store:

- JHora version;
- export date;
- input birth data;
- settings;
- Jyotish Agent calculation version;
- differences and explanation.

## Minimum Capture Packet

Before a fixture can be `jhora_verified`, capture:

- birth input screen with coordinates and timezone;
- calculation model: Drik Siddhanta or SSS;
- ayanamsa, true/mean nodes, bhava/house, varga and dasha options;
- D1 plus D9/D10/D30/D60;
- panchanga, Vimshottari, shadbala, ashtakavarga, upagrahas and special lagnas;
- screenshot/export file paths and reviewer/date.
