from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from user_db_handler import get_user_by_id, update_user
from datetime import datetime, timedelta
import json
import os

bp = Blueprint('home', __name__, url_prefix='/')

# Define daily nutritional requirements
DAILY_REQUIREMENTS = {
    "calories": 2000,
    "carbohydrate": 300,
    "protein": 50,
    "dietary_fiber": 25,
    "vitamin_b1": 1.2,
    "vitamin_b2": 1.3,
    "vitamin_b3": 16,
    "vitamin_b6": 1.7,
    "vitamin_b12": 2.4,
    "folate": 400,
    "vitamin_c": 90,
    "vitamin_d": 15
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
        for entry in user['food_timeline']:
            if entry['date'] == today_str:
                today_timeline = entry
                for intake_item in entry['intake']:
                    for nutrient, value in intake_item['nutrients'].items():
                        if nutrient in todays_intake_total:
                            todays_intake_total[nutrient] += value
            elif entry['date'] == yesterday_str:
                yesterday_timeline = entry

    # Calculate percentage of daily requirement met
    nutrition_progress = {}
    for nutrient, total in todays_intake_total.items():
        requirement = DAILY_REQUIREMENTS.get(nutrient, 1)
        percentage = (total / requirement) * 100 if requirement > 0 else 0
        nutrition_progress[nutrient] = {
            "total": round(total, 2),
            "percentage": round(percentage, 2),
            "requirement": requirement
        }
    
    # Recommended food (placeholder)
    recommended_food = [
        {"name": "우주 비빔밥", "image": "https://via.placeholder.com/150"},
        {"name": "동결건조 과일 믹스", "image": "https://via.placeholder.com/150"}
    ]

    return render_template(
        'index.html',
        user=user,
        nutrition_progress=nutrition_progress,
        recommended_food=recommended_food,
        today_timeline=today_timeline,
        yesterday_timeline=yesterday_timeline
    )

# Helper to load main database for ingredients
def load_main_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', '..' , 'main_db.json')
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

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
            like_ids = [int(x) for x in request.form.getlist('like')]
            forbid_ids = [int(x) for x in request.form.getlist('forbid')]

            update_fields = {
                'height': height,
                'weight': weight,
                'like': like_ids,
                'forbid': forbid_ids
            }
            
            if update_user(user_id, update_fields):
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
    main_db = load_main_db()
    all_ingredients = main_db.get('ingredient', [])
    return render_template('edit_profile.html', user=user, all_ingredients=all_ingredients)