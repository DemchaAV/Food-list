"""
Full validation of scotts.js — prints a clean summary.
"""
import json
import re
from pathlib import Path
from collections import Counter

path = Path(__file__).parent / "data" / "categories" / "scotts.js"
text = path.read_text(encoding="utf-8")

match = re.search(
    r"window\.registerFoodCategory\s*\(\s*(\[.*\])\s*\)\s*;?\s*$",
    text,
    re.DOTALL,
)
try:
    items = json.loads(match.group(1))
    print(f"✅ Valid JSON — {len(items)} items")
except json.JSONDecodeError as e:
    print(f"❌ Invalid JSON: {e}")
    exit(1)

# Type distribution for glossary
glossary_types = Counter()
for item in items:
    g = item.get("glossary")
    glossary_types[type(g).__name__] += 1

print(f"\n📊 Glossary formats: {dict(glossary_types)}")

# Count items per format
str_items = []
dict_items = []
list_items = []
list_str_items = []    # list with plain strings
list_obj_items = []    # list with {term, definition} objects
other_items = []

for i, item in enumerate(items):
    g = item.get("glossary")
    name = item.get("name", "?")
    if isinstance(g, str):
        str_items.append(f"  [{i}] {name}")
    elif isinstance(g, dict):
        dict_items.append(f"  [{i}] {name} — {len(g)} entries")
    elif isinstance(g, list):
        has_str = any(isinstance(x, str) for x in g)
        has_obj = any(isinstance(x, dict) for x in g)
        if has_obj and not has_str:
            list_obj_items.append(f"  [{i}] {name} — {len(g)} entries")
        elif has_str and not has_obj:
            list_str_items.append(f"  [{i}] {name} — {len(g)} entries")
        elif not g:
            other_items.append(f"  [{i}] {name} — empty list")
        else:
            other_items.append(f"  [{i}] {name} — MIXED list")
    elif g is None:
        other_items.append(f"  [{i}] {name} — null")

print(f"\n🔤 String glossary ({len(str_items)}):")
for s in str_items: print(s)

print(f"\n📖 Dict glossary ({{term: def}}) ({len(dict_items)}):")
for s in dict_items: print(s)

print(f"\n📋 Array of {{term, definition}} objects ({len(list_obj_items)}):")
for s in list_obj_items: print(s)

print(f"\n📋 Array of plain strings ({len(list_str_items)}):")
for s in list_str_items: print(s)

if other_items:
    print(f"\n⚠️ Other/null ({len(other_items)}):")
    for s in other_items: print(s)

# Summary
print(f"\n{'='*50}")
print(f"SUMMARY: {len(items)} items total")
print(f"  String:            {len(str_items)}")
print(f"  Dict {{key: val}}:   {len(dict_items)}")
print(f"  Array [{{term,def}}]: {len(list_obj_items)}")
print(f"  Array [strings]:   {len(list_str_items)}")
print(f"  Other/null/empty:  {len(other_items)}")
