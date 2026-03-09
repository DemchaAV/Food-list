# Versioning Rules

## Source of truth

- `manifest.json` field `version`

## Affected files

- `manifest.json`
- `sw.js`
- `index.html`
- `food_builder.html`
- `food_trainer.html`
- `mobile_food.html`

## Cache/update path

- `index.html` fetches `manifest.json`
- service worker is registered with `?v=<version>`
- `sw.js` builds a cache name from that version
