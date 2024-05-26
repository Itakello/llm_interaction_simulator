from flask import current_app, redirect, render_template, request, url_for
from werkzeug.wrappers.response import Response

from .core.database_manager import DatabaseManager


def initialize_routes(app) -> None:

    @app.route("/")
    def index() -> str:
        db_manager: DatabaseManager = current_app.config["DB_MANAGER"]
        experiments = db_manager.get_experiments()
        return render_template("index.html", experiments=experiments)

    @app.route("/submit", methods=["POST"])
    def submit() -> Response:
        data = request.form["data"]
        db_manger: DatabaseManager = current_app.config["DB_MANAGER"]
        db_manger.db.test.insert_one({"data": data})
        return redirect(url_for("index"))
