# Screen Inventory

## Canonical Technical Workflow

| Route | Purpose | Primary Action | Required States |
|---|---|---|---|
| `/charts` | Saved chart list | Open or create chart | loading, empty, error, populated |
| `/charts/new` | Create birth chart profile | Save and calculate | validation, disabled, error |
| `/charts/:id` | Main technical chart workspace | Inspect chart facts | loading, no calculation, calculated, error, mobile |
| `/charts/:id/edit` | Edit birth profile | Save changes | validation, dirty, success, error |
| `/charts/demo-d1` | Public/demo technical chart | Inspect demo calculation | loaded, degraded API, mobile |
| `/launch-status` | Launch diagnostics | Verify deployed runtime | health checking, ok, error |

## Secondary Routes

| Route | Purpose |
|---|---|
| `/reports` | AI review quality contracts and preview material |
| `/dashas` | Dasha-focused workspace |
| `/vargas` | Varga-focused workspace |
| `/transits` | Transit workspace |
| `/settings` | User/settings surface |
| `/sources` | Evidence/source surface |

## Design Rule

Do not redesign all routes at once. Start with `/charts/:id`, then derive list/create/edit patterns from it.
