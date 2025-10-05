import sys
import os
# Ensure repo root is on sys.path so imports like `import database_handler` work when running from /scripts
repo_root = os.path.dirname(os.path.dirname(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import database_handler as db

name = {'kor': '자동화 테스트 디시', 'eng': 'Automated Test Dish'}
# choose two known ingredient ids from ingredient.json: 1 (Rice), 10 (Tomato)
required_ingredients = [
    {'id': 1, 'amount_g': 100.0},
    {'id': 10, 'amount_g': 50.0}
]
new_id = db.add_dish(
    name=name,
    image_url=None,
    required_ingredients=required_ingredients,
    required_cooking_method_ids=[],
    nutrition_data=None,
    cooking_instructions={'kor': '테스트용: 100g 쌀 + 50g 토마토'}
)
print('Added dish id:', new_id)
# load and print the new dish nutrition summary
dish = next((d for d in db._load_table('dish') if d['id'] == new_id), None)
if dish:
    print('Dish name:', dish['name'])
    print('Required ingredients:', dish.get('required_ingredients'))
    print('Nutrition (first 10):')
    for n in dish.get('nutrition_info', [])[:20]:
        print(' -', n.get('name'), ':', n.get('amount_per_dish'))
else:
    print('Failed to find the newly added dish in dish.json')
