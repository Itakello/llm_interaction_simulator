from flask import Blueprint, current_app, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug import Response

from ..managers.database_manager import DatabaseManager
from ..models.experiment import Experiment
from ..models.llm import LLM

# from ..models.role import Role

experiment_bp = Blueprint("experiment_bp", __name__)


@experiment_bp.route("/", methods=["GET"])
@login_required
@login_required
def index() -> str:
    db_manager: DatabaseManager = current_app.config["DB_MANAGER"]
    experiments = db_manager.get_experiments()
    return render_template("index.html", experiments=experiments)


@experiment_bp.route("/experiment/create", methods=["GET", "POST"])
@login_required
def create_experiment() -> Response | str:
    if request.method == "POST":
        db_manager: DatabaseManager = current_app.config["DB_MANAGER"]

        creator = db_manager.username
        starting_message = request.form["starting_message"]
        note = request.form["note"]
        favourite = "favourite" in request.form
        llms = request.form.getlist("llms")

        experiment = Experiment(
            starting_message=starting_message,
            note=note,
            favourite=favourite,
            creator=creator,
            llms_list=[LLM(model=llm) for llm in llms],
            roles_list=[],
            shared_sections_list=[],
            summarizer_sections_list=[],
            placeholders_list=[],
            conversation_ids=[],
        )

        db_manager.save_experiment(experiment)
        return redirect(url_for("experiment.list_experiments"))

    return render_template("create_experiment.html")
