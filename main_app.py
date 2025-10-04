from flask import Flask, render_template, request, redirect, url_for, session, flash
from database_manager import load_database, add_research_data, add_foods_first, add_cooking_method, add_foods_second
from user_manager import load_users, add_user, update_user_profile
import json
from functools import wraps

app = Flask(__name__)
# 세션을 사용하기 위해 시크릿 키를 설정해야 합니다.
app.secret_key = 'supersecretkey' # 실제 프로덕션 환경에서는 더 복잡하고 안전한 키를 사용하세요.

# 로그인 여부를 확인하는 데코레이터
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    """로그인 상태에 따라 대시보드 또는 로그인 페이지로 리디렉션합니다."""
    if 'logged_in' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 처리"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        # 실제 프로덕션에서는 비밀번호 해시를 비교해야 합니다.
        # 예: from werkzeug.security import check_password_hash
        if username in users and users[username]['password'] == password:
            session['logged_in'] = True
            session['username'] = username
            flash('로그인 성공!', 'success')
            return redirect(url_for('index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
    return render_template('login.html')

@app.route('/index')
@login_required
def index():
    """메인 대시보드 - 데이터베이스의 모든 내용을 표시합니다."""
    db = load_database()
    return render_template('index.html', db=db, username=session.get('username'))

@app.route('/add/research', methods=['POST'])
@login_required
def handle_add_research():
    """새 연구 데이터 추가를 처리합니다."""
    data = request.form.get('data')
    summary_kor = request.form.get('summary_kor')
    summary_eng = request.form.get('summary_eng')
    summary = {"kor": summary_kor, "eng": summary_eng}
    add_research_data(data, summary)
    return redirect(url_for('index'))

@app.route('/add/foods-first', methods=['POST'])
@login_required
def handle_add_foods_first():
    """새 1차 가공 음식 추가를 처리합니다."""
    name_kor = request.form.get('name_kor')
    name_eng = request.form.get('name_eng')
    name = {"kor": name_kor, "eng": name_eng}
    research_ids = [int(id) for id in request.form.getlist('research_ids')]
    
    try:
        nutrients = json.loads(request.form.get('nutrients_per_unit_mass', '{}'))
    except (json.JSONDecodeError, TypeError):
        nutrients = {}
        
    calories = float(request.form.get('calories', 0.0))
    
    nutrition_info = {
        "nutrients_per_unit_mass": nutrients,
        "calories": calories
    }
    
    add_foods_first(name, research_ids, nutrition_info)
    return redirect(url_for('index'))

@app.route('/add/cooking-method', methods=['POST'])
@login_required
def handle_add_cooking_method():
    """새 조리 방법 추가를 처리합니다."""
    name_kor = request.form.get('name_kor')
    name_eng = request.form.get('name_eng')
    name = {"kor": name_kor, "eng": name_eng}
    
    description_kor = request.form.get('description_kor')
    description_eng = request.form.get('description_eng')
    description = {"kor": description_kor, "eng": description_eng}
    
    research_ids = [int(id) for id in request.form.getlist('research_ids')]
    
    add_cooking_method(name, description, research_ids)
    return redirect(url_for('index'))

@app.route('/add/foods-second', methods=['POST'])
@login_required
def handle_add_foods_second():
    """새 2차 가공 음식 추가를 처리합니다."""
    name_kor = request.form.get('name_kor')
    name_eng = request.form.get('name_eng')
    name = {"kor": name_kor, "eng": name_eng}
    
    required_ingredient_ids = [int(id) for id in request.form.getlist('required_ingredient_ids')]
    required_cooking_method_ids = [int(id) for id in request.form.getlist('required_cooking_method_ids')]
    image_url = request.form.get('image_url')
    
    add_foods_second(name, required_ingredient_ids, required_cooking_method_ids, image_url)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 처리"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if add_user(username, password):
            # 회원가입 성공 후 추가 정보 입력을 위해 사용자 이름을 세션에 저장
            session['new_user_username'] = username
            flash('회원가입이 거의 완료되었습니다! 추가 정보를 입력해주세요.', 'info')
            return redirect(url_for('complete_profile'))
        else:
            flash('이미 존재하는 아이디입니다.', 'danger')
    return render_template('register.html')

@app.route('/complete-profile', methods=['GET', 'POST'])
def complete_profile():
    """회원가입 후 추가 정보 입력 처리"""
    if 'new_user_username' not in session:
        # 비정상적인 접근 방지
        return redirect(url_for('register'))

    if request.method == 'POST':
        username = session['new_user_username']
        profile_data = {
            "height": request.form.get('height'),
            "weight": request.form.get('weight'),
            "gender": request.form.get('gender'),
            "preferred_food": request.form.get('preferred_food')
        }
        update_user_profile(username, profile_data)
        session.pop('new_user_username', None) # 임시 세션 정보 삭제
        flash('프로필 정보가 저장되었습니다. 이제 로그인해주세요.', 'success')
        return redirect(url_for('login'))
    
    return render_template('complete_profile.html')

@app.route('/logout')
def logout():
    """로그아웃 처리"""
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(port=5001, debug=True)