from flask import Blueprint, render_template, request, redirect, url_for, flash
from .auth_routes import login_required
import database_handler as db
from datetime import datetime

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
            name_codes = request.form.getlist('name_codes')
            name_names = request.form.getlist('name_names')
            name_dict = dict(zip(name_codes, name_names))

            if not name_dict or not any(name_dict.values()):
                flash('최소 하나 이상의 언어로 이름을 입력해야 합니다.', 'danger')
                return redirect(url_for('add_data.add_ingredient_route'))

            research_ids = [int(x) for x in request.form.getlist('research_ids')]
            details = request.form['details']
            production_time = request.form['production_time']
            
            nutrient_names = request.form.getlist('nutrient_name')
            nutrient_values = request.form.getlist('nutrient_value')
            
            # Create nutrients list for the new format
            nutrition_info = []
            for name, value in zip(nutrient_names, nutrient_values):
                if name and value:
                    nutrition_info.append({
                        "name": name,
                        "amount_per_unit_mass": float(value)
                    })

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

    all_research = db._load_table('research-data')
    nutrition_categories = db.get_nutrition_categories()
    return render_template('add_ingredient_form.html', all_research=all_research, nutrition_categories=nutrition_categories)

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
    all_research = db._load_table('research-data')
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
            name_codes = request.form.getlist('name_codes')
            name_names = request.form.getlist('name_names')
            name_dict = dict(zip(name_codes, name_names))

            req_ing_ids = [int(x) for x in request.form.getlist('required_ingredient_ids')]
            req_cook_ids = [int(x) for x in request.form.getlist('cooking-method-ids')]
            cooking_instructions = request.form['cooking_instructions']

            # nutrition_info는 여러 nutrient를 리스트로 받음
            nutrition_info = []
            nut_names = request.form.getlist('nutrient_name')
            nut_values = request.form.getlist('nutrient_value')
            for n, v in zip(nut_names, nut_values):
                if n and v:
                    nutrition_info.append({"name": n, "amount_per_dish": float(v)})

            db.add_dish(
                name=name_dict,
                required_ingredient_ids=req_ing_ids,
                required_cooking_method_ids=req_cook_ids,
                nutrition_info=nutrition_info,
                cooking_instructions=cooking_instructions
            )
            flash(f"'{name_dict.get('kor', list(name_dict.values())[0])}' 요리가 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_dish_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    all_ingredients = db._load_table('ingredient')
    all_cooking_methods = db._load_table('cooking-methods')
    return render_template('add_dish_form.html', all_ingredients=all_ingredients, all_cooking_methods=all_cooking_methods)

@bp.route('/storaged-ingredient', methods=['GET', 'POST'])
def add_storaged_ingredient_route():
    if request.method == 'POST':
        try:
            storage_id = int(request.form['storage_id'])
            mass_g = int(request.form['mass_g'])
            expiration_date = request.form['expiration_date']
            production_end_date = request.form['production_end_date']
            processing_type = request.form['processing_type']

            try:
                datetime.strptime(expiration_date, '%Y-%m-%d')
                datetime.strptime(production_end_date, '%Y-%m-%d')
            except ValueError:
                flash("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.", 'danger')
                all_ingredients = db._load_table('ingredient')
                return render_template('add_storaged_ingredient_form.html', all_ingredients=all_ingredients)

            db.add_storaged_ingredient(
                storage_id=storage_id,
                mass_g=mass_g,
                expiration_date=expiration_date,
                production_end_date=production_end_date,
                processing_type=processing_type
            )
            flash(f"보관 식재료가 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_storaged_ingredient_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    all_ingredients = db._load_table('ingredient')
    return render_template('add_storaged_ingredient_form.html', all_ingredients=all_ingredients)
