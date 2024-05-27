import os

from flask import Flask

from .auth import login_manager
from .blueprints.experiment_bp import experiment_bp
from .blueprints.user_bp import user_bp
from .managers.database_manager import DatabaseManager


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = os.getenv("SECRET_KEY", "mysecret")

    app.config["DB_MANAGER"] = DatabaseManager()

    login_manager.init_app(app)

    with app.app_context():
        app.register_blueprint(user_bp)
        login_manager.login_view = "login"  # type: ignore
        app.register_blueprint(experiment_bp)

    return app
