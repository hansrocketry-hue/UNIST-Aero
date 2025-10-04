from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
USER_INFO_FILE = 'user_info.json'

def load_user_info():
    """사용자 정보를 JSON 파일에서 읽어옵니다."""
    if os.path.exists(USER_INFO_FILE):
        with open(USER_INFO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_user_info(name):
    """사용자 정보를 JSON 파일에 저장합니다."""
    user_info = {"name": name}
    with open(USER_INFO_FILE, 'w', encoding='utf-8') as f:
        json.dump(user_info, f, indent=4, ensure_ascii=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    메인 페이지:
    - GET 요청: 사용자 정보가 없으면 title.html을 보여주고, 있으면 index.html로 리다이렉트합니다.
    - POST 요청: 이름을 저장하고 index.html로 리다이렉트합니다.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            save_user_info(name)
            return redirect(url_for('main_page'))  # 이름을 저장한 후 main_page로 리다이렉트
        else:
            # 이름이 제공되지 않은 경우, title.html을 다시 렌더링하고 오류 메시지를 표시할 수 있습니다.
            return render_template('title.html', error="이름을 입력해주세요.")

    user_info = load_user_info()
    if user_info:
        return redirect(url_for('main_page'))  # 이미 사용자 정보가 있으면 main_page로 리다이렉트
    else:
        return render_template('title.html')  # 사용자 정보가 없으면 title.html을 보여줌

@app.route('/main_page')
def main_page():
    """실제 메인 페이지."""
    return "<h1>Welcome to the Main Page!</h1>"  # 간단한 메인 페이지 내용


if __name__ == '__main__':
    app.run(port=5001, debug=True)