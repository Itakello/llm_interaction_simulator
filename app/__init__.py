from flask import Flask

from .core.database_manager import DatabaseManager


def create_app():
    app = Flask(__name__, template_folder="../templates")

    app.config["DB_MANAGER"] = DatabaseManager()

    with app.app_context():
        from .routes import initialize_routes

        initialize_routes(app)

    return app
