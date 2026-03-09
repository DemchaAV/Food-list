"""
normalize_glossary.py
Converts glossary fields in wrapped menu JS files to a consistent
array-of-objects format: [{term, definition}, ...].
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MENU_FILES = [
    (ROOT / "data" / "categories" / "scotts.js", "registerFoodCategory"),
    (ROOT / "data" / "categories" / "scotts_previous.js", "registerPreviousFoodCategory"),
]


def to_glossary_entry(term, definition):
    clean_term = str(term or "").strip()
    clean_definition = str(definition or "").strip()
    if not clean_term and not clean_definition:
        return None
    if not clean_term:
        clean_term = "Info"
    return {"term": clean_term, "definition": clean_definition}


def parse_string_entry(value):
    text = str(value or "").strip()
    if not text:
        return None
    idx = text.find(":")
    if 0 < idx < 60:
        return to_glossary_entry(text[:idx], text[idx + 1 :])
    return to_glossary_entry("Info", text)


def normalize_glossary(value):
    """Convert any supported glossary shape to [{term, definition}, ...]."""
    if value is None:
        return []
    if isinstance(value, str):
        entry = parse_string_entry(value)
        return [entry] if entry else []
    if isinstance(value, dict):
        if "term" in value or "definition" in value:
            entry = to_glossary_entry(value.get("term"), value.get("definition"))
            return [entry] if entry else []
        entries = [to_glossary_entry(term, definition) for term, definition in value.items()]
        return [entry for entry in entries if entry]
    if isinstance(value, list):
        normalized = []
        for item in value:
            if isinstance(item, str):
                entry = parse_string_entry(item)
            elif isinstance(item, dict):
                if "term" in item or "definition" in item:
                    entry = to_glossary_entry(item.get("term"), item.get("definition"))
                else:
                    first_term, first_definition = next(iter(item.items()), ("Info", ""))
                    entry = to_glossary_entry(first_term, first_definition)
            else:
                entry = to_glossary_entry("Info", item)
            if entry:
                normalized.append(entry)
        return normalized
    return [to_glossary_entry("Info", value)]


def normalize_wrapped_file(path, wrapper_name):
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf"window\.{wrapper_name}\s*\(\s*(\[.*\])\s*\)\s*;?\s*$",
        text,
        re.DOTALL,
    )
    if not match:
        raise ValueError(f"Could not parse wrapped items from {path.name}")

    items = json.loads(match.group(1))
    changed = 0
    for item in items:
        old = item.get("glossary")
        new_val = normalize_glossary(old)
        if old != new_val:
            changed += 1
        item["glossary"] = new_val

    content = f"window.{wrapper_name}(\n{json.dumps(items, indent=2, ensure_ascii=False)}\n);\n"
    path.write_text(content, encoding="utf-8")
    return changed, len(items)


for menu_path, wrapper in MENU_FILES:
    changed_count, total = normalize_wrapped_file(menu_path, wrapper)
    print(f"OK: Normalized glossary in {menu_path.name} for {changed_count}/{total} items")
