# Places And Timezones

## Current State

The MVP uses a small backend place catalog so the frontend does not hard-code coordinates or timezones.

Current catalog entries:

- Vrindavan, Uttar Pradesh, IN
- Mayapur, West Bengal, IN
- Yekaterinburg, Sverdlovsk Oblast, RU
- Moscow, Moscow, RU

## API

```text
GET /api/places/search?q=vrind
```

Birth chart calculation accepts only:

```json
{
  "birth_date": "1990-08-15",
  "birth_time": "10:24",
  "place_name": "Vrindavan, Uttar Pradesh, India"
}
```

The backend resolves the place to coordinates and timezone before calculating.

## Next Step

Replace or extend the static catalog with a real geocoding provider and historical timezone validation. Keep provider choice behind an adapter so API keys and terms can be reviewed before production use.

