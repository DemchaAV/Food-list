---
name: app-version-bump
description: Bump the Food-list application version after meaningful changes so the PWA and service worker fetch fresh menu data and assets. Use this skill whenever menu data, HTML, JS, CSS, manifest, or service worker related files change.
---

# App Version Bump

Use this skill after meaningful changes in `C:\Users\Demch\OneDrive\projects\Food-list`.

## Why

This project reads `manifest.json.version` on the landing page and registers `sw.js?v=<version>`.

Changing the version ensures users get fresh cached menu data and updated pages.

## Required Rule

Before finishing a real change, bump `manifest.json.version`.

## Version Format

- first version of the day: `YYYY.M.D`
- another version on the same day: `YYYY.M.D.HHmm`

## Command

```powershell
python .agent/skills/app-version-bump/scripts/bump_app_version.py
```

## References

- `references/versioning-rules.md`
