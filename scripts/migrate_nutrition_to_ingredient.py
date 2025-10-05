import json
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
ING_PATH = os.path.join(ROOT, 'ingredient.json')
NUT_PATH = os.path.join(ROOT, 'nutrition.json')

def load_json(p):
    if not os.path.exists(p):
        return None
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(p, data):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def migrate():
    ingredients = load_json(ING_PATH)
    nutrition = load_json(NUT_PATH)
    if ingredients is None:
        print('ingredient.json not found; aborting')
        return
    if nutrition is None:
        print('nutrition.json not found; nothing to migrate')
        return

    nut_by_ing = {n.get('ingredient_id'): n for n in nutrition}

    changed = False
    for ing in ingredients:
        iid = ing.get('id')
        if iid in nut_by_ing:
            ing_n = nut_by_ing[iid].get('nutrients', [])
            # place nutrition data under 'nutrition' key
            ing['nutrition'] = ing_n
            # remove legacy nutrition_id if present
            if 'nutrition_id' in ing:
                del ing['nutrition_id']
            changed = True

    if changed:
        # backup original nutrition.json
        bak = NUT_PATH + '.bak'
        if not os.path.exists(bak):
            os.rename(NUT_PATH, bak)
            print(f'Backed up {NUT_PATH} -> {bak}')
        else:
            os.remove(NUT_PATH)
            print(f'Removed original {NUT_PATH} (backup exists)')

        save_json(ING_PATH, ingredients)
        print('Migration complete: embedded nutrition into ingredient.json')
    else:
        print('No matching nutrition entries found; nothing changed')

if __name__ == '__main__':
    migrate()
