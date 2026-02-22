"""
cleanup_scotts.py
─────────────────
Reads data/categories/scotts.js, sends every menu item to the local
Ollama gemma3:4b model for cleanup, backs up the original file,
and writes a corrected version.

Requirements: pip install requests   (usually pre-installed)
GPU:          NVIDIA GTX 1660 Ti 6 GB — gemma3:4b fits comfortably.

Usage:        python cleanup_scotts.py
"""

import json
import re
import shutil
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: 'requests' library not found. Install it:  pip install requests")
    sys.exit(1)

# ─── Configuration ────────────────────────────────────────────────────
SCOTTS_JS_PATH = Path(__file__).parent / "data" / "categories" / "scotts.js"
BACKUP_PATH = SCOTTS_JS_PATH.with_suffix(".js.backup")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"
TEMPERATURE = 0.1
TIMEOUT_SECONDS = 120
MAX_RETRIES = 2

# Fields the model must NEVER change
IMMUTABLE_FIELDS = {"id", "image", "category", "name"}

# ─── System prompt for the model ─────────────────────────────────────
SYSTEM_PROMPT = """\
You are a data-quality assistant for a restaurant menu database.
You will receive a single JSON object representing one menu item.

Your task – return a CORRECTED version of that JSON object.

Rules:
1. Return ONLY valid JSON. No markdown, no code fences, no commentary.
2. Fix spelling and grammar mistakes in all text fields.
3. Extract allergens from "description", "additionalNotes", and "glossary"
   into the "allergens" array.
   Use these canonical allergen names:
     Gluten, Dairy, Eggs, Fish, Crustaceans, Molluscs, Nuts, Peanuts,
     Soya, Celery, Mustard, Sesame, Sulphites, Lupin, Pork Gelatine, Alcohol
   Only add allergens that are clearly mentioned or directly inferable.
   If none are found, set "allergens" to an empty array [].
4. If "wineSuggestion" is null BUT wine info exists in "description",
   move it into "wineSuggestion" (with "name" and "notes") and remove it
   from "description".
5. If "wineSuggestion.name" contains tasting notes text, move that text
   into "wineSuggestion.notes" and keep only the wine name in "name".
6. If "description" is null but the description text is inside "subtitle",
   move that text into "description" and clean up "subtitle" so it only
   contains the short subtitle line.
7. Fill incomplete "glossary" entries (e.g. "Pink radicchio-" with no
   definition) with a short, accurate definition if you know it.
8. Do NOT change: "id", "image", "category", "name".
9. Do NOT invent facts. If you are unsure, leave the field as-is.
10. Keep every field present in the output, even if its value is null.
11. "kitchenMep" and "serviceMep" — fix typos only, do not invent content.
12. Keep "subtitle" in UPPER CASE style as it currently is.
"""

# ─── Helpers ──────────────────────────────────────────────────────────

def read_scotts_js(path: Path) -> list[dict]:
    """Read scotts.js, strip JS wrapper, return list of items."""
    text = path.read_text(encoding="utf-8")

    # Remove: window.registerFoodCategory(\n ... \n);
    match = re.search(
        r"window\.registerFoodCategory\s*\(\s*(\[.*\])\s*\)\s*;?\s*$",
        text,
        re.DOTALL,
    )
    if not match:
        print("ERROR: Could not parse scotts.js wrapper")
        sys.exit(1)

    return json.loads(match.group(1))


def write_scotts_js(path: Path, items: list[dict]) -> None:
    """Write items back into scotts.js with the JS wrapper."""
    json_str = json.dumps(items, indent=2, ensure_ascii=False)
    content = f"window.registerFoodCategory(\n{json_str}\n);\n"
    path.write_text(content, encoding="utf-8")


