from flask import current_app
from flask_login import LoginManager

from .managers.database_manager import DatabaseManager
from .models.user import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    db_manager: DatabaseManager = current_app.config["DB_MANAGER"]
    user = db_manager.get_user_by_id(user_id)
    return user


def init_login_manager(app) -> None:
    login_manager.init_app(app)
    login_manager.login_view = "user.login"  # type: ignore
