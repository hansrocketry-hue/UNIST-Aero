from flask import Blueprint, render_template, request, redirect, url_for, flash
from .auth_routes import login_required
import database_handler as db
from datetime import datetime, timedelta

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
            # Build multilingual name dict safely
            name_codes = request.form.getlist('name_codes')
            name_names = request.form.getlist('name_names')
            name_dict = {}
            # Zip by index to be resilient against mismatched lengths
            for i in range(min(len(name_codes), len(name_names))):
                code = name_codes[i]
                val = name_names[i]
                if code and val:
                    name_dict[code] = val

            if not name_dict or not any(name_dict.values()):
                flash('최소 하나 이상의 언어로 이름을 입력해야 합니다.', 'danger')
                return redirect(url_for('add_data.add_ingredient_route'))

            # Parse research ids safely (ignore invalid values)
            research_ids = []
            for raw in request.form.getlist('research_ids'):
                try:
                    research_ids.append(int(raw))
                except (ValueError, TypeError):
                    continue

            # details and production_time may be optional in the form; use .get to avoid KeyError
            details = request.form.get('details', '')
            production_time = request.form.get('production_time', '')

            # Parse nutrition fields robustly
            nutrient_names = request.form.getlist('nutrient_name')
            nutrient_values = request.form.getlist('nutrient_value')
            nutrition_info = []
            for n, v in zip(nutrient_names, nutrient_values):
                if not n:
                    continue
                try:
                    fv = float(v)
                except (ValueError, TypeError):
                    # skip invalid numeric values
                    continue
                nutrition_info.append({
                    "name": n,
                    "amount_per_unit_mass": fv
                })

            db.add_ingredient(
                name=name_dict,
                research_ids=research_ids,
                nutrition_data=nutrition_info,
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
            req_cook_ids = [int(x) for x in request.form.getlist('required_cooking_method_ids')]

            # cooking_instructions provided by dynamic multilingual fields created by JS
            ci_codes = request.form.getlist('cooking_instructions_codes')
            ci_texts = request.form.getlist('cooking_instructions_names') or request.form.getlist('cooking_instructions_texts')
            cooking_instructions = dict(zip(ci_codes, ci_texts)) if ci_codes and ci_texts else None

            # nutrition_info: get list entries or fallback to single calories field
            nutrition_info = []
            nut_names = request.form.getlist('nutrient_name')
            nut_values = request.form.getlist('nutrient_value')
            for n, v in zip(nut_names, nut_values):
                if n and v:
                    nutrition_info.append({"name": n, "amount_per_dish": float(v)})

            calories_field = request.form.get('calories')
            if calories_field:
                try:
                    cal_val = float(calories_field)
                    if not any(n.get('name') == 'Calories (Total)' for n in nutrition_info):
                        nutrition_info.insert(0, {"name": "Calories (Total)", "amount_per_dish": cal_val})
                except ValueError:
                    pass

            image_url = request.form.get('image_url') or None

            db.add_dish(
                name=name_dict,
                image_url=image_url,
                required_ingredient_ids=req_ing_ids,
                required_cooking_method_ids=req_cook_ids,
                nutrition_data=nutrition_info,
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
            mode = request.form['mode']
            start_date = request.form['start_date']
            processing_type = request.form.get('processing_type')

            # Validate start date format
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                flash("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.", 'danger')
                all_ingredients = db._load_table('ingredient')
                processing_options = db.PROCESSING_OPTIONS
                return render_template('add_storaged_ingredient_form.html', 
                                    all_ingredients=all_ingredients,
                                    processing_options=processing_options)

            # Get ingredient data for validation
            ingredient = next((item for item in db._load_table('ingredient') if item['id'] == storage_id), None)
            if not ingredient:
                flash(f"해당 ID({storage_id})의 식재료를 찾을 수 없습니다.", 'danger')
                all_ingredients = db._load_table('ingredient')
                return render_template('add_storaged_ingredient_form.html', all_ingredients=all_ingredients)

            # Additional validations based on mode
            today = datetime.now().date()
            start_date = start_date_obj.date()

            if start_date < today:
                flash("시작일은 오늘 이후여야 합니다.", 'danger')
                all_ingredients = db._load_table('ingredient')
                processing_options = db.PROCESSING_OPTIONS
                return render_template('add_storaged_ingredient_form.html',
                                    all_ingredients=all_ingredients,
                                    processing_options=processing_options)

            storage_data = {
                'storage_id': storage_id,
                'mass_g': mass_g,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'mode': mode,
                'processing_type': processing_type
            }

            if mode == 'production':
                # Check if ingredient is producible
                if not ingredient.get('production_time', {}).get('producible', False):
                    flash(f"선택한 식재료({ingredient['name'].get('kor', 'N/A')})는 생산이 불가능합니다.", 'danger')
                    all_ingredients = db._load_table('ingredient')
                    processing_options = db.PROCESSING_OPTIONS
                    return render_template('add_storaged_ingredient_form.html',
                                        all_ingredients=all_ingredients,
                                        processing_options=processing_options)

                # Calculate production time range
                min_time = ingredient['production_time'].get('min', 0)
                max_time = ingredient['production_time'].get('max', 0)
                
                min_end_date = start_date + timedelta(days=min_time)
                max_end_date = start_date + timedelta(days=max_time)
                
                storage_data['min_end_date'] = min_end_date.strftime('%Y-%m-%d')
                storage_data['max_end_date'] = max_end_date.strftime('%Y-%m-%d')
            else:  # storage mode
                # Get and validate expiration date only (end_date removed; expiration_date represents the storage end)
                expiration_date = request.form.get('expiration_date')
                if not expiration_date:
                    flash("보관 모드에서는 보관 기한을 입력해야 합니다.", 'danger')
                    all_ingredients = db._load_table('ingredient')
                    processing_options = db.PROCESSING_OPTIONS
                    return render_template('add_storaged_ingredient_form.html',
                                        all_ingredients=all_ingredients,
                                        processing_options=processing_options)

                try:
                    expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d')
                except ValueError:
                    flash("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.", 'danger')
                    all_ingredients = db._load_table('ingredient')
                    processing_options = db.PROCESSING_OPTIONS
                    return render_template('add_storaged_ingredient_form.html',
                                        all_ingredients=all_ingredients,
                                        processing_options=processing_options)

                # expiration_date must be after or equal to start_date (we consider same-day storage allowed)
                if expiration_date_obj.date() <= start_date:
                    flash("보관 기한은 시작일 이후여야 합니다.", 'danger')
                    all_ingredients = db._load_table('ingredient')
                    processing_options = db.PROCESSING_OPTIONS
                    return render_template('add_storaged_ingredient_form.html',
                                        all_ingredients=all_ingredients,
                                        processing_options=processing_options)

                storage_data['expiration_date'] = expiration_date

            # All validations passed, add the storaged ingredient
            db.add_storaged_ingredient(**storage_data)
            flash(f"{mode.capitalize()} 식재료가 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_storaged_ingredient_route'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    all_ingredients = db._load_table('ingredient')
    return render_template('add_storaged_ingredient_form.html', all_ingredients=all_ingredients)
