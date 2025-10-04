import json
import os

USER_DB_FILE = 'user-info.json'

def load_users():
    """사용자 정보 파일을 읽어오거나, 파일이 없으면 초기 구조를 생성합니다."""
    if not os.path.exists(USER_DB_FILE):
        return {}
    with open(USER_DB_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    """사용자 정보를 JSON 파일에 저장합니다."""
    with open(USER_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

def add_user(username, password):
    """새로운 사용자를 추가합니다."""
    users = load_users()
    if username in users:
        return False  # 이미 존재하는 사용자
    
    # 실제 프로덕션 환경에서는 비밀번호를 해싱하여 저장해야 합니다.
    # 예: from werkzeug.security import generate_password_hash
    # users[username] = {"password": generate_password_hash(password)}
    users[username] = {"password": password}
    save_users(users)
    return True

def update_user_profile(username, profile_data):
    """사용자의 프로필 정보를 업데이트합니다."""
    users = load_users()
    if username in users:
        # 'profile' 키가 없으면 새로 생성하고, 있으면 기존 값에 업데이트
        users[username].setdefault('profile', {}).update(profile_data)
        save_users(users)
        return True
    return False # 사용자가 존재하지 않음