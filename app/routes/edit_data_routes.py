"""
edit_data_routes.py - 데이터 수정을 위한 라우트 모듈
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
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
        'link': request.form.get('link')
    }
    summary = {
        'kor': request.form.get('summary_kor'),
        'eng': request.form.get('summary_eng')
    }
    
    db.update_research_data(research_id, reference_data, summary)
    return redirect(url_for('visualize.research_detail', research_id=research_id))

@bp.route('/ingredient/<ingredient_id>')
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

@bp.route('/ingredient/<ingredient_id>', methods=['POST'])
def edit_ingredient_submit(ingredient_id):
    """식재료 수정 처리"""
    # Build multilingual name dict from dynamic fields
    name_codes = request.form.getlist('name_codes') or request.form.getlist('name_codes[]')
    name_names = request.form.getlist('name_names') or request.form.getlist('name_names[]')
    name = {}
    for i in range(min(len(name_codes), len(name_names))):
        code = name_codes[i]
        val = name_names[i]
        if code and val and val.strip():
            name[code] = val.strip()

    if not name:
        # At least one language name required
        from flask import flash
        flash('최소 하나 이상의 언어로 이름을 입력해야 합니다.', 'danger')
        return redirect(url_for('edit_data.edit_ingredient_route', ingredient_id=ingredient_id))
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
        'min': request.form.get('min') or request.form.get('min_time'),
        'max': request.form.get('max') or request.form.get('max_time')
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

@bp.route('/dish/<dish_id>')
def edit_dish_route(dish_id):
    """요리 수정 페이지"""
    dish_data = db._load_table('dish')
    dish = next((item for item in dish_data if item['id'] == dish_id), None)
    if not dish:
        return redirect(url_for('visualize.visualize_home'))
    
    ingredients = db._load_table('ingredient')
    all_dishes = db._load_table('dish')
    cooking_methods = db._load_table('cooking-methods')
    nutrition_categories = db.get_nutrition_categories()
    # Normalize dish['name'] into a dict for the template (kor/eng)
    if isinstance(dish.get('name'), str):
        dish['name'] = {
            'kor': dish['name'],
            'eng': dish['name']
        }
    elif not dish.get('name'):
        dish['name'] = {'kor': '', 'eng': ''}

    # Normalize dish['cooking_instructions'] as well
    if isinstance(dish.get('cooking_instructions'), str):
        dish['cooking_instructions'] = {
            'kor': dish['cooking_instructions'],
            'eng': dish['cooking_instructions']
        }
    elif not dish.get('cooking_instructions'):
        dish['cooking_instructions'] = {'kor': '', 'eng': ''}

    return render_template('edit_dish_form.html',
                         dish=dish,
                         ingredients=ingredients,
                         all_dishes=all_dishes,
                         cooking_methods=cooking_methods,
                         nutrition_categories=nutrition_categories)


@bp.route('/dish/<dish_id>', methods=['POST'])
def edit_dish_submit(dish_id):
    """요리 수정 처리"""
    name = {
        'kor': request.form.get('name_kor'),
        'eng': request.form.get('name_eng')
    }
    image_url = request.form.get('image_url')
    
    # 재료 정보 수집
    required_ingredients = []
    item_types = request.form.getlist('item_types[]')
    item_ids = request.form.getlist('item_ids[]')
    item_amounts = request.form.getlist('item_amounts[]')
    for type, id, amount in zip(item_types, item_ids, item_amounts):
        if type and id and amount and amount.strip():
            required_ingredients.append({
                'type': type,
                'id': id,  # Keep as string (supports both "i1" and "d1" format)
                'amount_g': float(amount)
            })

    # 조리 방법 ID 수집
    required_cooking_method_ids = [int(id) for id in request.form.getlist('cooking_method_ids[]')]
    cooking_instructions = {
        'kor': request.form.get('instructions_kor') or '',
        'eng': request.form.get('instructions_eng') or ''
    }
    # If both instruction fields are empty, treat cooking_instructions as None
    if not (cooking_instructions.get('kor').strip() or cooking_instructions.get('eng').strip()):
        cooking_instructions = None
    # Debug: log incoming form data to console to help diagnose save issues
    try:
        print(f"[edit_dish_submit] dish_id={dish_id}")
        print(f"[edit_dish_submit] name={name}")
        print(f"[edit_dish_submit] image_url={image_url}")
        print(f"[edit_dish_submit] required_ingredients={required_ingredients}")
        print(f"[edit_dish_submit] required_cooking_method_ids={required_cooking_method_ids}")
        print(f"[edit_dish_submit] cooking_instructions={cooking_instructions}")
    except Exception as e:
        print('[edit_dish_submit] error printing form data:', e)

    # 영양 정보는 자동 계산되도록 None으로 전달
    try:
        db.update_dish(dish_id, name, image_url, required_ingredients,
                      required_cooking_method_ids, nutrition_data=None,
                      cooking_instructions=cooking_instructions)
    except Exception as e:
        # Log error and return to detail page with no crash
        print(f"[edit_dish_submit] update_dish raised exception: {e}")
    
    return redirect(url_for('visualize.dish_detail', dish_id=dish_id))