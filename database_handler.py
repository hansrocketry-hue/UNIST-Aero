
import json
import os
from datetime import datetime

DATA_FILES = {
    'ingredient': 'ingredient.json',
    'storaged-ingredient': 'storaged-ingredient.json',
    'cooking-methods': 'cooking-methods.json',
    'research-data': 'research-data.json',
    'dish': 'dish.json',
    'nutrition': 'nutrition.json'  # legacy; prefer embedding nutrition into ingredient.json
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
        return "N1" if table_name == 'nutrition' else 1
    if table_name == 'nutrition':
        # For nutrition, use N1, N2, etc.
        return f"N{max(int(item['id'][1:]) for item in data) + 1}"
    return max(item.get('id', 0) for item in data) + 1

def add_ingredient(name, research_ids, nutrition_data, production_time):
    """Add ingredient and embed nutrition_data into the ingredient record.

    nutrition_data: list of nutrients e.g. [{"name":.., "amount_per_unit_mass": ..}, ...]
    """
    data = _load_table('ingredient')
    new_id = _get_next_id('ingredient')

    # Embed nutrition directly into ingredient record (new format)
    new_item = {
        "id": new_id,
        "name": name,
        "research_ids": research_ids,
        "nutrition": nutrition_data,
        "production_time": production_time
    }
    data.append(new_item)
    _save_table('ingredient', data)

    # For backwards compatibility, we do not create nutrition.json entries anymore.
    print(f"New ingredient '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id

def add_nutrition(nutrition_data):
    """Legacy helper kept for compatibility: writes to nutrition.json (deprecated).

    Prefer embedding nutrition in ingredient.json; this function will still write to
    nutrition.json if present, otherwise it's a no-op returning None.
    """
    try:
        data = _load_table('nutrition')
    except Exception:
        return None
    new_id = _get_next_id('nutrition')
    new_item = {
        "id": new_id,
        "ingredient_id": None,
        "nutrients": nutrition_data.get("nutrients", [])
    }
    data.append(new_item)
    _save_table('nutrition', data)
    return new_id

def get_ingredient_nutrition(ingredient_id):
    """Return the nutrition list for an ingredient.

    New format: nutrition embedded in ingredient['nutrition'] as a list of nutrients.
    Legacy fallback: read nutrition.json and match by ingredient['nutrition_id'].
    """
    ingredient_data = _load_table('ingredient')
    ingredient = next((item for item in ingredient_data if item.get('id') == ingredient_id), None)
    if not ingredient:
        return None

    # New format: look for embedded nutrition
    if 'nutrition' in ingredient:
        return ingredient['nutrition']

    # Legacy format: try nutrition.json via nutrition_id
    nut_id = ingredient.get('nutrition_id')
    if not nut_id:
        return None
    nutrition_data = _load_table('nutrition')
    nutrition = next((item for item in nutrition_data if item.get('id') == nut_id), None)
    return nutrition.get('nutrients') if nutrition else None

def update_ingredient_nutrition_reference(ingredient_id, nutrition_id):
    """Legacy helper: updates cross-reference in nutrition.json and ingredient.json.

    With the new embedded format this is typically unnecessary; keep it for backwards
    compatibility but do nothing if nutrition.json is absent.
    """
    nutrition_path = DATA_FILES.get('nutrition')
    if not nutrition_path or not os.path.exists(nutrition_path):
        return
    nutrition_data = _load_table('nutrition')
    ingredient_data = _load_table('ingredient')

    for item in nutrition_data:
        if item.get('id') == nutrition_id:
            item['ingredient_id'] = ingredient_id
            break

    for item in ingredient_data:
        if item.get('id') == ingredient_id:
            item['nutrition_id'] = nutrition_id
            break

    _save_table('nutrition', nutrition_data)
    _save_table('ingredient', ingredient_data)

def add_storaged_ingredient(storage_id, mass_g, start_date, mode, processing_type=None, end_date=None, 
                          expiration_date=None, min_end_date=None, max_end_date=None):
    data = _load_table('storaged-ingredient')
    ingredients = _load_table('ingredient')
    
    # Find the ingredient
    ingredient = next((item for item in ingredients if item['id'] == storage_id), None)
    if not ingredient:
        raise ValueError(f"Ingredient with ID {storage_id} not found.")
    
    # For production mode, check if the ingredient is producible
    if mode == "production":
        if not ingredient.get('production_time', {}).get('producible', False):
            raise ValueError(f"Ingredient {ingredient['name'].get('kor', 'N/A')} cannot be produced.")
        if not min_end_date or not max_end_date:
            raise ValueError("Production mode requires both min_end_date and max_end_date")
    else:
        if not end_date or not expiration_date:
            raise ValueError("Storage mode requires both end_date and expiration_date")
    
    new_id = _get_next_id('storaged-ingredient')
    new_item = {
        "id": new_id,
        "storage-id": storage_id,
        "mass_g": mass_g,
        "mode": mode,
        "start_date": start_date,
        "processing_type": processing_type
    }
    
    # Add mode-specific fields
    if mode == "production":
        new_item["min_end_date"] = min_end_date
        new_item["max_end_date"] = max_end_date
    else:
        new_item["end_date"] = end_date
        new_item["expiration_date"] = expiration_date
    data.append(new_item)
    _save_table('storaged-ingredient', data)
    print(f"New {mode} ingredient batch added with ID {new_id}.")
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

def add_dish(name, image_url, required_ingredient_ids, required_cooking_method_ids, nutrition_data=None, cooking_instructions=None):
    """Add a dish.

    Parameters:
    - name: dict of language codes to names
    - image_url: optional string
    - required_ingredient_ids: list of ingredient ids
    - required_cooking_method_ids: list of cooking method ids
    - nutrition_data: list of nutrient dicts (each with 'name' and 'amount_per_dish')
    - cooking_instructions: optional dict of language codes to instructions
    """
    data = _load_table('dish')
    new_id = _get_next_id('dish')

    # If nutrition_data was provided by the caller and is non-empty, use it.
    # Otherwise, compute totals based on ingredient nutrition.
    final_nutrition = []
    if nutrition_data:
        final_nutrition = nutrition_data
    else:
        total_nutrition = {"nutrients": []}
        for ingredient_id in required_ingredient_ids:
            ingredient_nutrition = get_ingredient_nutrition(ingredient_id)
            if ingredient_nutrition:
                if not total_nutrition["nutrients"]:
                    # copy to avoid mutating original
                    total_nutrition["nutrients"] = [dict(n) for n in ingredient_nutrition]
                else:
                    # try to sum by matching nutrient names; fall back to positional
                    for nutr in ingredient_nutrition:
                        matched = next((x for x in total_nutrition["nutrients"] if x.get('name') == nutr.get('name')), None)
                        if matched:
                            # handle both amount_per_unit_mass and amount_per_dish keys
                            if 'amount_per_unit_mass' in nutr:
                                key = 'amount_per_unit_mass'
                            else:
                                key = 'amount_per_dish'
                            matched[key] = matched.get(key, 0) + nutr.get(key, 0)
                        else:
                            total_nutrition["nutrients"].append(dict(nutr))
        final_nutrition = total_nutrition["nutrients"]

    new_item = {
        "id": new_id,
        "name": name,
        "image_url": image_url,
        "required_ingredient_ids": required_ingredient_ids,
        "cooking_instructions": cooking_instructions,
        "nutrition_info": final_nutrition,
        "cooking-method-ids": required_cooking_method_ids
    }
    data.append(new_item)
    _save_table('dish', data)
    print(f"New dish '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id
