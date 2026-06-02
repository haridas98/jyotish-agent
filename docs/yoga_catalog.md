# Yoga Catalog

The first yoga catalog seed starts broad and research-only.

Scope in this batch:

- Pancha Mahapurusha yogas.
- Lunar and solar yogas.
- Raja, dhana, viparita, arishta and bhanga families.
- Nabhasa yogas, including Ashraya, Dala, Akriti, and Sankhya groups.
- Sannyasa, tapas, and rare named yogas.
- Contested or risky items such as Kala Sarpa are marked research-only.

Command:

```powershell
cd C:\Projects\jyotish-agent\backend
.\.venv\Scripts\python manage.py seed_yoga_catalog
```

Rules:

- No yoga interpretation is public until exact shastra passages are attached and approved.
- Every yoga explanation must cite sources and state formation conditions.
- Difficult yogas are explained through Vaishnava remedy policy, not fear or fatalism.
- Rare yogas stay `catalog_only` until detection logic is audited against JHora fixtures.

Initial source priorities:

- Brhat Jataka.
- Phaladipika.
- Jataka Parijata.
- Saravali.
- Sarvartha Cintamani.
- BPHS with caution and cross-checking.
