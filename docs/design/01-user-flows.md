# User Flows

## Current Core Flow

```text
Open app -> Charts -> Create chart -> Calculate -> View chart detail -> Inspect D scopes / grahas / technical payload -> Edit chart if needed
```

## Launch Diagnostics Flow

```text
Open launch status -> Check production health -> Confirm deploy commit -> Open demo chart -> Verify technical markers
```

## Future AI Review Flow

```text
Open saved chart -> Confirm calculation facts -> Attach/choose approved evidence -> Generate gated review draft -> Quality gate -> Human review
```

## Design Priority

The first UX/UI design milestone should focus on the canonical chart workspace:

```text
/charts/:id
```

Reason: this is the most characteristic and complex screen. If it works, the rest of the product can inherit its navigation, density, typography, and panel model.
