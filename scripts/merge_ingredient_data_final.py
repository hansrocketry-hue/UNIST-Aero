import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(__file__))
ING_PATH = os.path.join(ROOT, 'ingredient.json')
FINAL_PATH = os.path.join(ROOT, 'ingredient_data_final.json')

def load(p):
    with open(p, 'r', encoding='utf-8') as f:
        return json.load(f)

def save(p, data):
    with open(p, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def parse_production_time(val):
    if isinstance(val, dict):
        return val
    if not val or not isinstance(val, str):
        return {"producible": False}
    s = val.strip()
    # look for two numbers
    m = re.search(r"(\d+)\D+(\d+)", s)
    if m:
        try:
            mn = int(m.group(1))
            mx = int(m.group(2))
            return {"min": mn, "max": mx, "producible": True}
        except ValueError:
            pass
    # single number
    m2 = re.search(r"(\d+)", s)
    if m2:
        try:
            v = int(m2.group(1))
            return {"min": v, "max": v, "producible": True}
        except ValueError:
            pass
    # contains 지구 or parentheses -> not producible locally
    if '지구' in s or '(' in s or '–' in s and not re.search(r"(\d+)", s):
        return {"producible": False, "note": s}
    return {"producible": False, "note": s}

def normalize_entry(e):
    out = {}
    out['id'] = e.get('id')
    out['name'] = e.get('name', {})
    out['research_ids'] = e.get('research_ids', [])
    # prefer nutrition_info then nutrition
    if 'nutrition_info' in e:
        out['nutrition'] = e.get('nutrition_info')
    elif 'nutrition' in e:
        out['nutrition'] = e.get('nutrition')
    else:
        out['nutrition'] = []
    # parse production_time
    out['production_time'] = parse_production_time(e.get('production_time'))
    return out

def main():
    if not os.path.exists(FINAL_PATH):
        print(f"{FINAL_PATH} not found")
        return
    final = load(FINAL_PATH)
    if os.path.exists(ING_PATH):
        existing = load(ING_PATH)
    else:
        existing = []

    idx = {item.get('id'): item for item in existing}

    changed = False
    for e in final:
        nid = e.get('id')
        norm = normalize_entry(e)
        if nid in idx:
            # replace existing
            if idx[nid] != norm:
                idx[nid] = norm
                changed = True
        else:
            idx[nid] = norm
            changed = True

    merged = [idx[k] for k in sorted(idx.keys())]

    if changed:
        # backup
        bak = ING_PATH + '.bak'
        if os.path.exists(ING_PATH) and not os.path.exists(bak):
            os.rename(ING_PATH, bak)
            print(f'Backed up {ING_PATH} -> {bak}')
        save(ING_PATH, merged)
        print(f'Wrote merged ingredient data to {ING_PATH} ({len(merged)} entries)')
    else:
        print('No changes detected; ingredient.json unchanged')

if __name__ == '__main__':
    main()