def call_ollama(item: dict) -> dict | None:
    """Send one item to Ollama, return cleaned JSON dict or None."""
    user_prompt = (
        "Here is the menu item JSON to clean up:\n\n"
        + json.dumps(item, indent=2, ensure_ascii=False)
    )

    payload = {
        "model": MODEL,
        "prompt": user_prompt,
        "system": SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": TEMPERATURE,
            "num_predict": 4096,
        },
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
            resp.raise_for_status()
            raw = resp.json().get("response", "")

            # Try to extract JSON from response (strip stray text/fences)
            raw = raw.strip()
            if raw.startswith("```"):
                raw = re.sub(r"^```\w*\n?", "", raw)
                raw = re.sub(r"\n?```$", "", raw)
                raw = raw.strip()

            cleaned = json.loads(raw)

            # Validate structure
            if not isinstance(cleaned, dict):
                raise ValueError("Response is not a JSON object")

            # Guard immutable fields
            for field in IMMUTABLE_FIELDS:
                cleaned[field] = item[field]

            # Ensure all expected fields exist
            for key in item:
                if key not in cleaned:
                    cleaned[key] = item[key]

            return cleaned

        except (json.JSONDecodeError, ValueError) as e:
            if attempt < MAX_RETRIES:
                print(f"      ⟳ Retry {attempt}/{MAX_RETRIES - 1} (bad JSON: {e})")
                # Second attempt: ask to fix
                payload["prompt"] = (
                    "The previous output was invalid JSON. "
                    "Here is the original item again. "
                    "Return ONLY the corrected JSON object, nothing else.\n\n"
                    + json.dumps(item, indent=2, ensure_ascii=False)
                )
            else:
                print(f"      ✗ Failed after {MAX_RETRIES} attempts: {e}")
                return None

        except requests.RequestException as e:
            print(f"      ✗ HTTP error: {e}")
            return None

    return None


def items_differ(original: dict, cleaned: dict) -> bool:
    """Check if the cleaned item is different from original."""
    return json.dumps(original, sort_keys=True) != json.dumps(cleaned, sort_keys=True)


# ─── Main ─────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  Scott's Menu Data Cleanup  (Ollama + gemma3:4b)")
    print("=" * 60)

    # 1. Read
    if not SCOTTS_JS_PATH.exists():
        print(f"ERROR: {SCOTTS_JS_PATH} not found")
        sys.exit(1)

    items = read_scotts_js(SCOTTS_JS_PATH)
    total = len(items)
    print(f"\n📂 Loaded {total} items from {SCOTTS_JS_PATH.name}")

    # 2. Backup
    shutil.copy2(SCOTTS_JS_PATH, BACKUP_PATH)
    print(f"💾 Backup saved to {BACKUP_PATH.name}\n")

    # 3. Process
    cleaned_items: list[dict] = []
    stats = {"success": 0, "changed": 0, "kept_original": 0}

    for i, item in enumerate(items, 1):
        name = item.get("name", "???")
        print(f"[{i:>2}/{total}] {name} ...", end=" ", flush=True)

        start = time.time()
        cleaned = call_ollama(item)
        elapsed = time.time() - start

        if cleaned is not None:
            changed = items_differ(item, cleaned)
            cleaned_items.append(cleaned)
            stats["success"] += 1
            if changed:
                stats["changed"] += 1
                print(f"✅ fixed ({elapsed:.1f}s)")
            else:
                print(f"✅ ok    ({elapsed:.1f}s)")
        else:
            cleaned_items.append(item)  # keep original
            stats["kept_original"] += 1
            print(f"⚠️  kept original ({elapsed:.1f}s)")

    # 4. Write
    print("\n" + "─" * 60)
    write_scotts_js(SCOTTS_JS_PATH, cleaned_items)
    print(f"📝 Written {total} items to {SCOTTS_JS_PATH.name}")

    # 5. Summary
    print(f"\n{'─' * 60}")
    print(f"  Total items:    {total}")
    print(f"  Processed OK:   {stats['success']}")
    print(f"  Changed:        {stats['changed']}")
    print(f"  Kept original:  {stats['kept_original']}")
    print(f"{'─' * 60}")
    print("Done! Compare scotts.js.backup vs scotts.js to review changes.")


if __name__ == "__main__":
    main()
