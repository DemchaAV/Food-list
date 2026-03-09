"""
validate_scotts.py
Validates scotts.js for JSON validity, field consistency, and data quality.
"""
import json
import re
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "data" / "categories" / "scotts.js"
text = path.read_text(encoding="utf-8")

# 1. Parse
match = re.search(
    r"window\.registerFoodCategory\s*\(\s*(\[.*\])\s*\)\s*;?\s*$",
    text,
    re.DOTALL,
)
if not match:
    print("ERROR: Cannot find registerFoodCategory wrapper")
    exit(1)

try:
    items = json.loads(match.group(1))
    print(f"OK: Valid JSON - {len(items)} items parsed")
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON - {e}")
    exit(1)

# 2. Required fields
REQUIRED = ["id", "name", "subtitle", "category", "description",
            "wineSuggestion", "glossary", "additionalNotes",
            "allergens", "kitchenMep", "serviceMep", "image"]

missing_fields = []
for i, item in enumerate(items):
    for f in REQUIRED:
        if f not in item:
            missing_fields.append(f"  Item {i} ({item.get('name','?')}): missing '{f}'")

if missing_fields:
    print(f"WARN: Missing fields ({len(missing_fields)}):")
    for m in missing_fields:
        print(m)
else:
    print("OK: All items have all required fields")

# 3. Type consistency
glossary_types = Counter()
allergens_types = Counter()
wine_types = Counter()
additionalNotes_types = Counter()

for item in items:
    glossary_types[type(item.get("glossary")).__name__] += 1
    allergens_types[type(item.get("allergens")).__name__] += 1
    wine_types[type(item.get("wineSuggestion")).__name__] += 1
    additionalNotes_types[type(item.get("additionalNotes")).__name__] += 1

print("\nField type distribution:")
print(f"  glossary:        {dict(glossary_types)}")
print(f"  allergens:       {dict(allergens_types)}")
print(f"  wineSuggestion:  {dict(wine_types)}")
print(f"  additionalNotes: {dict(additionalNotes_types)}")

# 4. Check glossary consistency
glossary_issues = []
for i, item in enumerate(items):
    g = item.get("glossary")
    if isinstance(g, list):
        for j, entry in enumerate(g):
            if isinstance(entry, str):
                glossary_issues.append(
                    f"  Item {i} ({item['name']}): glossary[{j}] is a plain string, expected {{term,definition}}"
                )
    elif g is not None and not isinstance(g, (str, dict)):
        glossary_issues.append(
            f"  Item {i} ({item['name']}): glossary is {type(g).__name__}"
        )

if glossary_issues:
    print(f"\nWARN: Glossary consistency issues ({len(glossary_issues)}):")
    for g in glossary_issues:
        print(g)
else:
    print("OK: Glossary format consistent")

# 5. Check unique IDs
ids = [item["id"] for item in items]
dupes = [id for id, count in Counter(ids).items() if count > 1]
if dupes:
    print(f"ERROR: Duplicate IDs: {dupes}")
else:
    print(f"OK: All {len(ids)} IDs unique")

# 6. Check allergens are arrays
allergen_issues = []
for i, item in enumerate(items):
    a = item.get("allergens")
    if not isinstance(a, list):
        allergen_issues.append(f"  Item {i} ({item['name']}): allergens is {type(a).__name__}: {a}")

if allergen_issues:
    print(f"ERROR: Allergens not arrays ({len(allergen_issues)}):")
    for a in allergen_issues:
        print(a)
else:
    print("OK: All allergens are arrays")

# 7. Check wineSuggestion structure
wine_issues = []
for i, item in enumerate(items):
    ws = item.get("wineSuggestion")
    if ws is not None and not isinstance(ws, dict):
        wine_issues.append(f"  Item {i} ({item['name']}): wineSuggestion is {type(ws).__name__}")
    elif isinstance(ws, dict):
        if "name" not in ws:
            wine_issues.append(f"  Item {i} ({item['name']}): wineSuggestion missing 'name'")
        if "notes" not in ws:
            wine_issues.append(f"  Item {i} ({item['name']}): wineSuggestion missing 'notes'")

if wine_issues:
    print(f"WARN: Wine suggestion issues ({len(wine_issues)}):")
    for w in wine_issues:
        print(w)
else:
    print("OK: All wineSuggestions valid (dict with name+notes or null)")

# 8. Null fields summary
null_counts = Counter()
for item in items:
    for f in REQUIRED:
        if item.get(f) is None:
            null_counts[f] += 1

if null_counts:
    print("\nNull field counts:")
    for field, count in sorted(null_counts.items(), key=lambda x: -x[1]):
        print(f"  {field}: {count}/{len(items)} null")

print("\nOK: Validation complete!")
