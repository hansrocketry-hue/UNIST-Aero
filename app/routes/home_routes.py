from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from user_db_handler import get_user_by_id, update_user
from datetime import datetime, timedelta
import json
import os
import database_handler as db

bp = Blueprint('home', __name__, url_prefix='/')

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
        # Get form data
        date = request.form.get('date')
        time = request.form.get('time')
        food_id = request.form.get('food_id')

        # Load user and dish data
        user = get_user_by_id(session['user_id'])
        dishes = db._load_table('dish')
        selected_dish = next((dish for dish in dishes if dish['id'] == int(food_id)), None)

        if not selected_dish:
            flash('Selected dish not found', 'error')
            return redirect(url_for('home.add_intake'))

        # Create intake entry with dish_id only
        new_intake = {
            "time": time,
            "dish_id": int(food_id)
        }

        # Update user's food timeline
        if 'food_timeline' not in user:
            user['food_timeline'] = []

        # Find or create date entry
        date_entry = next((entry for entry in user['food_timeline'] if entry['date'] == date), None)
        if date_entry:
            if 'intake' not in date_entry:
                date_entry['intake'] = []
            date_entry['intake'].append(new_intake)
        else:
            user['food_timeline'].append({
                'date': date,
                'intake': [new_intake]
            })

        # Sort food timeline by date (most recent first)
        user['food_timeline'].sort(key=lambda x: x['date'], reverse=True)

        # Update user data
        update_user(session['user_id'], user)
        flash('{% if session.get("lang","kor") == "eng" %}Food intake added successfully{% else %}섭취 기록이 추가되었습니다{% endif %}', 'success')
        return redirect(url_for('home.index'))

    # GET request - show form
    dishes = db._load_table('dish')
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('add_intake_form.html', 
                         dishes=dishes, 
                         today=today)

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
        # This case might happen if the user was deleted but the session still exists
        return redirect(url_for('auth.logout'))

    # Calculate today's total nutrient intake
    today_str = datetime.now().strftime('%Y-%m-%d')
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    todays_intake_total = {key: 0 for key in DAILY_REQUIREMENTS.keys()}
    
    today_timeline = None
    yesterday_timeline = None

    if 'food_timeline' in user:
        # Load dishes for nutrition lookup
        dishes = db._load_table('dish')
        dish_map = {dish['id']: dish for dish in dishes}

        for entry in user['food_timeline']:
            if entry['date'] == today_str:
                today_timeline = entry
                for intake_item in entry['intake']:
                    # Get dish from dish_id and add its nutrition to totals
                    dish = dish_map.get(intake_item.get('dish_id'))
                    if dish and 'nutrition_info' in dish:
                        for item in dish['nutrition_info']:
                            if item['name'] in todays_intake_total:
                                todays_intake_total[item['name']] +=  item['amount_per_dish']
            elif entry['date'] == yesterday_str:
                yesterday_timeline = entry
        print(todays_intake_total)

    # Calculate percentage of daily requirement met
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
    
    # Recommended food (placeholder)
    recommended_food = [
        {"name": "우주 비빔밥", "image": "https://via.placeholder.com/150"},
        {"name": "동결건조 과일 믹스", "image": "https://via.placeholder.com/150"}
    ]

    # Load all dishes for displaying names
    dishes = db._load_table('dish')
    dish_map = {dish['id']: dish for dish in dishes}
    
    return render_template(
        'index.html',
        user=user,
        nutrition_progress=nutrition_progress,
        recommended_food=recommended_food,
        today_timeline=today_timeline,
        yesterday_timeline=yesterday_timeline,
        dish_map=dish_map
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