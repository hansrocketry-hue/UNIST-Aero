from flask import Blueprint, render_template
from .auth_routes import login_required

bp = Blueprint('home', __name__, url_prefix='/')

@bp.route('/')
@login_required
def index():
    """홈페이지를 렌더링합니다."""
    return render_template('index.html')
