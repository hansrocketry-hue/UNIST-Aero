from flask import Blueprint, render_template
import database_handler as db

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
    ingredient_data = db.load_db().get('ingredient', [])
    ingredient = next((item for item in ingredient_data if item['id'] == ingredient_id), None)
    # Get related dishes
    dishes = db.load_db().get('dish', [])
    related_dishes = [d for d in dishes if ingredient_id in d.get('required_ingredient_ids', [])]
    return render_template('ingredient_detail.html', ingredient=ingredient, related_dishes=related_dishes)

@bp.route('/cooking-method/<int:method_id>')
def cooking_method_detail(method_id):
    """조리 방법 상세 페이지"""
    cooking_method_data = db.load_db().get('cooking-methods', [])
    method = next((item for item in cooking_method_data if item['id'] == method_id), None)
    # Get related dishes
    dishes = db.load_db().get('dish', [])
    related_dishes = [d for d in dishes if method_id in d.get('required_cooking_method_ids', [])]
    return render_template('cooking_method_detail.html', method=method, related_dishes=related_dishes)
