import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCOTTS_PATH = ROOT / 'data' / 'categories' / 'scotts.js'

with open(SCOTTS_PATH, 'r', encoding='utf-8') as f:
    data = f.read()

start = data.find('[')
end = data.rfind(']') + 1
json_data = data[start:end]

items = json.loads(json_data)

rules = {
    'Dairy': ['butter', 'cream', 'milk', 'cheese', 'burrata', 'parmesan', 'whey', 'yoghurt', 'creme fraiche', 'ricotta', 'mascarpone', 'stracciatella', 'buttermilk', 'fondant', 'gorgonzola', 'mozzarella'],
    'Gluten': ['bread', 'toast', 'flour', 'pastry', 'tart', 'crouton', 'croutons', 'pasta', 'crumble', 'crust', 'panko', 'brioche', 'dough', 'wafer', 'biscuit', 'cake', 'soy sauce', 'tempura', 'cracker', 'cracker'],
    'Crustaceans': ['prawn', 'prawns', 'lobster', 'crab', 'shrimp', 'langoustine', 'crayfish'],
    'Molluscs': ['oyster', 'oysters', 'clam', 'clams', 'mussel', 'mussels', 'scallop', 'scallops', 'squid', 'octopus', 'cuttlefish', 'whelk', 'whelks'],
    'Fish': ['fish', 'salmon', 'seabass', 'cod', 'halibut', 'tuna', 'caviar', 'anchovy', 'anchovies', 'monkfish', 'sole', 'turbot', 'roe', 'yellowtail', 'bass', 'snapper'],
    'Soya': ['soy', 'soya', 'miso', 'edamame', 'soy sauce', 'ponzu', 'tofu'],
    'Sesame': ['sesame', 'tahini'],
    'Egg': ['egg', 'eggs', 'mayo', 'mayonnaise', 'hollandaise', 'meringue', 'aioli', 'bearnaise', 'custard'],
    'Mustard': ['mustard', 'dijon'],
    'Celery': ['celery', 'celeriac'],
    'Nuts': ['almond', 'walnut', 'hazelnut', 'pistachio', 'pecan', 'cashew', 'macadamia', 'nut', 'marzipan', 'pine nut'],
    'Peanuts': ['peanut', 'peanuts'],
    'Sulphites': ['wine', 'vinegar', 'champagne', 'prosecco', 'port', 'sherry', 'mirin']
}

print("=== ALLERGEN VERIFICATION REPORT ===")

for item in items:
    desc = ((item.get('name') or '') + ' ' + 
            (item.get('subtitle') or '') + ' ' + 
            (item.get('description') or '') + ' ' + 
            (item.get('kitchenMep') or '') + ' ' + 
            str(item.get('glossary', []))).lower()
            
    current_allergens = item.get('allergens') or []
    normalized_allergens = set(a.lower() for a in current_allergens)
    
    if 'shellfish' in normalized_allergens:
        normalized_allergens.add('crustaceans')
        normalized_allergens.add('molluscs')
        
    suggested = set()
    found_keywords = {}
    for allergen, keywords in rules.items():
        for kw in keywords:
            if re.search(r'\b' + kw + r'\b', desc):
                suggested.add(allergen)
                if allergen not in found_keywords:
                    found_keywords[allergen] = []
                found_keywords[allergen].append(kw)
                
    missing = []
    for s in suggested:
        if s.lower() not in normalized_allergens:
            if s == 'Sulphites' and any('sulph' in a.lower() or 'sulf' in a.lower() for a in current_allergens):
                continue
            if s in ['Molluscs', 'Crustaceans'] and any(a.lower() == 'shellfish' for a in current_allergens):
                continue
            missing.append(f"{s} (from: {', '.join(found_keywords[s])})")
            
    if missing:
        print(f"Item ID: {item.get('id')}")
        print(f"Name: {item['name']}")
        print(f"Current: {current_allergens}")
        print(f"Missing: {missing}")
        print("-" * 50)
