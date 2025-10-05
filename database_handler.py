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
    prefix = ''
    if table_name == 'ingredient':
        prefix = 'i'
    elif table_name == 'dish':
        prefix = 'd'
    elif table_name == 'nutrition':
        prefix = 'N'
    else:
        if not data:
            return 1
        return max(item.get('id', 0) for item in data) + 1

    if not data:
        return f"{prefix}1"

    max_id = 0
    for item in data:
        item_id = item.get('id')
        if isinstance(item_id, str) and item_id.startswith(prefix):
            try:
                num_part = int(item_id[len(prefix):])
                if num_part > max_id:
                    max_id = num_part
            except (ValueError, TypeError):
                continue
    
    return f"{prefix}{max_id + 1}"

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

def update_research_data(research_id, reference_data, summary):
    """Update an existing research data entry.
    
    Args:
        research_id: The ID of the research data to update
        reference_data: Dictionary containing link and title
        summary: Dictionary containing kor and eng summaries
    """
    data = _load_table('research-data')
    for item in data:
        if item['id'] == research_id:
            # Preserve existing reference_data keys when the form omits them
            existing_ref = item.get('reference_data', {}) or {}
            merged_ref = existing_ref.copy()
            # Only overwrite keys that are provided (non-None)
            for k, v in (reference_data or {}).items():
                if v is not None:
                    merged_ref[k] = v

            # Preserve existing summary keys similarly
            existing_summary = item.get('summary', {}) or {}
            merged_summary = existing_summary.copy()
            for k, v in (summary or {}).items():
                if v is not None:
                    merged_summary[k] = v

            item['reference_data'] = merged_ref
            item['summary'] = merged_summary
            _save_table('research-data', data)
            print(f"Research data with ID {research_id} updated successfully.")
            return True
    print(f"Research data with ID {research_id} not found.")
    return False

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

def update_ingredient(ingredient_id, name, research_ids, nutrition_data, production_time):
    """Update an existing ingredient entry.

    Parameters:
    - ingredient_id: numeric id
    - name: dict of language codes to names
    - research_ids: list of research ids
    - nutrition_data: list of nutrient dicts (name, amount_per_unit_mass)
    - production_time: dict or other value to store in ingredient['production_time']
    """
    data = _load_table('ingredient')
    for item in data:
        if item.get('id') == ingredient_id:
            # Replace fields provided. Use provided values directly so caller controls structure.
            item['name'] = name
            item['research_ids'] = research_ids
            item['nutrition'] = nutrition_data
            item['production_time'] = production_time
            _save_table('ingredient', data)
            print(f"Ingredient with ID {ingredient_id} updated.")
            return True
    print(f"Ingredient with ID {ingredient_id} not found.")
    return False

