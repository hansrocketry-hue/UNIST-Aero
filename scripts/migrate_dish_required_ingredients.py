"""
Migrate dish.json entries from 'required_ingredient_ids' to 'required_ingredients' (list of {id, amount_g}).
This script tries to extract quantities (grams) from cooking_instructions when available using simple regexes
for patterns like '70g', '10 g', '150g', or patterns like '200g 물로' where numbers followed by g indicate grams.
If no quantity is found for an ingredient, the script will guess a reasonable default depending on ingredient type:
- staple grains (rice, pasta): 70-150g
- vegetables: 10-60g
- condiments/seasonings: 1-20g
- default fallback: 10g

The heuristics are intentionally simple. After running, a backup of the original dish.json is written to dish.json.bak
and dish.json is overwritten with the migrated structure.

Usage: run with the workspace python (e.g., python scripts/migrate_dish_required_ingredients.py)
"""
import json
import re
import os

WORKDIR = os.path.dirname(os.path.dirname(__file__)) if os.path.basename(__file__) == 'migrate_dish_required_ingredients.py' else '.'
DISH_PATH = os.path.join(WORKDIR, 'dish.json')
ING_PATH = os.path.join(WORKDIR, 'ingredient.json')

# Simple ingredient name hints to classify probable typical amounts (grams)
STAPLE_HINTS = ['rice', '밥', 'pasta', '면', 'udon', 'soba', 'risotto', 'rice']
VEG_HINTS = ['lettuce', 'kale', 'tomato', 'potato', 'onion', 'cabbage', 'carrot', 'veg', 'vegetable', '채소', '야채']
CONDIMENT_HINTS = ['salt', 'sugar', 'soy', 'soy sauce', 'ssamjang', '고추장', '된장', '간장']

GRAM_RE = re.compile(r"(\d+(?:[\.,]\d+)?)\s*(?:g|g\b|grams?)", re.IGNORECASE)
NUMBER_G_RE = re.compile(r"(\d+(?:[\.,]\d+)?)\s*g\b", re.IGNORECASE)


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def guess_amount_for_ingredient(ing_name_kor, ing_name_eng):
    name = (ing_name_eng or '') + ' ' + (ing_name_kor or '')
    name = name.lower()
    # staple
    for h in STAPLE_HINTS:
        if h in name:
            return 100.0
    for h in VEG_HINTS:
        if h in name:
            return 30.0
    for h in CONDIMENT_HINTS:
        if h in name:
            return 5.0
    # fallback
    return 10.0


def extract_first_gram_from_text(text):
    if not text:
        return None
    # find first match like '70g' or '70 g' or '70g,' etc.
    m = NUMBER_G_RE.search(text)
    if m:
        try:
            return float(m.group(1).replace(',', '.'))
        except Exception:
            pass
    # fallback to broader grams regex
    m2 = GRAM_RE.search(text)
    if m2:
        try:
            return float(m2.group(1).replace(',', '.'))
        except Exception:
            pass
    return None


def migrate():
    dishes = load_json(DISH_PATH)
    ingredients = load_json(ING_PATH)
    ing_by_id = {i['id']: i for i in ingredients}

    if not dishes:
        print('No dishes found; aborting.')
        return

    # backup
    bak_path = DISH_PATH + '.bak'
    if not os.path.exists(bak_path):
        os.rename(DISH_PATH, bak_path)
        print(f'Backed up {DISH_PATH} -> {bak_path}')
        dishes = load_json(bak_path)
    else:
        print(f'Backup {bak_path} already exists; reading {DISH_PATH} directly')

    migrated = []
    for d in dishes:
        newd = dict(d)
        reqs = []
        # If already migrated, keep
        if 'required_ingredients' in d and isinstance(d['required_ingredients'], list) and d['required_ingredients']:
            migrated.append(newd)
            continue

        raw_ids = d.get('required_ingredient_ids', []) or []
        # Try to extract grams from cooking instructions
        ci = d.get('cooking_instructions')
        ci_text = ''
        if isinstance(ci, dict):
            ci_text = ' '.join(ci.values())
        elif isinstance(ci, str):
            ci_text = ci

        # If cooking instruction has numeric grams, use it as a default per-ingredient if only one main ingredient
        first_gram = extract_first_gram_from_text(ci_text)

        for iid in raw_ids:
            try:
                iid_int = int(iid)
            except Exception:
                continue
            ing = ing_by_id.get(iid_int)
            kor = ing.get('name', {}).get('kor') if ing else None
            eng = ing.get('name', {}).get('eng') if ing else None
            amt = None
            # Try per-ingredient mentions like '70g rice' by searching ingredient name near a number
            if ci_text:
                # naive approach: look for patterns like '<num>g ... <ingredient name fragment>' or '<ingredient name> <num>g'
                # We'll search for number+g and if ingredient name appears within 20 characters of the match, use it
                for m in NUMBER_G_RE.finditer(ci_text):
                    num = m.group(1)
                    start, end = m.span()
                    window = ci_text[max(0, start-20):min(len(ci_text), end+20)].lower()
                    # check for ingredient name words in window
                    found = False
                    if kor and kor.lower() in window:
                        found = True
                    if not found and eng and eng.lower() in window:
                        found = True
                    if found:
                        try:
                            amt = float(num.replace(',', '.'))
                            break
                        except Exception:
                            pass
            # If we didn't find per-ingredient amt, use first_gram if exists and there is only one raw id
            if amt is None:
                if first_gram and len(raw_ids) == 1:
                    amt = first_gram
            # still None: guess by ingredient type
            if amt is None:
                amt = guess_amount_for_ingredient(kor, eng)

            reqs.append({'id': iid_int, 'amount_g': float(amt)})

        newd['required_ingredients'] = reqs
        # Optionally remove old field to avoid confusion
        if 'required_ingredient_ids' in newd:
            del newd['required_ingredient_ids']
        migrated.append(newd)

    # write migrated dish.json
    save_json(DISH_PATH, migrated)
    print(f'Migration complete: wrote {len(migrated)} dishes to {DISH_PATH}')


if __name__ == '__main__':
    migrate()
