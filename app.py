from flask import Flask, render_template, request, redirect, url_for
from database_manager import load_database, add_research_data, add_foods_first, add_cooking_method, add_foods_second
import json

app = Flask(__name__)

@app.route('/')
def index():
    """메인 페이지 - 데이터베이스의 모든 내용을 표시합니다."""
    db = load_database()
    return render_template('index.html', db=db)

@app.route('/add/research', methods=['POST'])
def handle_add_research():
    """새 연구 데이터 추가를 처리합니다."""
    data = request.form.get('data')
    summary_kor = request.form.get('summary_kor')
    summary_eng = request.form.get('summary_eng')
    summary = {"kor": summary_kor, "eng": summary_eng}
    add_research_data(data, summary)
    return redirect(url_for('index'))

@app.route('/add/foods-first', methods=['POST'])
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

if __name__ == '__main__':
    app.run(port=5001, debug=True)