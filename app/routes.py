import os

from flask import current_app, redirect, render_template, request, url_for
from werkzeug.wrappers.response import Response

from .core.database_manager import DatabaseManager


def initialize_routes(app):

    @app.route("/")
    def index() -> str:
        print(os.getcwd())
        return render_template("index.html")

    @app.route("/submit", methods=["POST"])
    def submit() -> Response:
        data = request.form["data"]
        db_manger: DatabaseManager = current_app.config["DB_MANAGER"]
        db_manger.db.test.insert_one({"data": data})
        return redirect(url_for("index"))
