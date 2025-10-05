from flask import Flask
import os

def create_app():
    """Flask 애플리케이션을 생성하고 블루프린트를 등록합니다."""
    app = Flask(__name__)
    # Ensure templates are reloaded automatically during development
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.auto_reload = True
    app.config['SECRET_KEY'] = os.urandom(24) # 세션을 위한 비밀 키 설정

    # 블루프린트 import 및 등록
    from .routes import home_routes, add_data_routes, auth_routes, visualize_routes
    app.register_blueprint(home_routes.bp)
    app.register_blueprint(add_data_routes.bp)
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(visualize_routes.bp)

    return app
