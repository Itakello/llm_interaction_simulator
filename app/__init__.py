import os

from flask import Flask

from .auth import init_login_manager
from .blueprints import register_blueprints
from .managers.database_manager import DatabaseManager


def create_app() -> Flask:
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = os.getenv("SECRET_KEY", "mysecret")

    app.config["DB_MANAGER"] = DatabaseManager()

    init_login_manager(app)

    register_blueprints(app)

    return app
