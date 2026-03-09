---
name: change-validation
description: Validate Food-list changes before finishing a task. Use this skill whenever menu data, HTML, JS, CSS, manifest, service worker, or food-related scripts are modified and the result must be proven with targeted checks and smoke testing.
---

# Change Validation

Use this skill after implementation changes in `C:\Users\Demch\OneDrive\projects\Food-list`.

## Required Rules

1. Run a targeted validation for the changed behavior.
2. Run a smoke check for the affected page or data flow.
3. Bump the app version for meaningful app changes.
4. If no suitable test exists, add the smallest useful validation rather than skipping it.

## Common Commands

### Menu data changes

```powershell
python .agent/skills/app-version-bump/scripts/bump_app_version.py
python validate_scotts.py
python validate_scotts_full.py
```

Use `validate_scotts.py` as the minimum bar for current menu data changes.

### UI/static changes

```powershell
python -m http.server 8080
```

Smoke-check the affected page and confirm:

- page renders
- loader still resolves data
- version/service worker behavior still works where touched
- changed interaction works

## Output Contract

Final report must say:

- validations run
- pass/fail status
- smoke-tested page(s)
- blockers or unverified areas

## References

- `references/validation-checklist.md`
