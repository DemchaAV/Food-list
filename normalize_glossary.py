"""
normalize_glossary.py
Converts all glossary fields in scotts.js to a consistent array of strings format.
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


def normalize_glossary(g):
    """Convert any glossary format to array of strings."""
    if g is None:
        return []
    if isinstance(g, str):
        if not g.strip():
            return []
        return [g]
    if isinstance(g, dict):
        if not g:
            return []
        return [f"{k}: {v}" for k, v in g.items()]
    if isinstance(g, list):
        result = []
        for item in g:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                if "term" in item and "definition" in item:
                    result.append(f"{item['term']}: {item['definition']}")
                else:
                    result.append(json.dumps(item))
        return result
    return []


changed = 0
for item in items:
    old = item.get("glossary")
    new_val = normalize_glossary(old)
    if old != new_val:
        changed += 1
    item["glossary"] = new_val

json_str = json.dumps(items, indent=2, ensure_ascii=False)
content = f"window.registerFoodCategory(\n{json_str}\n);\n"
path.write_text(content, encoding="utf-8")
print(f"✅ Normalized {changed} glossary fields to arrays of strings")
print("Done!")
