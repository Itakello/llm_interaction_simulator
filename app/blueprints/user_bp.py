from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user
from werkzeug import Response
from werkzeug.security import check_password_hash, generate_password_hash

from ..core.database_manager import DatabaseManager
from ..models.user import User

user_bp = Blueprint("user", __name__)


@user_bp.route("/register", methods=["GET", "POST"])
def register() -> Response | str:
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        db_manager: DatabaseManager = current_app.config["DB_MANAGER"]
        if db_manager.get_user_by_username(username):
            flash("Username already exists")
            return redirect(url_for("user.register"))

        user = User(username=username, password=hashed_password)
        db_manager.insert_user(user)
        flash("Registration successful! Please log in.")
        return redirect(url_for("user.login"))

    return render_template("register.html")


@user_bp.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db_manager: DatabaseManager = current_app.config["DB_MANAGER"]
        user = db_manager.get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("index"))

        flash("Invalid username or password")
        return redirect(url_for("user.login"))

    return render_template("login.html")


@user_bp.route("/logout")
# @login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for("user.login"))
