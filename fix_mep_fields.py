"""
fix_mep_fields.py
Fixes the MEP field mapping for new items:
- Cover → serviceMep
- Service → kitchenMep (was incorrectly combined into serviceMep)
"""
import json
import re
from pathlib import Path

path = Path(__file__).parent / "data" / "categories" / "scotts.js"
text = path.read_text(encoding="utf-8")

match = re.search(
    r"window\.registerFoodCategory\s*\(\s*(\[.*\])\s*\)\s*;?\s*$",
    text,
    re.DOTALL,
)
items = json.loads(match.group(1))

# Fix mapping for new items:
# cover → serviceMep
# service → kitchenMep
fixes = {
    "curried-parsnip-soup-fried-onion-pakora": {
        "serviceMep": "Soup spoon",
        "kitchenMep": "Soupier",
    },
    "scotts-prawn-cocktail-marie-rose-sauce": {
        "serviceMep": "Small knife/ fork",
        "kitchenMep": "Silver couple, side plate",
    },
    "robata-grilled-octopus-romesco-sauce-pink-fir-potatoes-salsa-verde": {
        "serviceMep": "Small knife/ fork",
        "kitchenMep": "Speckled plate",
    },
    "fillet-of-halibut-brown-shrimp-cucumber-chives-champagne-veloute": {
        "serviceMep": "Large knife/fork",
        "kitchenMep": "White bowl",
    },
    "fillet-of-hake-braised-white-beans-cavolo-nero-pancetta-chicken-butter-sauce": {
        "serviceMep": "Large knife/fork",
        "kitchenMep": "White bowl",
    },
    "portland-crab-linguini-chilli-garlic-datterini-tomatoes": {
        "serviceMep": "Large fork/ spoon",
        "kitchenMep": "White bowl",
    },
    "grilled-hispi-cabbage-bagna-cauda-shaved-parmesan-sourdough-bread-crumbs": {
        "serviceMep": "Fork and knife",
        "kitchenMep": "Side plate",
    },
    "fried-jerusalem-artichokes-spring-onion-hot-honey-dressing": {
        "serviceMep": "Serving spoon",
        "kitchenMep": "Silver oval",
    },
    "amedei-chocolate-mousse-sea-salt-olive-oil-sourdough-crisp": {
        "serviceMep": "Dessert spoon",
        "kitchenMep": "Posset glass, side plate",
    },
}

count = 0
for item in items:
    if item["id"] in fixes:
        fix = fixes[item["id"]]
        old_service = item.get("serviceMep")
        old_kitchen = item.get("kitchenMep")
        item["serviceMep"] = fix["serviceMep"]
        item["kitchenMep"] = fix["kitchenMep"]
        count += 1
        print(f"  Fixed: {item['name']}")
        print(f"    kitchenMep: {old_kitchen} → {fix['kitchenMep']}")
        print(f"    serviceMep: {old_service} → {fix['serviceMep']}")

output = "window.registerFoodCategory(" + json.dumps(items, indent=2, ensure_ascii=False) + ");\n"
path.write_text(output, encoding="utf-8")
print(f"\n✅ Fixed {count} items")
