import json
import os

DB_FILE = 'main_db.json'

def load_database():
    """데이터베이스 파일을 읽어오거나, 파일이 없으면 초기 구조를 생성합니다."""
    if not os.path.exists(DB_FILE):
        return {
            "research_data": [],
            "foods-first": [],
            "cooking_methods": [],
            "foods-second": []
        }
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_database(data):
    """데이터베이스를 JSON 파일에 저장합니다."""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def get_next_id(table_name):
    """테이블에서 사용할 다음 ID를 계산합니다."""
    db = load_database()
    table = db.get(table_name, [])
    if not table:
        return 1
    
    max_id = 0
    for item in table:
        if 'id' in item and item['id'] > max_id:
            max_id = item['id']
            
    return max_id + 1

def add_research_data(data, summary):
    """새로운 연구 데이터를 추가합니다."""
    db = load_database()
    
    research_id = get_next_id("research_data")
    new_research = {
        "id": research_id,
        "data": data,
        "summary": summary
    }
    db["research_data"].append(new_research)
    save_database(db)
    print(f"연구 데이터 추가 완료 (ID: {research_id})")
    return research_id

def add_foods_first(name, research_ids, nutrition_info):
    """새로운 1차 가공 음식을 추가합니다."""
    db = load_database()
    
    food_id = get_next_id("foods-first")
    new_food = {
        "id": food_id,
        "name": name,
        "research_ids": research_ids,
        "nutrition_info": nutrition_info
    }
    db["foods-first"].append(new_food)
    save_database(db)
    print(f"1차 가공 음식 추가 완료 (ID: {food_id})")
    return food_id

def add_cooking_method(name, description, research_ids):
    """새로운 조리 방법을 추가합니다."""
    db = load_database()
    
    method_id = get_next_id("cooking_methods")
    new_method = {
        "id": method_id,
        "name": name,
        "description": description,
        "research_ids": research_ids
    }
    db["cooking_methods"].append(new_method)
    save_database(db)
    print(f"조리 방법 추가 완료 (ID: {method_id})")
    return method_id

def add_foods_second(name, required_ingredient_ids, required_cooking_method_ids, image_url=None):
    """새로운 2차 가공 음식을 추가합니다."""
    db = load_database()
    
    food_id = get_next_id("foods-second")
    new_food = {
        "id": food_id,
        "name": name,
        "required_ingredient_ids": required_ingredient_ids,
        "required_cooking_method_ids": required_cooking_method_ids,
        "image_url": image_url
    }
    db["foods-second"].append(new_food)
    save_database(db)
    print(f"2차 가공 음식 추가 완료 (ID: {food_id})")
    return food_id

if __name__ == '__main__':
    # --- 데이터베이스 초기화 ---
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("기존 데이터베이스 파일을 삭제했습니다.")

    # --- 예시 데이터 추가 ---
    
    # 1. 연구 데이터 추가
    research_id_hydration = add_research_data(
        data="NASA-STD-3001: Space Flight Human-System Standard",
        summary={
            "kor": "저중력 환경에서 물 주입을 통한 건조 식품 복원 기술은 안정적임.",
            "eng": "Technology for restoring dried food through water injection in a low-gravity environment is stable."
        }
    )
    
    research_id_bibimbap = add_research_data(
        data="J. Food Sci. 2023, 88, 123-130: Nutritional and Sensory Properties of Freeze-Dried Bibimbap for Long-Term Space Missions",
        summary={
            "kor": "동결 건조 비빔밥은 장기 보관 시 영양 손실이 적고, 수화 시 맛과 질감이 잘 복원됨.",
            "eng": "Freeze-dried bibimbap shows less nutritional loss during long-term storage and restores its taste and texture well upon hydration."
        }
    )

    # 2. 1차 가공 음식 추가
    food_first_id = add_foods_first(
        name= {
            "kor": "동결 건조 비빔밥",
            "eng": "Freeze-Dried Bibimbap"
        },
        research_ids=[research_id_bibimbap],
        nutrition_info= {
            "nutrients_per_unit_mass": {"protein": 15, "carbohydrates": 60, "fat": 10},
            "calories": 350
        }
    )

    # 3. 조리 방법 추가
    method_id_hydration = add_cooking_method(
        name={"kor": "수화", "eng": "Hydration"},
        description= {
            "kor": "동결 건조된 식품에 정수된 물을 주입하여 원상태로 복원.",
            "eng": "Restores freeze-dried food to its original state by injecting purified water."
        },
        research_ids=[research_id_hydration]
    )

    # 4. 2차 가공 음식 추가
    add_foods_second(
        name= {
            "kor": "우주 비빔밥",
            "eng": "Space Bibimbap"
        },
        required_ingredient_ids=[food_first_id],
        required_cooking_method_ids=[method_id_hydration],
        image_url="http://example.com/images/space_bibimbap.jpg"
    )

    print("\n--- 데이터베이스 최종 상태 ---")
    final_db = load_database()
    print(json.dumps(final_db, indent=2, ensure_ascii=False))