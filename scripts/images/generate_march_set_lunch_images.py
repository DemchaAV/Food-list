#!/usr/bin/env python3
"""Generate realistic images for March set lunch items only.

Usage (PowerShell):
  $env:OPENAI_API_KEY='sk-...'
  python scripts/images/generate_march_set_lunch_images.py
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
SCOTTS_PATH = ROOT / "data" / "categories" / "scotts.js"
IMG_DIR = ROOT / "data" / "categories" / "menu_images"
MARCH_JSON_PATH = Path(r"C:\Users\Demch\Downloads\march-set-lunch-menu.json")
API_URL = "https://api.openai.com/v1/images/generations"
MODEL = "gpt-image-1.5"


def load_scotts_items() -> tuple[str, List[dict], str]:
    content = SCOTTS_PATH.read_text(encoding="utf-8")
    start = content.find("[")
    end = content.rfind("]") + 1
    items = json.loads(content[start:end])
    return content[:start], items, content[end:]


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "dish"


def build_prompt(item: dict) -> str:
    name = (item.get("name") or "").strip()
    subtitle = (item.get("subtitle") or "").strip()
    description = (item.get("description") or "").strip()
    category = (item.get("category") or "").strip()
    kitchen_mep = (item.get("kitchenMep") or "").strip()

    parts = [
        f"Photorealistic high-end restaurant food photo of {name}.",
        "Single plated dish, elegant fine dining plating, realistic ingredient textures, natural lighting, shallow depth of field.",
        "No text, no logo, no watermark, no people, no hands, no cutlery in frame unless essential to plating.",
    ]
    if category:
        parts.append(f"Menu category: {category}.")
    if subtitle:
        parts.append(f"Key plated elements: {subtitle}.")
    if description:
        parts.append(f"Dish description: {description[:420]}.")
    if kitchen_mep:
        parts.append(f"Serveware guidance: present on {kitchen_mep}.")
    return " ".join(parts)


def call_images_api(api_key: str, prompt: str, size: str = "1024x1024") -> bytes:
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "size": size,
        "n": 1,
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"API error {exc.code}: {err_body}") from exc

    if "data" not in data or not data["data"]:
        raise RuntimeError(f"Unexpected API response: {data}")

    b64 = data["data"][0].get("b64_json")
    if not b64:
        raise RuntimeError(f"No b64_json in API response: {data}")

    return base64.b64decode(b64)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate realistic images for March set lunch items")
    parser.add_argument("--size", default="1024x1024", help="Image size, e.g. 1024x1024")
    parser.add_argument("--dry-run", action="store_true", help="Show planned actions without API calls")
    parser.add_argument("--limit", type=int, default=0, help="Optional limit for number of generated images (0 = all March items)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key and not args.dry_run:
        print("OPENAI_API_KEY is not set.")
        return 1

    IMG_DIR.mkdir(parents=True, exist_ok=True)

    march_seed = json.loads(MARCH_JSON_PATH.read_text(encoding="utf-8"))
    target_ids = {item["id"] for item in march_seed}

    prefix, scotts_items, suffix = load_scotts_items()
    march_items = [item for item in scotts_items if item.get("id") in target_ids]
    if args.limit > 0:
        march_items = march_items[: args.limit]

    if not march_items:
        print("No March set lunch items found in scotts.js")
        return 1

    updated_paths: Dict[str, str] = {}
    failures: List[str] = []

    for item in march_items:
        dish_name = (item.get("name") or "").strip()
        filename = f"{slugify(dish_name)}-generated.png"
        out_path = IMG_DIR / filename
        rel_path = f"data/categories/menu_images/{filename}"
        prompt = build_prompt(item)

        if args.dry_run:
            print(f"[dry-run] {dish_name} -> {out_path}")
            continue

        print(f"Generating: {dish_name}")
        try:
            image_bytes = call_images_api(api_key=api_key, prompt=prompt, size=args.size)
            out_path.write_bytes(image_bytes)
            updated_paths[dish_name] = rel_path
            print(f"Saved: {out_path}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{dish_name}: {exc}")
            print(f"Failed: {dish_name} -> {exc}")

    if args.dry_run:
        print(f"[dry-run] Would generate/update {len(march_items)} March set lunch images.")
        return 0

    updated = 0
    for item in scotts_items:
        item_name = item.get("name")
        if item_name in updated_paths:
            item["image"] = updated_paths[item_name]
            updated += 1

    SCOTTS_PATH.write_text(prefix + json.dumps(scotts_items, ensure_ascii=False, indent=2) + suffix, encoding="utf-8")
    print(f"Updated image paths in {SCOTTS_PATH} for {updated} March item(s)")

    if failures:
        print(f"Failed items: {len(failures)}")
        for failure in failures:
            print(f" - {failure}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
