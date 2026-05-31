# Ephemeris Layer

## MVP Decision

The calculation layer uses a provider interface. Swiss Ephemeris is the first target provider, but it is optional and must not be assumed to be legally cleared for public service use.

For local private development, Swiss Ephemeris is enabled first because it already supports the astrological coordinate workflow needed for jyotish: sidereal mode, ayanamsa selection, planetary speed, and lunar nodes. JPL/NASA data remains the higher-level astronomical reference option for later audit/parity work, but it is not the first MVP adapter because it would require more coordinate transformation and jyotish-specific plumbing.

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
