import json
from datetime import datetime

DB_FILE = 'food_db.json'

def load_db():
    """데이터베이스 파일을 읽어옵니다."""
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"ingredients": []}

def save_db(db):
    """데이터베이스를 파일에 저장합니다."""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def add_ingredient(name, mass_g, quantity, expiration_date, cultivation_period, main_db_food_id):
    """새로운 식재료를 데이터베이스에 추가합니다.

    Args:
        name (str): 식재료 이름
        mass_g (int): 보유 질량 (그램)
        quantity (int): 보유량 (-1 for uncountable)
        expiration_date (str): 보관 기한 (YYYY-MM-DD)
        cultivation_period (str): 재배 기간
        main_db_food_id (int): main_db.json의 foods-first ID
    """
    db = load_db()
    
    try:
        # 날짜 형식이 올바른지 확인
        datetime.strptime(expiration_date, '%Y-%m-%d')
    except ValueError:
        print("오류: 보관 기한은 'YYYY-MM-DD' 형식이어야 합니다.")
        return

    # 새 ID 생성
    if not db["ingredients"]:
        new_id = 1
    else:
        new_id = max(item.get('id', 0) for item in db["ingredients"]) + 1

    new_ingredient = {
        "id": new_id,
        "main_db_food_id": main_db_food_id,
        "name": name,
        "mass_g": mass_g,
        "quantity": quantity,
        "expiration_date": expiration_date,
        "cultivation_period": cultivation_period
    }
    
    db["ingredients"].append(new_ingredient)
    save_db(db)
    print(f"'{name}'(ID: {new_id})이(가) 데이터베이스에 추가되었습니다.")

if __name__ == '__main__':
    # 이 파일은 다른 파일에서 import하여 사용하는 것을 목적으로 하므로,
    # 직접 실행했을 때에는 데이터베이스 내용만 출력하도록 수정합니다.
    print("현재 데이터베이스 내용:")
    db = load_db()
    print(json.dumps(db, indent=4, ensure_ascii=False))
