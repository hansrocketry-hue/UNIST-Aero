
import json
import os
from datetime import datetime

DATA_FILES = {
    'ingredient': 'ingredient.json',
    'storaged-ingredient': 'storaged-ingredient.json',
    'cooking-methods': 'cooking-methods.json',
    'research-data': 'research-data.json',
    'dish': 'dish.json',
}

def _load_table(table_name):
    path = DATA_FILES[table_name]
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_table(table_name, data):
    path = DATA_FILES[table_name]
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def _get_next_id(table_name):
    data = _load_table(table_name)
    if not data:
        return 1
    return max(item.get('id', 0) for item in data) + 1

def add_ingredient(name, research_ids, nutrition_info, production_time):
    data = _load_table('ingredient')
    new_id = _get_next_id('ingredient')
    new_item = {
        "id": new_id,
        "name": name,
        "research_ids": research_ids,
        "nutrition_info": nutrition_info,
        "production_time": production_time
    }
    data.append(new_item)
    _save_table('ingredient', data)
    print(f"New ingredient '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id

def add_storaged_ingredient(storage_id, mass_g, expiration_date, production_end_date, processing_type):
    data = _load_table('storaged-ingredient')
    new_id = _get_next_id('storaged-ingredient')
    new_item = {
        "id": new_id,
        "storage-id": storage_id,
        "mass_g": mass_g,
        "start_date": production_end_date,
        "expiration_date": expiration_date,
        "production_end_date": production_end_date,
        "processing_type": processing_type
    }
    data.append(new_item)
    _save_table('storaged-ingredient', data)
    print(f"New storaged ingredient batch added with ID {new_id}.")
    return new_id

def add_cooking_method(name, description, research_ids):
    data = _load_table('cooking-methods')
    new_id = _get_next_id('cooking-methods')
    new_item = {
        "id": new_id,
        "name": name,
        "description": description,
        "research_ids": research_ids
    }
    data.append(new_item)
    _save_table('cooking-methods', data)
    print(f"New cooking method '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id

def add_research_data(reference_data, summary):
    data = _load_table('research-data')
    new_id = _get_next_id('research-data')
    new_item = {
        "id": new_id,
        "reference_data": reference_data,
        "summary": summary
    }
    data.append(new_item)
    _save_table('research-data', data)
    print(f"New research data added with ID {new_id}.")
    return new_id

def get_nutrition_categories():
    with open('nutrition_category.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def add_dish(dish_type, name, image_url, required_ingredient_ids, required_cooking_method_ids, nutrition_info, cooking_instructions=None):
    data = _load_table('dish')
    new_id = _get_next_id('dish')
    new_item = {
        "id": new_id,
        "name": name,
        "required_ingredient_ids": required_ingredient_ids,
        "cooking_instructions": cooking_instructions,
        "nutrition_info": nutrition_info,
        "cooking-method-ids": required_cooking_method_ids
    }
    data.append(new_item)
    _save_table('dish', data)
    print(f"New dish '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id
