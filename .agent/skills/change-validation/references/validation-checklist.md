# Validation Checklist

## Menu data updates

```powershell
python .agent/skills/app-version-bump/scripts/bump_app_version.py
python validate_scotts.py
```

Optional deeper validation:

```powershell
python validate_scotts_full.py
```

Verify:

- `manifest.json` version changed
- `data/categories/scotts.js` still parses
- current and previous menu toggles still work where relevant

## UI smoke targets

- `index.html`
- `food_builder.html`
- `food_trainer.html`
- `mobile_food.html`
