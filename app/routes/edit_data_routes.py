"""
edit_data_routes.py - 데이터 수정을 위한 라우트 모듈
"""

from flask import Blueprint, render_template, request, redirect, url_for
import database_handler as db
from datetime import datetime

bp = Blueprint('edit_data', __name__, url_prefix='/edit')

@bp.route('/research/<int:research_id>')
def edit_research_route(research_id):
    """연구 자료 수정 페이지"""
    research_data = db._load_table('research-data')
    research = next((item for item in research_data if item['id'] == research_id), None)
    if not research:
        return redirect(url_for('visualize.visualize_home'))
    return render_template('edit_research_form.html', research=research)

@bp.route('/research/<int:research_id>', methods=['POST'])
def edit_research_submit(research_id):
    """연구 자료 수정 처리"""
    reference_data = {
        'title': request.form.get('title'),
        'authors': request.form.get('authors'),
        'journal': request.form.get('journal'),
        'year': request.form.get('year'),
        'doi': request.form.get('doi')
    }
    summary = {
        'kor': request.form.get('summary_kor'),
        'eng': request.form.get('summary_eng')
    }
    
    db.update_research_data(research_id, reference_data, summary)
    return redirect(url_for('visualize.research_detail', research_id=research_id))

@bp.route('/ingredient/<int:ingredient_id>')
def edit_ingredient_route(ingredient_id):
    """식재료 수정 페이지"""
    ingredient_data = db._load_table('ingredient')
    ingredient = next((item for item in ingredient_data if item['id'] == ingredient_id), None)
    if not ingredient:
        return redirect(url_for('visualize.visualize_home'))
    research_data = db._load_table('research-data')
    nutrition_categories = db.get_nutrition_categories()
    return render_template('edit_ingredient_form.html', 
                         ingredient=ingredient,
                         research_data=research_data,
                         nutrition_categories=nutrition_categories)

@bp.route('/ingredient/<int:ingredient_id>', methods=['POST'])
def edit_ingredient_submit(ingredient_id):
    """식재료 수정 처리"""
    name = {
        'kor': request.form.get('name_kor'),
        'eng': request.form.get('name_eng')
    }
    research_ids = [int(id) for id in request.form.getlist('research_ids[]')]
    
    # 영양 정보 수집
    nutrition_data = []
    nutrition_categories = db.get_nutrition_categories()
    for category in nutrition_categories:
        category_name = category['name']
        amount = request.form.get(f'nutrition_{category_name}')
        if amount and amount.strip():
            nutrition_data.append({
                'name': category_name,
                'amount_per_unit_mass': float(amount)
            })

    # 생산 시간 정보
    production_time = {
        'producible': bool(request.form.get('producible')),
        'min_time': request.form.get('min_time'),
        'max_time': request.form.get('max_time'),
        'unit': request.form.get('time_unit', 'days')
    }

    db.update_ingredient(ingredient_id, name, research_ids, nutrition_data, production_time)
    return redirect(url_for('visualize.ingredient_detail', ingredient_id=ingredient_id))

@bp.route('/cooking-method/<int:method_id>')
def edit_cooking_method_route(method_id):
    """조리 방법 수정 페이지"""
    cooking_methods = db._load_table('cooking-methods')
    method = next((item for item in cooking_methods if item['id'] == method_id), None)
    if not method:
        return redirect(url_for('visualize.visualize_home'))
    research_data = db._load_table('research-data')
    return render_template('edit_cooking_method_form.html', 
                         method=method,
                         research_data=research_data)

@bp.route('/cooking-method/<int:method_id>', methods=['POST'])
def edit_cooking_method_submit(method_id):
    """조리 방법 수정 처리"""
    name = {
        'kor': request.form.get('name_kor'),
        'eng': request.form.get('name_eng')
    }
    description = {
        'kor': request.form.get('description_kor'),
        'eng': request.form.get('description_eng')
    }
    research_ids = [int(id) for id in request.form.getlist('research_ids[]')]

    db.update_cooking_method(method_id, name, description, research_ids)
    return redirect(url_for('visualize.cooking_method_detail', method_id=method_id))

@bp.route('/dish/<int:dish_id>')
def edit_dish_route(dish_id):
    """요리 수정 페이지"""
    dish_data = db._load_table('dish')
    dish = next((item for item in dish_data if item['id'] == dish_id), None)
    if not dish:
        return redirect(url_for('visualize.visualize_home'))
    
    ingredients = db._load_table('ingredient')
    cooking_methods = db._load_table('cooking-methods')
    nutrition_categories = db.get_nutrition_categories()
    
    return render_template('edit_dish_form.html',
                         dish=dish,
                         ingredients=ingredients,
                         cooking_methods=cooking_methods,
                         nutrition_categories=nutrition_categories)

@bp.route('/dish/<int:dish_id>', methods=['POST'])
def edit_dish_submit(dish_id):
    """요리 수정 처리"""
    name = {
        'kor': request.form.get('name_kor'),
        'eng': request.form.get('name_eng')
    }
    image_url = request.form.get('image_url')
    
    # 재료 정보 수집
    required_ingredients = []
    ingredient_ids = request.form.getlist('ingredient_ids[]')
    ingredient_amounts = request.form.getlist('ingredient_amounts[]')
    for id, amount in zip(ingredient_ids, ingredient_amounts):
        if id and amount and amount.strip():
            required_ingredients.append({
                'id': int(id),
                'amount_g': float(amount)
            })

    # 조리 방법 ID 수집
    required_cooking_method_ids = [int(id) for id in request.form.getlist('cooking_method_ids[]')]
    
    # 조리 설명
    cooking_instructions = {
        'kor': request.form.get('instructions_kor'),
        'eng': request.form.get('instructions_eng')
    }

    # 영양 정보는 자동 계산되도록 None으로 전달
    db.update_dish(dish_id, name, image_url, required_ingredients, 
                  required_cooking_method_ids, nutrition_data=None,
                  cooking_instructions=cooking_instructions)
                  
    return redirect(url_for('visualize.dish_detail', dish_id=dish_id))