# Panchanga MVP

Current status: draft calculation layer, not yet JHora-parity-certified.

## Implemented

- Tithi from Moon-Sun elongation, 12 degrees per tithi.
- Paksha split: tithi 1-15 Shukla, 16-30 Krishna.
- Vara from local weekday.
- Yoga from Sun+Moon longitude, 13 degrees 20 minutes per yoga.
- Karana from half-tithi, 6 degrees per karana.

## Review Requirements

- Compare against JHora exports for ordinary and boundary cases.
- Confirm naming conventions against the chosen report language.
- Add transition times later; current MVP identifies the value at birth moment only.
- Do not derive auspicious/inauspicious interpretation until the source and Vaishnava policy layers are connected.
