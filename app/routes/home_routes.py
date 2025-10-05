from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from user_db_handler import get_user_by_id, update_user
from datetime import datetime, timedelta
import json
import os
import database_handler as db

bp = Blueprint('home', __name__, url_prefix='/')

def get_all_base_ingredients(dish_id, all_dishes_map):
    """Recursively find all base ingredients and their total amounts for a given dish."""
    base_ingredients = {}
    dish = all_dishes_map.get(dish_id)
    if not dish or 'required_ingredients' not in dish:
        return {}

    for item in dish.get('required_ingredients', []):
        item_id = item.get('id')
        item_type = item.get('type')
        amount = item.get('amount_g', 0)

        if item_type == 'ingredient':
            base_ingredients[item_id] = base_ingredients.get(item_id, 0) + amount
        elif item_type == 'dish':
            sub_ingredients = get_all_base_ingredients(item_id, all_dishes_map)
            # The amount of the sub-dish itself is not used here, as we are calculating the base ingredients.
            # If you needed to scale sub-ingredients by the sub-dish amount, you would do it here.
            for sub_id, sub_amount in sub_ingredients.items():
                base_ingredients[sub_id] = base_ingredients.get(sub_id, 0) + sub_amount
    
    return base_ingredients

def get_display_name(item, lang):
    """Return the name in the specified language, with a fallback to other languages."""
    if not isinstance(item.get('name'), dict):
        return item.get('name', 'N/A')
    return item['name'].get(lang) or item['name'].get('kor') or item['name'].get('eng') or list(item['name'].values())[0]

SCHOFIELD = {
    'male': [
        (0, 3, 59.512, -30.4),
        (3, 10, 22.706, 504.3),
        (10, 18, 17.686, 658.2),
        (18, 30, 15.057, 692.2),
        (30, 60, 11.472, 873.1),
        (60, 120, 11.711, 587.7),  # older-adult coeff (Schofield includes >60 variant)
    ],
    'female': [
        (0, 3, 58.317, -31.1),
        (3, 10, 20.315, 485.9),
        (10, 18, 13.384, 692.6),
        (18, 30, 14.818, 486.6),
        (30, 60, 8.126, 845.6),
        (60, 120, 9.082, 658.5),
    ]
}

def schofield_bmr(weight: float, age: int, sex: str) -> float:
    sex = sex.lower()
    if sex not in SCHOFIELD:
        raise ValueError("sex must be 'male' or 'female'")
    for (amin, amax, a, b) in SCHOFIELD[sex]:
        if amin <= age <= amax:
            return a * weight + b
    # fallback to closest age bracket
    brackets = SCHOFIELD[sex]
    if age < brackets[0][0]:
        a, b = brackets[0][2], brackets[0][3]
    else:
        a, b = brackets[-1][2], brackets[-1][3]
    return a * weight + b

PAL = [1.4, 1.55, 1.75, 1.9, 2.2]

@bp.route('/add-intake', methods=['GET', 'POST'])
def add_intake():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        date = request.form.get('date')
        time = request.form.get('time')
        food_id = request.form.get('food_id')
        intake_action = request.form.get('intake_action')  # Differentiate between 'consume' and 'log_only'

        user = get_user_by_id(session['user_id'])
        dishes = db._load_table('dish')
        selected_dish = next((dish for dish in dishes if dish['id'] == food_id), None)

        if not selected_dish:
            flash('Selected dish not found', 'error')
            return redirect(url_for('home.add_intake'))

        if intake_action == 'consume':
            all_dishes_map = {dish['id']: dish for dish in dishes}
            total_required_ingredients = get_all_base_ingredients(food_id, all_dishes_map)

            storaged_ingredients = db._load_table('storaged-ingredient')
            
            # 1. Check stock for all base ingredients
            for ing_id, ing_amount in total_required_ingredients.items():
                stock_item = next((item for item in storaged_ingredients if item.get('storage-id') == ing_id and item.get('mode') == 'storage'), None)
                if not stock_item or stock_item.get('mass_g', 0) < ing_amount:
                    ingredients = db._load_table('ingredient')
                    ingredient = next((ing for ing in ingredients if ing['id'] == ing_id), None)
                    ingredient_name = get_display_name(ingredient, session.get('lang', 'kor')) if ingredient else 'Unknown Ingredient'
                    flash(f'"{ingredient_name}" is out of stock to make this dish.', 'error')
                    return redirect(url_for('home.add_intake'))

            # 2. Deduct all base ingredients from stock
            for ing_id, ing_amount in total_required_ingredients.items():
                for item in storaged_ingredients:
                    if item.get('storage-id') == ing_id and item.get('mode') == 'storage':
                        item['mass_g'] -= ing_amount
                        break
            
            db._save_table('storaged-ingredient', storaged_ingredients)

        new_intake = {"time": time, "dish_id": food_id}

        if 'food_timeline' not in user:
            user['food_timeline'] = []

        date_entry = next((entry for entry in user['food_timeline'] if entry['date'] == date), None)
        if date_entry:
            if 'intake' not in date_entry:
                date_entry['intake'] = []
            date_entry['intake'].append(new_intake)
        else:
            user['food_timeline'].append({'date': date, 'intake': [new_intake]})

        user['food_timeline'].sort(key=lambda x: x['date'], reverse=True)
        update_user(session['user_id'], user)
        flash('{% if session.get("lang","kor") == "eng" %}Food intake added successfully{% else %}섭취 기록이 추가되었습니다{% endif %}', 'success')
        return redirect(url_for('home.index'))

    dishes = db._load_table('dish')
    lang = session.get('lang', 'kor')
    for dish in dishes:
        dish['display_name'] = get_display_name(dish, lang)
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_intake_form.html', dishes=dishes, today=today)

