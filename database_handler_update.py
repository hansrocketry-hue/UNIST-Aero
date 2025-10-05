def update_research_data(research_id, reference_data, summary):
    """연구 자료 수정"""
    data = _load_table('research-data')
    for item in data:
        if item['id'] == research_id:
            item.update({
                'reference_data': reference_data,
                'summary': summary
            })
            break
    _save_table('research-data', data)
    print(f"Research data with ID {research_id} updated.")
    return research_id

def update_ingredient(ingredient_id, name, research_ids, nutrition_data, production_time):
    """식재료 정보 수정"""
    data = _load_table('ingredient')
    for item in data:
        if item['id'] == ingredient_id:
            item.update({
                'name': name,
                'research_ids': research_ids,
                'nutrition': nutrition_data,
                'production_time': production_time
            })
            break
    _save_table('ingredient', data)
    print(f"Ingredient with ID {ingredient_id} updated.")
    return ingredient_id

def update_cooking_method(method_id, name, description, research_ids):
    """조리 방법 수정"""
    data = _load_table('cooking-methods')
    for item in data:
        if item['id'] == method_id:
            item.update({
                'name': name,
                'description': description,
                'research_ids': research_ids
            })
            break
    _save_table('cooking-methods', data)
    print(f"Cooking method with ID {method_id} updated.")
    return method_id

def update_dish(dish_id, name, image_url, required_ingredients, required_cooking_method_ids, 
               nutrition_data=None, cooking_instructions=None):
    """요리(dish) 정보 수정"""
    data = _load_table('dish')
    
    # Compute nutrition if not provided
    if not nutrition_data:
        try:
            with open('nutrition_category.json', 'r', encoding='utf-8') as f:
                categories = [c.get('name') for c in json.load(f)]
        except Exception:
            categories = []

        nutrient_sums = {name: 0.0 for name in categories}

        for req in required_ingredients:
            iid = req.get('id')
            amt_g = req.get('amount_g', 0)
            ing_nut = get_ingredient_nutrition(iid) or []
            for nutr in ing_nut:
                name = nutr.get('name')
                per_g = nutr.get('amount_per_unit_mass') or nutr.get('amount_per_dish') or 0
                added = per_g * amt_g
                if name in nutrient_sums:
                    nutrient_sums[name] += added
                else:
                    nutrient_sums[name] = nutrient_sums.get(name, 0.0) + added

        nutrition_data = []
        seen = set()
        for cat in categories:
            val = nutrient_sums.get(cat, 0.0)
            out_name = cat if cat != 'Calories' else 'Calories (Total)'
            nutrition_data.append({"name": out_name, "amount_per_dish": val})
            seen.add(out_name)
        for k, v in nutrient_sums.items():
            if k not in seen and k != 'Calories':
                nutrition_data.append({"name": k, "amount_per_dish": v})

    # Update dish data
    for item in data:
        if item['id'] == dish_id:
            item.update({
                'name': name,
                'image_url': image_url,
                'required_ingredients': required_ingredients,
                'cooking_instructions': cooking_instructions,
                'nutrition_info': nutrition_data,
                'cooking-method-ids': required_cooking_method_ids
            })
            break
    
    _save_table('dish', data)
    print(f"Dish with ID {dish_id} updated.")
    return dish_id