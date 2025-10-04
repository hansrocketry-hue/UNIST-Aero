from flask import Blueprint, render_template, request, redirect, url_for, flash
import database_handler as db

bp = Blueprint('add_data', __name__, url_prefix='/add')

@bp.route('/')
def add_data_home():
    """데이터 추가 메인 페이지"""
    return render_template('add_data.html')

@bp.route('/ingredient', methods=['GET', 'POST'])
def add_ingredient_route():
    if request.method == 'POST':
        try:
            name_kor = request.form['name_kor']
            name_eng = request.form['name_eng']
            research_ids = [int(x) for x in request.form.getlist('research_ids')]
            calories = float(request.form['calories'])
            details = request.form['details']
            production_time = request.form['production_time']
            
            nutrition_info = {"calories": calories, "nutrients_per_unit_mass": {}, "details": details}
            
            db.add_ingredient(
                name={"kor": name_kor, "eng": name_eng},
                research_ids=research_ids,
                nutrition_info=nutrition_info,
                production_time=production_time
            )
            flash(f"'{name_kor}'이(가) 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_ingredient_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')

    all_research = db.load_db().get('research-data', [])
    return render_template('add_ingredient_form.html', all_research=all_research)

@bp.route('/cooking-method', methods=['GET', 'POST'])
def add_cooking_method_route():
    if request.method == 'POST':
        try:
            name_kor = request.form['name_kor']
            name_eng = request.form['name_eng']
            desc_kor = request.form['desc_kor']
            desc_eng = request.form['desc_eng']
            research_ids = [int(x) for x in request.form.getlist('research_ids')]

            db.add_cooking_method(
                name={"kor": name_kor, "eng": name_eng},
                description={"kor": desc_kor, "eng": desc_eng},
                research_ids=research_ids
            )
            flash(f"'{name_kor}' 조리 방법이 성공적으로 추가되었습니다.", 'success')
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
            summary_kor = request.form['summary_kor']
            summary_eng = request.form['summary_eng']

            db.add_research_data(
                reference_data={"link": link, "title": title},
                summary={"kor": summary_kor, "eng": summary_eng}
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
            name_kor = request.form['name_kor']
            name_eng = request.form['name_eng']
            image_url = request.form['image_url']
            req_ing_ids = [int(x) for x in request.form.getlist('required_ingredient_ids')]
            req_cook_ids = [int(x) for x in request.form.getlist('required_cooking_method_ids')]
            calories = float(request.form['calories'])
            cooking_instructions = request.form['cooking_instructions']

            db.add_dish(
                dish_type=dish_type,
                name={"kor": name_kor, "eng": name_eng},
                image_url=image_url,
                required_ingredient_ids=req_ing_ids,
                required_cooking_method_ids=req_cook_ids,
                nutrition_info={"calories": calories, "nutrients_per_unit_mass": {}},
                cooking_instructions=cooking_instructions
            )
            flash(f"'{name_kor}' 요리가 성공적으로 추가되었습니다.", 'success')
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
