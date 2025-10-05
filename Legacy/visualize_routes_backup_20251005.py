"""
백업: 2025년 10월 5일
수정된 visualize_routes.py의 게이지 계산 로직이 포함된 백업 파일
주요 변경사항: storaged-ingredient 시각화의 생산/저장 모드별 게이지 계산 로직
"""

from flask import Blueprint, render_template
import database_handler as db
from datetime import datetime
from dateutil.relativedelta import relativedelta
import re

bp = Blueprint('visualize', __name__, url_prefix='/visualize')

@bp.route('/storaged-ingredient')
def visualize_storaged_ingredient():
    """Storaged ingredient visualization page"""
    storaged_ingredients = db._load_table('storaged-ingredient')
    ingredients = db._load_table('ingredient')
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

        # 생산 모드인지 확인
        is_production = item.get('mode') == 'production'
        
        if is_production:
            # 생산 모드: min_end_date와 max_end_date 사용
            if not (item.get('min_end_date') and item.get('max_end_date')):
                continue
                
            try:
                min_end_date = datetime.strptime(item['min_end_date'], '%Y-%m-%d')
                max_end_date = datetime.strptime(item['max_end_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                continue

            # bar start should be the earlier of start_date and today
            bar_start = start_date if start_date < today else today
            bar_end = max_end_date
            span_days = (bar_end - bar_start).days
            if span_days <= 0:
                continue

            # positions relative to bar_start/span
            def pct(days):
                return max(0.0, min(100.0, (days / span_days) * 100.0))

            # compute key day offsets
            start_offset = (start_date - bar_start).days
            today_offset = (today - bar_start).days
            min_offset = (min_end_date - bar_start).days
            max_offset = (max_end_date - bar_start).days

            # grey: area between today and start if start in future
            grey_width = 0.0
            if start_date > today:
                grey_width = pct(start_offset - today_offset)  # start - today

            # green: from start to current_time (only if start <= today)
            green_left = pct(start_offset) if start_offset >= 0 else 0.0
            green_width = 0.0
            if today >= start_date:
                current_time = min(today, max_end_date)
                current_offset = (current_time - bar_start).days
                green_width = pct(max(0, current_offset - start_offset))

            # expected (sky-blue): from min_end_date to max_end_date
            expected_left = pct(min_offset)
            expected_width = pct(max_offset - min_offset)

            # marker for today's position relative to bar
            today_pos = pct(today_offset)
            start_pos = pct(start_offset)

            processed_item = {
                'name': ingredient_info['name'].get('kor', 'N/A'),
                'mass_g': item.get('mass_g'),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'is_production': True,
                'grey_width': grey_width,
                'green_left': green_left,
                'green_width': green_width,
                'expected_left': expected_left,
                'expected_width': expected_width,
                'today_pos': today_pos,
                'start_pos': start_pos,
                'min_end_date': min_end_date.strftime('%Y-%m-%d'),
                'max_end_date': max_end_date.strftime('%Y-%m-%d')
            }

        else:
            # 저장 모드: expiration_date 사용
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
            if total_duration <= 0:
                continue

            # 현재 진행률 계산 (시작일부터 현재까지)
            current_time = min(today, expiration_date)
            current_time = max(current_time, start_date)  # 시작일보다 이전이면 시작일 사용
            current_progress = ((current_time - start_date).days / total_duration) * 100

            processed_item = {
                'name': ingredient_info['name'].get('kor', 'N/A'),
                'mass_g': item.get('mass_g'),
                'start_date': start_date.strftime('%Y-%m-%d'),
                'is_production': False,
                'current_progress': current_progress,
                'expiration_date': expiration_date.strftime('%Y-%m-%d')
            }

        processed_storaged_ingredients.append(processed_item)

    return render_template('visualize_storaged_ingredient.html', 
                       storaged_ingredients=processed_storaged_ingredients,
                       today=today.strftime('%Y-%m-%d'))