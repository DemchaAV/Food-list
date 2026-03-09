---
name: update-food-data
description: Update Food-list menu data and related generated or validated files when dishes, allergens, glossary entries, or menu content change. Use this skill for edits to scotts.js, scotts_previous.js, related JSON inputs, and menu-supporting Python scripts.
---

# Update Food Data

Use this skill for menu and content changes in `C:\Users\Demch\OneDrive\projects\Food-list`.

## Primary Files

- current menu: `data/categories/scotts.js`
- previous menu: `data/categories/scotts_previous.js`
- raw/supporting data: `data/categories/food.json`
- validators: `scripts/validation/validate_scotts.py`, `scripts/validation/validate_scotts_full.py`

## Required Workflow

1. Edit the relevant menu/source files.
2. Keep `scotts.js` and `scotts_previous.js` aligned with the loader contract:
   - current data via `window.registerFoodCategory(...)`
   - previous data via `window.registerPreviousFoodCategory(...)`
3. After meaningful menu changes, run:

```powershell
python scripts/validation/validate_scotts.py
python .agent/skills/app-version-bump/scripts/bump_app_version.py
```

4. If the change affects glossary or structure broadly, also run:

```powershell
python scripts/validation/validate_scotts_full.py
```

5. Smoke-test at least one affected food page over HTTP.

## Guardrails

- do not break loader compatibility with current/previous menu switching
- prefer validating data rather than hand-waving large content edits
- keep menu images under `data/categories/menu_images/` when relevant

## References

- `references/data-flow.md`
