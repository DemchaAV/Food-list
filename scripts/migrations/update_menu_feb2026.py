"""
update_menu_feb2026.py
Applies the February 2026 menu changes to scotts.js:
- Removes 9 DROP items
- Adds 9 ADD items with tags: ["new"]
- Updates Chocolate Truffles (Baileys -> Hazelnut praline)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "data" / "categories" / "scotts.js"
text = path.read_text(encoding="utf-8")

# Parse current data
match = re.search(
    r"window\.registerFoodCategory\s*\(\s*(\[.*\])\s*\)\s*;?\s*$",
    text,
    re.DOTALL,
)
if not match:
    print("FATAL: Cannot find registerFoodCategory wrapper")
    exit(1)

items = json.loads(match.group(1))
print(f"Loaded {len(items)} items")

# === 1. DROP items ===
drop_ids = [
    "caramelised-jerusalem-artichoke23",
    "scott-s-king-prawn-and-avocado9",
    "robata-grilled-octopus25",
    "fillet-of-halibut30",
    "pan-fried-fillet-of-hake33",
    "pan-fried-skate-wing31",
    "kimchi-fried-brussels-sprouts45",
    "baked-cauliflower-cheese44",
    "chocolate-and-hazelnut-delice53",
]

dropped = []
new_items = []
for item in items:
    if item["id"] in drop_ids:
        dropped.append(item["name"])
    else:
        new_items.append(item)

print(f"\nDropped {len(dropped)} items:")
for d in dropped:
    print(f"  - {d}")

items = new_items

# === 2. ADD items ===
add_items = [
    {
        "id": "curried-parsnip-soup-fried-onion-pakora",
        "name": "CURRIED PARSNIP SOUP, FRIED ONION PAKORA",
        "subtitle": None,
        "category": "Starters",
        "description": "Roasted parsnips blended in vegetable stock and cream with onions, leeks and curry powder until smooth. On the side are onion pakora. Sliced onion in a chickpea flour batter, deep-fried until crispy.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Dairy", "Celery"],
        "kitchenMep": None,
        "serviceMep": "Service: Soupier; Cover: Soup spoon",
        "image": None,
        "tags": ["new"],
        "price": "£12.50",
        "abb": "Parsnip soup",
        "cover": "Soup spoon",
        "service": "Soupier"
    },
    {
        "id": "scotts-prawn-cocktail-marie-rose-sauce",
        "name": "SCOTT'S PRAWN COCKTAIL, MARIE ROSE SAUCE",
        "subtitle": None,
        "category": "Starters",
        "description": "Silver coupe filled with shredded iceberg lettuce, cucumber, spring onion and dill, topped with Marie Rose sauce and finished with five peeled prawns and a gem leaf.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Crustecean", "Mustard", "Sulphites", "Egg", "Fish", "Gluten"],
        "kitchenMep": None,
        "serviceMep": "Service: Silver couple, side plate; Cover: Small knife/fork",
        "image": None,
        "tags": ["new"],
        "price": "£17.50",
        "abb": "Prawn cocktail",
        "cover": "Small knife/ fork",
        "service": "Silver couple, side plate"
    },
    {
        "id": "robata-grilled-octopus-romesco-sauce-pink-fir-potatoes-salsa-verde",
        "name": "ROBATA GRILLED OCTOPUS WITH ROMESCO SAUCE, PINK FIR POTATOES AND SALSA VERDE",
        "subtitle": None,
        "category": "Starters",
        "description": "Grilled octopus served on a romesco sauce (peppers, almonds, smoked paprika) and finished with salsa verde (parsley, basil, mint and capers) and crispy fried pink fir potatoes.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Mollusc", "Nut (A)"],
        "kitchenMep": None,
        "serviceMep": "Service: Speckled plate; Cover: Small knife/fork",
        "image": None,
        "tags": ["new"],
        "price": "£19.75",
        "abb": "Octopus",
        "cover": "Small knife/ fork",
        "service": "Speckled plate"
    },
    {
        "id": "fillet-of-halibut-brown-shrimp-cucumber-chives-champagne-veloute",
        "name": "FILLET OF HALIBUT, BROWN SHRIMP, CUCUMBER AND CHIVES, CHAMPAGNE VELOUTE AND WHIPPED PINK FIR POTATOES",
        "subtitle": None,
        "category": "Mains",
        "description": "Pan-fried fillet of halibut served on a bed of whipped, buttered pink fir potatoes and topped with a light cream based Champagne veloute finished with peeled brown shrimp, diced cucumber and chives. Finished with chive oil.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Fish", "Dairy", "Crustacea", "Celery", "Sulphites"],
        "kitchenMep": None,
        "serviceMep": "Service: White bowl; Cover: Large knife/fork",
        "image": None,
        "tags": ["new"],
        "price": "£39.50",
        "abb": "Halibut",
        "cover": "Large knife/fork",
        "service": "White bowl"
    },
    {
        "id": "fillet-of-hake-braised-white-beans-cavolo-nero-pancetta-chicken-butter-sauce",
        "name": "FILLET OF HAKE WITH BRAISED WHITE BEANS, CAVOLO NERO, PANCETTA AND CHICKEN BUTTER SAUCE",
        "subtitle": None,
        "category": "Mains",
        "description": "Pan fried fillet of hake cooked until crispy and golden brown, served on a bed of braised white butter beans, sauteed cavolo nero, and smoked pancetta. Finished with a light chicken butter sauce.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Fish", "Dairy", "Sulphites", "Celery"],
        "kitchenMep": None,
        "serviceMep": "Service: White bowl; Cover: Large knife/fork",
        "image": None,
        "tags": ["new"],
        "price": "£34.00",
        "abb": "Hake",
        "cover": "Large knife/fork",
        "service": "White bowl"
    },
    {
        "id": "portland-crab-linguini-chilli-garlic-datterini-tomatoes",
        "name": "PORTLAND CRAB LINGUINI, CHILLI, GARLIC AND DATTERINI TOMATOES",
        "subtitle": None,
        "category": "Mains",
        "description": "Linguini pasta cooked and tossed with picked white crab, olive oil, chilli, garlic and datterini tomatoes, finished with chopped parsley.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Crustacean", "Dairy", "Sulphites", "Gluten"],
        "kitchenMep": None,
        "serviceMep": "Service: White bowl; Cover: Large fork/spoon",
        "image": None,
        "tags": ["new"],
        "price": "£34.00",
        "abb": "Crab linguni",
        "cover": "Large fork/ spoon",
        "service": "White bowl"
    },
    {
        "id": "grilled-hispi-cabbage-bagna-cauda-shaved-parmesan-sourdough-bread-crumbs",
        "name": "GRILLED HISPI CABBAGE, BAGNA CAUDA, SHAVED PARMESAN AND SOURDOUGH BREAD CRUMBS",
        "subtitle": None,
        "category": "Sides",
        "description": "Chargrilled hispi cabbage served on a bed of Bagna Cauda (anchovy, parmesan, garlic, milk). Topped with crispy golden bread crumbs and heaps of shaved Parmigiano Reggiano.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Dairy", "Mustard", "Sulphites", "Gluten", "Fish", "Egg"],
        "kitchenMep": None,
        "serviceMep": "Service: Side plate; Cover: Fork and knife",
        "image": None,
        "tags": ["new"],
        "price": "£7.75",
        "abb": "Cabbage",
        "cover": "Fork and knife",
        "service": "Side plate"
    },
    {
        "id": "fried-jerusalem-artichokes-spring-onion-hot-honey-dressing",
        "name": "FRIED JERUSALEM ARTICHOKES WITH SPRING ONION AND HOT HONEY DRESSING",
        "subtitle": None,
        "category": "Sides",
        "description": "First roasted at a low temperature until soft and then fried at a low temperature to create a blistered skin. Finish by frying at a high temperature until crispy and golden brown and then tossed in hot honey dressing, chives and spring onions.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Sulphites"],
        "kitchenMep": None,
        "serviceMep": "Service: Silver oval; Cover: Serving spoon",
        "image": None,
        "tags": ["new"],
        "price": "£7.50",
        "abb": "Artichokes",
        "cover": "Serving spoon",
        "service": "Silver oval"
    },
    {
        "id": "amedei-chocolate-mousse-sea-salt-olive-oil-sourdough-crisp",
        "name": "AMEDEI CHOCOLATE MOUSSE WITH SEA SALT, OLIVE OIL AND SOURDOUGH CRISP",
        "subtitle": None,
        "category": "Desserts",
        "description": "Dark chocolate mousse, served with chocolate sponge, olive oil, sea salt and sourdough crisp that has been lightly toasted.",
        "wineSuggestion": {"name": None, "notes": None},
        "glossary": [],
        "additionalNotes": None,
        "allergens": ["Dairy", "Gluten", "Eggs", "Pork Gelatine"],
        "kitchenMep": None,
        "serviceMep": "Service: Posset glass, side plate; Cover: Dessert spoon",
        "image": None,
        "tags": ["new"],
        "price": "£13.50",
        "abb": "Mousse",
        "cover": "Dessert spoon",
        "service": "Posset glass, side plate"
    },
]

# Insert ADD items at correct positions (by category)
# Strategy: insert each ADD item right before the first item of the next category,
# or at the end of its category group.

def find_insert_index(items_list, category, after_categories=None):
    """Find the index to insert a new item at the end of its category group."""
    last_idx = -1
    for i, item in enumerate(items_list):
        if item["category"] == category:
            last_idx = i
    if last_idx >= 0:
        return last_idx + 1
    return len(items_list)

for add_item in add_items:
    idx = find_insert_index(items, add_item["category"])
    items.insert(idx, add_item)
    print(f"  + Added '{add_item['name']}' at position {idx} in {add_item['category']}")

# === 3. CHANGE: Chocolate Truffles — Baileys -> Hazelnut praline ===
for item in items:
    if item["id"] == "chocolate-truffles59":
        old_desc = item["description"]
        item["description"] = old_desc.replace(
            "3 dark chocolate truffle shells filled with baileys and chocolate ganache",
            "3 dark chocolate truffle shells filled with hazelnut praline"
        )
        # Also update flavors in subtitle if needed
        print(f"\n  ~ Updated Chocolate Truffles description")
        print(f"    Old: {old_desc}")
        print(f"    New: {item['description']}")
        break

# === Write back ===
output = "window.registerFoodCategory(" + json.dumps(items, indent=2, ensure_ascii=False) + ");\n"
path.write_text(output, encoding="utf-8")
print(f"\n✅ Written {len(items)} items to scotts.js")
print(f"   (was {len(dropped) + len(items) - len(add_items)} items, dropped {len(dropped)}, added {len(add_items)})")
