#!/usr/bin/env python3
"""Scrape allergens per dish/drink from viewthe.menu pages into JSON.

Example:
    python scrape_viewthemenu_allergens.py --url https://viewthe.menu/dbav --out data/viewthemenu_allergens.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


@dataclass
class RecipeRecord:
    menu_id: str
    menu_name: str
    section_name: str
    guid: str
    recipe_id: Optional[str]
    name: str = ""
    allergen_status: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        contains = sorted([k for k, v in self.allergen_status.items() if v == "yes"])
        may_contain = sorted([k for k, v in self.allergen_status.items() if v == "may"])
        return {
            "menu_id": self.menu_id,
            "menu_name": self.menu_name,
            "section_name": self.section_name,
            "guid": self.guid,
            "recipe_id": self.recipe_id,
            "item_name": self.name,
            "contains": contains,
            "may_contain": may_contain,
            "allergen_status": dict(sorted(self.allergen_status.items())),
        }


class ViewTheMenuParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.menu_names: Dict[str, str] = {}

        self.current_menu_id: Optional[str] = None
        self.current_menu_depth = 0

        self.current_course_name = ""
        self.capture_course_name = False

        self.capture_menu_option_name = False
        self.menu_option_id: Optional[str] = None

        self.current_recipe: Optional[RecipeRecord] = None
        self.current_recipe_depth = 0
        self.capture_recipe_name = False

        self.current_label_name: Optional[str] = None

        self.items: List[RecipeRecord] = []

    @staticmethod
    def _attrs_to_dict(attrs: List[Tuple[str, Optional[str]]]) -> Dict[str, str]:
        return {k: (v or "") for k, v in attrs}

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        attr = self._attrs_to_dict(attrs)
        cls = attr.get("class", "")

        if tag == "section" and "k10-menus" in cls and attr.get("data-menu-identifier"):
            self.current_menu_id = attr["data-menu-identifier"]
            self.current_menu_depth = 1
            self.current_course_name = ""
            return

        if self.current_menu_id:
            self.current_menu_depth += 1

        if tag == "span" and attr.get("data-menu-identifier") and "k10-menu-selector__option-name" in cls:
            self.menu_option_id = attr.get("data-menu-identifier")
            self.capture_menu_option_name = True

        if tag == "div" and "k10-course__name" in cls:
            self.capture_course_name = True

        is_recipe_info = (
            tag == "div"
            and "k10-recipe" in cls
            and "k10-w-recipe__info" in cls
            and attr.get("data-guid")
        )
        if is_recipe_info and self.current_menu_id:
            self.current_recipe = RecipeRecord(
                menu_id=self.current_menu_id,
                menu_name=self.menu_names.get(self.current_menu_id, ""),
                section_name=self.current_course_name,
                guid=attr.get("data-guid", ""),
                recipe_id=attr.get("data-recipe-id") or None,
            )
            self.current_recipe_depth = 1
            self.current_label_name = None
            return

        if self.current_recipe:
            self.current_recipe_depth += 1

            if tag == "span" and "k10-w-recipe__name" in cls:
                self.capture_recipe_name = True

            if tag == "div" and "k10-recipe__label" in cls and attr.get("data-label-name"):
                self.current_label_name = clean_text(attr.get("data-label-name", ""))

            if tag == "span" and self.current_label_name and attr.get("data-label-name", "").startswith("LabelValue"):
                raw_value = attr.get("data-label-name", "")
                value = raw_value.replace("LabelValue", "").lower()
                if value in {"yes", "may", "no"}:
                    self.current_recipe.allergen_status[self.current_label_name] = value

    def handle_data(self, data: str) -> None:
        text = clean_text(data)
        if not text:
            return

        if self.capture_menu_option_name and self.menu_option_id:
            current = self.menu_names.get(self.menu_option_id, "")
            self.menu_names[self.menu_option_id] = clean_text(f"{current} {text}")

        if self.capture_course_name:
            self.current_course_name = clean_text(f"{self.current_course_name} {text}")

        if self.capture_recipe_name and self.current_recipe:
            self.current_recipe.name = clean_text(f"{self.current_recipe.name} {text}")

    def handle_endtag(self, tag: str) -> None:
        if self.capture_menu_option_name and tag == "span":
            self.capture_menu_option_name = False
            self.menu_option_id = None

        if self.capture_course_name and tag == "div":
            self.capture_course_name = False

        if self.capture_recipe_name and tag == "span":
            self.capture_recipe_name = False

        if self.current_recipe:
            self.current_recipe_depth -= 1
            if self.current_recipe_depth == 0:
                self.current_recipe.menu_name = self.menu_names.get(self.current_recipe.menu_id, self.current_recipe.menu_name)
                self.items.append(self.current_recipe)
                self.current_recipe = None
                self.current_label_name = None
                return

        if self.current_menu_id:
            self.current_menu_depth -= 1
            if self.current_menu_depth == 0:
                self.current_menu_id = None
                self.current_course_name = ""


def fetch_html(url: str, timeout: int = 30) -> str:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def dedupe_records(items: List[RecipeRecord]) -> List[RecipeRecord]:
    merged: Dict[Tuple[str, str], RecipeRecord] = {}
    for item in items:
        key = (item.menu_id, item.guid)
        existing = merged.get(key)
        if not existing:
            merged[key] = item
            continue

        if not existing.name and item.name:
            existing.name = item.name
        if not existing.section_name and item.section_name:
            existing.section_name = item.section_name
        if not existing.recipe_id and item.recipe_id:
            existing.recipe_id = item.recipe_id

        for allergen, status in item.allergen_status.items():
            if status == "yes":
                existing.allergen_status[allergen] = "yes"
            elif status == "may" and existing.allergen_status.get(allergen) != "yes":
                existing.allergen_status[allergen] = "may"
            elif status == "no" and allergen not in existing.allergen_status:
                existing.allergen_status[allergen] = "no"

    result = list(merged.values())
    result.sort(key=lambda x: (x.menu_name.lower(), x.section_name.lower(), x.name.lower(), x.guid))
    return result


def with_mguid(url: str, mguid: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["mguid"] = mguid
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(query),
            parsed.fragment,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape allergens from viewthe.menu pages")
    parser.add_argument("--url", default="https://viewthe.menu/dbav", help="Menu URL")
    parser.add_argument("--out", default="data/viewthemenu_allergens.json", help="Output JSON path")
    parser.add_argument("--html-file", help="Use local HTML file instead of downloading")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.html_file:
        html = Path(args.html_file).read_text(encoding="utf-8")
        parser = ViewTheMenuParser()
        parser.feed(html)
        records = dedupe_records(parser.items)
        output = {
            "source_url": args.url,
            "total_items": len(records),
            "menus_fetched": sorted({r.menu_id for r in records}),
            "items": [r.to_dict() for r in records],
        }
    else:
        html = fetch_html(args.url)
        base_parser = ViewTheMenuParser()
        base_parser.feed(html)
        menu_ids = sorted(base_parser.menu_names.keys())
        if not menu_ids and base_parser.items:
            menu_ids = sorted({r.menu_id for r in base_parser.items})

        all_items: List[RecipeRecord] = []
        fetched_menus: List[str] = []
        errors: Dict[str, str] = {}
        for menu_id in menu_ids:
            menu_url = with_mguid(args.url, menu_id)
            try:
                menu_html = fetch_html(menu_url)
                menu_parser = ViewTheMenuParser()
                menu_parser.feed(menu_html)
                all_items.extend(menu_parser.items)
                fetched_menus.append(menu_id)
            except Exception as exc:  # noqa: BLE001
                errors[menu_id] = str(exc)

        records = dedupe_records(all_items or base_parser.items)
        output = {
            "source_url": args.url,
            "total_items": len(records),
            "menus_found": menu_ids,
            "menus_fetched": fetched_menus,
            "errors": errors,
            "items": [r.to_dict() for r in records],
        }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved {len(records)} items to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
