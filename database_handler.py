import json
from datetime import datetime

DB_FILE = 'main_db.json'

def load_db():
    """데이터베이스 파일을 읽어옵니다."""
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "ingredient": [],
            "storaged-ingredient": [],
            "cooking-methods": [],
            "research-data": [],
            "dish": []
        }

def save_db(db):
    """데이터베이스를 파일에 저장합니다."""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def _get_next_id(db, table_name):
    """테이블에서 다음 ID를 가져옵니다."""
    if not db.get(table_name):
        return 1
    return max(item.get('id', 0) for item in db[table_name]) + 1

def add_ingredient(name, research_ids, nutrition_info, production_time):
    db = load_db()
    new_id = _get_next_id(db, 'ingredient')
    new_item = {
        "id": new_id,
        "name": name,
        "research_ids": research_ids,
        "nutrition_info": nutrition_info,
        "production_time": production_time
    }
    db['ingredient'].append(new_item)
    save_db(db)
    print(f"New ingredient '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id

def add_storaged_ingredient(storage_id, mass_g, expiration_date, production_end_date):
    db = load_db()
    new_id = _get_next_id(db, 'storaged-ingredient')
    new_item = {
        "id": new_id,
        "storage-id": storage_id,
        "mass_g": mass_g,
        "expiration_date": expiration_date,
        "production_end_date": production_end_date
    }
    db['storaged-ingredient'].append(new_item)
    save_db(db)
    print(f"New storaged ingredient batch added with ID {new_id}.")
    return new_id

def add_cooking_method(name, description, research_ids):
    db = load_db()
    new_id = _get_next_id(db, 'cooking-methods')
    new_item = {
        "id": new_id,
        "name": name,
        "description": description,
        "research_ids": research_ids
    }
    db['cooking-methods'].append(new_item)
    save_db(db)
    print(f"New cooking method '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id

def add_research_data(reference_data, summary):
    db = load_db()
    new_id = _get_next_id(db, 'research-data')
    new_item = {
        "id": new_id,
        "reference_data": reference_data,
        "summary": summary
    }
    db['research-data'].append(new_item)
    save_db(db)
    print(f"New research data added with ID {new_id}.")
    return new_id

def add_dish(dish_type, name, image_url, required_ingredient_ids, required_cooking_method_ids, nutrition_info, cooking_instructions=None):
    db = load_db()
    new_id = _get_next_id(db, 'dish')
    new_item = {
        "id": new_id,
        "type": dish_type,
        "name": name,
        "image_url": image_url,
        "required_ingredient_ids": required_ingredient_ids,
        "required_cooking_method_ids": required_cooking_method_ids,
        "nutrition_info": nutrition_info,
        "cooking_instructions": cooking_instructions
    }
    db['dish'].append(new_item)
    save_db(db)
    print(f"New dish '{name.get('kor', 'N/A')}' added with ID {new_id}.")
    return new_id
