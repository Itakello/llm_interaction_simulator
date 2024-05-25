import os

from flask import Flask

from .auth import login_manager
from .blueprints.user_bp import user_bp
from .core.database_manager import DatabaseManager


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates")
    app.secret_key = os.getenv("SECRET_KEY", "mysecret")

    app.config["DB_MANAGER"] = DatabaseManager()

    login_manager.init_app(app)

    with app.app_context():
        from .routes import initialize_routes

        initialize_routes(app)
        app.register_blueprint(user_bp)

    return app
