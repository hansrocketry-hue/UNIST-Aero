from flask import Blueprint, render_template
import database_handler as db
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

bp = Blueprint('visualize', __name__, url_prefix='/visualize')

@bp.route('/')
def visualize_home():
    """데이터 시각화 메인 페이지"""
    data = db.load_db()
    return render_template('visualize.html', data=data)

@bp.route('/research/<int:research_id>')
def research_detail(research_id):
    """연구 자료 상세 페이지"""
    research_data = db.load_db().get('research-data', [])
    research = next((item for item in research_data if item['id'] == research_id), None)
    # Get related ingredients
    ingredients = db.load_db().get('ingredient', [])
    related_ingredients = [ing for ing in ingredients if research_id in ing.get('research_ids', [])]
    # Get related cooking methods
    cooking_methods = db.load_db().get('cooking-methods', [])
    related_cooking_methods = [cm for cm in cooking_methods if research_id in cm.get('research_ids', [])]
    return render_template('research_detail.html', research=research, related_ingredients=related_ingredients, related_cooking_methods=related_cooking_methods)

@bp.route('/ingredient/<int:ingredient_id>')
def ingredient_detail(ingredient_id):
    """식재료 상세 페이지"""
    all_data = db.load_db()
    ingredient_data = all_data.get('ingredient', [])
    ingredient = next((item for item in ingredient_data if item['id'] == ingredient_id), None)
    
    related_dishes = []
    if ingredient:
        dishes = all_data.get('dish', [])
        related_dishes = [d for d in dishes if ingredient_id in d.get('required_ingredient_ids', [])]

    research_data = all_data.get('research-data', [])
    
    return render_template('ingredient_detail.html', ingredient=ingredient, related_dishes=related_dishes, research_data=research_data)

@bp.route('/cooking-method/<int:method_id>')
def cooking_method_detail(method_id):
    """조리 방법 상세 페이지"""
    all_data = db.load_db()
    cooking_method_data = all_data.get('cooking-methods', [])
    method = next((item for item in cooking_method_data if item['id'] == method_id), None)
    
    related_dishes = []
    if method:
        dishes = all_data.get('dish', [])
        related_dishes = [d for d in dishes if method_id in d.get('required_cooking_method_ids', [])]

    research_data = all_data.get('research-data', [])
    
    return render_template('cooking_method_detail.html', method=method, related_dishes=related_dishes, research_data=research_data)

@bp.route('/storaged-ingredient')
def visualize_storaged_ingredient():
    """Storaged ingredient visualization page"""
    db_data = db.load_db()
    storaged_ingredients = db_data.get('storaged-ingredient', [])
    ingredients = db_data.get('ingredient', [])
    
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
