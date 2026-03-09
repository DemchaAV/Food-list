import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
JS_FILE = os.path.join(ROOT, "data", "categories", "scotts.js")
IMG_DIR = os.path.join(ROOT, "data", "categories", "menu_images")
OUT_FILE = JS_FILE

def normalize_name(name):
    # Remove (SLM), punctuation, spaces, and make lowercase
    name = re.sub(r'\(slm\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'[^a-zA-Z0-9]', '', name)
    return name.lower()

MANUAL_MAPPINGS = {
    "selectionofthreecheeses": [
        "SELECTION OF THREE CHEESES_0.jpeg", 
        "SELECTION OF THREE CHEESES_1.jpeg", 
        "SELECTION OF THREE CHEESES_2.jpeg"
    ],
    # Also fix delice name manually to use its specific photo
    "chocolateandhazelnutdelice": "CHOCOLATE AND HAZELNUT DELICE.jpeg",
    "slmchocolateandhazelnutdelice": "(SLM) CHOCOLATE AND HAZELNUT DELICE.jpeg" 
}

def main():
    with open(JS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    prefix = "window.registerFoodCategory("
    suffix = ");"

    start_idx = content.find(prefix)
    if start_idx == -1:
        print("Could not find window.registerFoodCategory(")
        return

    start_idx += len(prefix)
    end_idx = content.rfind(suffix)
    if end_idx == -1:
        print("Could not find suffix );")
        return

    json_str = content[start_idx:end_idx].strip()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return

    images = os.listdir(IMG_DIR)

    img_map = {}
    for img in images:
        name_without_ext = os.path.splitext(img)[0]
        norm = normalize_name(name_without_ext)
        img_map[norm] = img

    matched_count = 0
    missing = []
    
    # Validation flags
    issues = []

    for item in data:
        item_name = item.get('name', '')
        norm_item = normalize_name(item_name)
        
        # Check standard normalize name match, mapping, or manual array override
        if norm_item in MANUAL_MAPPINGS:
            val = MANUAL_MAPPINGS[norm_item]
            if isinstance(val, list):
                item['image'] = [f"data/categories/menu_images/{v}" for v in val]
            else:
                item['image'] = f"data/categories/menu_images/{val}"
            matched_count += 1
        elif norm_item in img_map:
            item['image'] = f"data/categories/menu_images/{img_map[norm_item]}"
            matched_count += 1
        else:
            missing.append(item_name)
            item['image'] = None
            issues.append(f"Image not found for item: {item_name}")

        # Basic data validation for each item
        if not item.get('id'):
            issues.append(f"Missing ID for item: {item_name}")
        if not item.get('category'):
            issues.append(f"Missing category for item: {item_name}")
        if not item.get('description'):
            issues.append(f"Missing description for item: {item_name}")

    new_json_str = json.dumps(data, indent=2, ensure_ascii=False)
    final_content = content[:start_idx] + "\n" + new_json_str + "\n" + content[end_idx:]

    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"Successfully processed {len(data)} items.")
    print(f"Matched images for {matched_count} items.")
    print(f"Missing images for {len(missing)} items:")
    for m in missing:
        print(f" - {m}")

    print("\n--- Validation Report ---")
    if not issues:
        print("All data fields are perfectly valid.")
    else:
        for issue in issues:
            print(issue)
            
    # Unused images logic
    used_images = set()
    for item in data:
        img_val = item.get('image')
        if isinstance(img_val, list):
            used_images.update(img_val)
        elif isinstance(img_val, str):
            used_images.add(img_val)

    all_image_paths = set(f"data/categories/menu_images/{img}" for img in images)
    unused = all_image_paths - used_images
    if unused:
        print(f"\nThere are {len(unused)} unused images in the folder:")
        for u in unused:
            print(f" - {u}")

    print("\nFile scotts.js has been successfully updated with the image associations.")

if __name__ == "__main__":
    main()
