import json
import os
from datetime import datetime

USER_DB_PATH = os.path.join(os.path.dirname(__file__), 'user_db.json')

def load_users():
    """Loads the list of users from the JSON file."""
    if not os.path.exists(USER_DB_PATH):
        return []
    with open(USER_DB_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    """Saves the list of users to the JSON file."""
    with open(USER_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def get_user_by_id(user_id):
    """Finds a user by their ID."""
    users = load_users()
    for user in users:
        if user.get('id') == user_id:
            return user
    return None

def get_user_by_username(username):
    """Finds a user by their username."""
    users = load_users()
    for user in users:
        if user.get('username') == username:
            return user
    return None

def update_user(user_id, update_fields):
    """Updates a user's information by their ID."""
    users = load_users()
    user_found = False
    for i, user in enumerate(users):
        if user.get('id') == user_id:
            users[i].update(update_fields)
            user_found = True
            break
    if user_found:
        save_users(users)
    return user_found

def add_food_to_timeline(user_id, food_intake_data):
    """Adds a food intake record to a user's timeline for the current day."""
    users = load_users()
    user_found = False
    today_str = datetime.now().strftime('%Y-%m-%d')

    for user in users:
        if user.get('id') == user_id:
            user_found = True
            if 'food_timeline' not in user:
                user['food_timeline'] = []

            # Find today's entry
            todays_entry = None
            for entry in user['food_timeline']:
                if entry.get('date') == today_str:
                    todays_entry = entry
                    break
            
            # Add current time to intake data
            food_intake_data['time'] = datetime.now().strftime('%H:%M')

            if todays_entry:
                # Add to existing entry for today
                todays_entry['intake'].append(food_intake_data)
            else:
                # Create a new entry for today
                user['food_timeline'].append({
                    "date": today_str,
                    "intake": [food_intake_data]
                })
            break

    if user_found:
        save_users(users)
    return user_found

def get_all_users():
    """Returns the full list of users."""
    return load_users()

# Note: Functions like add_user, delete_user, authenticate_user would also need refactoring
# to work with the list structure, but are omitted here to focus on the core request.
