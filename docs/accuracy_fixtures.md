# Accuracy Fixtures

Fixture runner status: implemented.

Run all fixtures in a directory:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py run_accuracy_fixtures apps\calculations\fixtures\accuracy --json
```

Fail the process on any mismatch:

```powershell
.\.venv\Scripts\python manage.py run_accuracy_fixtures apps\calculations\fixtures\accuracy --fail-on-diff
```

After promoting reviewed JHora witnesses, gate the authoritative suite explicitly:

```powershell
.\.venv\Scripts\python manage.py run_accuracy_fixtures apps\calculations\fixtures\accuracy `
  --fail-on-authoritative-diff `
  --min-authoritative 20 `
  --min-jhora-verified 20
```

## Review Status

- `draft`: not authoritative, internal smoke or unreviewed import.
- `reviewed`: reviewed source, usable for regression.
- `jhora_verified`: values copied from a recorded JHora export with fixed settings.
- `approved`: accepted as authoritative by project review.

Only `reviewed`, `jhora_verified`, and `approved` count as authoritative in the runner.

Current state: no fixture is yet `jhora_verified`. The next verification target is the reviewed JHora/PL batch promoted through `promote_jhora_witness_batch`.

## Rule

Do not mark a fixture as `jhora_verified` without recording:

- JHora version;
- export/screenshot path;
- ayanamsa;
- node type;
- house system;
- timezone source;
- who reviewed it and when.

The included `internal-smoke-vrindavan-1990` fixture is deliberately `draft`; it only checks that the pipeline stays stable.

## Varga Checks

The fixture harness now also checks exact varga placements. Add reviewed JHora values under:

```json
{
  "expected": {
    "vargas": {
      "D9": {
        "Lagna": { "rashi": "Karka" },
        "Surya": { "rashi": "Makara" }
      },
      "D60": {
        "Surya": { "rashi": "Meena" }
      }
    }
  }
}
```

Use `rashi_index` too when the source export gives it.

## Classical Layer Checks

The fixture harness also compares captured JHora classical layers when they are present under `jhora_expected`:

- Bhinna Ashtakavarga rows for Sun through Saturn;
- Shadbala total virupas against the current calculated `known_total`.

The Lagna/Ascendant Ashtakavarga row is currently parsed but skipped until the app implements that row explicitly.

Other services go under `external_expected`. They are comparison witnesses, not primary authority:

```json
{
  "external_expected": [
    {
      "id": "vedic_horo",
      "name": "VedicHoro",
      "authority_tier": "black_box_service",
      "url": "https://vedic-horo.com/",
      "compare": false,
      "skip_reason": "raw text captured, visual cell order not confirmed",
      "expected": {
        "ashtakavarga": {},
        "shadbala": {}
      }
    }
  ]
}
```

Use `"compare": false` until the capture mapping is visually confirmed. This prevents false failures from tables whose DOM/text order differs from the rendered chart order.

See `docs/calculation_authority.md` for the authority order.

## Draft Classical Layers To Audit

The app now calculates draft layers that must receive fixture coverage before they can be marked authoritative:

- Bhinna/Sarva Ashtakavarga scores across reviewed JHora export fixtures;
- Shadbala six groups and component subtotals against reviewed JHora export fixtures;
- Gulika/Mandi exact longitude now uses real sunrise/sunset segmentation but still needs JHora parity fixtures;
- full ashtakuta compatibility tables;
- task-specific muhurta scoring.
