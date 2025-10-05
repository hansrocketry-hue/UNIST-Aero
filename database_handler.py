
import json
import os
from datetime import datetime

DATA_FILES = {
    'ingredient': 'ingredient.json',
    'storaged-ingredient': 'storaged-ingredient.json',
    'cooking-methods': 'cooking-methods.json',
    'research-data': 'research-data.json',
    'dish': 'dish.json',
    'nutrition': 'nutrition.json'
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
    # First, add nutrition data
    nutrition_data = {
        "nutrients": nutrition_data
    }
    nutrition_id = add_nutrition(nutrition_data)
    
    # Then add ingredient with reference to nutrition
    data = _load_table('ingredient')
    new_id = _get_next_id('ingredient')
    new_item = {
        "id": new_id,
        "name": name,
        "research_ids": research_ids,
        "nutrition_id": nutrition_id,
        "production_time": production_time
    }
    data.append(new_item)
    _save_table('ingredient', data)
    
    # Update nutrition record with ingredient reference
    update_ingredient_nutrition_reference(new_id, nutrition_id)
    
    print(f"New ingredient '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id

def add_nutrition(nutrition_data):
    data = _load_table('nutrition')
    new_id = _get_next_id('nutrition')
    new_item = {
        "id": new_id,
        "ingredient_id": None,  # Will be updated when ingredient is created
        "nutrients": nutrition_data["nutrients"]
    }
    data.append(new_item)
    _save_table('nutrition', data)
    return new_id

def get_ingredient_nutrition(ingredient_id):
    ingredient_data = _load_table('ingredient')
    nutrition_data = _load_table('nutrition')
    
    # Find the ingredient
    ingredient = next((item for item in ingredient_data if item['id'] == ingredient_id), None)
    if not ingredient:
        return None
        
    # Find its nutrition data
    nutrition = next((item for item in nutrition_data if item['id'] == ingredient['nutrition_id']), None)
    return nutrition['nutrients'] if nutrition else None

def update_ingredient_nutrition_reference(ingredient_id, nutrition_id):
    """Update the ingredient's nutrition reference after creating both records"""
    nutrition_data = _load_table('nutrition')
    ingredient_data = _load_table('ingredient')
    
    # Update nutrition record with ingredient_id
    for item in nutrition_data:
        if item['id'] == nutrition_id:
            item['ingredient_id'] = ingredient_id
            break
    
    # Update ingredient record with nutrition_id
    for item in ingredient_data:
        if item['id'] == ingredient_id:
            item['nutrition_id'] = nutrition_id
            break
    
    _save_table('nutrition', nutrition_data)
    _save_table('ingredient', ingredient_data)

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

def add_dish(dish_type, name, image_url, required_ingredient_ids, required_cooking_method_ids, nutrition_data, cooking_instructions=None):
    data = _load_table('dish')
    new_id = _get_next_id('dish')
    
    # Calculate total nutrition info based on required ingredients
    total_nutrition = {"nutrients": []}
    for ingredient_id in required_ingredient_ids:
        ingredient_nutrition = get_ingredient_nutrition(ingredient_id)
        if ingredient_nutrition:
            # Assuming we need to sum up the nutritional values
            # This is a simplified version - you might want to add weight/portion calculations
            if not total_nutrition["nutrients"]:
                total_nutrition["nutrients"] = ingredient_nutrition
            else:
                for i, nutrient in enumerate(ingredient_nutrition):
                    total_nutrition["nutrients"][i]["amount_per_unit_mass"] += nutrient["amount_per_unit_mass"]
    
    new_item = {
        "id": new_id,
        "name": name,
        "required_ingredient_ids": required_ingredient_ids,
        "cooking_instructions": cooking_instructions,
        "nutrition_info": total_nutrition["nutrients"],
        "cooking-method-ids": required_cooking_method_ids
    }
    data.append(new_item)
    _save_table('dish', data)
    print(f"New dish '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id
