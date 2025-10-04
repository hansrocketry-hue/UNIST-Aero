from flask import Blueprint, render_template

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('/')
def index():
    """홈페이지를 렌더링합니다."""
    return render_template('index.html')
