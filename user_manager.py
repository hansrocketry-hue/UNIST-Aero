import json
from werkzeug.security import generate_password_hash, check_password_hash

DB_FILE = 'user_db.json'

def load_users():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] # 이제 리스트를 반환

def save_users(users):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def get_user_by_username(username):
    users = load_users()
    for user in users:
        if user.get('username') == username:
            return user
    return None

def _get_next_id(users):
    if not users:
        return 1
    return max(user.get('id', 0) for user in users) + 1

def add_user(username, password, name, height, weight, gender, like_ids, forbid_ids, activity_level, language='kor'):
    users = load_users()
    if get_user_by_username(username):
        return False  # 이미 존재하는 사용자

    new_user = {
        "id": _get_next_id(users),
        "username": username,
        "password_hash": generate_password_hash(password),
        "name": name,
        "height": height,
        "weight": weight,
        "gender": gender,
        "activity_level": activity_level,
        "language": language,
        "like": like_ids,
        "forbid": forbid_ids
    }
    users.append(new_user)
    save_users(users)
    return True

def verify_user(username, password):
    user = get_user_by_username(username)
    if user and 'password_hash' in user and check_password_hash(user['password_hash'], password):
        return True
    return False
