def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return True
    return False
import json
import os

USER_DB_PATH = os.path.join(os.path.dirname(__file__), 'user_db.json')

def load_users():
    if not os.path.exists(USER_DB_PATH):
        return {}
    with open(USER_DB_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    with open(USER_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def add_user(username, user_info):
    users = load_users()
    if username in users:
        return False
    users[username] = user_info
    save_users(users)
    return True

def authenticate_user(username, password):
    users = load_users()
    user = users.get(username)
    return user is not None and user.get('password') == password

def update_user(username, update_fields):
    users = load_users()
    if username not in users:
        return False
    users[username].update(update_fields)
    save_users(users)
    return True

def update_like_list(username, new_like_list):
    users = load_users()
    if username not in users:
        return False
    users[username]['like'] = new_like_list
    save_users(users)
    return True

def update_forbid_list(username, new_forbid_list):
    users = load_users()
    if username not in users:
        return False
    users[username]['forbid'] = new_forbid_list
    save_users(users)
    return True

def update_name(username, new_name):
    users = load_users()
    if username not in users:
        return False
    users[username]['name'] = new_name
    save_users(users)
    return True

def get_user(username):
    users = load_users()
    return users.get(username)

def get_all_users():
    return load_users()
