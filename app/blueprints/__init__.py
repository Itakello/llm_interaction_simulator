from .experiment_bp import experiment_bp
from .user_bp import user_bp


def register_blueprints(app) -> None:
    app.register_blueprint(experiment_bp)
    app.register_blueprint(user_bp)
