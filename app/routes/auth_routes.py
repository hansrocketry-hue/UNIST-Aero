from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
import user_manager as um
import database_handler as db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    """로그인된 사용자인지 확인하는 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            name = request.form['name']
            height = int(request.form['height'])
            weight = int(request.form['weight'])
            gender = request.form['gender']
            activity_level = int(request.form['activity_level'])
            like_ids = [int(x) for x in request.form.getlist('like_ids')]
            forbid_ids = [int(x) for x in request.form.getlist('forbid_ids')]

            if um.add_user(username, password, name, height, weight, gender, like_ids, forbid_ids, activity_level):
                flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('이미 존재하는 사용자 이름입니다.', 'danger')
        except Exception as e:
            flash(f"입력 중 오류가 발생했습니다: {e}", 'danger')
    
    all_ingredients = db.load_db().get('ingredient', [])
    return render_template('signup.html', all_ingredients=all_ingredients)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if um.verify_user(username, password):
            user = um.get_user_by_username(username)
            if user:
                session['user_id'] = user['id']
                session['user'] = {'username': user['username'], 'id': user['id']}
                return redirect(url_for('home.index'))
            else:
                flash('사용자 정보를 가져오는 데 실패했습니다.', 'danger')
        else:
            flash('사용자 이름 또는 비밀번호가 올바르지 않습니다.', 'danger')
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    flash('로그아웃되었습니다.', 'success')
    return redirect(url_for('auth.login'))