# Define daily nutritional requirements
DAILY_REQUIREMENTS = {
    "Calories (Total)": 2000,
    "Carbohydrates": 300,
    "Protein": 50,
    "Dietary Fiber": 25,
    "Vitamin B1 (Thiamin)": 1.2,
    "Vitamin B2 (Riboflavin)": 1.3,
    "Vitamin B3 (Niacin)": 16,
    "Vitamin B6": 1.7,
    "Vitamin D": 15,
    "Folate": 400,
    "Vitamin C": 90,
    "Vitamin B12" : 2.4,
    "Fat":0,
    "Sodium":2000
}

NUTRIENT_UNITS = {
    "Calories (Total)": "kcal",
    "Carbohydrates": "g",
    "Protein": "g",
    "Dietary Fiber": "g",
    "Fat": "g",
    "Sodium": "mg",
    "Vitamin B1 (Thiamin)": "mg",
    "Vitamin B2 (Riboflavin)": "mg",
    "Vitamin B3 (Niacin)": "mg",
    "Vitamin B6": "mg",
    "Vitamin C": "mg",
    "Folate": "μg",
    "Vitamin B12": "μg",
    "Vitamin D": "μg",
    # 다른 영양소 단위도 필요시 추가
}

@bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user = get_user_by_id(user_id)

    if not user:
        return redirect(url_for('auth.logout'))

    today_str = datetime.now().strftime('%Y-%m-%d')
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    todays_intake_total = {key: 0 for key in DAILY_REQUIREMENTS.keys()}
    
    today_timeline = None
    yesterday_timeline = None

    if 'food_timeline' in user:
        dishes = db._load_table('dish')
        dish_map = {dish['id']: dish for dish in dishes}

        for entry in user['food_timeline']:
            if entry['date'] == today_str:
                today_timeline = entry
                for intake_item in entry.get('intake', []):
                    dish = dish_map.get(intake_item.get('dish_id'))
                    if dish and 'nutrition_info' in dish:
                        dish_mass = db.get_dish_total_mass(dish)
                        for item in dish['nutrition_info']:
                            if item['name'] in todays_intake_total:
                                per_gram = item.get('amount_per_unit_mass', 0)
                                todays_intake_total[item['name']] += per_gram * dish_mass
            elif entry['date'] == yesterday_str:
                yesterday_timeline = entry

    nutrition_progress = {}
    bmr = schofield_bmr(user['weight'], user['age'], user['gender'])
    pal = user['activity_level']

    DAILY_REQUIREMENTS['Calories (Total)'] = bmr * pal
    DAILY_REQUIREMENTS['Protein'] = bmr * pal * 0.25 / 4
    DAILY_REQUIREMENTS['Fat'] = bmr * pal * 0.25 / 4
    DAILY_REQUIREMENTS['Carbohydrates'] = bmr * pal * 0.5 / 4

    for nutrient, total in todays_intake_total.items():
        requirement = DAILY_REQUIREMENTS.get(nutrient, 1)
        percentage = (total / requirement) * 100 if requirement > 0 else 0
        nutrition_progress[nutrient] = {
            "total": round(total, 2),
            "percentage": round(percentage, 2),
            "requirement": requirement,
            "unit": NUTRIENT_UNITS.get(nutrient, '')
        }
    
    all_dishes = db._load_table('dish')
    stored_ingredients = db._load_table('storaged-ingredient')
    
    available_ingredients = {}
    for item in stored_ingredients:
        if item.get('mode') == 'storage':
            ingredient_id = item.get('storage-id')
            mass = item.get('mass_g', 0)
            if ingredient_id:
                available_ingredients[ingredient_id] = available_ingredients.get(ingredient_id, 0) + mass

    scored_dishes = []
    like_ingredients = user.get('like', [])
    forbid_ingredients = user.get('forbid', [])

    for dish in all_dishes:
        is_makeable = True
        has_forbid_ingredient = False
        
        if dish.get('required_ingredients'):
            for req in dish['required_ingredients']:
                if req.get('id') in forbid_ingredients:
                    has_forbid_ingredient = True
                    break
        if has_forbid_ingredient:
            continue

        if dish.get('required_ingredients'):
            for req in dish['required_ingredients']:
                if available_ingredients.get(req.get('id'), 0) < req.get('amount_g', 0):
                    is_makeable = False
                    break
        
        if is_makeable:
            nutrition_score = 0
            preference_score = 0
            if dish.get('nutrition_info'):
                dish_mass = db.get_dish_total_mass(dish)
                for info in dish['nutrition_info']:
                    nutrient_name = info.get('name')
                    per_gram = info.get('amount_per_unit_mass', 0)
                    nutrient_amount = per_gram * dish_mass
                    requirement = DAILY_REQUIREMENTS.get(nutrient_name, 0)
                    intake = todays_intake_total.get(nutrient_name, 0)
                    gap = requirement - intake
                    if gap > 0 and requirement > 0:
                        nutrition_score += (nutrient_amount / requirement) * 100

            if dish.get('required_ingredients'):
                for req in dish['required_ingredients']:
                    if req.get('id') in like_ingredients:
                        preference_score += 50

            total_score = nutrition_score + preference_score
            scored_dishes.append({'dish': dish, 'score': total_score})

    scored_dishes.sort(key=lambda x: x['score'], reverse=True)
    
    recommended_food = []
    lang = session.get('lang', 'kor')
    for scored_dish in scored_dishes[:3]:
        dish_data = scored_dish['dish']
        recommended_food.append({
            'id': dish_data.get('id'),
            'name': get_display_name(dish_data, lang),
            'image': dish_data.get('image_url')
        })

    dishes = db._load_table('dish')
    dish_map = {dish['id']: dish for dish in dishes}
    
    return render_template(
        'index.html',
        user=user,
        nutrition_progress=nutrition_progress,
        recommended_food=recommended_food,
        today_timeline=today_timeline,
        yesterday_timeline=yesterday_timeline,
        dish_map=dish_map,
        get_display_name=get_display_name
    )

@bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    user = get_user_by_id(user_id)

    if request.method == 'POST':
        try:
            height = int(request.form['height'])
            weight = int(request.form['weight'])
            age = int(request.form.get('age', user.get('age', 30)))
            like_ids = [int(x) for x in request.form.getlist('like')]
            forbid_ids = [int(x) for x in request.form.getlist('forbid')]
            language = request.form.get('language', 'kor')

            update_fields = {
                'height': height,
                'weight': weight,
                'age': age,
                'like': like_ids,
                'forbid': forbid_ids,
                'language': language
            }
            
            if update_user(user_id, update_fields):
                # update session language if changed
                session['lang'] = language
                flash('프로필이 성공적으로 업데이트되었습니다.', 'success')
                return redirect(url_for('home.index'))
            else:
                flash('프로필 업데이트에 실패했습니다.', 'danger')
        except ValueError:
            flash('키와 몸무게는 숫자로 입력해야 합니다.', 'danger')
        except Exception as e:
            flash(f'오류가 발생했습니다: {e}', 'danger')
        
        return redirect(url_for('home.edit_profile'))

    # GET request
    all_ingredients = db._load_table('ingredient')
    return render_template('edit_profile.html', user=user, all_ingredients=all_ingredients)