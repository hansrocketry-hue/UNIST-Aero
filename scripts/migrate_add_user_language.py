import json
import os

DB = os.path.join(os.path.dirname(__file__), '..', 'user_db.json')
BACKUP = DB + '.bak'

if not os.path.exists(DB):
    print('user_db.json not found')
    exit(1)

with open(DB, 'r', encoding='utf-8') as f:
    users = json.load(f)

# backup
with open(BACKUP, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=4)

changed = 0
for u in users:
    if 'language' not in u:
        u['language'] = 'kor'
        changed += 1

with open(DB, 'w', encoding='utf-8') as f:
    json.dump(users, f, ensure_ascii=False, indent=4)

print(f'Migration complete. Updated {changed} users. Backup saved to {BACKUP}')
