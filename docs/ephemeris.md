# Ephemeris Layer

## MVP Decision

The calculation layer uses a provider interface. Swiss Ephemeris is the first target provider, but it is optional and must not be assumed to be legally cleared for public service use.

## Optional Install

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python -m pip install -e ".[swisseph]"
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

