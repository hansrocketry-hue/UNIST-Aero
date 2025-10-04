from flask import Blueprint, render_template, request, redirect, url_for, flash
from .auth_routes import login_required
import database_handler as db

bp = Blueprint('add_data', __name__, url_prefix='/add')

@bp.route('/')
@login_required
def add_data_home():
    """데이터 추가 메인 페이지"""
    return render_template('add_data.html')

@bp.route('/ingredient', methods=['GET', 'POST'])
@login_required
def add_ingredient_route():
    if request.method == 'POST':
        try:
            lang_codes = request.form.getlist('lang_codes')
            lang_names = request.form.getlist('lang_names')
            name_dict = dict(zip(lang_codes, lang_names))

            research_ids = [int(x) for x in request.form.getlist('research_ids')]
            calories = float(request.form['calories'])
            details = request.form['details']
            production_time = request.form['production_time']
            
            nutrition_info = {"calories": calories, "nutrients_per_unit_mass": {}, "details": details}
            
            db.add_ingredient(
                name=name_dict,
                research_ids=research_ids,
                nutrition_info=nutrition_info,
                production_time=production_time
            )
            
            flash(f"'{name_dict.get('kor', list(name_dict.values())[0])}'이(가) 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_ingredient_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')

    all_research = db.load_db().get('research-data', [])
    return render_template('add_ingredient_form.html', all_research=all_research)

@bp.route('/cooking-method', methods=['GET', 'POST'])
def add_cooking_method_route():
    if request.method == 'POST':
        try:
            name_codes = request.form.getlist('name_codes')
            name_names = request.form.getlist('name_names')
            name_dict = dict(zip(name_codes, name_names))

            desc_codes = request.form.getlist('desc_codes')
            desc_names = request.form.getlist('desc_names')
            desc_dict = dict(zip(desc_codes, desc_names))

            research_ids = [int(x) for x in request.form.getlist('research_ids')]

            db.add_cooking_method(
                name=name_dict,
                description=desc_dict,
                research_ids=research_ids
            )
            flash(f"'{name_dict.get('kor', list(name_dict.values())[0])}' 조리 방법이 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_cooking_method_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    all_research = db.load_db().get('research-data', [])
    return render_template('add_cooking_method_form.html', all_research=all_research)

@bp.route('/research-data', methods=['GET', 'POST'])
def add_research_data_route():
    if request.method == 'POST':
        try:
            link = request.form['link']
            title = request.form['title']
            summary_codes = request.form.getlist('summary_codes')
            summary_names = request.form.getlist('summary_names')
            summary_dict = dict(zip(summary_codes, summary_names))

            db.add_research_data(
                reference_data={"link": link, "title": title},
                summary=summary_dict
            )
            flash(f"'{title}' 연구 자료가 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_research_data_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    return render_template('add_research_data_form.html')

@bp.route('/dish', methods=['GET', 'POST'])
def add_dish_route():
    if request.method == 'POST':
        try:
            dish_type = request.form['dish_type']
            name_codes = request.form.getlist('name_codes')
            name_names = request.form.getlist('name_names')
            name_dict = dict(zip(name_codes, name_names))

            image_url = request.form['image_url']
            req_ing_ids = [int(x) for x in request.form.getlist('required_ingredient_ids')]
            req_cook_ids = [int(x) for x in request.form.getlist('required_cooking_method_ids')]
            calories = float(request.form['calories'])
            cooking_instructions_codes = request.form.getlist('cooking_instructions_codes')
            cooking_instructions_names = request.form.getlist('cooking_instructions_names')
            cooking_instructions_dict = dict(zip(cooking_instructions_codes, cooking_instructions_names))

            db.add_dish(
                dish_type=dish_type,
                name=name_dict,
                image_url=image_url,
                required_ingredient_ids=req_ing_ids,
                required_cooking_method_ids=req_cook_ids,
                nutrition_info={"calories": calories, "nutrients_per_unit_mass": {}},
                cooking_instructions=cooking_instructions_dict
            )
            flash(f"'{name_dict.get('kor', list(name_dict.values())[0])}' 요리가 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_dish_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    all_ingredients = db.load_db().get('ingredient', [])
    all_cooking_methods = db.load_db().get('cooking-methods', [])
    return render_template('add_dish_form.html', all_ingredients=all_ingredients, all_cooking_methods=all_cooking_methods)

@bp.route('/storaged-ingredient', methods=['GET', 'POST'])
def add_storaged_ingredient_route():
    if request.method == 'POST':
        try:
            storage_id = int(request.form['storage_id'])
            mass_g = int(request.form['mass_g'])
            expiration_date = request.form['expiration_date']
            production_end_date = request.form['production_end_date']

            db.add_storaged_ingredient(
                storage_id=storage_id,
                mass_g=mass_g,
                expiration_date=expiration_date,
                production_end_date=production_end_date
            )
            flash(f"보관 식재료가 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_storaged_ingredient_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    all_ingredients = db.load_db().get('ingredient', [])
    return render_template('add_storaged_ingredient_form.html', all_ingredients=all_ingredients)
