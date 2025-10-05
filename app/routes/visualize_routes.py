from flask import Blueprint, render_template, session
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
        'dish': db._load_table('dish')
    }
    # Ensure each ingredient has a 'nutrition_info' field from embedded nutrition if present
    for ingredient in data['ingredient']:
        if 'nutrition' in ingredient:
            ingredient['nutrition_info'] = ingredient['nutrition']
    
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

@bp.route('/ingredient/<ingredient_id>')
def ingredient_detail(ingredient_id):
    """식재료 상세 페이지"""
    ingredient_data = db._load_table('ingredient')
    ingredient = next((item for item in ingredient_data if item['id'] == ingredient_id), None)
    if ingredient:
        # Get nutrition info from embedded nutrition
        if 'nutrition' in ingredient:
            ingredient['nutrition_info'] = ingredient['nutrition']
            
        # Get related dishes (new schema: required_ingredients is list of {id, amount_g})
        dishes = db._load_table('dish')
        related_dishes = []
        for d in dishes:
            for req in d.get('required_ingredients', []):
                if req.get('id') == ingredient_id:
                    related_dishes.append(d)
                    break
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

@bp.route('/dish/<dish_id>')
def dish_detail(dish_id):
    """레시피(요리) 상세 페이지"""
    dishes = db._load_table('dish')
    dish = next((d for d in dishes if d['id'] == dish_id), None)
    ingredients = db._load_table('ingredient')
    cooking_methods = db._load_table('cooking-methods')
    # 필요한 조리방법 정보 추출
    method_ids = dish.get('cooking-method-ids', []) if dish else []
    required_methods = [m for m in cooking_methods if m['id'] in method_ids]
    # dish.required_ingredients: list of {id, amount_g}
    required_ingredients = []
    if dish:
        reqs = dish.get('required_ingredients', [])
        for req in reqs:
            iid = req.get('id')
            info = next((ing for ing in ingredients if ing['id'] == iid), None)
            if info:
                # include amount for template
                info_copy = dict(info)
                info_copy['used_amount_g'] = req.get('amount_g')
                required_ingredients.append(info_copy)
    # 칼로리 추출 (nutrition_info가 리스트이므로 Calories (Total) 항목 찾기)
    calories = None
    if dish and isinstance(dish.get('nutrition_info'), list):
        for n in dish['nutrition_info']:
            if n.get('name') == 'Calories (Total)':
                # Get per-gram calories
                calories = n.get('amount_per_unit_mass', 0)
                break
    # 조리설명(한글)
    selected_lang = session.get('lang', 'kor')
    cooking_instructions = dish.get('cooking_instructions')
    if isinstance(cooking_instructions, dict):
        cooking_instructions = cooking_instructions.get(selected_lang, '')
    return render_template(
        'dish_detail.html',
        dish=dish,
        required_methods=required_methods,
        required_ingredients=required_ingredients,
        calories=calories,
        cooking_instructions=cooking_instructions
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

        # 생산 모드인지 확인
        is_production = item.get('mode') == 'production'
        
        if is_production:
            # 생산 모드: min_end_date와 max_end_date 사용
            if not (item.get('min_end_date') and item.get('max_end_date')):
                continue
                
            try:
                min_end_date = datetime.strptime(item['min_end_date'], '%Y-%m-%d')
                max_end_date = datetime.strptime(item['max_end_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                continue

            # bar start should be the earlier of start_date and today
            bar_start = start_date if start_date < today else today
            bar_end = max_end_date
            span_days = (bar_end - bar_start).days
            if span_days <= 0:
                continue

            # positions relative to bar_start/span
            def pct(days):
                return max(0.0, min(100.0, (days / span_days) * 100.0))

            # compute key day offsets
            start_offset = (start_date - bar_start).days
            today_offset = (today - bar_start).days
            min_offset = (min_end_date - bar_start).days
            max_offset = (max_end_date - bar_start).days

            # grey: area between today and start if start in future
            grey_width = 0.0
            if start_date > today:
                grey_width = pct(start_offset - today_offset)  # start - today

            # green: from start to current_time (only if start <= today)
            green_left = pct(start_offset) if start_offset >= 0 else 0.0
            green_width = 0.0
            if today >= start_date:
                current_time = min(today, max_end_date)
                current_offset = (current_time - bar_start).days
                green_width = pct(max(0, current_offset - start_offset))

            # expected (sky-blue): from min_end_date to max_end_date
            expected_left = pct(min_offset)
            expected_width = pct(max_offset - min_offset)

            # marker for today's position relative to bar
            today_pos = pct(today_offset)
            start_pos = pct(start_offset)

            processed_item = {
                'name': ingredient_info['name'].get('kor', 'N/A'),
                'mass_g': item.get('mass_g'),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'is_production': True,
                'grey_width': grey_width,
                'green_left': green_left,
                'green_width': green_width,
                'expected_left': expected_left,
                'expected_width': expected_width,
                'today_pos': today_pos,
                'start_pos': start_pos,
                'min_end_date': min_end_date.strftime('%Y-%m-%d'),
                'max_end_date': max_end_date.strftime('%Y-%m-%d')
            }

        else:
            # 저장 모드: expiration_date 사용
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
            if total_duration <= 0:
                continue

            # 현재 진행률 계산 (시작일부터 현재까지)
            current_time = min(today, expiration_date)
            current_time = max(current_time, start_date)  # 시작일보다 이전이면 시작일 사용
            current_progress = ((current_time - start_date).days / total_duration) * 100
            current_progress = max(0, min(current_progress, 100))

            processed_item = {
                'name': ingredient_info['name'].get('kor', 'N/A'),
                'mass_g': item.get('mass_g'),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'is_production': False,
                'current_progress': current_progress,
                'expiration_date': expiration_date.strftime('%Y-%m-%d')
            }

        processed_storaged_ingredients.append(processed_item)

    return render_template('visualize_storaged_ingredient.html', 
                       storaged_ingredients=processed_storaged_ingredients,
                       today=today.strftime('%Y-%m-%d'))

    return render_template('visualize_storaged_ingredient.html', storaged_ingredients=processed_storaged_ingredients)
