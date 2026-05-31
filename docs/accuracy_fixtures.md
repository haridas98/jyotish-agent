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

## Review Status

- `draft`: not authoritative, internal smoke or unreviewed import.
- `reviewed`: reviewed source, usable for regression.
- `jhora_verified`: values copied from a recorded JHora export with fixed settings.
- `approved`: accepted as authoritative by project review.

Only `reviewed`, `jhora_verified`, and `approved` count as authoritative in the runner.

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
