from flask import Blueprint, render_template
import database_handler as db
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

bp = Blueprint('visualize', __name__, url_prefix='/visualize')

@bp.route('/')
def visualize_home():
    """데이터 시각화 메인 페이지"""
    # 분할 DB에 맞게 각 테이블별로 불러오기
    data = {
        'ingredient': db._load_table('ingredient'),
        'storaged-ingredient': db._load_table('storaged-ingredient'),
        'cooking-methods': db._load_table('cooking-methods'),
        'research-data': db._load_table('research-data'),
        'dish': db._load_table('dish'),
        'nutrition': db._load_table('nutrition')
    }
    
    # 각 식재료의 영양소 정보를 nutrition 테이블에서 가져와서 추가
    for ingredient in data['ingredient']:
        nutrition = next((n for n in data['nutrition'] if n['id'] == ingredient.get('nutrition_id')), None)
        if nutrition:
            ingredient['nutrition_info'] = nutrition['nutrients']
    
    ingredients = data['ingredient']
    cooking_methods = data['cooking-methods']
    dishes = data['dish']
    return render_template('visualize.html', data=data, ingredients=ingredients, cooking_methods=cooking_methods, dishes=dishes)

@bp.route('/research/<int:research_id>')
def research_detail(research_id):
    """연구 자료 상세 페이지"""
    research_data = db._load_table('research-data')
    research = next((item for item in research_data if item['id'] == research_id), None)
    # Get related ingredients
    ingredients = db._load_table('ingredient')
    related_ingredients = [ing for ing in ingredients if research_id in ing.get('research_ids', [])]
    # Get related cooking methods
    cooking_methods = db._load_table('cooking-methods')
    related_cooking_methods = [cm for cm in cooking_methods if research_id in cm.get('research_ids', [])]
    return render_template('research_detail.html', research=research, related_ingredients=related_ingredients, related_cooking_methods=related_cooking_methods)

@bp.route('/ingredient/<int:ingredient_id>')
def ingredient_detail(ingredient_id):
    """식재료 상세 페이지"""
    ingredient_data = db._load_table('ingredient')
    nutrition_data = db._load_table('nutrition')
    
    ingredient = next((item for item in ingredient_data if item['id'] == ingredient_id), None)
    if ingredient:
        # Get nutrition info
        nutrition = next((item for item in nutrition_data if item['id'] == ingredient.get('nutrition_id')), None)
        if nutrition:
            ingredient['nutrition_info'] = nutrition['nutrients']
            
        # Get related dishes
        dishes = db._load_table('dish')
        related_dishes = [d for d in dishes if ingredient_id in d.get('required_ingredient_ids', [])]
    else:
        related_dishes = []
        
    research_data = db._load_table('research-data')
    return render_template('ingredient_detail.html', ingredient=ingredient, related_dishes=related_dishes, research_data=research_data)

@bp.route('/cooking-method/<int:method_id>')
def cooking_method_detail(method_id):
    """조리 방법 상세 페이지"""
    cooking_method_data = db._load_table('cooking-methods')
    method = next((item for item in cooking_method_data if item['id'] == method_id), None)
    related_dishes = []
    if method:
        dishes = db._load_table('dish')
        # dish의 조리방법 필드명 변경 반영
        related_dishes = [d for d in dishes if method_id in d.get('cooking-method-ids', [])]
    research_data = db._load_table('research-data')
    return render_template('cooking_method_detail.html', method=method, related_dishes=related_dishes, research_data=research_data)

@bp.route('/dish/<int:dish_id>')
def dish_detail(dish_id):
    """레시피(요리) 상세 페이지"""
    dishes = db._load_table('dish')
    dish = next((d for d in dishes if d['id'] == dish_id), None)
    ingredients = db._load_table('ingredient')
    cooking_methods = db._load_table('cooking-methods')
    # 필요한 조리방법 정보 추출
    method_ids = dish.get('cooking-method-ids', []) if dish else []
    required_methods = [m for m in cooking_methods if m['id'] in method_ids]
    ingredient_ids = dish.get('required_ingredient_ids', []) if dish else []
    required_ingredients = [i for i in ingredients if i['id'] in ingredient_ids]
    # 칼로리 추출 (nutrition_info가 리스트이므로 Calories (Total) 항목 찾기)
    calories = None
    if dish and isinstance(dish.get('nutrition_info'), list):
        for n in dish['nutrition_info']:
            if n.get('name') == 'Calories (Total)':
                calories = n.get('amount_per_dish')
                break
    # 조리설명(한글)
    cooking_instructions_kor = dish.get('cooking_instructions')
    if isinstance(cooking_instructions_kor, dict):
        cooking_instructions_kor = cooking_instructions_kor.get('kor', '')
    return render_template(
        'dish_detail.html',
        dish=dish,
        required_methods=required_methods,
        required_ingredients=required_ingredients,
        calories=calories,
        cooking_instructions_kor=cooking_instructions_kor
    )

@bp.route('/storaged-ingredient')
def visualize_storaged_ingredient():
    """Storaged ingredient visualization page"""
    storaged_ingredients = db._load_table('storaged-ingredient')
    ingredients = db._load_table('ingredient')
    processed_storaged_ingredients = []
    today = datetime.now()

    for item in storaged_ingredients:
        ingredient_info = next((ing for ing in ingredients if ing['id'] == item.get('storage-id')), None)
        if not ingredient_info:
            continue

        start_date_str = item.get('start_date')
        if not start_date_str:
            continue
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

        expiration_date = None
        if 'expiration_date' in item and item['expiration_date']:
            try:
                expiration_date = datetime.strptime(item['expiration_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                expiration_date = None

        if not expiration_date and 'shelf_life' in item:
            shelf_life_str = item['shelf_life']
            years = int(re.search(r'(\d+)\s+year', shelf_life_str).group(1)) if re.search(r'(\d+)\s+year', shelf_life_str) else 0
            months = int(re.search(r'(\d+)\s+month', shelf_life_str).group(1)) if re.search(r'(\d+)\s+month', shelf_life_str) else 0
            days = int(re.search(r'(\d+)\s+day', shelf_life_str).group(1)) if re.search(r'(\d+)\s+day', shelf_life_str) else 0
            expiration_date = start_date + relativedelta(years=years, months=months, days=days)

        if not expiration_date:
            continue

        total_duration = (expiration_date - start_date).days
        elapsed_duration = (today - start_date).days
        progress = (elapsed_duration / total_duration) * 100 if total_duration > 0 else 0
        progress = max(0, min(progress, 100))

        processed_storaged_ingredients.append({
            'name': ingredient_info['name'].get('kor', 'N/A'),
            'mass_g': item.get('mass_g'),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'expiration_date': expiration_date.strftime('%Y-%m-%d'),
            'progress': progress
        })

    return render_template('visualize_storaged_ingredient.html', storaged_ingredients=processed_storaged_ingredients)
