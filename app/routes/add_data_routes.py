from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from .auth_routes import login_required
import database_handler as db
from datetime import datetime, timedelta

bp = Blueprint('add_data', __name__, url_prefix='/add')

def get_display_name(item, lang):
    """Return the name in the specified language, with a fallback to other languages."""
    if not isinstance(item.get('name'), dict):
        return item.get('name', 'N/A')
    return item['name'].get(lang) or item['name'].get('kor') or item['name'].get('eng') or list(item['name'].values())[0]

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

            # Parse required ingredients with amounts and types
            raw_item_types = request.form.getlist('item_types[]')
            raw_item_ids = request.form.getlist('item_ids[]')
            raw_item_amts = request.form.getlist('item_amounts[]')
            required_ingredients = []
            for i in range(min(len(raw_item_ids), len(raw_item_amts))):
                try:
                    item_type = raw_item_types[i] if i < len(raw_item_types) else 'ingredient'
                    item_id = raw_item_ids[i]  # Keep as string (supports both "i1" and "d1" format)
                    amt = float(raw_item_amts[i])
                except (ValueError, TypeError):
                    continue
                required_ingredients.append({"type": item_type, "id": item_id, "amount_g": amt})

            req_cook_ids = [int(x) for x in request.form.getlist('required_cooking_method_ids')]

            # cooking_instructions provided by dynamic multilingual fields created by JS
            ci_codes = request.form.getlist('cooking_instructions_codes')
            ci_texts = request.form.getlist('cooking_instructions_names') or request.form.getlist('cooking_instructions_texts')
            cooking_instructions = dict(zip(ci_codes, ci_texts)) if ci_codes and ci_texts else None

            # nutrition_info form inputs are ignored for dish creation — the backend will compute full
            # nutrition from ingredient g-per-nutrient values found in ingredient.json
            nutrition_info = []

            image_url = request.form.get('image_url') or None

            db.add_dish(
                name=name_dict,
                image_url=image_url,
                required_ingredients=required_ingredients,
                required_cooking_method_ids=req_cook_ids,
                nutrition_data=nutrition_info,
                cooking_instructions=cooking_instructions
            )
            flash(f"'{name_dict.get('kor', list(name_dict.values())[0])}' 요리가 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_dish_route'))
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    all_ingredients = db._load_table('ingredient')
    all_dishes = db._load_table('dish')
    all_cooking_methods = db._load_table('cooking-methods')
    
    # Add display names for the current language
    lang = session.get('lang', 'kor')
    for item in all_ingredients + all_dishes + all_cooking_methods:
        item['display_name'] = get_display_name(item, lang)
        
    return render_template('add_dish_form.html', 
                           all_ingredients=all_ingredients, 
                           all_dishes=all_dishes, 
                           all_cooking_methods=all_cooking_methods)

@bp.route('/storaged-ingredient', methods=['GET', 'POST'])
def add_storaged_ingredient_route():
    if request.method == 'POST':
        try:
            storage_id = request.form['storage_id']  # Keep as string (supports "i1" format)
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
                all_dishes = db._load_table('dish')
                processing_options = db.PROCESSING_OPTIONS
                return render_template('add_storaged_ingredient_form.html', 
                                    all_ingredients=all_ingredients,
                                    all_dishes=all_dishes,
                                    processing_options=processing_options)

            # Get item data for validation
            all_items = db._load_table('ingredient') + db._load_table('dish')
            item = next((it for it in all_items if it['id'] == storage_id), None)
            if not item:
                flash(f"해당 ID({storage_id})의 식재료 또는 요리를 찾을 수 없습니다.", 'danger')
                all_ingredients = db._load_table('ingredient')
                all_dishes = db._load_table('dish')
                return render_template('add_storaged_ingredient_form.html', all_ingredients=all_ingredients, all_dishes=all_dishes)

            # Additional validations based on mode
            start_date = start_date_obj.date()

            storage_data = {
                'storage_id': storage_id,
                'mass_g': mass_g,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'mode': mode,
                'processing_type': processing_type
            }

            if mode == 'production':
                # Check if ingredient is producible
                if not item.get('production_time', {}).get('producible', False):
                    flash(f"선택한 항목({item['name'].get('kor', 'N/A')})은 생산이 불가능합니다.", 'danger')
                    all_ingredients = db._load_table('ingredient')
                    all_dishes = db._load_table('dish')
                    processing_options = db.PROCESSING_OPTIONS
                    return render_template('add_storaged_ingredient_form.html',
                                        all_ingredients=all_ingredients,
                                        all_dishes=all_dishes,
                                        processing_options=processing_options)

                # Calculate production time range
                min_time = item['production_time'].get('min', 0)
                max_time = item['production_time'].get('max', 0)
                
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
                    all_dishes = db._load_table('dish')
                    processing_options = db.PROCESSING_OPTIONS
                    return render_template('add_storaged_ingredient_form.html',
                                        all_ingredients=all_ingredients,
                                        all_dishes=all_dishes,
                                        processing_options=processing_options)

                try:
                    expiration_date_obj = datetime.strptime(expiration_date, '%Y-%m-%d')
                except ValueError:
                    flash("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력해주세요.", 'danger')
                    all_ingredients = db._load_table('ingredient')
                    all_dishes = db._load_table('dish')
                    processing_options = db.PROCESSING_OPTIONS
                    return render_template('add_storaged_ingredient_form.html',
                                        all_ingredients=all_ingredients,
                                        all_dishes=all_dishes,
                                        processing_options=processing_options)

                # expiration_date must be after or equal to start_date (we consider same-day storage allowed)
                if expiration_date_obj.date() <= start_date:
                    flash("보관 기한은 시작일 이후여야 합니다.", 'danger')
                    all_ingredients = db._load_table('ingredient')
                    all_dishes = db._load_table('dish')
                    processing_options = db.PROCESSING_OPTIONS
                    return render_template('add_storaged_ingredient_form.html',
                                        all_ingredients=all_ingredients,
                                        all_dishes=all_dishes,
                                        processing_options=processing_options)

                storage_data['expiration_date'] = expiration_date

            # All validations passed, add the storaged ingredient
            db.add_storaged_ingredient(**storage_data)
            flash(f"{mode.capitalize()} 항목이 성공적으로 추가되었습니다.", 'success')
            return redirect(url_for('add_data.add_storaged_ingredient_route'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f"오류가 발생했습니다: {e}", 'danger')
    all_ingredients = db._load_table('ingredient')
    all_dishes = db._load_table('dish')
    return render_template('add_storaged_ingredient_form.html', all_ingredients=all_ingredients, all_dishes=all_dishes)

@bp.route('/nutrition-category', methods=['POST'])
@login_required
def add_nutrition_category_route():
    """새로운 영양 정보 카테고리 추가"""
    try:
        name = request.form.get('name')
        unit = request.form.get('unit')

        if not name or not unit:
            return jsonify({'success': False, 'message': 'Name and unit are required.'}), 400

        new_category = db.add_nutrition_category(name, unit)
        
        if new_category:
            return jsonify({'success': True, 'category': new_category})
        else:
            return jsonify({'success': False, 'message': 'Category already exists or another error occurred.'}), 409

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
