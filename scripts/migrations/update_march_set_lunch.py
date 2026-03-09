#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT_PATH = ROOT / "data" / "categories" / "scotts.js"
PREVIOUS_PATH = ROOT / "data" / "categories" / "scotts_previous.js"
MARCH_JSON_PATH = Path(r"C:\Users\Demch\Downloads\march-set-lunch-menu.json")


def load_wrapped_items(path: Path) -> tuple[str, list[dict], str]:
    text = path.read_text(encoding="utf-8")
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end <= start:
        raise ValueError(f"Could not locate JSON array in {path}")
    return text[:start], json.loads(text[start:end]), text[end:]


def write_wrapped_items(path: Path, prefix: str, items: list[dict], suffix: str) -> None:
    path.write_text(prefix + json.dumps(items, ensure_ascii=False, indent=2) + suffix, encoding="utf-8")


def is_set_lunch_item(item: dict) -> bool:
    item_id = str(item.get("id", "")).lower()
    category = str(item.get("category", "")).lower()
    return item_id.startswith("slm-") or "slm" in category


def replace_set_lunch(items: list[dict], replacement: list[dict]) -> tuple[list[dict], list[dict]]:
    kept: list[dict] = []
    removed: list[dict] = []
    insert_at: int | None = None

    for index, item in enumerate(items):
        if is_set_lunch_item(item):
            if insert_at is None:
                insert_at = index
            removed.append(item)
        else:
            kept.append(item)

    if insert_at is None:
        insert_at = len(items)

    rebuilt = list(items[:insert_at])
    rebuilt.extend(replacement)
    rebuilt.extend(item for item in items[insert_at:] if not is_set_lunch_item(item))
    return rebuilt, removed


def main() -> int:
    march_items = json.loads(MARCH_JSON_PATH.read_text(encoding="utf-8"))
    if not isinstance(march_items, list) or not march_items:
        raise ValueError("March set lunch JSON must contain a non-empty array.")

    current_prefix, current_items, current_suffix = load_wrapped_items(CURRENT_PATH)
    previous_prefix, previous_items, previous_suffix = load_wrapped_items(PREVIOUS_PATH)

    new_current_items, outgoing_current_slm = replace_set_lunch(current_items, march_items)
    if not outgoing_current_slm:
        raise ValueError("No outgoing set lunch items were found in current menu.")

    new_previous_items, _ = replace_set_lunch(previous_items, outgoing_current_slm)

    write_wrapped_items(CURRENT_PATH, current_prefix, new_current_items, current_suffix)
    write_wrapped_items(PREVIOUS_PATH, previous_prefix, new_previous_items, previous_suffix)

    print(f"Updated current menu with {len(march_items)} March set lunch items.")
    print(f"Moved {len(outgoing_current_slm)} outgoing set lunch items into previous menu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
