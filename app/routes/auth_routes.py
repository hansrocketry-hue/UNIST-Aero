
from flask import Blueprint, render_template, request, redirect, url_for, flash
from user_db_handler import add_user, authenticate_user, update_user, update_like_list, update_forbid_list, delete_user

auth_bp = Blueprint('auth', __name__)

# forbid 리스트 수정 라우트
@auth_bp.route('/update_forbid', methods=['GET', 'POST'])
def update_forbid():
    if request.method == 'POST':
        username = request.form['username']
        try:
            new_forbid = request.form.getlist('forbid')
            new_forbid = [int(x) for x in new_forbid]
        except Exception:
            flash('forbid 리스트 형식이 올바르지 않습니다.')
            return render_template('update_forbid.html')
        if update_forbid_list(username, new_forbid):
            flash('forbid 리스트가 성공적으로 변경되었습니다.')
        else:
            flash('존재하지 않는 아이디입니다.')
    return render_template('update_forbid.html')

# 회원 탈퇴 라우트
@auth_bp.route('/delete_account', methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            if delete_user(username):
                flash('회원 탈퇴가 완료되었습니다.')
                return redirect(url_for('auth.login'))
            else:
                flash('탈퇴 처리 중 오류가 발생했습니다.')
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.')
    return render_template('delete_account.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if authenticate_user(username, password):
            return redirect(url_for('home.index'))
        else:
            flash('로그인 실패: 아이디 또는 비밀번호가 올바르지 않습니다.')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        age = request.form.get('age')
        activity_level = request.form.get('activity_level')
        try:
            age = int(age)
            activity_level = int(activity_level)
            if activity_level < 1 or activity_level > 5:
                raise ValueError
        except (TypeError, ValueError):
            flash('나이와 활동지수는 숫자로, 활동지수는 1~5로 입력해주세요.')
            return render_template('register.html')
        user_info = {
            'name': username,
            'password': password,
            'age': age,
            'activity_level': activity_level,
            'like': [],
            'forbid': []
        }
        if add_user(username, user_info):
            flash('회원가입 성공! 로그인 해주세요.')
            return redirect(url_for('auth.login'))
        else:
            flash('이미 존재하는 아이디입니다.')
    return render_template('register.html')

@auth_bp.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        username = request.form['username']
        update_fields = {}
        new_password = request.form.get('new_password')
        new_age = request.form.get('new_age')
        new_activity_level = request.form.get('new_activity_level')
        if new_password:
            update_fields['password'] = new_password
        if new_age:
            try:
                update_fields['age'] = int(new_age)
            except ValueError:
                flash('나이는 숫자로 입력해주세요.')
                return render_template('update.html')
        if new_activity_level:
            try:
                val = int(new_activity_level)
                if val < 1 or val > 5:
                    raise ValueError
                update_fields['activity_level'] = val
            except ValueError:
                flash('활동지수는 1~5의 숫자로 입력해주세요.')
                return render_template('update.html')
        if update_fields:
            if update_user(username, update_fields):
                flash('정보가 성공적으로 변경되었습니다.')
                return redirect(url_for('auth.login'))
            else:
                flash('존재하지 않는 아이디입니다.')
        else:
            flash('변경할 정보가 없습니다.')
    return render_template('update.html')


# like 리스트 수정 라우트
@auth_bp.route('/update_like', methods=['GET', 'POST'])
def update_like():
    if request.method == 'POST':
        username = request.form['username']
        try:
            new_like = request.form.getlist('like')
            new_like = [int(x) for x in new_like]
        except Exception:
            flash('like 리스트 형식이 올바르지 않습니다.')
            return render_template('update_like.html')
        if update_like_list(username, new_like):
            flash('like 리스트가 성공적으로 변경되었습니다.')
        else:
            flash('존재하지 않는 아이디입니다.')
    return render_template('update_like.html')

# forbid 리스트 수정 라우트
@auth_bp.route('/update_forbid', methods=['GET', 'POST'])
def update_forbid():
    if request.method == 'POST':
        username = request.form['username']
        try:
            new_forbid = request.form.getlist('forbid')
            new_forbid = [int(x) for x in new_forbid]
        except Exception:
            flash('forbid 리스트 형식이 올바르지 않습니다.')
            return render_template('update_forbid.html')
        if update_forbid_list(username, new_forbid):
            flash('forbid 리스트가 성공적으로 변경되었습니다.')
        else:
            flash('존재하지 않는 아이디입니다.')
    return render_template('update_forbid.html')
