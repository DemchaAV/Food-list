import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCOTTS_PATH = ROOT / 'data' / 'categories' / 'scotts.js'

with open(SCOTTS_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

start = content.find('[')
end = content.rfind(']') + 1
items = json.loads(content[start:end])

def add_allergen(item, new_allergen):
    allergens = item.get('allergens', [])
    # Check case-insensitively
    if not any(a.lower() == new_allergen.lower() for a in allergens):
        allergens.append(new_allergen)
    item['allergens'] = allergens

for item in items:
    name = (item.get('name') or '').lower()
    subtitle = (item.get('subtitle') or '').lower()
    desc = (item.get('description') or '').lower()
    mep = ((item.get('kitchenMep') or '') + ' ' + (item.get('serviceMep') or '')).lower()
    
    full_text = name + ' ' + subtitle + ' ' + desc + ' ' + mep
    core_text = name + ' ' + subtitle
    
    # 1. Caviar -> Fish
    if 'caviar' in core_text:
        add_allergen(item, 'Fish')
        
    # 2. Lobster / Prawns -> Crustaceans, Shellfish
    if 'lobster' in core_text or 'prawn' in core_text:
        add_allergen(item, 'Crustaceans')
        add_allergen(item, 'Shellfish')
        
    # 3. Crab -> Crustaceans, Shellfish (only in core text)
    if 'crab' in core_text:
        add_allergen(item, 'Crustaceans')
        add_allergen(item, 'Shellfish')
        
    # 4. Scallops, Octopus, Clams -> Molluscs, Shellfish
    if 'scallop' in core_text or 'octopus' in core_text or 'clam' in core_text:
        add_allergen(item, 'Molluscs')
        add_allergen(item, 'Shellfish')
        
    # 5. Fish types -> Fish
    if any(fish in core_text for fish in ['sole', 'seabass', 'sea bass', 'tuna', 'trout', 'haddock', 'halibut', 'skate', 'monkfish', 'hake', 'pollock']):
        add_allergen(item, 'Fish')
        
    # 6. Mayo / Hollandaise -> Eggs
    if 'mayo' in full_text or 'hollandaise' in full_text:
        add_allergen(item, 'Eggs')

# Write back
new_json = json.dumps(items, indent=2, ensure_ascii=False)
new_content = content[:start] + new_json + content[end:]

with open(SCOTTS_PATH, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Applied smart allergen updates successfully!")
