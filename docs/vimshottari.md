# Vimshottari MVP Engine

Current status: draft calculation layer, not yet JHora-parity-certified.

## Implemented

- Mahadasha sequence from Moon nakshatra:
  Ketu, Shukra, Surya, Chandra, Mangala, Rahu, Guru, Shani, Budha.
- Period years:
  7, 20, 6, 10, 7, 18, 16, 19, 17.
- Balance at birth is calculated from the remaining fraction of the Moon's nakshatra.
- The first MVP uses `365.25` days per dasha year and records this in API output.

## Required Before Authority Claim

- Compare against Jagannatha Hora exports with fixed settings.
- Confirm year basis and rounding policy.
- Add antardasha and deeper levels only after mahadasha parity is stable.
- Mark disputed boundary cases for manual review.