def add_storaged_ingredient(storage_id, mass_g, start_date, mode, processing_type=None,
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
        if not expiration_date:
            raise ValueError("Storage mode requires expiration_date")
    
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

def update_cooking_method(method_id, name, description, research_ids):
    """Update an existing cooking method entry."""
    data = _load_table('cooking-methods')
    for item in data:
        if item.get('id') == method_id:
            item['name'] = name
            item['description'] = description
            item['research_ids'] = research_ids
            _save_table('cooking-methods', data)
            print(f"Cooking method with ID {method_id} updated.")
            return True
    print(f"Cooking method with ID {method_id} not found.")
    return False

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

def get_dish_total_mass(dish):
    """Calculate total mass of a dish from its required_ingredients.
    
    Args:
        dish: dish dict with 'required_ingredients' field
    
    Returns:
        float: total mass in grams
    """
    total_mass = 0.0
    for ing in dish.get('required_ingredients', []):
        total_mass += ing.get('amount_g', 0)
    return total_mass

def get_nutrition_categories():
    with open('nutrition_category.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def add_nutrition_category(name, unit):
    """새로운 영양 정보 카테고리를 추가합니다."""
    try:
        with open('nutrition_category.json', 'r+', encoding='utf-8') as f:
            categories = json.load(f)
            
            # Check for duplicates
            if any(c['name'].lower() == name.lower() for c in categories):
                return None  # Category already exists

            new_category = {'name': name, 'unit': unit}
            categories.append(new_category)
            
            f.seek(0)
            json.dump(categories, f, ensure_ascii=False, indent=4)
            f.truncate()
            
            return new_category
    except (FileNotFoundError, json.JSONDecodeError):
        # If file doesn't exist or is empty, create a new one
        new_category = {'name': name, 'unit': unit}
        with open('nutrition_category.json', 'w', encoding='utf-8') as f:
            json.dump([new_category], f, ensure_ascii=False, indent=4)
        return new_category
    except Exception as e:
        print(f"Error adding nutrition category: {e}")
        return None

def add_dish(name, image_url, required_ingredients, required_cooking_method_ids, nutrition_data=None, cooking_instructions=None):
    """Add a dish.

    Parameters:
    - name: dict of language codes to names
    - image_url: optional string
    - required_ingredients: list of dicts with 'type', 'id', and 'amount_g'
    - required_cooking_method_ids: list of cooking method ids
    - nutrition_data: list of nutrient dicts (each with 'name' and 'amount_per_unit_mass')
    - cooking_instructions: optional dict of language codes to instructions
    """
    data = _load_table('dish')
    new_id = _get_next_id('dish')

    # If nutrition_data was provided explicitly, use it.
    # Otherwise, compute totals based on required_ingredients which include amounts.
    final_nutrition = []
    if nutrition_data:
        final_nutrition = nutrition_data
    else:
        # Load nutrition categories to ensure we return a complete list (including zeros)
        try:
            with open('nutrition_category.json', 'r', encoding='utf-8') as f:
                categories = [c.get('name') for c in __import__('json').load(f)]
        except Exception:
            categories = []

        # Initialize sums for all categories
        nutrient_sums = {cat: 0.0 for cat in categories}
        total_mass_g = 0.0

        # Sum nutrients by name and calculate total mass
        for req in required_ingredients:
            item_id = req.get('id')
            item_type = req.get('type', 'ingredient') # Default to ingredient
            amount = req.get('amount_g', 0)
            total_mass_g += amount

            if item_type == 'ingredient':
                ing_nut = get_ingredient_nutrition(item_id) or []
                for nutr in ing_nut:
                    nutr_name = nutr.get('name')
                    per_g = nutr.get('amount_per_unit_mass', 0)
                    added = per_g * amount
                    if nutr_name in nutrient_sums:
                        nutrient_sums[nutr_name] += added
                    else:
                        nutrient_sums[nutr_name] = nutrient_sums.get(nutr_name, 0.0) + added
            elif item_type == 'dish':
                sub_dish = next((d for d in data if d['id'] == item_id), None)
                if sub_dish:
                    sub_dish_nut = sub_dish.get('nutrition_info', [])
                    for nutr in sub_dish_nut:
                        nutr_name = nutr.get('name')
                        # Sub-dish nutrition is now stored as amount_per_unit_mass
                        per_g = nutr.get('amount_per_unit_mass', 0)
                        added = per_g * amount
                        if nutr_name in nutrient_sums:
                            nutrient_sums[nutr_name] += added
                        else:
                            nutrient_sums[nutr_name] = nutrient_sums.get(nutr_name, 0.0) + added

        # Convert total sums to per-gram values
        final_nutrition = []
        seen = set()
        for cat in categories:
            total_val = nutrient_sums.get(cat, 0.0)
            per_g_val = total_val / total_mass_g if total_mass_g > 0 else 0.0
            out_name = cat if cat != 'Calories' else 'Calories (Total)'
            final_nutrition.append({"name": out_name, "amount_per_unit_mass": per_g_val})
            seen.add(out_name)
        for k, v in nutrient_sums.items():
            if k not in seen and k != 'Calories':
                per_g_val = v / total_mass_g if total_mass_g > 0 else 0.0
                final_nutrition.append({"name": k, "amount_per_unit_mass": per_g_val})

    new_item = {
        "id": new_id,
        "name": name,
        "image_url": image_url,
        "required_ingredients": required_ingredients,
        "cooking_instructions": cooking_instructions,
        "nutrition_info": final_nutrition,
        "cooking-method-ids": required_cooking_method_ids
    }
    data.append(new_item)
    _save_table('dish', data)
    # name may sometimes be a plain string (legacy callers); handle both dict and str
    try:
        display_name = name.get('kor') if isinstance(name, dict) else str(name)
    except Exception:
        display_name = str(name)
    print(f"New dish '{display_name or 'N/A'}' added with ID {new_id}.")
    return new_id

def update_dish(dish_id, name, image_url, required_ingredients, required_cooking_method_ids,
              nutrition_data=None, cooking_instructions=None):
    """Update an existing dish.

    Parameters:
    - dish_id: ID of the dish to update
    - name: dict of language codes to names
    - image_url: optional string
    - required_ingredients: list of dicts with 'type', 'id', and 'amount_g'
    - required_cooking_method_ids: list of cooking method ids
    - nutrition_data: list of nutrient dicts (each with 'name' and 'amount_per_unit_mass')
    - cooking_instructions: optional dict of language codes to instructions
    """
    data = _load_table('dish')
    dish = next((item for item in data if item['id'] == dish_id), None)
    if not dish:
        raise ValueError(f"Dish with ID {dish_id} not found")

    # If nutrition_data was provided explicitly, use it.
    # Otherwise, compute totals based on required_ingredients which include amounts.
    final_nutrition = []
    if nutrition_data:
        final_nutrition = nutrition_data
    else:
        # Load nutrition categories to ensure we return a complete list (including zeros)
        try:
            with open('nutrition_category.json', 'r', encoding='utf-8') as f:
                categories = [c.get('name') for c in __import__('json').load(f)]
        except Exception:
            categories = []

        # Initialize sums for all categories
        nutrient_sums = {cat: 0.0 for cat in categories}
        total_mass_g = 0.0

        # Sum nutrients by name and calculate total mass
        for req in required_ingredients:
            item_id = req.get('id')
            item_type = req.get('type', 'ingredient') # Default to ingredient
            amount = req.get('amount_g', 0)
            total_mass_g += amount

            if item_type == 'ingredient':
                ing_nut = get_ingredient_nutrition(item_id) or []
                for nutr in ing_nut:
                    nutr_name = nutr.get('name')
                    per_g = nutr.get('amount_per_unit_mass', 0)
                    added = per_g * amount
                    if nutr_name in nutrient_sums:
                        nutrient_sums[nutr_name] += added
                    else:
                        nutrient_sums[nutr_name] = nutrient_sums.get(nutr_name, 0.0) + added
            elif item_type == 'dish':
                sub_dish = next((d for d in data if d['id'] == item_id), None)
                if sub_dish:
                    sub_dish_nut = sub_dish.get('nutrition_info', [])
                    for nutr in sub_dish_nut:
                        nutr_name = nutr.get('name')
                        # Sub-dish nutrition is now stored as amount_per_unit_mass
                        per_g = nutr.get('amount_per_unit_mass', 0)
                        added = per_g * amount
                        if nutr_name in nutrient_sums:
                            nutrient_sums[nutr_name] += added
                        else:
                            nutrient_sums[nutr_name] = nutrient_sums.get(nutr_name, 0.0) + added

        # Convert total sums to per-gram values
        final_nutrition = []
        seen = set()
        for cat in categories:
            total_val = nutrient_sums.get(cat, 0.0)
            per_g_val = total_val / total_mass_g if total_mass_g > 0 else 0.0
            out_name = cat if cat != 'Calories' else 'Calories (Total)'
            final_nutrition.append({"name": out_name, "amount_per_unit_mass": per_g_val})
            seen.add(out_name)
        for k, v in nutrient_sums.items():
            if k not in seen and k != 'Calories':
                per_g_val = v / total_mass_g if total_mass_g > 0 else 0.0
                final_nutrition.append({"name": k, "amount_per_unit_mass": per_g_val})

    # Update the dish
    dish.update({
        "name": name,
        "image_url": image_url,
        "required_ingredients": required_ingredients,
        "cooking_instructions": cooking_instructions,
        "nutrition_info": final_nutrition,
        "cooking-method-ids": required_cooking_method_ids
    })

    _save_table('dish', data)
    dish_name = name.get('kor', 'N/A') if isinstance(name, dict) else str(name)
    print(f"Dish '{dish_name}' (ID: {dish_id}) updated.")

def recalculate_dish_nutrition(dish, all_ingredients, all_dishes):
    """Recalculates the nutrition for a single dish based on its ingredients."""
    nutrient_sums = {}
    total_mass_g = 0.0

    for req in dish.get('required_ingredients', []):
        item_id = req.get('id')
        item_type = req.get('type', 'ingredient')
        amount = req.get('amount_g', 0)
        total_mass_g += amount

        if item_type == 'ingredient':
            ingredient = next((ing for ing in all_ingredients if ing['id'] == item_id), None)
            if ingredient:
                for nutr in ingredient.get('nutrition', []):
                    nutr_name = nutr.get('name')
                    per_g = nutr.get('amount_per_unit_mass', 0)
                    nutrient_sums[nutr_name] = nutrient_sums.get(nutr_name, 0.0) + (per_g * amount)
        elif item_type == 'dish':
            sub_dish = next((d for d in all_dishes if d['id'] == item_id), None)
            if sub_dish:
                for nutr in sub_dish.get('nutrition_info', []):
                    nutr_name = nutr.get('name')
                    per_g = nutr.get('amount_per_unit_mass', 0)
                    nutrient_sums[nutr_name] = nutrient_sums.get(nutr_name, 0.0) + (per_g * amount)

    final_nutrition = []
    for name, total_val in nutrient_sums.items():
        per_g_val = total_val / total_mass_g if total_mass_g > 0 else 0.0
        output_name = 'Calories (Total)' if name == 'Calories' else name
        final_nutrition.append({"name": output_name, "amount_per_unit_mass": per_g_val})

    dish['nutrition_info'] = final_nutrition
    return dish
