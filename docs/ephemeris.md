# Ephemeris Layer

## MVP Decision

The calculation layer uses a provider interface. Swiss Ephemeris is the first target provider, but it is optional and must not be assumed to be legally cleared for public service use.

For local private development, Swiss Ephemeris is enabled first because it already supports the astrological coordinate workflow needed for jyotish: sidereal mode, ayanamsa selection, planetary speed, and lunar nodes.

JPL mode is wired through Swiss Ephemeris for numerical planet positions. It is a stronger astronomical reference than treating JHora as an opaque calculator, but it does not replace jyotish-specific settings: ayanamsa, true/mean nodes, houses, sunrise rules and varga rules must still match the selected tradition and audit fixture.

## Optional Install

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python -m pip install -e ".[swisseph]"
```

If Python 3.13 has no ready wheel and pip has trouble with isolated build dependencies, use:

```powershell
.\.venv\Scripts\python -m pip install setuptools wheel
.\.venv\Scripts\python -m pip install --no-build-isolation pyswisseph==2.10.3.2
```

Check status:

```powershell
Invoke-RestMethod http://127.0.0.1:8100/api/calculations/ephemeris/status
```

## Optional JPL Mode

Download a Swiss Ephemeris-compatible JPL file such as `de441.eph` or `de431.eph`, then configure `backend\.env`:

```env
SWISSEPH_EPHE_PATH=C:\path\to\swisseph\ephe
SWISSEPH_JPL_FILE=de441.eph
```

Then pass this calculation setting in chart input:

```json
{
  "ephemeris": "jpl"
}
```

If `ephemeris=jpl` is requested without `SWISSEPH_JPL_FILE`, the backend returns an explicit ephemeris availability error instead of silently falling back.

## Licensing Rule

Before production launch, decide one of:

- comply with the open-source Swiss Ephemeris/pyswisseph license terms;
- buy the needed commercial license;
- replace the provider with another legally suitable ephemeris source.

Do not hide this decision in code. Record it in this document and in deployment notes.

## References

- Swiss Ephemeris official site: https://www.astro.com/swisseph/
- pyswisseph package: https://pypi.org/project/pyswisseph/
- JPL Horizons API: https://ssd-api.jpl.nasa.gov/doc/horizons.html
